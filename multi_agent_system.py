"""
Hệ thống Multi-Agent cho phân tích tài chính
Các agent khác nhau có thể tương tác và giao tiếp với nhau
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage, SystemMessage
from langchain_core.documents import Document
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
import logging
import time
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache

# Kích hoạt bộ nhớ đệm trên RAM
set_llm_cache(InMemoryCache())

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinanceAgent:
    """
    Lớp cơ sở cho tất cả các agent trong hệ thống
    """
    def __init__(self, name: str, llm, tools: List, system_prompt: str):
        self.name = name
        self.llm = llm
        self.tools = tools
        self.system_prompt = system_prompt
        self.conversation_history: List[BaseMessage] = []
    
    def build_messages(self, user_input: str, chat_history: List[BaseMessage] = None) -> List[BaseMessage]:
        messages = [SystemMessage(content=self.system_prompt)]
        if chat_history:
            messages.extend(chat_history)
        messages.append(HumanMessage(content=user_input))
        return messages
    
    def process_input(self, user_input: str, chat_history: List[BaseMessage] = None) -> str:
        """
        Xử lý input từ người dùng hoặc từ agent khác
        """
        if chat_history is None:
            chat_history = self.conversation_history
        
        logger.info(f"[{self.name}] Processing user input...")
        
        messages = self.build_messages(user_input, chat_history)
        response_message = self.llm(messages)
        response = response_message.content.strip()
        
        self.conversation_history.append(HumanMessage(content=user_input))
        self.conversation_history.append(AIMessage(content=response))
        
        return response
    
    def clear_history(self):
        """Xóa lịch sử cuộc trò chuyện"""
        self.conversation_history = []


class ResearchAgent(FinanceAgent):
    """
    Agent chuyên biệt về tìm kiếm thông tin từ tài liệu tài chính
    """
    def __init__(self, llm, retriever_tool, vectorstore):
        self.retriever_tool = retriever_tool
        self.vectorstore = vectorstore
        
        system_prompt = """Bạn là một chuyên gia nghiên cứu tài chính với khả năng tìm kiếm và phân tích tài liệu.
Bạn sử dụng công cụ search_financial_documents để tìm thông tin từ tài liệu PDF.
Khi tìm kiếm, hãy:
1. Tìm kiếm các thuật ngữ và khái niệm chính
2. Tổng hợp thông tin từ nhiều nguồn
3. Cung cấp trích dẫn cụ thể từ tài liệu
4. Giải thích ý nghĩa của thông tin tìm được
Luôn cung cấp câu trả lời chi tiết và có cơ sở."""
        
        super().__init__("ResearchAgent", llm, [retriever_tool], system_prompt)

    def process_input(self, user_input: str, chat_history: List[BaseMessage] = None) -> str:
        """
        Tìm kiếm tài liệu trước khi trả lời yêu cầu.
        """
        logger.info(f"[{self.name}] Searching for information: {user_input[:100]}...")
        try:
            search_results = self.retriever_tool.run(user_input)
        except Exception as e:
            search_results = f"Lỗi khi truy vấn tài liệu: {e}"

        prompt = (
            f"Tôi đã thu thập các thông tin từ công cụ search_financial_documents cho yêu cầu sau:\n"
            f"{user_input}\n\n"
            f"Kết quả tìm kiếm:\n{search_results}\n\n"
            f"Hãy cung cấp câu trả lời chi tiết, sử dụng kết quả tìm kiếm như nguồn tham khảo.")

        return super().process_input(prompt, chat_history)


class AnalystAgent(FinanceAgent):
    """
    Agent chuyên biệt về phân tích dữ liệu thị trường
    """
    def __init__(self, llm, analyze_tool):
        self.analyze_tool = analyze_tool
        
        system_prompt = """Bạn là một nhà phân tích kỹ thuật chuyên nghiệp với kinh nghiệm sâu về thị trường chứng khoán.
