# 🤖 Hệ Thống Multi-Agent Phân Tích Tài Chính

## 📋 Giới thiệu

Hệ thống multi-agent này cho phép bạn phân tích thị trường chứng khoán bằng cách sử dụng **nhiều agent chuyên biệt** có thể giao tiếp và cộng tác với nhau.

## 🏗️ Kiến trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────┐
│           MultiAgentCoordinator (Điều phối viên)         │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │ ResearchAgent    │  │ AnalystAgent     │              │
│  │                  │  │                  │              │
│  │ - Tìm kiếm tài   │  │ - Phân tích dữ   │              │
│  │   liệu          │  │   liệu thị trường │              │
│  │ - Kéo thông tin  │  │ - Kỹ thuật phân  │              │
│  │   từ PDF        │  │   tích           │              │
│  └──────────────────┘  └──────────────────┘              │
│                                                           │
│  ┌──────────────────────────────────┐                    │
│  │ StrategyAgent                    │                    │
│  │                                  │                    │
│  │ - Tổng hợp thông tin            │                    │
│  │ - Đưa ra chiến lược giao dịch    │                    │
│  │ - Entry point, Target, Stop loss │                    │
│  └──────────────────────────────────┘                    │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## 👥 Các Agent Chuyên Biệt

### 1️⃣ **ResearchAgent** - Agent Nghiên Cứu

- **Nhiệm vụ:** Tìm kiếm và phân tích thông tin từ tài liệu
- **Công cụ:** `search_financial_documents`
- **Đầu vào:** Mã chứng khoán, chủ đề cần nghiên cứu
- **Đầu ra:** Thông tin cơ bản, lý thuyết phân tích kỹ thuật

**Ví dụ:**

```python
coordinator.ask_agents(
    question="Hãy tìm kiếm thông tin về phân tích Bollinger Bands",
    target_agent="research"
)
```

### 2️⃣ **AnalystAgent** - Agent Phân Tích

- **Nhiệm vụ:** Phân tích dữ liệu thị trường và kỹ thuật
- **Công cụ:** `analyze_stock_data`
- **Đầu vào:** Mã chứng khoán
- **Đầu ra:** Giá hiện tại, xu hướng, phân tích kỹ thuật

**Ví dụ:**

```python
coordinator.ask_agents(
    question="Phân tích mã AAPL, lấy giá 5 phiên gần nhất và xu hướng MA10",
    target_agent="analyst"
)
```

### 3️⃣ **StrategyAgent** - Agent Chiến Lược

- **Nhiệm vụ:** Tổng hợp thông tin và đưa ra chiến lược giao dịch
- **Công cụ:** Không trực tiếp, nhưng kết hợp thông tin từ các agent khác
- **Đầu vào:** Kết quả phân tích từ Research và Analyst
- **Đầu ra:** Chiến lược giao dịch với entry/target/stop-loss

## 🚀 Cách Sử Dụng

### **Cách 1: Phân tích Toàn diện (Recommended)**

```python
from multi_agent_system import create_multi_agent_system

# Khởi tạo hệ thống
coordinator = create_multi_agent_system(llm, tools_dict)

# Phân tích một mã chứng khoán
results = coordinator.analyze_ticker(
    ticker="AAPL",
    analysis_type="full"  # "full", "technical", "fundamental"
)

# Kết quả gồm 3 phần:
# - results["analyses"]["technical"]     # Phân tích kỹ thuật
# - results["analyses"]["fundamental"]   # Thông tin cơ bản
# - results["analyses"]["strategy"]      # Chiến lược giao dịch
```

**Quy trình tự động:**

1. **ResearchAgent** tìm kiếm thông tin cơ bản
2. **AnalystAgent** phân tích dữ liệu kỹ thuật
3. **StrategyAgent** tổng hợp và đưa ra chiến lược

### **Cách 2: Hỏi Agent Cụ Thể**

```python
# Hỏi Research Agent
response = coordinator.ask_agents(
    question="Hãy tìm kiếm thông tin về Moving Average",
    target_agent="research"
)

# Hỏi Analyst Agent
response = coordinator.ask_agents(
    question="Phân tích GC=F",
    target_agent="analyst"
)

# Hỏi Strategy Agent
response = coordinator.ask_agents(
    question="Đưa ra chiến lược cho AAPL",
    target_agent="strategy"
)
```

### **Cách 3: Sử dụng Streamlit App**

```bash
streamlit run app_multi_agent.py
```

**Các tính năng:**

- 📊 Phân tích Toàn diện
- 📈 Phân tích Kỹ thuật
- 💬 Hỏi Agent Cụ thể
- 🔄 Xóa lịch sử

## 📊 Ví Dụ Thực Tế

### Ví dụ 1: Phân tích AAPL

```python
results = coordinator.analyze_ticker("AAPL", "full")

# Output:
# {
#   "ticker": "AAPL",
#   "timestamp": "2024-01-15T10:30:00",
#   "analyses": {
#     "technical": "Phân tích kỹ thuật từ AnalystAgent...",
#     "fundamental": "Thông tin cơ bản từ ResearchAgent...",
#     "strategy": "Chiến lược từ StrategyAgent..."
#   }
# }
```

### Ví dụ 2: Phân tích Vàng (GC=F)

