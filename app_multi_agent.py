"""
Ứng dụng Streamlit sử dụng hệ thống Multi-Agent
Cho phép người dùng tương tác với nhiều agent khác nhau
"""

import pickle 
import os
import pandas as pd
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
import extract_data 
from datetime import datetime
import json

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

from multi_agent_system import create_multi_agent_system

# Cấu hình
load_dotenv()
st.set_page_config(
    page_title="Multi-Agent Finance Analyzer",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Multi-Agent Finance Analyzer")
st.markdown("Hệ thống phân tích tài chính với nhiều agent chuyên biệt")

# Khởi tạo embeddings
if "embedding" not in st.session_state:
    st.session_state.embedding = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
embedding = st.session_state.embedding

# Tham số
FAISS_PATH = "faiss_index_conversation"
SPLITS_PATH = "splits_conversation.pkl"
REBUILD = False  # Đặt thành True để rebuild vector store

# Xử lí tài liệu văn bản
@st.cache_resource
def load_or_build_vectorstore():
    if not REBUILD and os.path.exists(FAISS_PATH):
        vectorstore = FAISS.load_local(
            folder_path=FAISS_PATH,
            embeddings=embedding,
            allow_dangerous_deserialization=True
        )
        with open(SPLITS_PATH, "rb") as f:
            splits = pickle.load(f)
        return vectorstore, splits
    else:
        st.info("Đang đọc và băm nhỏ tài liệu lý thuyết...")
        all_docs = []
        try:
            document_finance = DirectoryLoader(
                "./data",
                glob="**/*.pdf",
                loader_cls=PyMuPDFLoader
            )
            all_docs.extend(document_finance.load())
        except Exception as e:
            st.warning(f"Không thể tải tài liệu PDF: {e}")
            all_docs = []
        
        if all_docs:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1200,
                chunk_overlap=300
            )
            splits = text_splitter.split_documents(all_docs)
            vectorstore = FAISS.from_documents(
                documents=splits,
                embedding=embedding,
                distance_strategy=DistanceStrategy.COSINE
            )
            vectorstore.save_local(FAISS_PATH)
            with open(SPLITS_PATH, "wb") as f:
                pickle.dump(splits, f)
        else:
            # Tạo vectorstore rỗng nếu không có tài liệu
            from langchain_core.documents import Document
            dummy_docs = [Document(page_content="dummy")]
            vectorstore = FAISS.from_documents(
                documents=dummy_docs,
                embedding=embedding
            )
            splits = []
        
        return vectorstore, splits

vectorstore, splits = load_or_build_vectorstore()

# Khởi tạo ensemble retriever
if "ensemble_retriever" not in st.session_state:
    if splits:
        bm25_retriever = BM25Retriever.from_documents(splits)
        bm25_retriever.k = 3
        vector_retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        st.session_state.ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[0.4, 0.6]
        )
    else:
        st.session_state.ensemble_retriever = vectorstore.as_retriever()

# Tạo retriever tool
retriever_tool = create_retriever_tool(
    st.session_state.ensemble_retriever,
    name="search_financial_documents",
    description="Tìm kiếm lý thuyết phân tích kỹ thuật, quy tắc giao dịch hoặc tin tức từ các tài liệu."
)

# Công cụ phân tích dữ liệu cổ phiếu
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
            return f"Không tìm thấy dữ liệu cho {ticker}. Vui lòng kéo dữ liệu trước."
        
        latest_file = max(matching_files, key=os.path.getmtime)
        df = pd.read_parquet(latest_file)
        
        if analysis_type == "recent_price":
            recent = df.tail(5)[['date', 'close', 'daily_return']].copy()
            recent['daily_return'] = (recent['daily_return'] * 100).round(2)
            return f"Giá 5 phiên gần nhất của {ticker}:\n{recent.to_string(index=False)}"
        
        elif analysis_type == "trend":
            df['MA10'] = df['close'].rolling(window=10).mean()
            df['MA20'] = df['close'].rolling(window=20).mean()
            recent = df.tail(10)[['date', 'close', 'MA10', 'MA20']].copy()
            trend = "Tăng" if recent['close'].iloc[-1] > recent['close'].iloc[-5] else "Giảm"
            return f"Xu hướng {ticker} (10 phiên gần nhất):\n{recent.to_string(index=False)}\nXu hướng: {trend}"
        
        else:
            return "analysis_type phải là 'recent_price' hoặc 'trend'"
    
    except Exception as e:
        return f"Lỗi khi phân tích: {str(e)}"

