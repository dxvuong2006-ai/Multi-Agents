# 🤖 Multi-Agent Finance Analyzer System

Hệ thống phân tích tài chính nâng cao sử dụng **LLM + Multi-Agent Architecture**. Các agent chuyên biệt có thể giao tiếp, cộng tác và đưa ra quyết định phân tích phức tạp.

## 📁 Cấu Trúc Dự Án

```
agent_extract_and_analyze_data/
├── 🎯 LỮC LỌC VÀ PHÂN TÍCH
│   ├── multi_agent_system.py          # Hệ thống multi-agent cơ bản
│   ├── advanced_features.py           # Tính năng nâng cao (agent & workflow)
│   ├── chatbot_finance.py             # App Streamlit cũ (single agent)
│   └── app_multi_agent.py             # App Streamlit mới (multi-agent) ⭐
│
├── 📚 DATA & TOOLS
│   ├── extract_data.py                # ETL pipeline
│   ├── data/                          # Dữ liệu (PDF, Parquet)
│   └── faiss_index_conversation/      # Vector Store
│
├── 📖 HƯỚNG DẪN VÀ EXAMPLES
│   ├── MULTI_AGENT_GUIDE.md           # Hướng dẫn chi tiết
│   ├── example_usage.py               # Ví dụ cơ bản
│   └── README.md                      # File này
│
└── ⚙️ CẤU HÌNH
    └── requirements.txt               # Dependencies
```

## 🚀 Bắt Đầu Nhanh

### 1️⃣ Cài Đặt

```bash
# Tạo virtual environment (nếu chưa có)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows

# Cài dependencies
pip install -r requirements.txt

# Thiết lập .env (nếu chưa có)
echo GOOGLE_API_KEY=your_key > .env
```

### 2️⃣ Chạy Ứng Dụng

**Option A: Streamlit App (Recommended)**

```bash
streamlit run app_multi_agent.py
```

**Option B: Python Script với Examples**

```bash
python example_usage.py
```

**Option C: Sử dụng Advanced Features**

```bash
python -c "from advanced_features import *; from multi_agent_system import *"
```

## 👥 Các Agent Trong Hệ Thống

### 📚 ResearchAgent

- **Vai trò:** Tìm kiếm thông tin từ tài liệu
- **Công cụ:** RAG (Retrieval-Augmented Generation)
- **Output:** Thông tin lý thuyết, quy tắc giao dịch, phân tích cơ bản

### 📊 AnalystAgent

- **Vai trò:** Phân tích dữ liệu kỹ thuật
- **Công cụ:** Trích xuất giá, tính toán chỉ báo
- **Output:** Phân tích kỹ thuật, xu hướng, entry point

### 💡 StrategyAgent

- **Vai trò:** Tổng hợp và đưa ra chiến lược
- **Công cụ:** Logic quyết định dựa trên phân tích
- **Output:** Chiến lược giao dịch, entry/target/stop-loss

### 🛡️ RiskManagementAgent (Advanced)

- **Vai trò:** Quản lý rủi ro
- **Công cụ:** Đánh giá rủi ro, position sizing
- **Output:** Mức rủi ro, khuyến nghị quản lý rủi ro

### 📰 NewsAnalysisAgent (Advanced)

- **Vai trò:** Phân tích tác động tin tức
- **Công cụ:** Sentiment analysis, impact assessment
- **Output:** Đánh giá cảm tính, dự báo phản ứng thị trường

### 💼 PortfolioAgent (Advanced)

- **Vai trò:** Quản lý danh mục
- **Công cụ:** Portfolio optimization, allocation
- **Output:** Khuyến nghị rebalancing, tối ưu hóa

## 📋 Các Cách Sử Dụng

### Cách 1: Phân tích Toàn Diện (Recommended)

```python
from multi_agent_system import create_multi_agent_system

coordinator = create_multi_agent_system(llm, tools_dict)
results = coordinator.analyze_ticker("AAPL", analysis_type="full")

# Kết quả bao gồm:
# - Technical Analysis (từ AnalystAgent)
# - Fundamental Research (từ ResearchAgent)
# - Trading Strategy (từ StrategyAgent)
```

### Cách 2: Hỏi Agent Cụ Thể

```python
# Hỏi Research Agent
info = coordinator.ask_agents(
    "Tìm kiếm thông tin về Moving Average",
    target_agent="research"
)

# Hỏi Analyst Agent
analysis = coordinator.ask_agents(
    "Phân tích GC=F",
    target_agent="analyst"
)

# Hỏi Strategy Agent
strategy = coordinator.ask_agents(
    "Đưa ra chiến lược cho AAPL",
    target_agent="strategy"
)
```

### Cách 3: Multi-Ticker Analysis (Advanced)

```python
from advanced_features import create_advanced_multi_agent_system

coordinator = create_advanced_multi_agent_system(llm, tools_dict)
results = coordinator.multi_ticket_analysis(["AAPL", "GOOGL", "MSFT"])

# So sánh các mã chứng khoán
print(results["comparative_analysis"])
```

