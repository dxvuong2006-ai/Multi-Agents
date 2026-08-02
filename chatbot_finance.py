import pickle 
import os
import pandas as pd
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv #tải khóa API 
import extract_data 
from datetime import datetime

from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader, CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_community.retrievers import BM25Retriever
from langchain_community.embeddings import HuggingFaceEmbeddings # Cập nhật import mới
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.retrievers.ensemble import EnsembleRetriever

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.retriever import create_retriever_tool
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage

from langchain_core.documents import Document

#cấu hình
load_dotenv()
st.set_page_config(page_title="Chatbot Analyze Finance - V.X.D",page_icon="🤖")
st.title("🤖Chatbot Analyze Finance - V.X.D")

#khởi tạo embeddings
if "embedding" not in st.session_state:
    st.session_state.embedding=HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
embedding=st.session_state.embedding 

#tham số
FAISS_PATH = "faiss_index_conversation"
SPLITS_PATH = "splits_conversation.pkl"
REBUILD = True

#xử lí tài liệu văn bản
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
    else :
        st.info("Đang đọc và băm nhỏ tài liệu lý thuyết")
        all_docs=[]
        document_finance=DirectoryLoader("./data",glob="**/*.pdf",loader_cls=PyMuPDFLoader)
        all_docs.extend(document_finance.load())
        text_splitter=RecursiveCharacterTextSplitter(chunk_size=1200,chunk_overlap=300)
        splits=text_splitter.split_documents(all_docs)
        vectorstore=FAISS.from_documents(
            documents=splits,
            embedding=embedding,
            distance_strategy=DistanceStrategy.COSINE
        )
        vectorstore.save_local(FAISS_PATH)
        with open(SPLITS_PATH,"wb") as f:
            pickle.dump(splits,f)
        return vectorstore,splits

vectorstore,splits=load_or_build_vectorstore()

if "ensemble_retriever" not in st.session_state:
    bm25_retriever=BM25Retriever.from_documents(splits)
    bm25_retriever.k=3
    vector_retriever=vectorstore.as_retriever(search_type="similarity",search_kwargs={"k":3})
    st.session_state.ensemble_retriever=EnsembleRetriever(
        retrievers=[bm25_retriever,vector_retriever],
        weights=[0.4,0.6]
    )

#biến retriever thành tool
retriever_tool=create_retriever_tool(
    st.session_state.ensemble_retriever,
    name="search_financial_documents",
    description="Tìm kiếm lý thuyết phân tích kỹ thuật, quy tắc giao dịch hoặc tin tức từ các tài liệu PDF đã tải lên."
)

