# 🏗️ Architecture Diagrams

## 1. Kiến Trúc Toàn Cảnh

```
┌─────────────────────────────────────────────────────────┐
│                  Frontend Layer (UI)                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │      Streamlit App (app_multi_agent.py)          │   │
│  │                                                   │   │
│  │  • Phân tích Toàn diện                          │   │
│  │  • Phân tích Kỹ thuật                           │   │
│  │  • Hỏi Agent Cụ thể                            │   │
│  │  • Quản lý lịch sử                             │   │
│  └──────────┬───────────────────────────────────────┘   │
│             │                                            │
└─────────────┼────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│           Orchestration Layer (Coordinator)              │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │   MultiAgentCoordinator / Advanced Coordinator   │   │
│  │                                                   │   │
│  │  • Quản lý lifecycle agent                      │   │
│  │  • Điều phối các workflow                       │   │
│  │  • Quản lý cuộc hội thoại                       │   │
│  │  • Lưu kết quả phân tích                        │   │
│  └──────────┬───────────────────────────────────────┘   │
│             │                                            │
└─────────────┼────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              Agent Layer (Multi-Agents)                  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────┬──────────────────┬─────────────┐   │
│  │                 │                  │             │   │
│  ▼                 ▼                  ▼             ▼   │
│                                                     │   │
│  ┌────────────────────┐  ┌─────────────────────┐   │   │
│  │ ResearchAgent      │  │ AnalystAgent        │   │   │
│  ├────────────────────┤  ├─────────────────────┤   │   │
│  │ • RAG Search       │  │ • Data Analysis     │   │   │
│  │ • Tìm kiếm PDF     │  │ • Technical Calc    │   │   │
│  │ • Thông tin cơ bản │  │ • Trend Analysis    │   │   │
│  └────────────────────┘  └─────────────────────┘   │   │
│                                                     │   │
│  ┌──────────────────────┐  ┌───────────────────┐   │   │
│  │ StrategyAgent        │  │ [Advanced Agents] │   │   │
│  ├──────────────────────┤  ├───────────────────┤   │   │
│  │ • Tổng hợp phân tích │  │ • RiskManagement  │   │   │
│  │ • Sinh chiến lược    │  │ • NewsAnalysis    │   │   │
│  │ • Entry/Target/SL    │  │ • Portfolio Mgmt  │   │   │
│  └──────────────────────┘  └───────────────────┘   │   │
│                                                     │   │
└─────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│               Tools & Data Layer                         │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┬──────────────────┬─────────────┐   │
│  │                  │                  │             │   │
│  ▼                  ▼                  ▼             ▼   │
│                                                     │   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐   │   │
│  │ RAG System   │  │ Stock Data   │  │ Tools    │   │   │
│  ├──────────────┤  ├──────────────┤  ├──────────┤   │   │
│  │ • FAISS      │  │ • Parquet    │  │ • Tech   │   │   │
│  │ • BM25       │  │ • API        │  │   Indic  │   │   │
│  │ • Embeddings │  │ • Historical │  │ • Calc   │   │   │
│  └──────────────┘  └──────────────┘  └──────────┘   │   │
│                                                     │   │
│  ┌─────────────────────────────────────────────┐   │   │
│  │ LLM (Google Gemini / OpenAI)                │   │   │
│  └─────────────────────────────────────────────┘   │   │
│                                                     │   │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow - Phân Tích Toàn Diện

```
User Input: "Phân tích AAPL"
       │
       ▼
┌─────────────────────────────┐
│ MultiAgentCoordinator       │
│ analyze_ticker("AAPL")      │
└──────────┬──────────────────┘
           │
           ├─────────────────────────────────┐
           │                                 │
           ▼ [STEP 1]                       ▼ [STEP 2]
    ┌────────────────────┐          ┌────────────────────┐
    │ AnalystAgent       │          │ ResearchAgent      │
    │ analyze_stock_data │          │ search_documents   │
    │ ("AAPL")           │          │ ("AAPL")           │
    └────────┬───────────┘          └────────┬───────────┘
             │                               │
             │ Analysis Output               │ Research Output
             │ • Giá gần đây                 │ • Quy tắc giao dịch
             │ • Xu hướng                    │ • Phân tích cơ bản
             │ • Chỉ báo kỹ thuật            │ • Thông tin lý thuyết
             │                               │
             └───────────────┬───────────────┘
                             │
                    [STEP 3] ▼
           ┌─────────────────────────────────┐
           │ StrategyAgent                   │
           │ process_input(combined_data)    │
           └────────┬────────────────────────┘
                    │
                    │ Strategy Output
                    │ • Entry Point
                    │ • Target Price
                    │ • Stop Loss
                    │ • Risk/Reward
                    │
                    ▼
           ┌─────────────────────────────────┐
           │ Results Aggregation             │
           │ {technical, fundamental, ...}   │
           └────────┬────────────────────────┘
                    │
                    ▼
           ┌─────────────────────────────────┐
           │ Return to User                  │
           │ Display in Streamlit            │
           └─────────────────────────────────┘
