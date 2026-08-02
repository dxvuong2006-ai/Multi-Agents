"""
Tùy chỉnh Nâng Cao cho Hệ Thống Multi-Agent
Bao gồm: Agent tùy chỉnh, Tool bổ sung, Workflow nâng cao
"""

from multi_agent_system import (
    FinanceAgent, 
    ResearchAgent, 
    AnalystAgent, 
    StrategyAgent,
    MultiAgentCoordinator
)
from langchain.tools import tool
from langchain_core.messages import BaseMessage
from typing import List, Dict, Any
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# 1. AGENT TÙY CHỈNH
# ============================================================================

class RiskManagementAgent(FinanceAgent):
    """
    Agent quản lý rủi ro - Đánh giá và cảnh báo rủi ro
    """
    def __init__(self, llm, tools_list=None):
        system_prompt = """Bạn là chuyên gia quản lý rủi ro tài chính với kinh nghiệm sâu.
        
Khi nhận yêu cầu, hãy:
1. Xác định các yếu tố rủi ro chính
2. Đánh giá mức độ rủi ro (Thấp/Trung/Cao)
3. Đưa ra khuyến nghị quản lý rủi ro:
   - Kích thước vị trí (position size)
   - Stop loss phù hợp
   - Diversification strategy
4. Cảnh báo các rủi ro tiềm ẩn

Luôn ưu tiên bảo vệ vốn của nhà đầu tư."""
        
        if tools_list is None:
            tools_list = []
        
        super().__init__("RiskManagementAgent", llm, tools_list, system_prompt)


class NewsAnalysisAgent(FinanceAgent):
    """
    Agent phân tích tin tức - Đánh giá tác động của tin tức
    """
    def __init__(self, llm, tools_list=None):
        system_prompt = """Bạn là chuyên gia phân tích tin tức thị trường tài chính.
        
Khi phân tích tin tức, hãy:
1. Xác định loại tin tức (Tích cực/Tiêu cực/Trung lập)
2. Đánh giá mức độ tác động (Yếu/Vừa/Mạnh)
3. Dự báo phản ứng thị trường:
   - Ngắn hạn (intraday)
   - Trung hạn (1-4 tuần)
   - Dài hạn (tháng/năm)
4. So sánh với các sự kiện tương tự trong quá khứ

Luôn cung cấp phân tích khách quan dựa trên dữ liệu lịch sử."""
        
        if tools_list is None:
            tools_list = []
        
        super().__init__("NewsAnalysisAgent", llm, tools_list, system_prompt)


class PortfolioAgent(FinanceAgent):
    """
    Agent quản lý danh mục - Tối ưu hóa portfolio
    """
    def __init__(self, llm, tools_list=None):
        system_prompt = """Bạn là chuyên gia quản lý danh mục đầu tư chuyên nghiệp.
        
Khi tối ưu hóa portfolio, hãy:
1. Phân tích cấu trúc danh mục hiện tại
2. Đánh giá sự cân bằng rủi ro/lợi nhuận
3. Xác định những vị trí:
   - Cần tăng cộng (overweight)
   - Cần giảm bớt (underweight)
   - Nên loại bỏ (sell)
4. Đề xuất chiến lược rebalancing
5. Tính toán:
   - Expected return
   - Portfolio volatility
   - Sharpe ratio

Sử dụng các nguyên tắc diversification hiện đại."""
        
        if tools_list is None:
            tools_list = []
        
        super().__init__("PortfolioAgent", llm, tools_list, system_prompt)


# ============================================================================
# 2. TOOL BỔ SUNG
# ============================================================================

