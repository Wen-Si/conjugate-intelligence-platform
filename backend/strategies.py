"""
策略数据库和分析引擎模块
包含股票、债券、期权、期货四大类共65+种投资策略
每个策略提供完整的参数定义和分析计算功能
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


# ============================================================
# 策略基类
# ============================================================

class BaseStrategy(ABC):
    """策略基类，定义所有策略的通用接口"""

    def __init__(self, strategy_id: str, name: str, category: str,
                 description: str, advantages: List[str],
                 disadvantages: List[str], risks: List[str],
                 parameters: Dict[str, Any]):
        self.id = strategy_id
        self.name = name
        self.category = category
        self.description = description
        self.advantages = advantages
        self.disadvantages = disadvantages
        self.risks = risks
        self.parameters = parameters

    def to_dict(self) -> Dict[str, Any]:
        """将策略信息转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "advantages": self.advantages,
            "disadvantages": self.disadvantages,
            "risks": self.risks,
            "parameters": self.parameters,
        }

    @abstractmethod
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        分析数据并返回结果

        Args:
            df: 包含金融数据的 DataFrame
            **kwargs: 自定义分析参数

        Returns:
            Dict: 包含分析指标的字典
        """
        pass


# ============================================================
# 通用分析计算函数
# ============================================================

def calc_returns(prices: np.ndarray) -> np.ndarray:
    """计算收益率序列"""
    return np.diff(prices) / prices[:-1]


def calc_annualized_return(returns: np.ndarray, periods_per_year: int = 252) -> float:
    """计算年化收益率"""
    if len(returns) == 0:
        return 0.0
    total_return = np.prod(1 + returns) - 1
    n_years = len(returns) / periods_per_year
    if n_years <= 0:
        return 0.0
    return (1 + total_return) ** (1 / n_years) - 1


def calc_max_drawdown(prices: np.ndarray) -> float:
    """计算最大回撤"""
    if len(prices) == 0:
        return 0.0
    cumulative = np.maximum.accumulate(prices)
    drawdowns = (prices - cumulative) / cumulative
    return np.min(drawdowns)


def calc_sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.03,
                      periods_per_year: int = 252) -> float:
    """计算夏普比率"""
    if len(returns) == 0 or np.std(returns) == 0:
        return 0.0
    excess = returns - risk_free_rate / periods_per_year
    return np.mean(excess) / np.std(returns) * np.sqrt(periods_per_year)


def calc_volatility(returns: np.ndarray, periods_per_year: int = 252) -> float:
    """计算年化波动率"""
    if len(returns) == 0:
        return 0.0
    return np.std(returns) * np.sqrt(periods_per_year)


def calc_win_rate(returns: np.ndarray) -> float:
    """计算胜率"""
    if len(returns) == 0:
        return 0.0
    return np.sum(returns > 0) / len(returns)


def calc_profit_loss_ratio(returns: np.ndarray) -> float:
    """计算盈亏比"""
    if len(returns) == 0:
        return 0.0
    wins = returns[returns > 0]
    losses = returns[returns < 0]
    if len(losses) == 0 or np.mean(np.abs(losses)) == 0:
        return float('inf') if len(wins) > 0 else 0.0
    return np.mean(wins) / np.mean(np.abs(losses))


def calc_calmar_ratio(returns: np.ndarray, prices: np.ndarray,
                      periods_per_year: int = 252) -> float:
    """计算卡玛比率"""
    ar = calc_annualized_return(returns, periods_per_year) * 100
    mdd = abs(calc_max_drawdown(prices)) * 100
    return ar / mdd if mdd > 0 else 0.0


def calc_sortino_ratio(returns: np.ndarray, risk_free_rate: float = 0.03,
                       periods_per_year: int = 252) -> float:
    """计算索提诺比率"""
    if len(returns) == 0:
        return 0.0
    excess = returns - risk_free_rate / periods_per_year
    downside = returns[returns < 0]
    if len(downside) == 0 or np.std(downside) == 0:
        return 0.0
    return np.mean(excess) / np.std(downside) * np.sqrt(periods_per_year)


def calc_var(returns: np.ndarray, confidence: float = 0.95) -> float:
    """计算在险价值(VaR)"""
    if len(returns) == 0:
        return 0.0
    return abs(np.percentile(returns, (1 - confidence) * 100))


def calc_downside_deviation(returns: np.ndarray, periods_per_year: int = 252) -> float:
    """计算下行偏差"""
    if len(returns) == 0:
        return 0.0
    downside = returns[returns < 0]
    return np.std(downside) * np.sqrt(periods_per_year) if len(downside) > 0 else 0.0


def common_analyze(prices: np.ndarray, returns: np.ndarray,
                   periods_per_year: int = 252) -> Dict[str, float]:
    """通用分析指标计算"""
    total_ret = (np.prod(1 + returns) - 1) * 100 if len(returns) > 0 else 0.0
    var_ret = np.var(returns)
    return {
        "annualized_return": round(calc_annualized_return(returns, periods_per_year) * 100, 4),
        "max_drawdown": round(calc_max_drawdown(prices) * 100, 4),
        "sharpe_ratio": round(calc_sharpe_ratio(returns), 4),
        "volatility": round(calc_volatility(returns, periods_per_year) * 100, 4),
        "win_rate": round(calc_win_rate(returns) * 100, 4),
        "profit_loss_ratio": round(calc_profit_loss_ratio(returns), 4),
        "total_return": round(total_ret, 4),
        "calmar_ratio": round(calc_calmar_ratio(returns, prices, periods_per_year), 4),
        "sortino_ratio": round(calc_sortino_ratio(returns), 4),
        "beta": round(1.0, 4),
        "alpha": round(calc_annualized_return(returns, periods_per_year) * 100 - 10.0, 4),
        "information_ratio": round(np.mean(returns) / np.std(returns) * np.sqrt(252), 4) if np.std(returns) > 0 else 0.0,
        "tracking_error": round(np.std(returns) * np.sqrt(252) * 100, 4),
        "downside_deviation": round(calc_downside_deviation(returns, periods_per_year) * 100, 4),
        "var": round(calc_var(returns) * 100, 4),
    }


def extract_price_series(df: pd.DataFrame, col: str = None) -> Optional[np.ndarray]:
    """从 DataFrame 中提取价格序列"""
    if df is None or df.empty:
        return None
    price_cols = ['close', 'Close', '收盘价', 'price', 'Price', '价格', '收盘', 'adj_close', 'Adj_Close']
    if col and col in df.columns:
        return df[col].values.astype(float)
    for c in price_cols:
        if c in df.columns:
            return df[c].values.astype(float)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        return df[numeric_cols[0]].values.astype(float)
    return None


# ============================================================
# 股票策略（20种）
# ============================================================

class MomentumStrategy(BaseStrategy):
    """动量策略 - 追踪价格趋势，买入近期表现强势的股票"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_momentum", name="动量策略", category="股票策略",
            description="基于价格动量效应，买入近期表现强势的股票，卖出表现弱势的股票。利用市场中资产价格持续沿同一方向运动的趋势特征。",
            advantages=["在趋势明显的市场中表现优异", "策略逻辑简单清晰，易于实现", "有大量学术研究支持其有效性"],
            disadvantages=["在震荡市中容易产生虚假信号", "可能面临动量崩溃风险", "交易频率较高，成本影响大"],
            risks=["趋势反转风险", "流动性风险", "过度拟合风险"],
            parameters={"lookback_period": {"value": 20, "description": "回溯期（交易日）"}, "holding_period": {"value": 10, "description": "持有期（交易日）"}, "top_n": {"value": 10, "description": "选股数量"}, "rebalance_freq": {"value": "weekly", "description": "调仓频率"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        lb = kwargs.get("lookback_period", 20)
        momentum = (prices[-1] / prices[-lb] - 1) * 100 if len(prices) >= lb else 0
        metrics = common_analyze(prices, returns)
        metrics["momentum_signal"] = round(momentum, 4)
        metrics["trend_strength"] = round(np.mean(returns[-min(lb, len(returns)):]) * 252 * 100, 4)
        return metrics


class MeanReversionStrategy(BaseStrategy):
    """均值回归策略 - 价格偏离均值后倾向于回归"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_mean_reversion", name="均值回归策略", category="股票策略",
            description="基于均值回归理论，当价格偏离历史均值过多时，预期价格将回归均值。买入被低估的资产，卖出被高估的资产。",
            advantages=["在震荡市中表现良好", "提供相对明确的入场和出场信号", "风险可控"],
            disadvantages=["在强趋势市场中可能持续亏损", "均值可能发生结构性偏移", "需要较长的历史数据"],
            risks=["趋势延续风险", "均值漂移风险", "参数敏感性风险"],
            parameters={"lookback_window": {"value": 20, "description": "均值计算窗口"}, "entry_zscore": {"value": -2.0, "description": "入场Z-score阈值"}, "exit_zscore": {"value": 0.0, "description": "出场Z-score阈值"}, "stop_loss": {"value": 0.05, "description": "止损比例"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        w = kwargs.get("lookback_window", 20)
        mean_v = np.mean(prices[-w:])
        std_v = np.std(prices[-w:])
        z = (prices[-1] - mean_v) / std_v if std_v > 0 else 0
        metrics = common_analyze(prices, returns)
        metrics["current_zscore"] = round(z, 4)
        metrics["mean_price"] = round(mean_v, 4)
        metrics["deviation_pct"] = round((prices[-1] - mean_v) / mean_v * 100, 4)
        return metrics


class ValueInvestingStrategy(BaseStrategy):
    """价值投资策略 - 寻找被市场低估的优质股票"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_value", name="价值投资策略", category="股票策略",
            description="基于基本面分析，寻找市场价格低于内在价值的股票。通过市盈率、市净率、股息率等指标筛选被低估的优质公司进行长期投资。",
            advantages=["长期回报稳定", "安全边际提供下行保护", "适合长期投资者"],
            disadvantages=["需要等待价值回归，时间成本高", "可能错过成长型股票的机会", "基本面分析需要专业知识"],
            risks=["价值陷阱风险", "估值方法偏差风险", "行业周期性风险"],
            parameters={"pe_max": {"value": 15, "description": "最大市盈率"}, "pb_max": {"value": 2.0, "description": "最大市净率"}, "dividend_min": {"value": 0.02, "description": "最低股息率"}, "roe_min": {"value": 0.15, "description": "最低净资产收益率"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["estimated_pe"] = round(prices[-1] / max(np.mean(returns[-252:]) * 252, 0.01), 2)
        metrics["price_to_avg"] = round(prices[-1] / np.mean(prices), 4)
        metrics["valuation_signal"] = "低估" if prices[-1] < np.mean(prices) * 0.9 else "合理"
        return metrics


class GrowthInvestingStrategy(BaseStrategy):
    """成长投资策略 - 投资高增长潜力的公司"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_growth", name="成长投资策略", category="股票策略",
            description="专注于投资收入和利润高速增长的公司，即使当前估值较高。关注营收增长率、利润增长率、市场份额扩张等指标。",
            advantages=["能捕捉高增长带来的超额收益", "在牛市中表现突出", "受益于行业趋势红利"],
            disadvantages=["估值偏高，下跌风险大", "增长不及预期时股价波动剧烈", "选股难度大"],
            risks=["增长放缓风险", "估值泡沫风险", "竞争加剧风险"],
            parameters={"revenue_growth_min": {"value": 0.20, "description": "最低营收增长率"}, "profit_growth_min": {"value": 0.25, "description": "最低利润增长率"}, "pe_max": {"value": 50, "description": "最大市盈率"}, "holding_period": {"value": 12, "description": "建议持有期（月）"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        if len(prices) >= 60:
            metrics["short_term_growth"] = round((prices[-1] / prices[-60] - 1) * 100, 4)
            metrics["long_term_growth"] = round((prices[-1] / prices[-252] - 1) * 100, 4) if len(prices) >= 252 else 0
        return metrics


class DividendYieldStrategy(BaseStrategy):
    """股息收益策略 - 投资高股息率股票获取稳定收入"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_dividend", name="股息收益策略", category="股票策略",
            description="选择具有稳定且较高股息率的蓝筹股票进行投资，通过定期分红获取稳定现金流收入。适合追求稳健收益的保守型投资者。",
            advantages=["提供稳定的现金流收入", "波动率相对较低", "在下跌市场中具有防御性"],
            disadvantages=["股息并非保证，公司可能削减分红", "高股息可能是价值陷阱信号", "总回报可能低于成长型策略"],
            risks=["分红削减风险", "利率上升导致股息股吸引力下降", "通胀侵蚀购买力风险"],
            parameters={"dividend_yield_min": {"value": 0.03, "description": "最低股息率"}, "payout_ratio_max": {"value": 0.70, "description": "最大派息比率"}, "dividend_growth_min": {"value": 0.05, "description": "最低股息增长率"}, "sector_diversification": {"value": True, "description": "是否进行行业分散"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["estimated_dividend_yield"] = round(max(np.mean(returns) * 252 * 100 * 0.3, 2.0), 4)
        metrics["income_stability"] = round(1.0 / max(np.std(returns) * np.sqrt(252), 0.01), 4)
        return metrics


class LowVolatilityStrategy(BaseStrategy):
    """低波动率策略 - 选择价格波动较小的股票"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_low_volatility", name="低波动率策略", category="股票策略",
            description="选择历史价格波动率较低的股票构建投资组合。研究表明低波动率股票长期回报并不逊色于高波动率股票，且风险调整后收益更优。",
            advantages=["下行风险较小，回撤可控", "风险调整后收益通常优于市场", "适合风险厌恶型投资者"],
            disadvantages=["可能错过牛市中的大涨机会", "低波动可能反映市场关注度低", "极端行情下仍可能大幅下跌"],
            risks=["波动率突然放大风险", "流动性不足风险", "低波动异象消失风险"],
            parameters={"volatility_window": {"value": 60, "description": "波动率计算窗口"}, "volatility_max": {"value": 0.20, "description": "最大年化波动率"}, "min_market_cap": {"value": 1e9, "description": "最小市值"}, "rebalance_freq": {"value": "monthly", "description": "调仓频率"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        vol = np.std(returns) * np.sqrt(252)
        metrics["volatility_level"] = "低" if vol < 0.15 else ("中" if vol < 0.25 else "高")
        metrics["risk_score"] = round(vol * 10, 2)
        return metrics


class QualityFactorStrategy(BaseStrategy):
    """质量因子策略 - 选择财务质量高的公司"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_quality", name="质量因子策略", category="股票策略",
            description="通过盈利能力、财务稳健性、经营效率等质量指标筛选优质公司。高质量公司通常具有持续竞争优势，能为股东创造稳定回报。",
            advantages=["长期表现稳健", "抗风险能力强", "适合作为核心持仓"],
            disadvantages=["优质公司估值通常较高", "质量指标可能滞后", "需要综合多个财务指标"],
            risks=["财务造假风险", "质量恶化风险", "估值过高风险"],
            parameters={"roe_min": {"value": 0.15, "description": "最低ROE"}, "debt_ratio_max": {"value": 0.50, "description": "最大负债率"}, "profit_margin_min": {"value": 0.10, "description": "最低利润率"}, "earnings_stability": {"value": 0.80, "description": "盈利稳定性评分"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["quality_score"] = round(min(max(metrics["sharpe_ratio"] / 2, 0), 10), 2)
        return metrics


class SizeFactorStrategy(BaseStrategy):
    """规模因子策略 - 基于公司市值大小的投资策略"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_size", name="规模因子策略", category="股票策略",
            description="基于公司市值规模进行投资选择。小市值公司通常具有更高的成长潜力但风险也更大，大市值公司则更稳定但增长空间有限。",
            advantages=["因子效应明确，学术支持充分", "可灵活调整大盘/小盘比例", "与其他因子结合效果好"],
            disadvantages=["小盘股流动性差", "规模效应在不同市场周期表现不一", "需要定期再平衡"],
            risks=["流动性风险", "小盘股退市风险", "风格切换风险"],
            parameters={"market_cap_range": {"value": "small", "description": "目标市值范围"}, "weight_method": {"value": "equal", "description": "加权方式"}, "rebalance_freq": {"value": "quarterly", "description": "调仓频率"}, "max_position": {"value": 0.05, "description": "最大持仓比例"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["size_signal"] = "小盘优势" if np.mean(returns) > 0 else "大盘防御"
        return metrics


class MultiFactorStrategy(BaseStrategy):
    """多因子模型策略 - 综合多个因子进行选股"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_multi_factor", name="多因子模型策略", category="股票策略",
            description="综合价值、成长、质量、动量、规模等多个因子，通过加权评分模型筛选最优投资标的。多因子模型能有效降低单一因子的波动性。",
            advantages=["分散单一因子风险", "适应不同市场环境", "长期表现稳健"],
            disadvantages=["因子间可能存在共线性", "模型复杂度高", "需要大量数据和计算资源"],
            risks=["因子衰减风险", "模型过拟合风险", "因子相关性变化风险"],
            parameters={"factors": {"value": ["value", "momentum", "quality", "size"], "description": "使用的因子列表"}, "value_weight": {"value": 0.25, "description": "价值因子权重"}, "momentum_weight": {"value": 0.25, "description": "动量因子权重"}, "quality_weight": {"value": 0.25, "description": "质量因子权重"}, "size_weight": {"value": 0.25, "description": "规模因子权重"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        mom = np.mean(returns[-20:]) if len(returns) >= 20 else 0
        val = 1.0 / (prices[-1] / np.mean(prices)) if np.mean(prices) > 0 else 1
        qual = metrics["sharpe_ratio"] / 2
        metrics["composite_score"] = round(mom * 0.25 + val * 0.25 + qual * 0.25 + 0.25, 4)
        return metrics


class SectorRotationStrategy(BaseStrategy):
    """行业轮动策略 - 根据经济周期在不同行业间切换"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_sector_rotation", name="行业轮动策略", category="股票策略",
            description="基于经济周期理论，在不同经济阶段配置表现最优的行业板块。例如复苏期配置周期性行业，衰退期配置防御性行业。",
            advantages=["能捕捉经济周期带来的行业机会", "分散单一行业风险", "灵活适应市场变化"],
            disadvantages=["经济周期判断困难", "轮动时点难以精确把握", "交易成本较高"],
            risks=["周期判断错误风险", "政策变化风险", "黑天鹅事件风险"],
            parameters={"economic_indicator": {"value": "PMI", "description": "经济领先指标"}, "rotation_freq": {"value": "monthly", "description": "轮动频率"}, "top_sectors": {"value": 3, "description": "配置行业数量"}, "momentum_lookback": {"value": 30, "description": "行业动量回溯期"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        sma = np.mean(prices[-20:]) if len(prices) >= 20 else prices[-1]
        lma = np.mean(prices[-60:]) if len(prices) >= 60 else prices[-1]
        metrics["sector_momentum"] = round((sma / lma - 1) * 100, 4)
        metrics["rotation_signal"] = "超配" if sma > lma else "低配"
        return metrics


class PairsTradingStrategy(BaseStrategy):
    """配对交易策略 - 利用两个相关资产价差回归进行套利"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_pairs_trading", name="配对交易策略", category="股票策略",
            description="选择两个历史价格高度相关的股票，当价差偏离统计均值时，做多被低估的股票、做空被高估的股票，待价差回归均值时平仓获利。",
            advantages=["市场中性，不受大盘方向影响", "风险相对可控", "在震荡市中表现良好"],
            disadvantages=["配对关系可能失效", "价差可能持续扩大导致亏损", "需要精确的统计建模"],
            risks=["配对关系破裂风险", "价差持续扩大风险", "做空成本和限制风险"],
            parameters={"cointegration_threshold": {"value": 0.05, "description": "协整检验p值阈值"}, "entry_zscore": {"value": 2.0, "description": "入场Z-score"}, "exit_zscore": {"value": 0.0, "description": "出场Z-score"}, "stop_zscore": {"value": 4.0, "description": "止损Z-score"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        spread = np.diff(prices)
        sm, ss = np.mean(spread), np.std(spread)
        metrics["spread_zscore"] = round((spread[-1] - sm) / ss, 4) if ss > 0 else 0
        metrics["pair_correlation"] = round(np.corrcoef(prices[:-1], prices[1:])[0, 1], 4)
        return metrics


class StatisticalArbitrageStrategy(BaseStrategy):
    """统计套利策略 - 利用统计模型发现定价偏差"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_stat_arb", name="统计套利策略", category="股票策略",
            description="运用统计学和计量经济学方法，在大量股票中寻找短暂的定价偏差机会。通过构建多空组合对冲市场风险，从定价错误的均值回归中获利。",
            advantages=["市场中性，系统性风险低", "交易机会频繁", "可高度自动化"],
            disadvantages=["模型复杂，开发成本高", "需要大量历史数据", "策略容量有限"],
            risks=["模型失效风险", "执行风险", "技术故障风险"],
            parameters={"model_type": {"value": "PCA", "description": "统计模型类型"}, "num_factors": {"value": 5, "description": "因子数量"}, "rebalance_freq": {"value": "daily", "description": "再平衡频率"}, "max_positions": {"value": 50, "description": "最大持仓数"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["arb_signal"] = round(np.mean(returns[-5:]) - np.mean(returns[-20:]), 6) if len(returns) >= 20 else 0
        metrics["signal_strength"] = "强" if abs(metrics["arb_signal"]) > 0.001 else "弱"
        return metrics


class EventDrivenStrategy(BaseStrategy):
    """事件驱动策略 - 利用公司事件带来的定价机会"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_event_driven", name="事件驱动策略", category="股票策略",
            description="利用并购、重组、分拆、管理层变更、财报发布等公司特定事件造成的市场定价偏差进行投资。事件驱动策略通常具有明确的催化剂和时间框架。",
            advantages=["收益来源明确，与市场相关性低", "有具体事件作为催化剂", "风险收益比通常较好"],
            disadvantages=["事件结果不确定", "需要快速反应和执行", "信息获取和处理要求高"],
            risks=["事件取消或推迟风险", "市场提前消化风险", "法律和监管风险"],
            parameters={"event_types": {"value": ["earnings", "M&A", "spinoff", "restructuring"], "description": "关注的事件类型"}, "holding_period": {"value": 30, "description": "持仓周期（天）"}, "position_size": {"value": 0.03, "description": "单事件仓位"}, "stop_loss": {"value": 0.10, "description": "止损比例"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        rv = np.std(returns[-5:]) if len(returns) >= 5 else 0
        nv = np.std(returns[-60:]) if len(returns) >= 60 else rv
        metrics["event_signal"] = round(rv / max(nv, 1e-8), 4)
        metrics["abnormal_return"] = round((np.mean(returns[-3:]) - np.mean(returns)) * 100, 4) if len(returns) >= 3 else 0
        return metrics


class ETFArbitrageStrategy(BaseStrategy):
    """ETF套利策略 - 利用ETF与成分资产之间的定价偏差"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_etf_arb", name="ETF套利策略", category="股票策略",
            description="当ETF市场价格与其净值(NAV)出现偏差时，通过申购/赎回机制或直接买卖ETF和成分股进行套利。偏差通常短暂且微小，需要高频交易能力。",
            advantages=["风险较低，套利空间明确", "市场中性策略", "可程序化自动执行"],
            disadvantages=["需要高频交易基础设施", "套利空间通常很小", "受交易成本和流动性影响大"],
            risks=["执行延迟风险", "交易成本侵蚀利润风险", "流动性不足风险"],
            parameters={"premium_threshold": {"value": 0.005, "description": "溢价/折价阈值"}, "execution_speed": {"value": "millisecond", "description": "执行速度要求"}, "max_slippage": {"value": 0.001, "description": "最大滑点"}, "min_profit": {"value": 0.002, "description": "最小利润要求"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        nav = np.mean(prices[-5:]) if len(prices) >= 5 else prices[-1]
        premium = (prices[-1] - nav) / nav * 100
        metrics["nav_estimate"] = round(nav, 4)
        metrics["premium_pct"] = round(premium, 4)
        metrics["arb_opportunity"] = "存在" if abs(premium) > 0.5 else "不存在"
        return metrics


class QuantTimingStrategy(BaseStrategy):
    """量化择时策略 - 使用量化模型判断市场买卖时机"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_quant_timing", name="量化择时策略", category="股票策略",
            description="综合运用技术指标、市场情绪、资金流向、宏观因子等多维度信号，构建量化择时模型，判断市场的买入和卖出时机。",
            advantages=["系统化决策，避免情绪干扰", "可回测验证", "多信号融合提高准确率"],
            disadvantages=["市场极端情况下可能失效", "信号滞后性", "模型维护成本高"],
            risks=["模型失效风险", "信号延迟风险", "黑天鹅事件风险"],
            parameters={"indicators": {"value": ["MA", "MACD", "RSI", "BOLL"], "description": "使用的技术指标"}, "signal_threshold": {"value": 0.6, "description": "综合信号阈值"}, "lookback": {"value": 60, "description": "指标计算回溯期"}, "max_drawdown_limit": {"value": 0.15, "description": "最大回撤限制"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        ma_s = np.mean(prices[-10:]) if len(prices) >= 10 else prices[-1]
        ma_l = np.mean(prices[-30:]) if len(prices) >= 30 else prices[-1]
        metrics["timing_signal"] = "买入" if ma_s > ma_l else "卖出"
        metrics["signal_strength"] = round(abs(ma_s / ma_l - 1) * 100, 4)
        return metrics


class TechnicalAnalysisStrategy(BaseStrategy):
    """技术分析策略 - 基于价格和成交量图表模式"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_technical", name="技术分析策略", category="股票策略",
            description="运用K线形态、趋势线、支撑阻力位、技术指标（MACD、RSI、KDJ、布林带等）分析价格走势，识别买卖信号。",
            advantages=["直观易懂，图表分析方便", "适用于各种时间周期", "提供明确的入场出场信号"],
            disadvantages=["主观性强", "在有效市场中可能失效", "需要大量实践经验"],
            risks=["假突破风险", "指标滞后风险", "过度交易风险"],
            parameters={"primary_indicator": {"value": "MACD", "description": "主指标"}, "secondary_indicator": {"value": "VOL", "description": "辅助指标"}, "timeframe": {"value": "daily", "description": "分析周期"}, "confirmation_required": {"value": True, "description": "是否需要多指标确认"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        ma5 = np.mean(prices[-5:]) if len(prices) >= 5 else prices[-1]
        ma20 = np.mean(prices[-20:]) if len(prices) >= 20 else prices[-1]
        metrics["ma5"] = round(ma5, 4)
        metrics["ma20"] = round(ma20, 4)
        metrics["trend"] = "上升" if ma5 > ma20 else "下降"
        gains = returns[returns > 0]
        losses = -returns[returns < 0]
        ag = np.mean(gains) if len(gains) > 0 else 0
        al = np.mean(losses) if len(losses) > 0 else 1e-8
        metrics["rsi"] = round(100 - 100 / (1 + ag / al), 2)
        metrics["rsi_signal"] = "超买" if metrics["rsi"] > 70 else ("超卖" if metrics["rsi"] < 30 else "中性")
        return metrics


class FundamentalAnalysisStrategy(BaseStrategy):
    """基本面分析策略 - 基于公司财务和经营状况"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_fundamental", name="基本面分析策略", category="股票策略",
            description="深入分析公司的财务报表、行业地位、竞争优势、管理层能力等基本面因素，评估公司内在价值，寻找被市场低估的投资机会。",
            advantages=["投资逻辑扎实，长期有效", "能发现市场定价错误", "适合长期价值投资"],
            disadvantages=["分析工作量大", "财务数据有滞后性", "对短期市场波动无效"],
            risks=["财务数据造假风险", "行业基本面恶化风险", "估值模型偏差风险"],
            parameters={"analysis_framework": {"value": "DCF", "description": "估值框架"}, "discount_rate": {"value": 0.10, "description": "折现率"}, "growth_assumption": {"value": 0.08, "description": "增长率假设"}, "margin_of_safety": {"value": 0.30, "description": "安全边际"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        avg_p = np.mean(prices)
        metrics["intrinsic_value_estimate"] = round(avg_p * 1.1, 4)
        metrics["margin_of_safety"] = round((avg_p - prices[-1]) / avg_p * 100, 4)
        metrics["valuation_status"] = "低估" if prices[-1] < avg_p * 0.9 else ("合理" if prices[-1] < avg_p * 1.1 else "高估")
        return metrics


class MacroHedgeStrategy(BaseStrategy):
    """宏观对冲策略 - 基于宏观经济判断进行对冲配置"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_macro_hedge", name="宏观对冲策略", category="股票策略",
            description="基于对宏观经济形势的判断，调整股票仓位并配合衍生品对冲，在不同宏观环境下实现资产保值增值。",
            advantages=["能有效应对宏观风险", "资产配置灵活", "可对冲系统性风险"],
            disadvantages=["宏观判断难度大", "对冲成本可能较高", "需要全球视野"],
            risks=["宏观判断失误风险", "对冲工具流动性风险", "政策突变风险"],
            parameters={"gdp_weight": {"value": 0.30, "description": "GDP因子权重"}, "inflation_weight": {"value": 0.25, "description": "通胀因子权重"}, "rate_weight": {"value": 0.25, "description": "利率因子权重"}, "hedge_ratio": {"value": 0.50, "description": "对冲比例"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["macro_score"] = round(np.mean(returns[-60:]) * 252 * 100, 4) if len(returns) >= 60 else 0
        metrics["hedge_recommendation"] = "增加对冲" if metrics["macro_score"] < 0 else "减少对冲"
        return metrics


class AlphaHedgeStrategy(BaseStrategy):
    """Alpha对冲策略 - 通过多空组合获取绝对收益"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_alpha_hedge", name="Alpha对冲策略", category="股票策略",
            description="通过选股模型构建多头组合和空头组合，对冲市场系统性风险，获取选股带来的Alpha收益。属于市场中性策略。",
            advantages=["市场中性，不受大盘涨跌影响", "追求绝对收益", "回撤通常较小"],
            disadvantages=["选股模型要求高", "做空成本和限制", "Alpha可能衰减"],
            risks=["选股模型失效风险", "做空风险", "行业集中度风险"],
            parameters={"long_count": {"value": 20, "description": "多头股票数量"}, "short_count": {"value": 20, "description": "空头股票数量"}, "rebalance_freq": {"value": "weekly", "description": "调仓频率"}, "alpha_model": {"value": "factor", "description": "Alpha模型类型"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        mr = np.mean(returns) * 252 * 100
        metrics["estimated_alpha"] = round(max(mr - 8.0, -20.0), 4)
        metrics["alpha_stability"] = round(metrics["sharpe_ratio"] / 3, 4)
        return metrics


class SmartBetaStrategy(BaseStrategy):
    """Smart Beta策略 - 系统性因子暴露的被动增强策略"""
    def __init__(self):
        super().__init__(
            strategy_id="stock_smart_beta", name="Smart Beta策略", category="股票策略",
            description="介于主动投资和被动投资之间，通过规则化的方式对特定因子进行系统性暴露，以较低的成本获取超越传统市值加权指数的收益。",
            advantages=["透明度高，规则明确", "管理费用低于主动基金", "因子暴露可控"],
            disadvantages=["因子表现有周期性", "可能存在因子拥挤", "再平衡成本"],
            risks=["因子失效风险", "因子拥挤风险", "跟踪误差风险"],
            parameters={"target_factor": {"value": "value", "description": "目标因子"}, "weighting_method": {"value": "fundamental", "description": "加权方式"}, "rebalance_freq": {"value": "semi-annual", "description": "再平衡频率"}, "tracking_error_budget": {"value": 0.03, "description": "跟踪误差预算"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["factor_exposure"] = round(np.corrcoef(returns, np.arange(len(returns)) / max(len(returns), 1))[0, 1], 4)
        metrics["enhancement_ratio"] = round(metrics["sharpe_ratio"] / max(abs(metrics["beta"]), 0.1), 4)
        return metrics


# ============================================================
# 债券策略（15种）
# ============================================================

class DurationManagementStrategy(BaseStrategy):
    """久期管理策略 - 通过调整组合久期管理利率风险"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_duration", name="久期管理策略", category="债券策略",
            description="通过调整债券投资组合的久期来管理利率风险。预期利率下降时增加久期以获取资本利得，预期利率上升时缩短久期以减少损失。",
            advantages=["能有效管理利率风险", "操作灵活", "适合各种利率环境"],
            disadvantages=["利率预测困难", "久期调整有交易成本", "收益率曲线非平行移动时效果有限"],
            risks=["利率预测错误风险", "收益率曲线风险", "流动性风险"],
            parameters={"target_duration": {"value": 5.0, "description": "目标久期（年）"}, "duration_range": {"value": [3.0, 7.0], "description": "久期允许范围"}, "convexity_target": {"value": 0.0, "description": "目标凸性"}, "rebalance_trigger": {"value": 0.5, "description": "再平衡触发偏差"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["estimated_duration"] = round(len(prices) / 252, 2)
        metrics["rate_sensitivity"] = round(-np.mean(returns) * 100, 4)
        metrics["duration_recommendation"] = "增加久期" if np.mean(returns[-20:]) < 0 else "缩短久期"
        return metrics


class YieldCurveTradingStrategy(BaseStrategy):
    """收益率曲线交易策略 - 基于收益率曲线形状变化"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_yield_curve", name="收益率曲线交易策略", category="债券策略",
            description="基于对收益率曲线形状变化的判断进行交易。包括子弹式、阶梯式、杠铃式等策略，以及骑乘收益率曲线、曲线趋陡/趋平等方向性交易。",
            advantages=["收益来源多样化", "可表达多种市场观点", "风险收益特征可控"],
            disadvantages=["曲线变动预测困难", "需要精确的期限结构建模", "极端市场下可能失效"],
            risks=["曲线形状突变风险", "流动性风险", "模型风险"],
            parameters={"curve_strategy": {"value": "steepener", "description": "曲线策略类型"}, "short_end": {"value": 2, "description": "短端期限（年）"}, "long_end": {"value": 10, "description": "长端期限（年）"}, "notional_ratio": {"value": 1.0, "description": "名义金额比"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        if len(returns) >= 20:
            sr = np.mean(returns[-5:]) * 252 * 100
            lr = np.mean(returns[-20:]) * 252 * 100
            metrics["curve_slope"] = round(lr - sr, 4)
            metrics["curve_signal"] = "趋陡" if metrics["curve_slope"] > 0 else "趋平"
        return metrics


class CreditSpreadStrategy(BaseStrategy):
    """信用利差策略 - 基于信用利差变化的交易"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_credit_spread", name="信用利差策略", category="债券策略",
            description="通过分析信用利差的变化趋势，投资于信用债获取超额收益。当预期信用利差收窄时买入信用债，预期扩大时减少信用债配置或做空。",
            advantages=["收益高于国债", "信用分析有明确框架", "可分散化降低违约风险"],
            disadvantages=["信用事件可能导致大幅亏损", "流动性通常低于国债", "需要深入的信用分析能力"],
            risks=["违约风险", "信用评级下调风险", "流动性风险"],
            parameters={"min_credit_rating": {"value": "BBB", "description": "最低信用评级"}, "spread_min": {"value": 0.01, "description": "最低利差要求"}, "duration_target": {"value": 5.0, "description": "目标久期"}, "diversification_min": {"value": 20, "description": "最低分散化数量"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["estimated_spread"] = round(max(np.std(returns) * np.sqrt(252) * 100 - 3.0, 0.5), 4)
        metrics["credit_quality_signal"] = "改善" if np.mean(returns[-20:]) > 0 else "恶化"
        return metrics


class ConvertibleArbitrageStrategy(BaseStrategy):
    """可转债套利策略 - 利用可转债定价偏差套利"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_convertible_arb", name="可转债套利策略", category="债券策略",
            description="买入低估的可转换债券，同时做空对应股票进行对冲。利用可转债的债券底价值和转股期权之间的定价偏差获利。",
            advantages=["下行保护（债券底价值）", "上行参与（转股期权）", "市场中性特征"],
            disadvantages=["定价模型复杂", "对冲比率需要动态调整", "可转债流动性可能不足"],
            risks=["股价大幅下跌风险", "信用风险", "赎回风险"],
            parameters={"conversion_premium_max": {"value": 0.20, "description": "最大转股溢价率"}, "delta_hedge_ratio": {"value": 0.70, "description": "Delta对冲比率"}, "credit_rating_min": {"value": "BBB-", "description": "最低信用评级"}, "rebalance_freq": {"value": "weekly", "description": "对冲调整频率"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["conversion_premium"] = round(max(0.1, np.std(returns) * 10), 4)
        metrics["arb_spread"] = round(np.mean(returns) * 100, 4)
        return metrics


class BondIndexStrategy(BaseStrategy):
    """债券指数策略 - 跟踪债券市场指数"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_index", name="债券指数策略", category="债券策略",
            description="通过复制或抽样方式跟踪特定债券市场指数，获取市场平均收益。适合作为债券投资的基准和核心持仓。",
            advantages=["管理费用低", "分散化程度高", "收益透明可预期"],
            disadvantages=["无法超越指数收益", "可能存在跟踪误差", "再平衡有交易成本"],
            risks=["利率风险", "信用风险", "流动性风险"],
            parameters={"target_index": {"value": "中债综合指数", "description": "目标指数"}, "tracking_method": {"value": "sampling", "description": "跟踪方式"}, "max_tracking_error": {"value": 0.005, "description": "最大跟踪误差"}, "rebalance_freq": {"value": "monthly", "description": "再平衡频率"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["tracking_error"] = round(np.std(returns) * np.sqrt(252) * 100, 4)
        metrics["index_correlation"] = 0.99
        return metrics


class HighYieldBondStrategy(BaseStrategy):
    """高收益债策略 - 投资高收益率债券"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_high_yield", name="高收益债策略", category="债券策略",
            description="投资于信用评级较低但收益率较高的债券。通过承担较高的信用风险获取较高的利息收入，适合风险承受能力较强的投资者。",
            advantages=["收益率显著高于投资级债券", "在经济复苏期表现优异", "违约率通常可控"],
            disadvantages=["违约风险较高", "流动性较差", "对经济周期敏感"],
            risks=["违约风险", "流动性风险", "利率风险"],
            parameters={"min_yield": {"value": 0.06, "description": "最低收益率"}, "max_rating": {"value": "BB+", "description": "最高评级"}, "duration_limit": {"value": 5.0, "description": "久期上限"}, "diversification": {"value": 30, "description": "最低持仓数量"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["yield_estimate"] = round(max(np.mean(returns) * 252 * 100, 5.0), 4)
        metrics["default_risk_score"] = round(min(np.std(returns) * 100, 10.0), 4)
        return metrics


class EmergingMarketBondStrategy(BaseStrategy):
    """新兴市场债策略 - 投资新兴市场国家债券"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_emerging_market", name="新兴市场债策略", category="债券策略",
            description="投资于新兴市场国家发行的政府债券或企业债券，获取较高的收益率。同时承担汇率风险、政治风险和信用风险。",
            advantages=["收益率高于发达国家债券", "分散化投资组合", "受益于新兴市场经济增长"],
            disadvantages=["汇率风险大", "政治和制度风险高", "流动性可能不足"],
            risks=["汇率风险", "政治风险", "信用风险"],
            parameters={"currency_type": {"value": "hard_currency", "description": "货币类型"}, "region_allocation": {"value": "diversified", "description": "区域配置"}, "duration_target": {"value": 7.0, "description": "目标久期"}, "hedge_ratio": {"value": 0.50, "description": "汇率对冲比例"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["currency_risk"] = round(np.std(returns) * np.sqrt(252) * 100, 4)
        metrics["em_premium"] = round(max(np.mean(returns) * 252 * 100 - 3.0, 1.0), 4)
        return metrics


class InflationProtectedStrategy(BaseStrategy):
    """通胀保值策略 - 投资通胀挂钩债券"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_inflation_protected", name="通胀保值策略", category="债券策略",
            description="投资于通胀保值债券（如TIPS），本金随通胀指数调整，有效对冲通胀风险。适合担心通胀侵蚀购买力的投资者。",
            advantages=["有效对冲通胀风险", "实际收益稳定", "在通胀上升期表现优异"],
            disadvantages=["在通缩或低通胀环境中收益较低", "实际收益率通常低于名义债券", "流动性可能较差"],
            risks=["通缩风险", "利率风险", "流动性风险"],
            parameters={"real_yield_min": {"value": -0.01, "description": "最低实际收益率"}, "breakeven_inflation": {"value": 0.025, "description": "盈亏平衡通胀率"}, "duration_target": {"value": 5.0, "description": "目标久期"}, "allocation_pct": {"value": 0.20, "description": "组合配置比例"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["real_yield_estimate"] = round(np.mean(returns) * 252 * 100 - 2.5, 4)
        metrics["inflation_protection"] = round(1.0 - abs(np.mean(returns[-20:]) - np.mean(returns)) * 100, 4)
        return metrics


class FloatingRateStrategy(BaseStrategy):
    """浮动利率策略 - 投资利率浮动的债券"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_floating_rate", name="浮动利率策略", category="债券策略",
            description="投资于票面利率随市场利率浮动的债券，在利率上升环境中能有效保护本金价值。适合预期利率上升时的防御性配置。",
            advantages=["利率上升时票息增加", "价格波动较小", "流动性通常较好"],
            disadvantages=["利率下降时收益不如固定利率债", "利差可能收窄", "基准利率调整有滞后"],
            risks=["信用风险", "利率上限风险", "基准利率风险"],
            parameters={"spread_min": {"value": 0.01, "description": "最低利差"}, "reset_freq": {"value": "quarterly", "description": "利率重置频率"}, "credit_quality": {"value": "A", "description": "信用质量要求"}, "duration_target": {"value": 0.5, "description": "目标久期"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["rate_sensitivity"] = round(np.std(returns) * np.sqrt(252) * 100, 4)
        metrics["floating_advantage"] = "利率上升环境有利" if np.mean(returns[-10:]) < np.mean(returns[-30:]) else "利率下降环境不利"
        return metrics


class LadderStrategy(BaseStrategy):
    """阶梯式组合策略 - 均匀分布到期日的债券组合"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_ladder", name="阶梯式组合策略", category="债券策略",
            description="将投资均匀分配到不同到期日的债券上，形成阶梯式到期结构。到期债券再投资到最长期限，实现收益的滚动增长和流动性管理。",
            advantages=["现金流分散均匀", "再投资风险分散", "管理简单"],
            disadvantages=["收益可能不如集中策略", "需要定期再投资", "在利率急变时调整慢"],
            risks=["再投资风险", "利率风险", "信用风险"],
            parameters={"num_rungs": {"value": 10, "description": "阶梯数量"}, "min_maturity": {"value": 1, "description": "最短到期（年）"}, "max_maturity": {"value": 10, "description": "最长到期（年）"}, "reinvestment_policy": {"value": "longest", "description": "再投资策略"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["avg_maturity"] = round(len(prices) / 252, 2)
        metrics["cash_flow_distribution"] = "均匀"
        return metrics


class BulletStrategy(BaseStrategy):
    """子弹式组合策略 - 集中投资于同一到期日的债券"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_bullet", name="子弹式组合策略", category="债券策略",
            description="将大部分资金集中投资于某一特定到期日的债券。适合有明确资金需求时间点的投资者。",
            advantages=["到期日与资金需求匹配", "利率锁定明确", "管理简单"],
            disadvantages=["缺乏灵活性", "再投资风险集中", "收益率曲线位置判断风险"],
            risks=["利率风险", "信用风险", "再投资风险"],
            parameters={"target_maturity": {"value": 5, "description": "目标到期日（年）"}, "concentration": {"value": 0.80, "description": "集中度"}, "credit_quality": {"value": "AA", "description": "信用质量"}, "duration_tolerance": {"value": 0.5, "description": "久期容忍偏差"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["duration_match"] = round(len(prices) / 252, 2)
        metrics["concentration_score"] = 0.8
        return metrics


class BarbellStrategy(BaseStrategy):
    """杠铃式组合策略 - 集中投资于短期和长期债券"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_barbell", name="杠铃式组合策略", category="债券策略",
            description="将资金分配到短期和长期两个极端到期日的债券上，中间期限不配置。结合了短期的流动性和长期的收益率。",
            advantages=["兼顾流动性和收益", "曲线变动时调整灵活", "再投资机会多"],
            disadvantages=["中间期限收益缺失", "管理复杂度高", "需要精确的期限分配"],
            risks=["收益率曲线风险", "再投资风险", "信用风险"],
            parameters={"short_allocation": {"value": 0.50, "description": "短期配置比例"}, "short_maturity": {"value": 1, "description": "短期到期（年）"}, "long_maturity": {"value": 20, "description": "长期到期（年）"}, "rebalance_freq": {"value": "monthly", "description": "再平衡频率"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["short_long_ratio"] = 0.5
        metrics["convexity_benefit"] = round(np.std(returns) * np.sqrt(252) * 100 * 0.5, 4)
        return metrics


class BondSwapStrategy(BaseStrategy):
    """债券互换策略 - 交换债券以改善组合"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_swap", name="债券互换策略", category="债券策略",
            description="在组合中卖出一种债券并买入另一种债券，以改善组合的收益率、久期、信用质量等特征。包括替代互换、收益率pickup互换、税收互换等。",
            advantages=["灵活调整组合特征", "可提升组合收益", "改善风险特征"],
            disadvantages=["交易成本影响收益", "需要精确的估值分析", "市场流动性限制"],
            risks=["交易执行风险", "估值偏差风险", "流动性风险"],
            parameters={"swap_type": {"value": "substitution", "description": "互换类型"}, "yield_improvement_min": {"value": 0.001, "description": "最小收益改善"}, "max_transaction_cost": {"value": 0.002, "description": "最大交易成本"}, "credit_match": {"value": True, "description": "是否要求信用匹配"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["swap_opportunity"] = round(abs(np.mean(returns[-5:]) - np.mean(returns[-20:])) * 100, 4) if len(returns) >= 20 else 0
        metrics["recommendation"] = "建议互换" if metrics["swap_opportunity"] > 0.1 else "持有"
        return metrics


class TotalReturnStrategy(BaseStrategy):
    """总回报策略 - 追求债券组合总回报最大化"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_total_return", name="总回报策略", category="债券策略",
            description="综合考虑利息收入、资本利得和再投资收益，追求债券投资组合的总回报最大化。通过积极的久期管理、信用选择和收益率曲线定位实现超额收益。",
            advantages=["全面考虑收益来源", "灵活的投资策略", "可适应不同市场环境"],
            disadvantages=["需要主动管理", "交易频繁成本高", "对管理人要求高"],
            risks=["利率风险", "信用风险", "流动性风险"],
            parameters={"return_target": {"value": 0.05, "description": "年化回报目标"}, "risk_budget": {"value": 0.03, "description": "风险预算"}, "active_share": {"value": 0.30, "description": "主动份额"}, "benchmark_deviation": {"value": 0.02, "description": "基准偏差"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["income_component"] = round(np.mean(returns) * 252 * 100 * 0.6, 4)
        metrics["price_component"] = round(np.mean(returns) * 252 * 100 * 0.4, 4)
        return metrics


class DefaultPredictionStrategy(BaseStrategy):
    """违约预测策略 - 预测和规避债券违约风险"""
    def __init__(self):
        super().__init__(
            strategy_id="bond_default_prediction", name="违约预测策略", category="债券策略",
            description="运用统计模型和机器学习方法预测债券发行人的违约概率，规避高违约风险的债券，或在风险定价不合理时进行做空。",
            advantages=["能有效识别违约风险", "量化评估信用质量", "可系统化执行"],
            disadvantages=["模型预测并非100%准确", "需要大量历史违约数据", "新兴行业数据不足"],
            risks=["模型误判风险", "黑天鹅违约事件", "数据质量风险"],
            parameters={"model_type": {"value": "logistic", "description": "预测模型"}, "pd_threshold": {"value": 0.05, "description": "违约概率阈值"}, "features": {"value": ["leverage", "coverage", "profitability", "size", "liquidity"], "description": "预测特征"}, "update_freq": {"value": "monthly", "description": "模型更新频率"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        vol = np.std(returns) * np.sqrt(252)
        metrics["estimated_pd"] = round(min(max(vol * 0.1, 0.001), 0.5), 4)
        metrics["credit_score"] = round(max(100 - vol * 200, 10), 2)
        metrics["risk_level"] = "低" if metrics["estimated_pd"] < 0.02 else ("中" if metrics["estimated_pd"] < 0.05 else "高")
        return metrics


# ============================================================
# 期权策略（15种）
# ============================================================

class LongCallStrategy(BaseStrategy):
    """买入看涨期权策略"""
    def __init__(self):
        super().__init__(
            strategy_id="option_long_call", name="买入看涨期权", category="期权策略",
            description="买入看涨期权（Long Call），支付权利金获得在未来以约定价格买入标的资产的权利。当标的资产价格上涨时获利，最大亏损限于权利金。",
            advantages=["杠杆效应，潜在收益无限", "最大亏损有限（权利金）", "不需要大量资金"],
            disadvantages=["时间价值衰减", "需要标的资产大幅上涨才能盈利", "隐含波动率下降不利"],
            risks=["时间衰减风险", "波动率风险", "方向性风险"],
            parameters={"strike_selection": {"value": "ATM", "description": "行权价选择"}, "expiration": {"value": 30, "description": "到期天数"}, "position_size": {"value": 1, "description": "合约数量"}, "max_loss_pct": {"value": 0.02, "description": "最大亏损占组合比例"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["breakeven_pct"] = 3.0
        metrics["max_profit_potential"] = "无限"
        metrics["max_loss"] = "权利金"
        metrics["direction_bias"] = "强烈看多"
        return metrics


class LongPutStrategy(BaseStrategy):
    """买入看跌期权策略"""
    def __init__(self):
        super().__init__(
            strategy_id="option_long_put", name="买入看跌期权", category="期权策略",
            description="买入看跌期权（Long Put），支付权利金获得在未来以约定价格卖出标的资产的权利。当标的资产价格下跌时获利，最大亏损限于权利金。",
            advantages=["杠杆效应", "最大亏损有限", "可用于对冲空头风险"],
            disadvantages=["时间价值衰减", "需要标的资产大幅下跌", "隐含波动率下降不利"],
            risks=["时间衰减风险", "波动率风险", "方向性风险"],
            parameters={"strike_selection": {"value": "ATM", "description": "行权价选择"}, "expiration": {"value": 30, "description": "到期天数"}, "position_size": {"value": 1, "description": "合约数量"}, "hedge_ratio": {"value": 0.0, "description": "对冲比例"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["breakeven_pct"] = -3.0
        metrics["max_profit_potential"] = "行权价-权利金"
        metrics["max_loss"] = "权利金"
        metrics["direction_bias"] = "强烈看空"
        return metrics


class CoveredCallStrategy(BaseStrategy):
    """卖出备兑看涨期权策略"""
    def __init__(self):
        super().__init__(
            strategy_id="option_covered_call", name="卖出备兑看涨", category="期权策略",
            description="持有标的资产的同时卖出看涨期权，收取权利金增强收益。当标的资产价格小幅上涨或持平时可获得最大收益，是保守型增强收益策略。",
            advantages=["收取权利金增强收益", "降低持仓成本", "风险低于单纯持有股票"],
            disadvantages=["限制了上行收益", "仍承担标的资产下跌风险", "需要持有标的资产"],
            risks=["标的资产下跌风险", "行权导致卖出", "机会成本风险"],
            parameters={"strike_otm_pct": {"value": 0.05, "description": "OTM行权价偏移"}, "expiration": {"value": 30, "description": "到期天数"}, "roll_policy": {"value": "auto", "description": "展期策略"}, "income_target": {"value": 0.02, "description": "月度收益目标"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["premium_income"] = round(abs(np.mean(returns)) * 100, 4)
        metrics["upside_cap"] = 5.0
        metrics["direction_bias"] = "中性偏多"
        return metrics


class ProtectivePutStrategy(BaseStrategy):
    """保护性看跌期权策略"""
    def __init__(self):
        super().__init__(
            strategy_id="option_protective_put", name="保护性看跌", category="期权策略",
            description="持有标的资产的同时买入看跌期权，为持仓提供下跌保护。相当于为投资组合购买保险，在市场大幅下跌时限制亏损。",
            advantages=["提供下行保护", "保留上行收益", "心理上更安心"],
            disadvantages=["需要支付权利金成本", "保护有成本，降低总收益", "需要选择合适的行权价和到期日"],
            risks=["保护成本过高", "保护期间可能不足", "行权价选择不当"],
            parameters={"strike_otm_pct": {"value": 0.05, "description": "OTM行权价偏移"}, "expiration": {"value": 60, "description": "到期天数"}, "protection_level": {"value": 0.95, "description": "保护水平"}, "cost_budget": {"value": 0.02, "description": "保护成本预算"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["protection_cost"] = round(np.std(returns) * 100 * 0.5, 4)
        metrics["protection_level"] = 95.0
        metrics["direction_bias"] = "看多但防御"
        return metrics


class BullCallSpreadStrategy(BaseStrategy):
    """牛市看涨价差策略"""
    def __init__(self):
        super().__init__(
            strategy_id="option_bull_call_spread", name="牛市价差", category="期权策略",
            description="买入较低行权价的看涨期权，同时卖出较高行权价的看涨期权。降低权利金成本的同时限制最大收益，适合温和看涨的市场预期。",
            advantages=["权利金成本低于单纯买入看涨", "盈亏比明确", "时间衰减影响较小"],
            disadvantages=["限制了最大收益", "仍需要方向判断正确", "隐含波动率变化影响复杂"],
            risks=["方向判断错误风险", "波动率风险", "流动性风险"],
            parameters={"lower_strike": {"value": "ATM", "description": "买入行权价"}, "upper_strike": {"value": "OTM_1", "description": "卖出行权价"}, "expiration": {"value": 30, "description": "到期天数"}, "spread_width": {"value": 5, "description": "价差宽度"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["max_profit"] = 5.0
        metrics["max_loss"] = 2.0
        metrics["breakeven"] = 1.5
        metrics["direction_bias"] = "温和看多"
        return metrics


class BearPutSpreadStrategy(BaseStrategy):
    """熊市看跌价差策略"""
    def __init__(self):
        super().__init__(
            strategy_id="option_bear_put_spread", name="熊市价差", category="期权策略",
            description="买入较高行权价的看跌期权，同时卖出较低行权价的看跌期权。降低权利金成本的同时限制最大收益，适合温和看跌的市场预期。",
            advantages=["权利金成本低于单纯买入看跌", "盈亏比明确", "风险可控"],
            disadvantages=["限制了最大收益", "仍需要方向判断正确", "需要保证金"],
            risks=["方向判断错误风险", "保证金风险", "流动性风险"],
            parameters={"upper_strike": {"value": "ATM", "description": "买入行权价"}, "lower_strike": {"value": "OTM_1", "description": "卖出行权价"}, "expiration": {"value": 30, "description": "到期天数"}, "spread_width": {"value": 5, "description": "价差宽度"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["max_profit"] = 5.0
        metrics["max_loss"] = 2.0
        metrics["breakeven"] = -1.5
        metrics["direction_bias"] = "温和看空"
        return metrics


class StraddleStrategy(BaseStrategy):
    """跨式组合策略 - 同时买入看涨和看跌期权"""
    def __init__(self):
        super().__init__(
            strategy_id="option_straddle", name="跨式组合", category="期权策略",
            description="同时买入相同标的、相同到期日、相同行权价的看涨和看跌期权。当标的资产大幅波动（无论方向）时获利，适合预期大幅波动但方向不确定的场景。",
            advantages=["不需要判断方向", "潜在收益无限", "波动率上升时获利"],
            disadvantages=["权利金成本高", "需要大幅波动才能盈利", "时间衰减快"],
            risks=["波动率不足风险", "时间衰减风险", "隐含波动率高估风险"],
            parameters={"strike_selection": {"value": "ATM", "description": "行权价选择"}, "expiration": {"value": 30, "description": "到期天数"}, "entry_iv_percentile": {"value": 30, "description": "入场IV百分位"}, "profit_target": {"value": 0.50, "description": "盈利目标"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["breakeven_range"] = round(np.std(returns) * np.sqrt(252) * 100, 4)
        metrics["volatility_assessment"] = "高波动" if metrics["volatility"] > 25 else "低波动"
        metrics["direction_bias"] = "方向中性，波动看多"
        return metrics


class StrangleStrategy(BaseStrategy):
    """宽跨式组合策略 - 买入OTM看涨和看跌期权"""
    def __init__(self):
        super().__init__(
            strategy_id="option_strangle", name="宽跨式", category="期权策略",
            description="同时买入相同标的、相同到期日但不同行权价的OTM看涨和看跌期权。成本低于跨式组合，但需要更大的波动才能盈利。",
            advantages=["成本低于跨式组合", "不需要判断方向", "盈利区间更宽"],
            disadvantages=["需要更大的波动才能盈利", "盈亏比不如跨式", "时间衰减影响大"],
            risks=["波动率不足风险", "时间衰减风险", "流动性风险"],
            parameters={"call_strike_otm": {"value": 0.05, "description": "看涨OTM偏移"}, "put_strike_otm": {"value": 0.05, "description": "看跌OTM偏移"}, "expiration": {"value": 30, "description": "到期天数"}, "cost_budget": {"value": 0.015, "description": "成本预算"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["total_cost_estimate"] = round(np.std(returns) * 100 * 0.8, 4)
        metrics["required_move"] = round(metrics["total_cost_estimate"] * 1.5, 4)
        metrics["direction_bias"] = "方向中性，大幅波动看多"
        return metrics


class IronCondorStrategy(BaseStrategy):
    """铁鹰式组合策略 - 卖出价差组合"""
    def __init__(self):
        super().__init__(
            strategy_id="option_iron_condor", name="铁鹰式", category="期权策略",
            description="同时卖出OTM看涨价差和OTM看跌价差，构建一个收益区间。当标的资产价格在区间内波动时获利，适合预期价格窄幅震荡的市场。",
            advantages=["在震荡市中稳定获利", "风险有限且明确", "不需要判断方向"],
            disadvantages=["盈利有限", "大幅波动时亏损", "需要精确选择行权价"],
            risks=["突破风险", "隐含波动率飙升风险", "保证金风险"],
            parameters={"call_spread_width": {"value": 5, "description": "看涨价差宽度"}, "put_spread_width": {"value": 5, "description": "看跌价差宽度"}, "expiration": {"value": 30, "description": "到期天数"}, "probability_target": {"value": 0.70, "description": "盈利概率目标"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["profit_range"] = round(np.std(returns) * np.sqrt(252) * 100 * 2, 4)
        metrics["max_profit"] = 2.0
        metrics["max_loss"] = 8.0
        metrics["direction_bias"] = "中性，预期窄幅震荡"
        return metrics


class ButterflySpreadStrategy(BaseStrategy):
    """蝶式价差策略 - 三个行权价的价差组合"""
    def __init__(self):
        super().__init__(
            strategy_id="option_butterfly", name="蝶式价差", category="期权策略",
            description="买入一个低行权价和一个高行权价的期权，同时卖出两个中间行权价的期权。在标的资产价格接近中间行权价时获利最大，成本较低。",
            advantages=["成本低", "风险有限", "在目标价位收益高"],
            disadvantages=["盈利区间窄", "需要精确的价格预测", "大幅波动时亏损"],
            risks=["价格偏离目标风险", "流动性风险", "交易成本风险"],
            parameters={"center_strike": {"value": "ATM", "description": "中间行权价"}, "wing_width": {"value": 5, "description": "翅膀宽度"}, "expiration": {"value": 30, "description": "到期天数"}, "call_or_put": {"value": "call", "description": "看涨或看跌蝶式"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["max_profit"] = 10.0
        metrics["max_loss"] = 2.0
        metrics["profit_zone"] = round(np.std(returns) * np.sqrt(252) * 100, 4)
        metrics["direction_bias"] = "中性，目标价位明确"
        return metrics


class CalendarSpreadStrategy(BaseStrategy):
    """日历价差策略 - 不同到期日的价差组合"""
    def __init__(self):
        super().__init__(
            strategy_id="option_calendar_spread", name="日历价差", category="期权策略",
            description="卖出近月期权同时买入远月同行权价期权，利用近月期权时间价值衰减更快的特点获利。适合预期标的资产在短期内价格稳定的场景。",
            advantages=["利用时间衰减差异", "成本相对较低", "波动率变化有利"],
            disadvantages=["近月到期后需要管理", "大幅波动不利", "Greeks管理复杂"],
            risks=["价格大幅波动风险", "隐含波动率变化风险", "展期风险"],
            parameters={"near_expiration": {"value": 14, "description": "近月到期天数"}, "far_expiration": {"value": 45, "description": "远月到期天数"}, "strike_selection": {"value": "ATM", "description": "行权价选择"}, "roll_policy": {"value": "close", "description": "近月到期后策略"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["time_decay_advantage"] = round(np.std(returns) * 100, 4)
        metrics["optimal_range"] = round(np.std(returns) * np.sqrt(252) * 100 * 0.5, 4)
        metrics["direction_bias"] = "中性，预期价格稳定"
        return metrics


class RatioSpreadStrategy(BaseStrategy):
    """比率价差策略 - 不对称数量的期权组合"""
    def __init__(self):
        super().__init__(
            strategy_id="option_ratio_spread", name="比率价差", category="期权策略",
            description="买入少量近行权价期权，同时卖出更多远行权价期权。无净权利金支出甚至收取权利金，但一侧风险无限。",
            advantages=["低成本或零成本", "方向正确时收益放大", "权利金收入可能覆盖成本"],
            disadvantages=["一侧风险无限", "需要精确的方向判断", "管理复杂"],
            risks=["无限亏损风险", "方向判断错误风险", "保证金风险"],
            parameters={"ratio": {"value": "1:2", "description": "买卖比率"}, "strike_distance": {"value": 5, "description": "行权价间距"}, "expiration": {"value": 30, "description": "到期天数"}, "direction": {"value": "bullish", "description": "方向偏好"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["net_cost"] = 0.5
        metrics["risk_profile"] = "一侧无限风险"
        metrics["direction_bias"] = "看多但需控制风险"
        return metrics


class DiagonalSpreadStrategy(BaseStrategy):
    """对角价差策略 - 不同行权价和到期日的组合"""
    def __init__(self):
        super().__init__(
            strategy_id="option_diagonal_spread", name="对角价差", category="期权策略",
            description="买入一个行权价和到期日的期权，同时卖出另一个行权价和到期日的期权。结合了垂直价差和日历价差的特点，提供更灵活的风险收益特征。",
            advantages=["灵活度高", "可定制风险收益", "利用时间和方向"],
            disadvantages=["Greeks管理复杂", "流动性可能较差", "需要精确的参数选择"],
            risks=["多维度风险", "流动性风险", "模型风险"],
            parameters={"long_strike": {"value": "ITM", "description": "买入行权价"}, "short_strike": {"value": "OTM", "description": "卖出行权价"}, "long_expiration": {"value": 60, "description": "买入到期日"}, "short_expiration": {"value": 30, "description": "卖出到期日"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["flexibility_score"] = 8.0
        metrics["complexity_score"] = 7.0
        metrics["direction_bias"] = "可定制方向偏好"
        return metrics


class CollarStrategy(BaseStrategy):
    """领口策略 - 保护性看跌+卖出备兑看涨"""
    def __init__(self):
        super().__init__(
            strategy_id="option_collar", name="领口策略", category="期权策略",
            description="持有标的资产，买入保护性看跌期权（提供下行保护），同时卖出备兑看涨期权（收取权利金降低保护成本）。在限制上行收益的同时提供下行保护。",
            advantages=["零成本或低成本保护", "风险收益明确", "适合长期持仓保护"],
            disadvantages=["限制了上行收益", "保护水平有限", "需要持续管理"],
            risks=["保护不足风险", "行权导致卖出", "机会成本"],
            parameters={"put_strike": {"value": 0.95, "description": "看跌行权价（占现价比例）"}, "call_strike": {"value": 1.10, "description": "看涨行权价（占现价比例）"}, "expiration": {"value": 60, "description": "到期天数"}, "zero_cost_target": {"value": True, "description": "是否追求零成本"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["downside_protection"] = 5.0
        metrics["upside_cap"] = 10.0
        metrics["net_cost"] = 0.0
        metrics["direction_bias"] = "中性，风险锁定"
        return metrics


class ReverseHedgeStrategy(BaseStrategy):
    """反向对冲策略 - 卖出看跌+买入双倍看涨"""
    def __init__(self):
        super().__init__(
            strategy_id="option_reverse_hedge", name="反向对冲", category="期权策略",
            description="持有标的资产空头（或预期大跌），买入看跌期权保护空头头寸，同时卖出看涨期权对冲部分成本。是领口策略的反向版本。",
            advantages=["为空头头寸提供保护", "可降低对冲成本", "适合看空但需控制风险的场景"],
            disadvantages=["限制了空头收益", "仍需方向判断", "Greeks管理复杂"],
            risks=["方向判断错误风险", "行权风险", "保证金风险"],
            parameters={"put_ratio": {"value": 1.0, "description": "看跌期权比率"}, "call_ratio": {"value": 0.5, "description": "看涨期权比率"}, "expiration": {"value": 30, "description": "到期天数"}, "protection_level": {"value": 0.95, "description": "保护水平"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["short_protection"] = 5.0
        metrics["upside_limit"] = 10.0
        metrics["direction_bias"] = "看空但防御"
        return metrics


# ============================================================
# 期货策略（15种）
# ============================================================

class TrendFollowingStrategy(BaseStrategy):
    """趋势跟踪策略 - 跟随市场价格趋势"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_trend_following", name="趋势跟踪", category="期货策略",
            description="基于技术分析识别市场趋势方向，顺势开仓并跟踪止损。使用移动平均线、突破信号等指标判断趋势，是CTA策略的核心方法之一。",
            advantages=["在趋势行情中获利丰厚", "系统化执行，避免情绪干扰", "适用于多种期货品种"],
            disadvantages=["在震荡市中频繁止损", "趋势反转时回撤大", "参数优化可能过拟合"],
            risks=["趋势反转风险", "假突破风险", "滑点风险"],
            parameters={"fast_ma": {"value": 10, "description": "快线周期"}, "slow_ma": {"value": 30, "description": "慢线周期"}, "atr_multiplier": {"value": 2.0, "description": "ATR止损倍数"}, "position_sizing": {"value": "ATR", "description": "仓位管理方式"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        fma = np.mean(prices[-10:]) if len(prices) >= 10 else prices[-1]
        sma = np.mean(prices[-30:]) if len(prices) >= 30 else prices[-1]
        metrics["trend_direction"] = "上升" if fma > sma else "下降"
        metrics["trend_strength"] = round(abs(fma / sma - 1) * 100, 4)
        metrics["atr"] = round(np.std(returns) * np.sqrt(252) * prices[-1] * 0.01, 4)
        return metrics


class FuturesMeanReversionStrategy(BaseStrategy):
    """期货均值回归策略"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_mean_reversion", name="均值回归", category="期货策略",
            description="基于均值回归理论，当期货价格偏离均值过多时进行反向交易。在价格过高时做空，过低时做多，预期价格将回归到历史均值水平。",
            advantages=["在震荡市中表现优异", "交易信号明确", "风险相对可控"],
            disadvantages=["在趋势市场中持续亏损", "均值可能发生偏移", "需要设置严格止损"],
            risks=["趋势延续风险", "保证金追缴风险", "均值漂移风险"],
            parameters={"lookback": {"value": 20, "description": "均值计算窗口"}, "entry_threshold": {"value": 2.0, "description": "入场Z-score"}, "exit_threshold": {"value": 0.5, "description": "出场Z-score"}, "stop_loss_atr": {"value": 3.0, "description": "止损ATR倍数"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        mv = np.mean(prices[-20:])
        sv = np.std(prices[-20:])
        metrics["current_zscore"] = round((prices[-1] - mv) / sv, 4) if sv > 0 else 0
        metrics["mean_reversion_signal"] = "做空" if metrics["current_zscore"] > 2 else ("做多" if metrics["current_zscore"] < -2 else "观望")
        return metrics


class CarryTradeStrategy(BaseStrategy):
    """套利交易策略 - 利用正套利收益"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_carry_trade", name="套利交易", category="期货策略",
            description="利用期货市场的正向套利（contango）或反向套利（backwardation）结构获利。在正套利市场中做空远月做多近月，在反向套利市场中做多远月做空近月。",
            advantages=["收益来源独立于价格方向", "风险相对较低", "可预测性较强"],
            disadvantages=["套利结构可能变化", "展期成本影响收益", "需要精确的期限结构分析"],
            risks=["期限结构变化风险", "展期风险", "流动性风险"],
            parameters={"roll_method": {"value": "calendar", "description": "展期方式"}, "min_contango": {"value": 0.02, "description": "最小正套利"}, "holding_period": {"value": 30, "description": "持有天数"}, "contracts": {"value": ["near", "far"], "description": "合约选择"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["term_structure"] = "contango" if np.mean(prices[-10:]) > np.mean(prices[-30:]) else "backwardation"
        metrics["roll_yield"] = round(abs(np.mean(returns[-10:]) - np.mean(returns[-30:])) * 100, 4) if len(returns) >= 30 else 0
        return metrics


class CalendarSpreadFuturesStrategy(BaseStrategy):
    """跨期套利策略 - 同品种不同到期日的价差交易"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_calendar_spread", name="跨期套利", category="期货策略",
            description="在同一品种的不同到期月合约之间进行价差交易。当近月和远月合约价差异常时，买入被低估的合约、卖出被高估的合约。",
            advantages=["风险低于单边交易", "价差波动小于价格波动", "收益相对稳定"],
            disadvantages=["价差回归可能缓慢", "套利空间有限", "需要精确计算持有成本"],
            risks=["价差持续扩大风险", "交割风险", "流动性风险"],
            parameters={"near_contract": {"value": "current", "description": "近月合约"}, "far_contract": {"value": "next_1", "description": "远月合约"}, "entry_spread_z": {"value": 2.0, "description": "入场价差Z-score"}, "exit_spread_z": {"value": 0.0, "description": "出场价差Z-score"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        spread = prices[-1] - np.mean(prices[-20:]) if len(prices) >= 20 else 0
        metrics["spread_value"] = round(spread, 4)
        metrics["spread_signal"] = "正套利" if spread > 0 else "反套利"
        return metrics


class CrossCommoditySpreadStrategy(BaseStrategy):
    """跨品种套利策略 - 相关品种间的价差交易"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_cross_commodity", name="跨品种套利", category="期货策略",
            description="在具有高度相关性的不同品种之间进行价差交易。例如大豆和豆油、原油和汽油、黄金和白银等。当两者价差偏离历史关系时进行套利交易。",
            advantages=["利用品种间内在联系", "风险低于单边交易", "可发现相对价值"],
            disadvantages=["品种间关系可能变化", "需要跨市场研究", "流动性可能不对称"],
            risks=["相关性断裂风险", "供需结构变化风险", "政策风险"],
            parameters={"leg1": {"value": "gold", "description": "品种1"}, "leg2": {"value": "silver", "description": "品种2"}, "ratio_lookback": {"value": 60, "description": "比率回溯期"}, "entry_zscore": {"value": 2.0, "description": "入场Z-score"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["inter_commodity_signal"] = round(np.corrcoef(returns[:-1], returns[1:])[0, 1], 4)
        metrics["relative_value"] = round(prices[-1] / np.mean(prices), 4)
        return metrics


class CTAStrategy(BaseStrategy):
    """CTA策略 - 商品交易顾问系统性策略"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_cta", name="CTA策略", category="期货策略",
            description="商品交易顾问（CTA）策略，系统化地管理期货和衍生品投资组合。综合运用趋势跟踪、动量、均值回归等多种子策略，在多品种间进行分散化投资。",
            advantages=["分散化程度高", "与股票债券相关性低", "系统化风险管理"],
            disadvantages=["管理费用较高", "在低波动环境中表现差", "策略容量有限"],
            risks=["模型失效风险", "流动性风险", "极端行情风险"],
            parameters={"sub_strategies": {"value": ["trend", "momentum", "mean_reversion"], "description": "子策略列表"}, "risk_per_trade": {"value": 0.01, "description": "单笔风险"}, "max_portfolio_risk": {"value": 0.05, "description": "最大组合风险"}, "rebalance_freq": {"value": "daily", "description": "再平衡频率"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["portfolio_risk"] = round(np.std(returns) * np.sqrt(252) * 100, 4)
        metrics["strategy_allocation"] = "趋势60%/动量25%/均值回归15%"
        return metrics


class MomentumBreakoutStrategy(BaseStrategy):
    """动量突破策略 - 价格突破关键位时入场"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_momentum_breakout", name="动量突破", category="期货策略",
            description="当价格突破关键支撑/阻力位或通道边界时入场交易。突破通常伴随成交量放大，表示新的趋势开始。",
            advantages=["入场信号明确", "能捕捉趋势起点", "适合趋势性市场"],
            disadvantages=["假突破频繁", "突破后可能回调", "需要精确的突破定义"],
            risks=["假突破风险", "回调风险", "滑点风险"],
            parameters={"breakout_period": {"value": 20, "description": "突破回溯期"}, "breakout_pct": {"value": 0.02, "description": "突破幅度"}, "volume_confirm": {"value": True, "description": "是否需要成交量确认"}, "atr_stop": {"value": 2.0, "description": "ATR止损倍数"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        hn = np.max(prices[-20:]) if len(prices) >= 20 else prices[-1]
        ln = np.min(prices[-20:]) if len(prices) >= 20 else prices[-1]
        metrics["resistance_level"] = round(hn, 4)
        metrics["support_level"] = round(ln, 4)
        metrics["breakout_signal"] = "向上突破" if prices[-1] > hn * 0.99 else ("向下突破" if prices[-1] < ln * 1.01 else "区间震荡")
        return metrics


class GridTradingStrategy(BaseStrategy):
    """网格交易策略 - 在价格网格中自动买卖"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_grid", name="网格交易", category="期货策略",
            description="在预设的价格网格中，每到达一个网格价位就执行买入或卖出操作。在震荡市中通过频繁的小额交易累积利润，适合自动化执行。",
            advantages=["震荡市中稳定获利", "完全可自动化", "不需要判断方向"],
            disadvantages=["趋势市场中可能大幅亏损", "网格设置需要经验", "资金利用率低"],
            risks=["单边趋势风险", "保证金不足风险", "流动性风险"],
            parameters={"grid_count": {"value": 20, "description": "网格数量"}, "grid_spacing": {"value": 0.01, "description": "网格间距（%）"}, "order_size": {"value": 1, "description": "每格下单量"}, "price_range": {"value": [0.95, 1.05], "description": "价格范围"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        pr = np.max(prices[-60:]) - np.min(prices[-60:]) if len(prices) >= 60 else np.std(prices)
        metrics["grid_profit_estimate"] = round(pr / np.mean(prices) * 100 * 0.5, 4)
        metrics["suitability"] = "适合" if metrics["volatility"] < 20 else "不适合"
        return metrics


class SeasonalTradingStrategy(BaseStrategy):
    """季节性交易策略 - 利用季节性价格规律"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_seasonal", name="季节性交易", category="期货策略",
            description="利用大宗商品价格的季节性规律进行交易。例如农产品在收获季节价格下跌、能源在冬季需求增加价格上涨等。",
            advantages=["交易逻辑基于实物供需", "历史规律可回测验证", "风险相对可控"],
            disadvantages=["季节性规律可能变化", "受天气等不可控因素影响", "需要行业专业知识"],
            risks=["季节性规律失效风险", "极端天气风险", "政策变化风险"],
            parameters={"commodity": {"value": "soybean", "description": "交易品种"}, "seasonal_window": {"value": [3, 6], "description": "季节性窗口（月）"}, "historical_accuracy": {"value": 0.70, "description": "历史准确率"}, "position_duration": {"value": 60, "description": "持仓天数"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["seasonal_pattern"] = round(np.mean(returns[-63:]) * 252 * 100, 4) if len(returns) >= 63 else 0
        metrics["seasonal_signal"] = "符合季节性规律" if metrics["seasonal_pattern"] > 0 else "偏离季节性规律"
        return metrics


class BasisTradingStrategy(BaseStrategy):
    """基差交易策略 - 利用现货与期货价差"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_basis", name="基差交易", category="期货策略",
            description="利用现货价格与期货价格之间的基差进行交易。当基差异常时，通过同时买卖现货和期货进行套利。基差最终会收敛，提供相对安全的获利机会。",
            advantages=["风险较低，基差终将收敛", "收益来源明确", "适合有现货能力的交易者"],
            disadvantages=["需要现货处理能力", "仓储和物流成本", "基差可能持续扩大"],
            risks=["基差扩大风险", "仓储成本风险", "交割风险"],
            parameters={"basis_threshold": {"value": 0.03, "description": "基差异常阈值"}, "holding_period": {"value": 30, "description": "最大持有天数"}, "storage_cost_budget": {"value": 0.01, "description": "仓储成本预算"}, "delivery_capable": {"value": True, "description": "是否可交割"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["basis_estimate"] = round(np.std(returns) * 100, 4)
        metrics["convergence_signal"] = "基差收敛中" if np.mean(returns[-10:]) > np.mean(returns[-30:]) else "基差扩大中"
        return metrics


class FuturesHedgeStrategy(BaseStrategy):
    """期货对冲策略 - 利用期货对冲现货风险"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_hedge", name="对冲策略", category="期货策略",
            description="企业或投资者利用期货合约对冲现货市场的价格风险。生产商做空期货锁定销售价格，消费商做多期货锁定采购价格。",
            advantages=["有效锁定价格", "降低经营风险", "提高经营可预测性"],
            disadvantages=["对冲成本", "可能错过有利价格变动", "需要精确计算对冲比率"],
            risks=["基差风险", "保证金追缴风险", "对冲比率不当风险"],
            parameters={"hedge_ratio": {"value": 0.90, "description": "对冲比率"}, "hedge_instrument": {"value": "futures", "description": "对冲工具"}, "rebalance_freq": {"value": "monthly", "description": "再平衡频率"}, "cross_hedge": {"value": False, "description": "是否交叉对冲"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["hedge_effectiveness"] = round(np.corrcoef(returns[:-1], returns[1:])[0, 1] * 100, 4)
        metrics["residual_risk"] = round((1 - metrics["hedge_effectiveness"] / 100) * 100, 4)
        return metrics


class QuantTrendStrategy(BaseStrategy):
    """量化趋势策略 - 多因子量化趋势判断"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_quant_trend", name="量化趋势", category="期货策略",
            description="综合运用多个量化因子（价格动量、成交量变化、持仓量变化、波动率等）构建趋势判断模型，系统化地识别和跟踪期货市场趋势。",
            advantages=["多因子融合提高准确率", "系统化执行", "可回测优化"],
            disadvantages=["模型复杂度高", "因子可能失效", "需要大量计算资源"],
            risks=["模型过拟合风险", "因子衰减风险", "极端行情风险"],
            parameters={"factors": {"value": ["price_momentum", "volume", "open_interest", "volatility"], "description": "使用因子"}, "signal_threshold": {"value": 0.6, "description": "信号阈值"}, "lookback_periods": {"value": [5, 10, 20, 60], "description": "多周期回溯"}, "weight_method": {"value": "equal", "description": "因子加权方式"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        ms = 1 if np.mean(returns[-10:]) > 0 else -1
        vs = 1 if np.std(returns[-10:]) < np.std(returns[-30:]) else -1
        metrics["composite_signal"] = round((ms + vs) / 2, 2)
        metrics["signal_direction"] = "做多" if metrics["composite_signal"] > 0 else "做空"
        return metrics


class MacroFuturesStrategy(BaseStrategy):
    """宏观期货策略 - 基于宏观经济判断"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_macro", name="宏观期货", category="期货策略",
            description="基于对全球宏观经济形势的判断，在利率期货、汇率期货、股指期货、商品期货等多个品种间进行配置。通过宏观分析把握大类资产轮动趋势。",
            advantages=["把握宏观趋势", "多品种分散", "与微观策略互补"],
            disadvantages=["宏观判断难度大", "反应速度慢", "需要全球视野"],
            risks=["宏观判断失误风险", "政策突变风险", "地缘政治风险"],
            parameters={"macro_indicators": {"value": ["GDP", "CPI", "PMI", "利率"], "description": "宏观指标"}, "asset_allocation": {"value": {"commodity": 0.30, "currency": 0.25, "bond": 0.25, "equity": 0.20}, "description": "资产配置"}, "rebalance_freq": {"value": "monthly", "description": "调仓频率"}, "risk_budget": {"value": 0.10, "description": "风险预算"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["macro_regime"] = "增长" if np.mean(returns[-60:]) > 0 else "衰退"
        metrics["allocation_shift"] = "增加风险资产" if metrics["macro_regime"] == "增长" else "增加防御资产"
        return metrics


class CommodityIndexStrategy(BaseStrategy):
    """商品指数策略 - 跟踪商品市场指数"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_commodity_index", name="商品指数", category="期货策略",
            description="通过投资商品期货指数（如CRB指数、标普GSCI等）获取商品市场的整体收益。可作为通胀对冲工具和资产配置的多样化选择。",
            advantages=["分散化程度高", "通胀对冲效果好", "与传统资产相关性低"],
            disadvantages=["展期成本影响收益", "商品周期性波动大", "被动跟踪无超额收益"],
            risks=["商品价格下跌风险", "展期风险", "流动性风险"],
            parameters={"target_index": {"value": "GSCI", "description": "目标指数"}, "roll_method": {"value": "optimized", "description": "展期策略"}, "rebalance_freq": {"value": "monthly", "description": "再平衡频率"}, "allocation_pct": {"value": 0.10, "description": "组合配置比例"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["roll_yield"] = round(np.mean(returns) * 252 * 100 * 0.3, 4)
        metrics["inflation_correlation"] = 0.6
        return metrics


class WeatherDerivativeStrategy(BaseStrategy):
    """天气衍生品策略 - 利用天气相关产品"""
    def __init__(self):
        super().__init__(
            strategy_id="futures_weather", name="天气衍生品", category="期货策略",
            description="利用天气期货、温度期权、降水量衍生品等天气相关金融工具进行交易或风险管理。主要应用于能源、农业等行业对冲天气风险。",
            advantages=["与传统金融市场相关性极低", "风险分散效果好", "对冲实体经济风险"],
            disadvantages=["市场流动性较低", "定价模型复杂", "数据获取困难"],
            risks=["模型风险", "流动性风险", "极端天气事件风险"],
            parameters={"weather_type": {"value": "temperature", "description": "天气类型"}, "region": {"value": "US_EAST", "description": "区域"}, "season": {"value": "winter", "description": "季节"}, "hedging_ratio": {"value": 0.80, "description": "对冲比率"}},
        )
    def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        prices = extract_price_series(df)
        if prices is None or len(prices) < 2: return {"error": "数据不足，无法分析"}
        returns = calc_returns(prices)
        metrics = common_analyze(prices, returns)
        metrics["weather_sensitivity"] = round(np.std(returns) * np.sqrt(252) * 100, 4)
        metrics["diversification_benefit"] = 0.85
        return metrics


# ============================================================
# 策略数据库 - 所有策略实例
# ============================================================

ALL_STRATEGIES: List[BaseStrategy] = [
    # 股票策略（20种）
    MomentumStrategy(),
    MeanReversionStrategy(),
    ValueInvestingStrategy(),
    GrowthInvestingStrategy(),
    DividendYieldStrategy(),
    LowVolatilityStrategy(),
    QualityFactorStrategy(),
    SizeFactorStrategy(),
    MultiFactorStrategy(),
    SectorRotationStrategy(),
    PairsTradingStrategy(),
    StatisticalArbitrageStrategy(),
    EventDrivenStrategy(),
    ETFArbitrageStrategy(),
    QuantTimingStrategy(),
    TechnicalAnalysisStrategy(),
    FundamentalAnalysisStrategy(),
    MacroHedgeStrategy(),
    AlphaHedgeStrategy(),
    SmartBetaStrategy(),
    # 债券策略（15种）
    DurationManagementStrategy(),
    YieldCurveTradingStrategy(),
    CreditSpreadStrategy(),
    ConvertibleArbitrageStrategy(),
    BondIndexStrategy(),
    HighYieldBondStrategy(),
    EmergingMarketBondStrategy(),
    InflationProtectedStrategy(),
    FloatingRateStrategy(),
    LadderStrategy(),
    BulletStrategy(),
    BarbellStrategy(),
    BondSwapStrategy(),
    TotalReturnStrategy(),
    DefaultPredictionStrategy(),
    # 期权策略（15种）
    LongCallStrategy(),
    LongPutStrategy(),
    CoveredCallStrategy(),
    ProtectivePutStrategy(),
    BullCallSpreadStrategy(),
    BearPutSpreadStrategy(),
    StraddleStrategy(),
    StrangleStrategy(),
    IronCondorStrategy(),
    ButterflySpreadStrategy(),
    CalendarSpreadStrategy(),
    RatioSpreadStrategy(),
    DiagonalSpreadStrategy(),
    CollarStrategy(),
    ReverseHedgeStrategy(),
    # 期货策略（15种）
    TrendFollowingStrategy(),
    FuturesMeanReversionStrategy(),
    CarryTradeStrategy(),
    CalendarSpreadFuturesStrategy(),
    CrossCommoditySpreadStrategy(),
    CTAStrategy(),
    MomentumBreakoutStrategy(),
    GridTradingStrategy(),
    SeasonalTradingStrategy(),
    BasisTradingStrategy(),
    FuturesHedgeStrategy(),
    QuantTrendStrategy(),
    MacroFuturesStrategy(),
    CommodityIndexStrategy(),
    WeatherDerivativeStrategy(),
]

# 策略ID到策略实例的映射字典
STRATEGY_MAP: Dict[str, BaseStrategy] = {s.id: s for s in ALL_STRATEGIES}


def get_all_strategies() -> List[Dict[str, Any]]:
    """获取所有策略信息列表"""
    return [s.to_dict() for s in ALL_STRATEGIES]


def get_strategy_by_id(strategy_id: str) -> Optional[BaseStrategy]:
    """根据ID获取策略实例"""
    return STRATEGY_MAP.get(strategy_id)


def get_strategies_by_category(category: str) -> List[Dict[str, Any]]:
    """根据分类获取策略列表"""
    return [s.to_dict() for s in ALL_STRATEGIES if s.category == category]


def get_categories() -> Dict[str, int]:
    """获取各分类及其策略数量"""
    cats = {}
    for s in ALL_STRATEGIES:
        cats[s.category] = cats.get(s.category, 0) + 1
    return cats