```python
coordinator.ask_agents(
    "Phân tích GC=F. Hiện tại là trend Up hay Down? Nên mua hay bán?",
    "analyst"
)
```

### Ví dụ 3: Tìm kiếm Thông tin Cụ Thể

```python
coordinator.ask_agents(
    "Hãy tìm kiếm các quy tắc để lọc cổ phiếu tốt và giải thích cách áp dụng",
    "research"
)
```

## 🔧 Cấu Hình

### File `multi_agent_system.py`

- **FinanceAgent** - Base class cho tất cả agent
- **ResearchAgent** - Extends FinanceAgent, sử dụng retriever tool
- **AnalystAgent** - Extends FinanceAgent, sử dụng analyze tool
- **StrategyAgent** - Extends FinanceAgent, không sử dụng tool trực tiếp
- **MultiAgentCoordinator** - Quản lí các agent và giao tiếp

### Tùy chỉnh Prompt

Mỗi agent có một `system_prompt` tùy chỉnh. Để thay đổi hành vi agent:

```python
class CustomAnalystAgent(AnalystAgent):
    def __init__(self, llm, analyze_tool):
        self.analyze_tool = analyze_tool
        system_prompt = """
        Your custom prompt here...
        """
        FinanceAgent.__init__(self, "CustomAnalyst", llm, [analyze_tool], system_prompt)
```

## 📁 Cấu trúc Tệp

```
project/
├── multi_agent_system.py      # Hệ thống multi-agent
├── app_multi_agent.py          # Ứng dụng Streamlit
├── chatbot_finance.py          # App cũ (single agent)
├── extract_data.py             # Pipeline ETL
├── requirements.txt            # Dependencies
├── data/                       # Thư mục dữ liệu
│   ├── *.pdf                   # Tài liệu PDF
│   └── *.parquet               # Dữ liệu thị trường
└── faiss_index_conversation/   # Vector store
    └── index.faiss             # Index FAISS
```

## ⚙️ Cài đặt và Chạy

### 1. Cập nhật Dependencies

```bash
# Thêm vào requirements.txt nếu cần:
# (Các package hiện tại đã đủ)
```

### 2. Chạy Ứng dụng

```bash
# Chạy Streamlit app multi-agent (recommended)
streamlit run app_multi_agent.py

# Hoặc sử dụng app cũ (single agent)
streamlit run chatbot_finance.py
```

## 🎯 Các Trường Hợp Sử Dụng

### 1. **Phân tích Chi tiết Một Mã**

```python
results = coordinator.analyze_ticker("AAPL", "full")
```

→ Nhận phân tích đầy đủ từ 3 agent

### 2. **Kiểm tra Nhanh Xu hướng**

```python
coordinator.ask_agents("GC=F trend up hay down?", "analyst")
```

→ Phân tích kỹ thuật nhanh

### 3. **Tìm Quy tắc Giao dịch**

```python
coordinator.ask_agents("Quy tắc giao dịch tốt là gì?", "research")
```

→ Thông tin lý thuyết từ tài liệu

### 4. **Đưa ra Quyết định Giao dịch**

```python
coordinator.ask_agents("Dữ liệu gần đây + lý thuyết = chiến lược?", "strategy")
```

→ Chiến lược cụ thể với entry/target/stop-loss

## 📈 Mở Rộng Hệ Thống

### Thêm Agent Mới

```python
class RiskManagementAgent(FinanceAgent):
    def __init__(self, llm, risk_tool):
        system_prompt = """
        Bạn là chuyên gia quản lý rủi ro...
        """
        super().__init__("RiskAgent", llm, [risk_tool], system_prompt)
```

### Thêm Tool Mới

```python
@tool
def calculate_portfolio_metrics(positions: dict) -> str:
    """Tính toán các chỉ số portfolio"""
    # Implementation...
```

## 💡 Tips & Tricks

1. **Agent Collaboration:** Các agent tự động hợp tác thông qua MultiAgentCoordinator
2. **Conversation History:** Mỗi agent giữ lịch sử cuộc trò chuyện riêng
3. **Caching:** Sử dụng `@st.cache_resource` để tăng tốc độ
4. **Logging:** Các hoạt động của agent được ghi lại (logging)

## ❓ FAQ

**Q: Tôi có cần tài liệu PDF không?**
A: Không bắt buộc. Nếu không có PDF, ResearchAgent vẫn có thể hoạt động dựa trên kiến thức của LLM.

**Q: Tôi có thể tùy chỉnh prompt của agent không?**
A: Có! Sửa `system_prompt` trong mỗi class agent.

**Q: Agent có thể gọi nhau trực tiếp không?**
A: Hiện tại không. Họ thông qua MultiAgentCoordinator. Để thêm giao tiếp trực tiếp, bạn có thể sửa MultiAgentCoordinator.

**Q: Làm thế nào để cải thiện độ chính xác?**
A:

- Thêm tài liệu chất lượng cao
- Tùy chỉnh prompt cho agent
- Sử dụng LLM mạnh hơn (gpt-4 thay vì gemini-pro)

## 📞 Hỗ Trợ

Nếu gặp vấn đề:

1. Kiểm tra logs (terminal)
2. Xem lại prompt của agent
3. Kiểm tra dữ liệu đầu vào
4. Thử agent khác để isolation