@tool
def calculate_technical_indicators(df_data: str, indicators: List[str]) -> str:
    """
    Tính toán các chỉ báo kỹ thuật
    - df_data: Dữ liệu dưới dạng JSON
    - indicators: Danh sách chỉ báo (SMA, EMA, RSI, MACD, Bollinger, ATR)
    """
    import pandas as pd
    import json
    
    try:
        data = json.loads(df_data)
        df = pd.DataFrame(data)
        
        results = {}
        
        # Simple Moving Average (SMA)
        if "SMA" in indicators:
            for period in [10, 20, 50, 200]:
                df[f'SMA_{period}'] = df['close'].rolling(window=period).mean()
            results['SMA'] = df[[f'SMA_{p}' for p in [10, 20, 50, 200]]].tail().to_dict()
        
        # Exponential Moving Average (EMA)
        if "EMA" in indicators:
            for period in [12, 26]:
                df[f'EMA_{period}'] = df['close'].ewm(span=period).mean()
            results['EMA'] = df[[f'EMA_{p}' for p in [12, 26]]].tail().to_dict()
        
        # Relative Strength Index (RSI)
        if "RSI" in indicators:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            results['RSI'] = df['RSI'].tail().to_dict()
        
        # Bollinger Bands
        if "Bollinger" in indicators:
            sma = df['close'].rolling(window=20).mean()
            std = df['close'].rolling(window=20).std()
            df['BB_Upper'] = sma + (std * 2)
            df['BB_Lower'] = sma - (std * 2)
            df['BB_Middle'] = sma
            results['Bollinger'] = df[['BB_Upper', 'BB_Middle', 'BB_Lower']].tail().to_dict()
        
        # Average True Range (ATR)
        if "ATR" in indicators:
            df['TR'] = df[['high', 'low', 'close']].apply(
                lambda row: max(
                    row['high'] - row['low'],
                    abs(row['high'] - df['close'].shift(1).iloc[-1]),
                    abs(row['low'] - df['close'].shift(1).iloc[-1])
                ),
                axis=1
            )
            df['ATR'] = df['TR'].rolling(window=14).mean()
            results['ATR'] = df['ATR'].tail().to_dict()
        
        return json.dumps(results, indent=2, ensure_ascii=False)
    
    except Exception as e:
        return f"Lỗi tính toán chỉ báo: {str(e)}"


@tool
def calculate_portfolio_metrics(positions: str) -> str:
    """
    Tính toán các chỉ số portfolio
    - positions: JSON string của danh sách vị trí {symbol: amount, ...}
    """
    import json
    
    try:
        positions_data = json.loads(positions)
        
        total_value = sum(positions_data.values())
        allocation = {
            symbol: {
                "amount": amount,
                "percentage": round((amount / total_value) * 100, 2) if total_value > 0 else 0
            }
            for symbol, amount in positions_data.items()
        }
        
        metrics = {
            "total_portfolio_value": total_value,
            "allocation": allocation,
            "largest_position": max(allocation.items(), key=lambda x: x[1]["percentage"]),
            "number_of_positions": len(positions_data),
            "diversification_score": round(1 - max([a["percentage"] for a in allocation.values()]) / 100, 2)
        }
        
        return json.dumps(metrics, indent=2, ensure_ascii=False)
    
    except Exception as e:
        return f"Lỗi tính toán portfolio: {str(e)}"


@tool
def evaluate_market_sentiment(news_list: str) -> str:
    """
    Đánh giá cảm tính thị trường từ danh sách tin tức
    - news_list: JSON array của tin tức
    """
    import json
    
    try:
        news_data = json.loads(news_list)
        
        sentiment_score = 0
        total_impact = 0
        
        for item in news_data:
            # Tính sentiment score (-1 negative, 0 neutral, 1 positive)
            sentiment = item.get("sentiment", 0)
            impact = item.get("impact_level", 0.5)  # 0-1
            
            sentiment_score += sentiment * impact
            total_impact += impact
        
        avg_sentiment = sentiment_score / total_impact if total_impact > 0 else 0
        
        if avg_sentiment > 0.3:
            market_sentiment = "Tích cực 📈"
        elif avg_sentiment < -0.3:
            market_sentiment = "Tiêu cực 📉"
        else:
            market_sentiment = "Trung lập ➡️"
        
        return f"""ĐÁNH GIÁ CẢM TÍ THỊ TRƯỜNG:
Market Sentiment: {market_sentiment}
Sentiment Score: {round(avg_sentiment, 2)} (từ -1 đến 1)
Total Impact: {round(total_impact, 2)}
Khuyến nghị: {'Tăng vị trí long' if avg_sentiment > 0 else 'Tăng vị trí short' if avg_sentiment < 0 else 'Giữ nguyên'}"""
    
    except Exception as e:
        return f"Lỗi đánh giá sentiment: {str(e)}"


# ============================================================================
# 3. EXTENDED COORDINATOR - MỞ RỘNG
# ============================================================================

