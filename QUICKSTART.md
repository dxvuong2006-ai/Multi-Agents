# ⚡ Quick Start Guide - Multi-Agent Finance Analyzer

## 🚀 30 Giây Để Bắt Đầu

### Bước 1: Cài đặt

```bash
pip install -r requirements.txt
```

### Bước 2: Thiết lập API Key

```bash
# Tạo file .env trong thư mục project
echo GOOGLE_API_KEY=your_google_api_key > .env
```

### Bước 3: Chạy Ứng dụng

```bash
streamlit run app_multi_agent.py
```

**Đó là tất cả! 🎉** Ứng dụng sẽ mở ở `http://localhost:8501`

---

## 💡 5 Cách Sử Dụng Phổ Biến

### 1. Phân tích Nhanh Một Mã Chứng Khoán

```bash
streamlit run app_multi_agent.py
# -> Chọn "Phân tích Toàn diện"
# -> Nhập AAPL
# -> Click "Phân tích"
```

**Kết quả:** Phân tích kỹ thuật + thông tin cơ bản + chiến lược giao dịch

---

### 2. Hỏi Agent Cụ Thể

```bash
streamlit run app_multi_agent.py
# -> Chọn "Hỏi Agent Cụ thể"
# -> Chọn agent: "Analyst Agent"
# -> Câu hỏi: "GC=F trend up hay down?"
# -> Click "Gửi"
```

---

### 3. Sử dụng Python Script (Nâng cao)

```python
from multi_agent_system import create_multi_agent_system
from langchain_google_genai import ChatGoogleGenerativeAI

# Khởi tạo
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
coordinator = create_multi_agent_system(llm, tools_dict)

# Phân tích
results = coordinator.analyze_ticker("AAPL", "full")
print(results["analyses"]["strategy"])
```

---

### 4. Chạy Ví Dụ Tự Động

```bash
python example_usage.py
```

**Chạy 2 ví dụ mặc định:**

- ✅ Phân tích AAPL toàn diện
- ✅ Hỏi các agent cụ thể

---

### 5. Tính Năng Nâng Cao (Advanced)

```python
from advanced_features import create_advanced_multi_agent_system, AdvancedWorkflow

# Hệ thống mở rộng với thêm agent (Risk, News, Portfolio)
coordinator = create_advanced_multi_agent_system(llm, tools_dict)

# Phân tích swing trading
setup = AdvancedWorkflow.swing_trading_setup(coordinator, "AAPL")

# Đánh giá portfolio
results = coordinator.comprehensive_portfolio_review({
    "AAPL": 10000,
    "GC=F": 5000
})
```

---

## 📊 Streamlit App - Hướng Dẫn Sử Dụng

### Tab 1: "Phân tích Toàn diện" 📊

**Giao diện:**

```
Mã chứng khoán: [AAPL________________]  [Phân tích]

Kết quả:
├─ 📈 Phân tích Kỹ thuật
│  └─ (Từ AnalystAgent)
├─ 📚 Thông tin Cơ bản
│  └─ (Từ ResearchAgent)
└─ 💡 Chiến lược Giao dịch
   └─ (Từ StrategyAgent)
```

**Cách dùng:**

1. Nhập mã chứng khoán (VD: AAPL, GC=F, MSFT)
2. Click "Phân tích"
3. Chờ 10-30 giây
4. Xem kết quả chi tiết

---

### Tab 2: "Phân tích Kỹ thuật" 📈

**Giao diện:**

```
Mã chứng khoán: [GC=F________________]  [Phân tích]

Kết quả:
📊 (Chỉ phân tích kỹ thuật, nhanh hơn)
```

**Cách dùng:**

- Kiểm tra nhanh xu hướng
- Lấy giá gần đây
- So sánh Moving Average

---

### Tab 3: "Hỏi Agent Cụ thể" 💬

**Giao diện:**

```
Chọn Agent: [Research Agent ▼]

Câu hỏi:
[________________________________________]
[________________________________________]

[Gửi]
```

**Cách dùng:**

1. Chọn agent:
   - **Research Agent**: Tìm kiếm thông tin
   - **Analyst Agent**: Phân tích dữ liệu
   - **Strategy Agent**: Tư vấn chiến lược

2. Nhập câu hỏi
3. Click "Gửi"

**Ví dụ câu hỏi:**

```
Research Agent:
- "Chiến lược giao dịch tốt là gì?"
- "Tìm kiếm thông tin về RSI"

Analyst Agent:
- "Phân tích AAPL"
- "GC=F trend up hay down?"

Strategy Agent:
- "Nên giao dịch AAPL không?"
- "Entry point cho MSFT ở đâu?"
```

---

## 🎯 Ví Dụ Thực Tế

### Ví dụ 1: Phân tích Vàng (GC=F)