```

---

## 3. Agent Communication Pattern

```
┌─────────────────────────────────────────────────────────┐
│           MultiAgentCoordinator                         │
└─────────────────────────────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌──────────┐      ┌──────────────┐      ┌──────────┐
│ Research │      │ Analyst      │      │ Strategy │
│ Agent    │◄────►│ Agent        │◄────►│ Agent    │
└──────────┘      └──────────────┘      └──────────┘
    │                   │                   │
    │ Chat History      │ Chat History      │ Chat History
    └────────┬──────────┴──────────────────┘
             │
             ▼
     ┌──────────────────┐
     │ Conversation Log │
     └──────────────────┘
```

**Note:** Agent không giao tiếp trực tiếp. Tất cả giao tiếp đi qua Coordinator.

---

## 4. Tool Architecture

```
┌──────────────────────────────────────────────┐
│            Agent Tools System                 │
├──────────────────────────────────────────────┤
│                                               │
│  ResearchAgent Tools:                         │
│  ├─ search_financial_documents                │
│  │  ├─ Input: Query string                    │
│  │  ├─ Process: FAISS + BM25                  │
│  │  └─ Output: Relevant documents             │
│  │                                             │
│  AnalystAgent Tools:                          │
│  ├─ analyze_stock_data                        │
│  │  ├─ Input: Ticker, analysis_type           │
│  │  ├─ Process: Read Parquet, Calculate       │
│  │  └─ Output: Price, trend, indicators       │
│  │                                             │
│  StrategyAgent Tools:                         │
│  ├─ None (không dùng trực tiếp)               │
│  └─ Nhưng sử dụng output từ agents khác       │
│                                               │
│  [Advanced Tools]:                            │
│  ├─ calculate_technical_indicators            │
│  │  └─ SMA, EMA, RSI, MACD, Bollinger, ATR   │
│  ├─ calculate_portfolio_metrics               │
│  │  └─ Allocation, Diversification            │
│  └─ evaluate_market_sentiment                 │
│     └─ Sentiment score, Impact level          │
│                                               │
└──────────────────────────────────────────────┘
```

---

## 5. State Management

```
┌─────────────────────────────────┐
│ MultiAgentCoordinator State      │
├─────────────────────────────────┤
│                                  │
│ agents: Dict[str, FinanceAgent]  │
│  ├─ research                     │
│  ├─ analyst                      │
│  ├─ strategy                     │
│  ├─ risk_management (opt)        │
│  ├─ news_analysis (opt)          │
│  └─ portfolio (opt)              │
│                                  │
│ conversation_log: List[Dict]     │
│  └─ Lưu tất cả phân tích         │
│                                  │
└─────────────────────────────────┘
         │
         ▼ (each agent has)
┌─────────────────────────────────┐
│ FinanceAgent State               │
├─────────────────────────────────┤
│                                  │
│ name: str                        │
│ llm: ChatGoogleGenerativeAI      │
│ tools: List[Tool]                │
│ executor: AgentExecutor          │
│ conversation_history: List[Msg]  │
│                                  │
└─────────────────────────────────┘
```

---

## 6. Streamlit App Flow

```
┌───────────────────────────────────────────────────┐
│       Streamlit App (app_multi_agent.py)          │
└───────────────────────────────────────────────────┘
        │
        ├─ Session State Init
        │  ├─ embedding
        │  ├─ ensemble_retriever
        │  ├─ llm
        │  └─ coordinator
        │
        └─ Main UI
           │
           ├─ Sidebar
           │  └─ System Info, Settings
           │
           └─ Main Content
              │
              ├─ Tab 1: Phân tích Toàn diện
              │  ├─ Input: Ticker
              │  ├─ Process: analyze_ticker("full")
              │  └─ Output: 3 analyses
              │
              ├─ Tab 2: Phân tích Kỹ thuật
              │  ├─ Input: Ticker
              │  ├─ Process: analyze_ticker("technical")
              │  └─ Output: 1 analysis
              │
              └─ Tab 3: Hỏi Agent Cụ thể
                 ├─ Input: Agent choice, Question
                 ├─ Process: ask_agents()
                 └─ Output: Agent response