Bạn sử dụng công cụ analyze_stock_data để lấy dữ liệu thực tế.
Khi phân tích, hãy:
1. Trích xuất dữ liệu giá và xu hướng
2. Phân tích biến động giá (volatility)
3. Xác định mô hình kỹ thuật (support, resistance)
4. Đánh giá sức mạnh xu hướng
5. Đưa ra dự báo xu hướng ngắn hạn
Luôn cung cấp phân tích định lượng với con số cụ thể."""
        
        super().__init__("AnalystAgent", llm, [analyze_tool], system_prompt)

    def analyze_ticker(self, ticker: str) -> str:
        """
        Gọi công cụ phân tích dữ liệu rồi tổng hợp kết quả.
        """
        logger.info(f"[{self.name}] Gathering data for ticker: {ticker}")
        try:
            recent_price = self.analyze_tool.invoke({"ticker": ticker, "analysis_type": "recent_price"})
        except Exception as e:
            recent_price = f"Lỗi khi lấy giá gần nhất: {e}"

        try:
            trend = self.analyze_tool.invoke({"ticker": ticker, "analysis_type": "trend"})
        except Exception as e:
            trend = f"Lỗi khi lấy xu hướng: {e}"

        prompt = (
            f"Đây là dữ liệu kỹ thuật cho mã {ticker}:\n"
            f"Giá 5 phiên gần nhất:\n{recent_price}\n\n"
            f"Xu hướng và MA10/MA20:\n{trend}\n\n"
            f"Hãy phân tích kỹ thuật chi tiết dựa trên dữ liệu này và đưa ra nhận xét về xu hướng, sự hỗ trợ/kháng cự, và sức mạnh thị trường.")

        return super().process_input(prompt)


class StrategyAgent(FinanceAgent):
    """
    Agent tổng hợp thông tin từ các agent khác để đưa ra chiến lược giao dịch
    """
    def __init__(self, llm):
        system_prompt = """Bạn là một strategist giao dịch chuyên nghiệp.
Bạn sẽ nhận thông tin phân tích từ ResearchAgent (thông tin về lý thuyết) và AnalystAgent (dữ liệu kỹ thuật).
Dựa trên các thông tin đó, bạn sẽ:
1. Tổng hợp các phân tích
2. Xác định điểm mạnh và yếu
3. Đánh giá rủi ro
4. Đưa ra chiến lược giao dịch cụ thể với:
   - Điểm vào (entry point)
   - Mục tiêu giá (target)
   - Điểm dừng lỗ (stop loss)
   - Khối lượng giao dịch
5. Giải thích lý do cho từng quyết định
Luôn cẩn thận và quản lý rủi ro."""
        
        super().__init__("StrategyAgent", llm, [], system_prompt)


class MultiAgentCoordinator:
    """
    Điều phối viên quản lý giao tiếp giữa các agent
    """
    def __init__(self, llm, tools_dict: Dict[str, Any]):
        self.llm = llm
        self.agents: Dict[str, FinanceAgent] = {}
        self.conversation_log: List[Dict] = []
        
        # Khởi tạo các agent
        self._initialize_agents(tools_dict)
    
    def _initialize_agents(self, tools_dict: Dict[str, Any]):
        """Khởi tạo tất cả các agent"""
        # Research Agent
        self.agents["research"] = ResearchAgent(
            self.llm,
            tools_dict["retriever_tool"],
            tools_dict["vectorstore"]
        )
        
        # Analyst Agent
        self.agents["analyst"] = AnalystAgent(
            self.llm,
            tools_dict["analyze_tool"]
        )
        
        # Strategy Agent
        self.agents["strategy"] = StrategyAgent(self.llm)
    
    def analyze_ticker(self, ticker: str, analysis_type: str = "full") -> Dict[str, Any]:
        """
        PHIÊN BẢN TỐI ƯU CHI PHÍ TOKEN & API QUOTA
        Trích xuất dữ liệu thô bằng Python, sau đó gọi LLM 1 lần duy nhất để tổng hợp toàn bộ.
        """
        import re  # Import thư viện xử lý chuỗi
        
        results = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "analyses": {
                "technical": "",
                "fundamental": "",
                "strategy": ""
            }
        }
        
        logger.info(f"=== Starting OPTIMIZED analysis for {ticker} ===")
        
        # BƯỚC 1: EXTRACT DỮ LIỆU THỰC TẾ (KHÔNG TỐN TOKEN LLM)
        logger.info("[Python Phase] Extracting Parquet Data...")
        try:
            recent_price = self.agents["analyst"].analyze_tool.invoke({"ticker": ticker, "analysis_type": "recent_price"})
            trend = self.agents["analyst"].analyze_tool.invoke({"ticker": ticker, "analysis_type": "trend"})
        except Exception as e:
            recent_price, trend = f"Lỗi: {e}", f"Lỗi: {e}"

        # Xử lý riêng cho Tab 2 (Chỉ phân tích kỹ thuật) - Tốn 1 LLM Call
        if analysis_type == "technical":
            tech_prompt = f"Phân tích dữ liệu kỹ thuật sau của {ticker}:\n{recent_price}\n{trend}"
            results["analyses"]["technical"] = self.agents["analyst"].process_input(tech_prompt)
            return results
            
        # BƯỚC 2: EXTRACT TÀI LIỆU RAG (KHÔNG TỐN TOKEN LLM)
        logger.info("[Python Phase] Extracting PDF Documents...")
        try:
            search_query = f"Các lý thuyết phân tích kỹ thuật, chỉ báo và bộ lọc cổ phiếu phù hợp để đánh giá mã {ticker}"
            search_results = self.agents["research"].retriever_tool.invoke(search_query)
        except Exception as e:
            search_results = f"Lỗi truy vấn: {e}"

        # BƯỚC 3: LLM CALL DUY NHẤT (Gộp toàn bộ vào 1 Master Prompt)
        logger.info("[LLM Phase] Sending combined context to LLM (1 API Call)...")
        master_prompt = f"""Bạn là một Chuyên gia Tài chính và Chiến lược gia Giao dịch cấp cao.