#công cụ phân tích
@tool
def analyze_stock_data(ticker:str,analysis_type:str) ->str:
    """
    Sử dụng công cụ này để trích xuất dữ liệu giá và xu hướng thực tế của một mã chứng khoán từ cơ sở dữ liệu.
    - ticker: Mã chứng khoán (ví dụ: GC=F, AAPL).
    - analysis_type: Bắt buộc truyền vào 'recent_price' (để lấy giá 5 phiên gần nhất) hoặc 'trend' (để xem xu hướng đường MA10).
    """
    try:
        data_dir=Path("data")
        today_str=datetime.today().strftime('%Y-%m-%d')
        expected_filename= f"{ticker.replace('=', '_')}_historical_{today_str}.parquet"
        expected_file_path= data_dir/expected_filename
        if not expected_file_path.exists():
            print(f">>> [Data Freshness] Dữ liệu mã {ticker} chưa cập nhật cho ngày hôm nay ({today_str}). Đang gọi Pipeline ETL...")
            success=extract_data.run_pipeline(ticker)
        else:
            print(f">>> [Data Freshness] Dữ liệu mã {ticker} đã là mới nhất (ngày {today_str}). Sử dụng file sẵn có.")
        files=list(data_dir.glob(f"{ticker.replace('=', '_')}_historical_*.parquet"))
        if not files:
            print(f">>> Agent phát hiện thiếu dữ liệu. Đang tự động gọi Pipeline kéo mã {ticker}...")

            success=extract_data.run_pipeline(ticker)
            files=list(data_dir.glob(f"{ticker.replace('=','_')}_historical_*.parquet"))
        #lấy ra files mới nhất
        latest_file=max(files,key=os.path.getctime)
        df=pd.read_parquet(latest_file)

        #sắp xếp thời gian
        df=df.sort_values(by='date',ascending=False)
        
        if analysis_type=="recent_price":
            recent=df.head(5)
            result=f"Giá trị 5 phiên gần nhất của {ticker}:\n"
            for _,row in recent.iterrows():
                result += f"- {row['date'].strftime('%Y-%m-%d')}: Mở {row['open']:.2f}, Đóng {row['close']:.2f}, Khối lượng {row['volume']}\n"
            return result
        elif analysis_type=="trend":
            ma10=df['close'].head(10).mean()
            current_price=df['close'].iloc[0]
            trend="TĂNG" if current_price>ma10 else "GIẢM"
            return f"Đường MA10 hiện tại là {ma10:.2f}. Giá đóng cửa gần nhất là {current_price:.2f}. Xét theo MA10 ngắn hạn, xu hướng đang là {trend}."
        return "Yêu cầu phân tích không xác định. Chỉ hỗ trợ: recent_price, trend."
    
    except Exception as e:
        return f"Lỗi khi xử lý dữ liệu file Parquet: {e}"

tools=[retriever_tool,analyze_stock_data]

#cấu hình agent và promt

if "agent_executor" not in st.session_state:
    print("Khởi tạo Agent...")
    
    #sử dụng gemini
    llm=ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Bạn là một Chuyên gia Phân tích Tài chính cấp cao. Bạn có 2 công cụ:
        1. 'search_financial_documents': Đọc lý thuyết phân tích từ tài liệu hệ thống.
        2. 'analyze_stock_data': Trích xuất dữ liệu giá và xu hướng thực tế từ database.
        
        QUY TẮC:
        - Khi người dùng hỏi về một mã chứng khoán (ví dụ: GC=F), HÃY TÌM LÝ THUYẾT trước, sau đó GỌI DATA TOOL để lấy số liệu thực tế, cuối cùng ĐỐI CHIẾU 2 cái lại để đưa ra kết luận.
        - Luôn trích dẫn tài liệu nếu dùng lý thuyết (ví dụ: Theo tài liệu X...).
        - Cảnh báo rủi ro ở cuối: "Lưu ý: Phân tích này chỉ mang tính tham khảo..."
        - Nếu hỏi chuyện phiếm, hãy trả lời tự nhiên ngắn gọn, KHÔNG gọi tool."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent=create_tool_calling_agent(llm,tools,prompt)
    st.session_state.agent_executor=AgentExecutor(agent=agent, tools=tools, verbose=True)

#thiết lập giao diện streamlit
if "messages" not in st.session_state:
    st.session_state.messages=[]

for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

if user_input := st.chat_input("Nhập mã chứng khoán hoặc câu hỏi lý thuyết..."):
    st.chat_message("user").write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Đang suy luận và tra cứu dữ liệu..."):
            try:
                # Gọi Agent hoạt động (truyền cả chat history)
                response = st.session_state.agent_executor.invoke({
                    "input": user_input,
                    "chat_history": st.session_state.messages[-1:] # Nhớ 4 tin nhắn gần nhất
                })
                
                answer = response["output"]
                st.markdown(answer)
                
                # Lưu vào lịch sử
                st.session_state.messages.append(HumanMessage(content=user_input))
                st.session_state.messages.append(AIMessage(content=answer))
                
            except Exception as e:
                st.error(f"Đã xảy ra lỗi hệ thống: {e}")