# Khởi tạo LLM
if "llm" not in st.session_state:
    google_model = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
    st.session_state.llm = ChatGoogleGenerativeAI(
        model=google_model,
        temperature=0.3
    )

# Khởi tạo hệ thống multi-agent
if "coordinator" not in st.session_state:
    st.session_state.coordinator = create_multi_agent_system(
        st.session_state.llm,
        {
            "retriever_tool": retriever_tool,
            "vectorstore": vectorstore,
            "analyze_tool": analyze_stock_data
        }
    )

# Giao diện chính
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📊 Chọn chế độ phân tích")
    analysis_mode = st.radio(
        "Chế độ:",
        ["Phân tích Toàn diện", "Phân tích Kỹ thuật", "Hỏi Agent Cụ thể"],
        horizontal=True
    )

with col2:
    if st.button("🔄 Xóa Lịch sử"):
        st.session_state.coordinator.clear_all_histories()
        st.success("Đã xóa lịch sử!")

st.divider()

# Tab 1: Phân tích toàn diện
if analysis_mode == "Phân tích Toàn diện":
    st.markdown("### 🎯 Phân tích Toàn diện Mã Chứng khoán")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        ticker = st.text_input("Nhập mã chứng khoán:", "AAPL").upper()
    with col2:
        if st.button("Phân tích", use_container_width=True):
            if ticker:
                with st.spinner(f"Đang phân tích {ticker}..."):
                    results = st.session_state.coordinator.analyze_ticker(
                        ticker,
                        analysis_type="full"
                    )
                
                # Hiển thị kết quả
                st.success("✅ Phân tích hoàn thành!")
                
                with col1:
                    # Phân tích Kỹ thuật
                    with st.expander("📈 Phân tích Kỹ thuật", expanded=True):
                        st.markdown(results["analyses"]["technical"])
                
                # Thông tin Cơ bản
                    with st.expander("📚 Thông tin Cơ bản", expanded=True):
                        st.markdown(results["analyses"]["fundamental"])
                
                # Chiến lược Giao dịch
                    with st.expander("💡 Chiến lược Giao dịch", expanded=True):
                        st.markdown(results["analyses"]["strategy"])
                
                # JSON output (cho developer)
                    with st.expander("📋 JSON Output"):
                        st.json(results)

# Tab 2: Phân tích Kỹ thuật
elif analysis_mode == "Phân tích Kỹ thuật":
    st.markdown("### 📊 Phân tích Kỹ thuật")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        ticker = st.text_input("Nhập mã chứng khoán:", "GC=F").upper()
    with col2:
        if st.button("Phân tích", use_container_width=True):
            if ticker:
                with st.spinner(f"Đang phân tích {ticker}..."):
                    results = st.session_state.coordinator.analyze_ticker(
                        ticker,
                        analysis_type="technical"
                    )
                
                st.success("✅ Phân tích hoàn thành!")
                st.markdown(results["analyses"]["technical"])

# Tab 3: Hỏi Agent cụ thể
else:
    st.markdown("### 💬 Hỏi Agent Cụ thể")
    
    agent_choice = st.selectbox(
        "Chọn Agent:",
        ["Research Agent", "Analyst Agent", "Strategy Agent"]
    )
    
    agent_map = {
        "Research Agent": "research",
        "Analyst Agent": "analyst",
        "Strategy Agent": "strategy"
    }
    
    user_question = st.text_area(
        "Câu hỏi của bạn:",
        placeholder="Ví dụ: Hãy phân tích mã AAPL..."
    )
    
    if st.button("Gửi", use_container_width=True):
        if user_question:
            with st.spinner("Đang xử lý..."):
                response = st.session_state.coordinator.ask_agents(
                    user_question,
                    target_agent=agent_map[agent_choice]
                )
            st.markdown(f"**{agent_choice}:**\n{response}")

# Sidebar - Thông tin hệ thống
with st.sidebar:
    st.markdown("### ℹ️ Thông tin Hệ thống")
    
    agent_info = st.session_state.coordinator.get_agent_info()
    st.write("**Agent khả dụng:**")
    for key, name in agent_info.items():
        st.write(f"  • {name}")
    
    st.divider()
    st.markdown("### 🔧 Cấu hình")
    
    st.write(f"**Timestamp hiện tại:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"**Vector Store:** {len(splits)} documents")