class AdvancedMultiAgentCoordinator(MultiAgentCoordinator):
    """
    Mở rộng MultiAgentCoordinator với các tính năng nâng cao
    """
    
    def __init__(self, llm, tools_dict: Dict[str, Any], custom_agents: Dict[str, Any] = None):
        super().__init__(llm, tools_dict)
        
        # Thêm các agent tùy chỉnh
        if custom_agents:
            for agent_name, agent_instance in custom_agents.items():
                self.agents[agent_name] = agent_instance
    
    def multi_ticket_analysis(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Phân tích nhiều mã chứng khoán cùng lúc
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "tickers": tickers,
            "individual_analysis": {},
            "comparative_analysis": ""
        }
        
        print(f"📊 Phân tích {len(tickers)} mã chứng khoán...")
        
        # Phân tích từng mã
        for ticker in tickers:
            print(f"  • {ticker}...")
            results["individual_analysis"][ticker] = self.analyze_ticker(
                ticker,
                analysis_type="technical"
            )
        
        # Phân tích so sánh
        comparison_prompt = f"""Dựa trên phân tích kỹ thuật của các mã: {', '.join(tickers)}
        
Vui lòng so sánh:
1. Xu hướng tương đối
2. Sức mạnh momentum
3. Cơ hội giao dịch đôi (Pair Trading)
4. Khuyến nghị: Mã nào có cơ hội tốt nhất?"""
        
        comparison = self.agents["strategy"].process_input(comparison_prompt)
        results["comparative_analysis"] = comparison
        
        return results
    
    def comprehensive_portfolio_review(self, portfolio_positions: Dict[str, float]) -> Dict[str, Any]:
        """
        Đánh giá portfolio toàn diện
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "portfolio_positions": portfolio_positions
        }
        
        print("📈 Đánh giá portfolio...")
        
        # Tính toán portfolio metrics
        import json
        metrics = evaluate_market_sentiment(json.dumps({"sentiment": 0, "impact_level": 0}))
        results["portfolio_metrics"] = metrics
        
        # Phân tích rủi ro nếu có Risk Agent
        if "risk_management" in self.agents:
            risk_prompt = f"""Đánh giá rủi ro cho portfolio với vị trí:
{json.dumps(portfolio_positions, indent=2)}

Cảnh báo các rủi ro tiềm ẩn và khuyến nghị quản lý rủi ro."""
            
            risk_analysis = self.agents["risk_management"].process_input(risk_prompt)
            results["risk_analysis"] = risk_analysis
        
        # Tối ưu hóa portfolio nếu có Portfolio Agent
        if "portfolio" in self.agents:
            optimization_prompt = f"""Tối ưu hóa portfolio với vị trí hiện tại:
{json.dumps(portfolio_positions, indent=2)}

Đề xuất những thay đổi để cân bằng rủi ro/lợi nhuận tốt hơn."""
            
            optimization = self.agents["portfolio"].process_input(optimization_prompt)
            results["optimization_suggestion"] = optimization
        
        return results
    
    def market_scenario_analysis(self, scenario: str) -> Dict[str, Any]:
        """
        Phân tích kịch bản thị trường
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "scenario": scenario,
            "responses": {}
        }
        
        print(f"🎬 Phân tích kịch bản: {scenario}...")
        
        # Mỗi agent phân tích kịch bản từ góc độ của nó
        for agent_name in ["analyst", "research", "strategy"]:
            if agent_name in self.agents:
                prompt = f"""Trong kịch bản: {scenario}
                
Hãy phân tích tác động và đề xuất chiến lược."""
                
                response = self.agents[agent_name].process_input(prompt)
                results["responses"][agent_name] = response
        
        return results
    
    def generate_trading_plan(self, ticker: str, investment_amount: float) -> Dict[str, Any]:
        """
        Tạo kế hoạch giao dịch chi tiết
        """
        print(f"\n📋 Tạo kế hoạch giao dịch cho {ticker}...")
        
        # Bước 1: Phân tích toàn diện
        print("  [Bước 1] Phân tích toàn diện...")
        analysis = self.analyze_ticker(ticker, analysis_type="full")
        
        # Bước 2: Tạo kế hoạch chi tiết
        print("  [Bước 2] Tạo kế hoạch chi tiết...")
        plan_prompt = f"""Dựa trên phân tích toàn diện của {ticker} với khoản đầu tư {investment_amount}:

Tạo kế hoạch giao dịch CHI TIẾT bao gồm:
1. Mục tiêu đầu tư (ngắn/trung/dài hạn)
2. Entry point và lý do
3. Position size tối ưu
4. Take profit levels (nhiều mức)
5. Stop loss levels
6. Risk/Reward ratio
7. Timeline
8. Điều kiện để thoát vị trí
9. Quản lý vốn (money management rules)
10. Kế hoạch B (nếu có biến động thị trường)"""
        
        trading_plan = self.agents["strategy"].process_input(plan_prompt)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker,
            "investment_amount": investment_amount,
            "analysis": analysis,
            "trading_plan": trading_plan
        }