Bạn được cung cấp các dữ liệu THÔ dưới đây về mã chứng khoán {ticker}.
Nhiệm vụ của bạn là tổng hợp và phân tích toàn diện (đóng vai trò cả Analyst, Researcher và Strategist).

--- 1. DỮ LIỆU THỊ TRƯỜNG THỰC TẾ ---
{recent_price}
{trend}

--- 2. TÀI LIỆU LÝ THUYẾT & TIN TỨC ---
{search_results}

YÊU CẦU BẮT BUỘC: Bạn phải định dạng câu trả lời với chính xác 3 thẻ (tags) dưới đây để hệ thống cắt chuỗi đổ vào giao diện. KHÔNG được đổi tên thẻ.

[TECHNICAL_START]
(Viết phân tích kỹ thuật chi tiết của bạn tại đây: Đánh giá xu hướng, hỗ trợ/kháng cự dựa trên dữ liệu giá)
[TECHNICAL_END]

[FUNDAMENTAL_START]
(Viết thông tin cơ bản tại đây: Áp dụng các lý thuyết từ tài liệu vào tình hình hiện tại)
[FUNDAMENTAL_END]

[STRATEGY_START]
(Viết chiến lược giao dịch tại đây: Đề xuất Entry point, Target, Stop loss cụ thể)
[STRATEGY_END]
"""
        
        # Gọi Agent Chiến lược xử lý toàn bộ data (Tốn 1 LLM Call)
        raw_response = self.agents["strategy"].process_input(master_prompt)
        
        # BƯỚC 4: PARSING KẾT QUẢ ĐỂ ĐỔ VÀO GIAO DIỆN STREAMLIT
        tech_match = re.search(r'\[TECHNICAL_START\](.*?)\[TECHNICAL_END\]', raw_response, re.DOTALL)
        fund_match = re.search(r'\[FUNDAMENTAL_START\](.*?)\[FUNDAMENTAL_END\]', raw_response, re.DOTALL)
        strat_match = re.search(r'\[STRATEGY_START\](.*?)\[STRATEGY_END\]', raw_response, re.DOTALL)
        
        if tech_match and fund_match and strat_match:
            results["analyses"]["technical"] = tech_match.group(1).strip()
            results["analyses"]["fundamental"] = fund_match.group(1).strip()
            results["analyses"]["strategy"] = strat_match.group(1).strip()
        else:
            # Fallback an toàn nếu LLM quên viết thẻ
            results["analyses"]["strategy"] = raw_response
            results["analyses"]["technical"] = "Vui lòng xem toàn bộ phân tích ở phần Chiến lược Giao dịch."
            results["analyses"]["fundamental"] = "Vui lòng xem toàn bộ phân tích ở phần Chiến lược Giao dịch."
            
        self.conversation_log.append({"timestamp": results["timestamp"], "ticker": ticker, "analysis_type": analysis_type, "results": results})
        logger.info("=== Optimized analysis completed ===")
        
        return results
    
    def ask_agents(self, question: str, target_agent: str = "strategy") -> str:
        """
        Hỏi một agent cụ thể
        
        Args:
            question: Câu hỏi
            target_agent: Agent nhắm tới ("research", "analyst", "strategy")
        
        Returns:
            Câu trả lời từ agent
        """
        if target_agent not in self.agents:
            return f"Agent '{target_agent}' does not exist. Available agents: {list(self.agents.keys())}"
        
        logger.info(f"Sending question to {target_agent}...")
        response = self.agents[target_agent].process_input(question)
        return response
    
    def clear_all_histories(self):
        """Xóa lịch sử của tất cả các agent"""
        for agent in self.agents.values():
            agent.clear_history()
        self.conversation_log.clear()
    
    def get_agent_info(self) -> Dict[str, str]:
        """Lấy thông tin về tất cả các agent"""
        info = {}
        for name, agent in self.agents.items():
            info[name] = agent.name
        return info


def create_multi_agent_system(llm, tools_dict: Dict[str, Any]) -> MultiAgentCoordinator:
    """
    Hàm tiện ích để tạo hệ thống multi-agent
    
    Args:
        llm: Language Model (ví dụ: ChatGoogleGenerativeAI)
        tools_dict: Dictionary chứa các tools cần thiết
            - retriever_tool: Tool tìm kiếm tài liệu
            - vectorstore: Vector store
            - analyze_tool: Tool phân tích dữ liệu
    
    Returns:
        MultiAgentCoordinator instance
    """
    return MultiAgentCoordinator(llm, tools_dict)