### Cách 4: Portfolio Review (Advanced)

```python
positions = {
    "AAPL": 10000,
    "GC=F": 5000,
    "MSFT": 8000
}
results = coordinator.comprehensive_portfolio_review(positions)
```

### Cách 5: Trading Workflow (Advanced)

```python
from advanced_features import AdvancedWorkflow

# Swing Trading Setup
setup = AdvancedWorkflow.swing_trading_setup(coordinator, "AAPL")

# Breakout Trading Setup
setup = AdvancedWorkflow.breakout_trading_setup(coordinator, "GC=F")
```

## 💻 Examples

### Ví dụ 1: Phân tích AAPL

```bash
python example_usage.py
# Chạy ví dụ 1: Full Analysis
```

### Ví dụ 2: Tạo Kế Hoạch Giao Dịch

```python
from advanced_features import create_advanced_multi_agent_system

coordinator = create_advanced_multi_agent_system(llm, tools_dict)
plan = coordinator.generate_trading_plan("AAPL", investment_amount=10000)
print(plan["trading_plan"])
```

### Ví dụ 3: Phân tích Kịch Bản

```python
results = coordinator.market_scenario_analysis(
    "Fed tăng lãi suất 0.5%, VIX tăng mạnh"
)
```

## 🎯 Các Tính Năng Chính

### ✅ Tính Năng Cơ Bản

- [x] Single-ticker analysis
- [x] Multi-agent collaboration
- [x] RAG-based research
- [x] Technical analysis
- [x] Trading strategy generation
- [x] Conversation history management

### ✅ Tính Năng Nâng Cao

- [x] Multi-ticker comparison
- [x] Portfolio optimization
- [x] Risk management
- [x] Market sentiment analysis
- [x] Trading scenario analysis
- [x] Advanced technical indicators
- [x] Swing trading workflows
- [x] Breakout trading workflows

### 🔄 Cải Tiến Tiếp Theo

- [ ] Real-time market data integration
- [ ] Machine learning models
- [ ] Backtesting framework
- [ ] Live trading integration
- [ ] Custom indicator builder
- [ ] Advanced sentiment analysis
- [ ] Multi-timeframe analysis
- [ ] Price prediction models

## 🔧 Tùy Chỉnh

### Tạo Agent Mới

```python
from multi_agent_system import FinanceAgent

class MyCustomAgent(FinanceAgent):
    def __init__(self, llm, tools):
        system_prompt = """
        Bạn là...
        Khi..., hãy...
        """
        super().__init__("MyAgent", llm, tools, system_prompt)
```

### Tạo Tool Mới

```python
from langchain.tools import tool

@tool
def my_custom_tool(input_param: str) -> str:
    """
    Mô tả công cụ
    """
    # Implementation
    return "Result"
```

## 📊 Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────┐
│     User (Streamlit UI)              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  MultiAgentCoordinator               │
│  ┌──────────────────────────────┐   │
│  │  Workflow & Orchestration     │   │
│  └──────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼────┐   ┌─────▼─────┐
│ Agent 1   │   │  Agent 2  │
│ Research  │   │ Analyst   │
└─────┬────┘   └─────┬─────┘
      │              │
┌─────▼────┐   ┌─────▼─────┐
│  Tools   │   │  Tools    │
│  RAG     │   │  Analysis │
└──────────┘   └───────────┘
```

## 📈 Performance Tips

1. **Caching**: Sử dụng `@st.cache_resource` cho data nặng
2. **Batch Processing**: Phân tích nhiều mã cùng lúc
3. **Vector Store**: Tính toán embeddings từ trước
4. **LLM Choice**: Sử dụng model phù hợp (gemini-pro vs gpt-4)
5. **Conversation History**: Xóa history để giải phóng memory

## 🐛 Troubleshooting

### Lỗi: "Module not found"

```bash
pip install -r requirements.txt
```

### Lỗi: "API Key not found"

```bash
# Tạo file .env
echo GOOGLE_API_KEY=your_key > .env
```

### Lỗi: "Vector store not found"

```python
# Rebuild vector store
coordinator.clear_all_histories()
```

## 📚 Tài Liệu Thêm

- [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - Hướng dẫn chi tiết
- [example_usage.py](example_usage.py) - Ví dụ thực tế
- [multi_agent_system.py](multi_agent_system.py) - Mã nguồn hệ thống
- [advanced_features.py](advanced_features.py) - Tính năng nâng cao

## 🤝 Contribution

Hãy tạo issue hoặc pull request để cải thiện hệ thống!

## 📄 License

MIT License

## 👨‍💼 Author

Phát triển bởi AI Assistant

---

**Trạng thái hiện tại**: ✅ Sẵn sàng sử dụng

**Phiên bản**: 1.0.0

**Cập nhật lần cuối**: May 2026