# ============================================================================
# 4. WORKFLOW NÂNG CAO
# ============================================================================

class AdvancedWorkflow:
    """
    Các workflow nâng cao cho các tình huống phức tạp
    """
    
    @staticmethod
    def swing_trading_setup(coordinator, ticker: str):
        """
        Workflow cho Swing Trading
        """
        print(f"\n🔄 SWING TRADING SETUP cho {ticker}")
        print("=" * 60)
        
        # 1. Xác định xu hướng dài hạn
        print("[1] Xác định xu hướng dài hạn...")
        trend_q = f"Phân tích xu hướng dài hạn của {ticker} (4H/Daily)"
        trend = coordinator.ask_agents(trend_q, "analyst")
        
        # 2. Tìm điểm entry
        print("[2] Tìm điểm entry...")
        entry_q = f"Các mức support/resistance quan trọng của {ticker} là gì?"
        entries = coordinator.ask_agents(entry_q, "analyst")
        
        # 3. Quản lý rủi ro
        print("[3] Quản lý rủi ro...")
        if "risk_management" in coordinator.agents:
            risk_q = f"Với {ticker}, position size nên là bao nhiêu? Stop loss ở đâu?"
            risk = coordinator.ask_agents(risk_q, "risk_management")
        else:
            risk = "Risk Management Agent không sẵn"
        
        print("\n✅ Swing Trading Setup hoàn thành!")
        return {
            "ticker": ticker,
            "trend_analysis": trend,
            "entry_levels": entries,
            "risk_management": risk
        }
    
    @staticmethod
    def breakout_trading_setup(coordinator, ticker: str):
        """
        Workflow cho Breakout Trading
        """
        print(f"\n🚀 BREAKOUT TRADING SETUP cho {ticker}")
        print("=" * 60)
        
        # 1. Xác định các mức resistance
        print("[1] Xác định mức resistance chính...")
        resistance_q = f"{ticker} đang consolidate ở mức nào? Mức breakout target là gì?"
        resistances = coordinator.ask_agents(resistance_q, "analyst")
        
        # 2. Xác định trigger
        print("[2] Xác định trigger giao dịch...")
        trigger_q = f"Những tín hiệu nào cho thấy {ticker} sắp breakout?"
        triggers = coordinator.ask_agents(trigger_q, "analyst")
        
        # 3. Kế hoạch thoát
        print("[3] Kế hoạch thoát...")
        exit_q = f"Sau khi breakout, mục tiêu giá và stop loss của {ticker} nên là bao nhiêu?"
        exit_plan = coordinator.ask_agents(exit_q, "strategy")
        
        print("\n✅ Breakout Trading Setup hoàn thành!")
        return {
            "ticker": ticker,
            "resistance_levels": resistances,
            "trigger_signals": triggers,
            "exit_plan": exit_plan
        }


# ============================================================================
# 5. FACTORY FUNCTIONS
# ============================================================================

def create_advanced_multi_agent_system(llm, tools_dict: Dict[str, Any]) -> AdvancedMultiAgentCoordinator:
    """
    Tạo hệ thống multi-agent nâng cao với thêm các agent tùy chỉnh
    """
    
    # Tạo các agent bổ sung
    custom_agents = {
        "risk_management": RiskManagementAgent(llm),
        "news_analysis": NewsAnalysisAgent(llm),
        "portfolio": PortfolioAgent(llm)
    }
    
    # Tạo coordinator nâng cao
    coordinator = AdvancedMultiAgentCoordinator(llm, tools_dict, custom_agents)
    
    return coordinator