```
Input:  AAPL
Mode:   Phân tích Toàn diện

Output:
📈 Phân tích Kỹ thuật:
   - Giá hiện tại: $230.15
   - Trend: Tăng
   - MA10 vs MA20: MA10 > MA20 (bullish)
   - RSI: 65 (strong)
   - Khuyến nghị: BUY

📚 Thông tin Cơ bản:
   - Cổ phiếu công nghệ hàng đầu
   - Quy tắc: Mua khi RSI < 30, Bán khi RSI > 70
   - P/E ratio: 25 (trung bình)

💡 Chiến lược:
   - Entry: $228
   - Target: $240
   - Stop Loss: $220
   - Risk/Reward: 1:3
```

### Ví dụ 2: Hỏi Research Agent

```
Input:  "Hãy tìm kiếm quy tắc để lọc cổ phiếu tốt"
Agent:  Research Agent

Output:
- Quy tắc 1: P/E ratio < 20
- Quy tắc 2: ROE > 15%
- Quy tắc 3: Trend up trên Daily chart
- ...
```

### Ví dụ 3: Hỏi Analyst Agent

```
Input:  "Tôi có nên mua AAPL hiện tại không?"
Agent:  Analyst Agent

Output:
Dựa trên phân tích kỹ thuật gần đây:
- Breakout trên 230
- Support: 225
- Resistance: 240
- Khuyến nghị: BUY
```

---

## 🔄 Workflow Tiêu Biểu

### Workflow 1: Tìm Điểm Giao Dịch

```
User Input: "AAPL"
    ↓
[Phân tích Toàn diện]
    ↓
Analyst → "Phân tích kỹ thuật AAPL"
    ├─ Giá gần đây
    ├─ Trend
    └─ Entry points
    ↓
Research → "Thông tin cơ bản AAPL"
    ├─ Quy tắc giao dịch
    └─ Phân tích cơ bản
    ↓
Strategy → "Chiến lược cho AAPL"
    ├─ Entry point cụ thể
    ├─ Target giá
    └─ Stop loss
    ↓
Output: Chiến lược giao dịch chi tiết
```

### Workflow 2: Hỏi Nhanh

```
User: "Trend GC=F?"
    ↓
Analyst Agent
    ↓
Output: "Trend Up/Down + lý do"
```

---

## ⚙️ Cấu Hình Mặc Định

| Thiết lập       | Giá trị          | Thay đổi được |
| --------------- | ---------------- | ------------- |
| LLM Model       | gemini-pro       | ✅ Có         |
| Temperature     | 0.3              | ✅ Có         |
| Embedding Model | all-MiniLM-L6-v2 | ✅ Có         |
| Chunk Size      | 1200             | ✅ Có         |
| Retriever k     | 3                | ✅ Có         |

**Cách thay đổi:**

```python
# File: app_multi_agent.py
st.session_state.llm = ChatGoogleGenerativeAI(
    model="gemini-pro",  # ← Thay đổi ở đây
    temperature=0.3      # ← Hoặc ở đây
)
```

---

## 🐛 Vấn Đề Thường Gặp

### ❌ Lỗi: "ModuleNotFoundError: No module named 'langchain'"

```bash
pip install -r requirements.txt
```

### ❌ Lỗi: "Google API key not found"

```bash
# Kiểm tra .env file
cat .env  # Linux/Mac
type .env # Windows

# Nếu không có, tạo mới
echo GOOGLE_API_KEY=your_key > .env
```

### ❌ Lỗi: "Vector store not found"

```python
# Vector store sẽ tự động tạo lần đầu
# Hoặc rebuild thủ công:
import os
import shutil
shutil.rmtree("faiss_index_conversation", ignore_errors=True)
# Chạy app lại sẽ rebuild
```

### ❌ Streamlit chậm

```bash
# Cấp phát cache
streamlit cache clear
streamlit run app_multi_agent.py
```

---

## 🎓 Học Tiếp Theo

### Cấp 1: Sử Dụng Cơ Bản

- ✅ Chạy Streamlit app
- ✅ Phân tích mã chứng khoán
- ✅ Hiểu kết quả

### Cấp 2: Sử Dụng Nâng Cao

- 📖 Đọc [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md)
- 🐍 Chạy [example_usage.py](example_usage.py)
- 💻 Tùy chỉnh prompt

### Cấp 3: Phát Triển

- 🏗️ Đọc [advanced_features.py](advanced_features.py)
- 🔧 Tạo Agent mới
- 🚀 Tạo Workflow mới

---

## 📞 Hỗ Trợ

| Vấn đề           | Giải pháp                         |
| ---------------- | --------------------------------- |
| Chậm             | Xóa cache `streamlit cache clear` |
| Lỗi API          | Kiểm tra .env file                |
| PDF không tải    | Đặt `REBUILD = True`              |
| Không có kết quả | Chờ 30 giây, thử lại              |

---

## 🎉 Tiếp Theo

Bây giờ bạn có thể:

- ✅ Phân tích bất kỳ mã chứng khoán nào
- ✅ Nhận tư vấn chiến lược từ AI
- ✅ So sánh quan điểm từ nhiều agent
- ✅ Tạo kế hoạch giao dịch chi tiết

**Hãy bắt đầu ngay!** 🚀

```bash
streamlit run app_multi_agent.py
```

---

**Phiên bản**: 1.0  
**Cập nhật**: May 2026