```

---

## 7. File Dependencies

```
app_multi_agent.py
├─ import multi_agent_system.py
│  ├─ FinanceAgent (base)
│  ├─ ResearchAgent
│  ├─ AnalystAgent
│  ├─ StrategyAgent
│  └─ MultiAgentCoordinator
│
├─ import extract_data.py
│  └─ ETL functions
│
└─ LangChain, Streamlit, etc.

example_usage.py
├─ import multi_agent_system.py
└─ import extract_data.py

advanced_features.py
├─ import multi_agent_system.py
│  ├─ Extend FinanceAgent
│  ├─ Create new agents
│  └─ Extend MultiAgentCoordinator
│
└─ New tools + workflows
```

---

## 8. Request/Response Cycle

```
User Request
     │
     ▼
┌─────────────────────────────┐
│ Streamlit Input             │
│ • Ticker: "AAPL"            │
│ • Mode: "full"              │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Coordinator.analyze_ticker  │
│ (ticker, analysis_type)     │
└────────┬────────────────────┘
         │
    ┌────┴────┐
    │          │
    ▼ (Async) ▼ (Async)
  Agent 1    Agent 2      [Parallel execution]
    │          │
    └────┬─────┘
         │
         ▼
    ┌─────────────────┐
    │ Agent 3 Process │
    └────────┬────────┘
             │
             ▼
    ┌──────────────────────┐
    │ Aggregate Results     │
    │ {analysis1,          │
    │  analysis2,          │
    │  analysis3}          │
    └────────┬─────────────┘
             │
             ▼
    ┌──────────────────────┐
    │ Return to Streamlit  │
    │ Display Results      │
    └──────────────────────┘
```

---

## 9. Advanced Workflow Example

```
Input: "Generate Trading Plan for AAPL with $10,000"
       │
       ▼
┌──────────────────────────────────┐
│ generate_trading_plan()          │
└────────┬─────────────────────────┘
         │
         ├─ Step 1: Phân tích toàn diện
         │  └─ analyze_ticker("AAPL", "full")
         │     ├─ ResearchAgent: Thông tin cơ bản
         │     ├─ AnalystAgent: Phân tích kỹ thuật
         │     └─ StrategyAgent: Chiến lược ban đầu
         │
         ├─ Step 2: Tạo kế hoạch chi tiết
         │  └─ StrategyAgent.process_input(detailed_prompt)
         │     ├─ Entry points (3 mức)
         │     ├─ Position sizing
         │     ├─ Risk management
         │     ├─ Take profit levels
         │     └─ Exit conditions
         │
         ├─ Step 3: Đánh giá rủi ro [Optional]
         │  └─ RiskManagementAgent.process_input()
         │     ├─ Risk score
         │     ├─ VaR calculation
         │     └─ Recommended position size
         │
         └─ Return: Complete Trading Plan
            {
              "ticker": "AAPL",
              "investment": 10000,
              "analysis": {...},
              "trading_plan": "...",
              "risk_assessment": "..." [opt]
            }
```

---

## 10. System Requirements

```
┌─────────────────────────────────────────────┐
│ System Architecture                         │
├─────────────────────────────────────────────┤
│                                              │
│ 🎯 Frontend                                  │
│ • Streamlit 1.38.0                          │
│ • Browser (any modern)                      │
│                                              │
│ 🧠 AI/LLM                                    │
│ • Google Gemini API                         │
│ • LangChain 0.2.16                          │
│ • HuggingFace Embeddings                    │
│                                              │
│ 📦 Data Processing                          │
│ • Pandas, NumPy                             │
│ • FAISS (Vector Store)                      │
│ • BM25Retriever                             │
│                                              │
│ 🐍 Runtime                                   │
│ • Python 3.8+                               │
│ • Virtual Environment recommended           │
│                                              │
│ 🔑 Authentication                           │
│ • Google API Key (.env)                     │
│                                              │
│ 💾 Storage                                   │
│ • Local file system (data/)                 │
│ • FAISS index (faiss_index_conversation/)   │
│ • Parquet files (historical data)           │
│                                              │
└─────────────────────────────────────────────┘
```

---

Hết.
