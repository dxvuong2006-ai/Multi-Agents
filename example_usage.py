"""
Ví dụ cách sử dụng hệ thống Multi-Agent 
từ Python script (không cần Streamlit)
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Import từ hệ thống multi-agent
from multi_agent_system import create_multi_agent_system

# Import các công cụ cần thiết
import pickle
import pandas as pd
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_community.retrievers import BM25Retriever
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.retrievers.ensemble import EnsembleRetriever

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools.retriever import create_retriever_tool
from langchain.tools import tool

# Khởi tạo biến môi trường
load_dotenv()

# ============================================================================
# BƯỚC 1: Khởi tạo Vector Store
# ============================================================================

def setup_vectorstore():
    """Khởi tạo hoặc tải vector store"""
    print("📚 Khởi tạo vector store...")
    
    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    FAISS_PATH = "faiss_index_conversation"
    SPLITS_PATH = "splits_conversation.pkl"
    
    # Cố gắng tải vector store có sẵn
    if os.path.exists(FAISS_PATH):
        print("✅ Tải vector store có sẵn...")
        vectorstore = FAISS.load_local(
            folder_path=FAISS_PATH,
            embeddings=embedding,
            allow_dangerous_deserialization=True
        )
        with open(SPLITS_PATH, "rb") as f:
            splits = pickle.load(f)
    else:
        # Nếu chưa có, tạo mới từ PDF
        print("📖 Đọc tài liệu PDF...")
        all_docs = []
        try:
            document_loader = DirectoryLoader(
                "./data",
                glob="**/*.pdf",
                loader_cls=PyMuPDFLoader
            )
            all_docs = document_loader.load()
            print(f"✅ Đã tải {len(all_docs)} tài liệu")
        except Exception as e:
            print(f"⚠️  Lỗi tải tài liệu: {e}")
            all_docs = []
        
        # Tạo vector store
        if all_docs:
            print("✂️  Chia nhỏ tài liệu...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1200,
                chunk_overlap=300
            )
            splits = text_splitter.split_documents(all_docs)
            
            print("🔄 Tạo embeddings...")
            vectorstore = FAISS.from_documents(
                documents=splits,
                embedding=embedding,
                distance_strategy=DistanceStrategy.COSINE
            )
            
            # Lưu lại
            vectorstore.save_local(FAISS_PATH)
            with open(SPLITS_PATH, "wb") as f:
                pickle.dump(splits, f)
            print("✅ Vector store tạo thành công")
        else:
            print("⚠️  Tạo vector store rỗng")
            from langchain_core.documents import Document
            vectorstore = FAISS.from_documents(
                documents=[Document(page_content="dummy")],
                embedding=embedding
            )
            splits = []
    
    return vectorstore, splits, embedding

# ============================================================================
# BƯỚC 2: Tạo các Tool cần thiết
# ============================================================================

def setup_tools(vectorstore, splits):
    """Tạo các tool cho agent"""
    print("\n🔧 Khởi tạo các công cụ...")
    
    # Ensemble Retriever
    if splits:
        bm25_retriever = BM25Retriever.from_documents(splits)
        bm25_retriever.k = 3
        vector_retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[0.4, 0.6]
        )
    else:
        ensemble_retriever = vectorstore.as_retriever()
    
    # Retriever Tool
    retriever_tool = create_retriever_tool(
        ensemble_retriever,
        name="search_financial_documents",
        description="Tìm kiếm lý thuyết phân tích kỹ thuật, quy tắc giao dịch từ tài liệu."
    )
    
    # Stock Analysis Tool
    @tool
    def analyze_stock_data(ticker: str, analysis_type: str) -> str:
        """
        Trích xuất dữ liệu giá và xu hướng của một mã chứng khoán.
        - ticker: Mã chứng khoán (ví dụ: GC=F, AAPL)
        - analysis_type: 'recent_price' hoặc 'trend'
        """
        try:
            data_dir = Path("data")
            file_pattern = f"{ticker.replace('=', '_')}_historical_*.parquet"
            
            matching_files = list(data_dir.glob(file_pattern))
            if not matching_files:
                return f"Không tìm thấy dữ liệu cho {ticker}"
            
            latest_file = max(matching_files, key=os.path.getmtime)
            df = pd.read_parquet(latest_file)
            
            if analysis_type == "recent_price":
                recent = df.tail(5)[['date', 'close', 'daily_return']]
                return f"Giá 5 phiên gần nhất:\n{recent.to_string()}"
            
            elif analysis_type == "trend":
                df['MA10'] = df['close'].rolling(window=10).mean()
                recent = df.tail(10)[['date', 'close', 'MA10']]
                return f"Xu hướng:\n{recent.to_string()}"
            
            else:
                return "analysis_type phải là 'recent_price' hoặc 'trend'"
        
        except Exception as e:
            return f"Lỗi: {str(e)}"
    
    print("✅ Công cụ khởi tạo thành công")
    
    return {
        "retriever_tool": retriever_tool,
        "vectorstore": vectorstore,
        "analyze_tool": analyze_stock_data
    }

# ============================================================================
# BƯỚC 3: Khởi tạo LLM và Multi-Agent System
# ============================================================================

def setup_multi_agent(tools_dict):
    """Khởi tạo hệ thống multi-agent"""
    print("\n🤖 Khởi tạo hệ thống multi-agent...")
    
    google_model = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
    llm = ChatGoogleGenerativeAI(
        model=google_model,
        temperature=0.3
    )
    
    coordinator = create_multi_agent_system(llm, tools_dict)
    
    print("✅ Hệ thống multi-agent sẵn sàng")
    return coordinator

# ============================================================================
# ÍDỤ 1: Phân tích Toàn diện
# ============================================================================

def example_1_full_analysis(coordinator):
    """Ví dụ 1: Phân tích toàn diện một mã chứng khoán"""
    print("\n" + "="*60)
    print("VÍ DỤ 1: PHÂN TÍCH TOÀN DIỆN")
    print("="*60)
    
    ticker = "AAPL"
    print(f"\nPhân tích {ticker}...")
    
    results = coordinator.analyze_ticker(ticker, analysis_type="full")
    
    # Hiển thị kết quả
    print("\n📈 PHÂN TÍCH KỸ THUẬT:")
    print("-" * 60)
    print(results["analyses"]["technical"][:500] + "...\n")
    
    print("📚 THÔNG TIN CƠ BẢN:")
    print("-" * 60)
    print(results["analyses"]["fundamental"][:500] + "...\n")
    
    print("💡 CHIẾN LƯỢC GIAO DỊCH:")
    print("-" * 60)
    print(results["analyses"]["strategy"][:500] + "...\n")
    
    # Lưu kết quả
    with open(f"results_{ticker}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ Kết quả lưu vào results_{ticker}.json\n")

# ============================================================================
# VÍ DỤ 2: Hỏi Agent Cụ Thể
# ============================================================================

def example_2_ask_specific_agent(coordinator):
    """Ví dụ 2: Hỏi các agent cụ thể"""
    print("="*60)
    print("VÍ DỤ 2: HỎI AGENT CỤ THỂ")
    print("="*60)
    
    # Hỏi Research Agent
    print("\n🔍 Hỏi Research Agent...")
    print("-" * 60)
    research_q = "Hãy tìm kiếm thông tin về các phương pháp phân tích kỹ thuật hiệu quả"
    response = coordinator.ask_agents(research_q, target_agent="research")
    print(f"Q: {research_q}")
    print(f"A: {response[:400]}...\n")
    
    # Hỏi Analyst Agent
    print("📊 Hỏi Analyst Agent...")
    print("-" * 60)
    analyst_q = "Phân tích GC=F (Vàng). Hiện tại là trend tăng hay giảm?"
    response = coordinator.ask_agents(analyst_q, target_agent="analyst")
    print(f"Q: {analyst_q}")
    print(f"A: {response[:400]}...\n")
    
    # Hỏi Strategy Agent
    print("💼 Hỏi Strategy Agent...")
    print("-" * 60)
    strategy_q = "Dựa trên xu hướng hiện tại, tôi có nên mua vàng (GC=F) không?"
    response = coordinator.ask_agents(strategy_q, target_agent="strategy")
    print(f"Q: {strategy_q}")
    print(f"A: {response[:400]}...\n")

# ============================================================================
# VÍ DỤ 3: Phân tích Nhiều Mã Cùng Lúc
# ============================================================================

def example_3_analyze_multiple(coordinator):
    """Ví dụ 3: Phân tích nhiều mã chứng khoán"""
    print("="*60)
    print("VÍ DỤ 3: PHÂN TÍCH NHIỀU MÃ")
    print("="*60)
    
    tickers = ["AAPL", "GC=F"]
    results_summary = {}
    
    for ticker in tickers:
        print(f"\nPhân tích {ticker}...")
        results = coordinator.analyze_ticker(ticker, analysis_type="technical")
        results_summary[ticker] = {
            "analysis": results["analyses"]["technical"][:300],
            "timestamp": results["timestamp"]
        }
    
    # Tổng hợp
    print("\n📊 TỔNG HỢP:")
    print("-" * 60)
    for ticker, data in results_summary.items():
        print(f"\n{ticker}:")
        print(data["analysis"] + "...\n")

# ============================================================================
# VÍ DỤ 4: So Sánh Quan Điểm Giữa Các Agent
# ============================================================================

def example_4_compare_agents(coordinator):
    """Ví dụ 4: So sánh quan điểm của các agent"""
    print("="*60)
    print("VÍ DỤ 4: SO SÁNH QUAN ĐIỂM CÁC AGENT")
    print("="*60)
    
    ticker = "AAPL"
    question_prefix = f"Với mã chứng khoán {ticker}, "
    
    questions = {
        "research": question_prefix + "hãy tìm kiếm thông tin để hỗ trợ quyết định giao dịch",
        "analyst": question_prefix + "phân tích dữ liệu kỹ thuật gần đây",
        "strategy": question_prefix + "đưa ra chiến lược giao dịch cụ thể"
    }
    
    comparison = {}
    
    for agent_type, question in questions.items():
        print(f"\n[{agent_type.upper()}]")
        print("-" * 60)
        response = coordinator.ask_agents(question, target_agent=agent_type)
        comparison[agent_type] = response
        print(response[:500] + "...\n")
    
    # Lưu so sánh
    with open(f"comparison_{ticker}.json", "w", encoding="utf-8") as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)
    print(f"✅ So sánh lưu vào comparison_{ticker}.json")

# ============================================================================
# MAIN: Chạy Các Ví Dụ
# ============================================================================

def main():
    """Hàm chính"""
    print("🚀 HỆ THỐNG MULTI-AGENT PHÂN TÍCH TÀI CHÍNH")
    print("=" * 60)
    
    # Bước 1: Khởi tạo
    vectorstore, splits, embedding = setup_vectorstore()
    tools_dict = setup_tools(vectorstore, splits)
    coordinator = setup_multi_agent(tools_dict)
    
    # Bước 2: Chạy các ví dụ
    print("\n✨ Bắt đầu các ví dụ...")
    
    # Uncomment các ví dụ bạn muốn chạy:
    
    # Ví dụ 1: Phân tích toàn diện
    example_1_full_analysis(coordinator)
    
    # Ví dụ 2: Hỏi agent cụ thể
    example_2_ask_specific_agent(coordinator)
    
    # Ví dụ 3: Phân tích nhiều mã
    # example_3_analyze_multiple(coordinator)
    
    # Ví dụ 4: So sánh quan điểm
    # example_4_compare_agents(coordinator)
    
    print("\n" + "="*60)
    print("✅ HOÀN THÀNH!")
    print("="*60)
    
    # Xóa lịch sử khi kết thúc
    coordinator.clear_all_histories()

if __name__ == "__main__":
    main()
