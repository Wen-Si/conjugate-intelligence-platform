"""
数据模型定义模块
使用 Pydantic 定义所有请求/响应的数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================
# 用户认证相关模型
# ============================================================

class UserRegister(BaseModel):
    """用户注册请求模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """JWT Token 响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    username: str = Field(..., description="用户名")


class UserInfo(BaseModel):
    """用户信息响应模型"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱地址")


# ============================================================
# 策略相关模型
# ============================================================

class StrategyCategory(str, Enum):
    """策略分类枚举"""
    STOCK = "股票策略"
    BOND = "债券策略"
    OPTION = "期权策略"
    FUTURES = "期货策略"


class StrategyInfo(BaseModel):
    """策略信息响应模型"""
    id: str = Field(..., description="策略唯一标识")
    name: str = Field(..., description="策略名称")
    category: str = Field(..., description="策略分类")
    description: str = Field(..., description="策略描述")
    advantages: List[str] = Field(default_factory=list, description="策略优势")
    disadvantages: List[str] = Field(default_factory=list, description="策略劣势")
    risks: List[str] = Field(default_factory=list, description="风险提示")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="策略参数")


class StrategyListResponse(BaseModel):
    """策略列表响应模型"""
    total: int = Field(..., description="策略总数")
    categories: Dict[str, int] = Field(default_factory=dict, description="各分类策略数量")
    strategies: List[StrategyInfo] = Field(default_factory=list, description="策略列表")


# ============================================================
# 分析相关模型
# ============================================================

class AnalyzeRequest(BaseModel):
    """分析请求模型"""
    strategy_id: str = Field(..., description="策略ID")
    data: List[Dict[str, Any]] = Field(..., description="Excel数据（字典列表）")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="自定义参数")


class AnalysisMetrics(BaseModel):
    """分析指标模型"""
    annualized_return: Optional[float] = Field(None, description="年化收益率(%)")
    max_drawdown: Optional[float] = Field(None, description="最大回撤(%)")
    sharpe_ratio: Optional[float] = Field(None, description="夏普比率")
    volatility: Optional[float] = Field(None, description="年化波动率(%)")
    win_rate: Optional[float] = Field(None, description="胜率(%)")
    profit_loss_ratio: Optional[float] = Field(None, description="盈亏比")
    total_return: Optional[float] = Field(None, description="总收益率(%)")
    calmar_ratio: Optional[float] = Field(None, description="卡玛比率")
    sortino_ratio: Optional[float] = Field(None, description="索提诺比率")
    beta: Optional[float] = Field(None, description="Beta系数")
    alpha: Optional[float] = Field(None, description="Alpha系数")
    information_ratio: Optional[float] = Field(None, description="信息比率")
    tracking_error: Optional[float] = Field(None, description="跟踪误差(%)")
    downside_deviation: Optional[float] = Field(None, description="下行偏差(%)")
    var: Optional[float] = Field(None, description="在险价值(VaR)(%)")


class AnalysisResult(BaseModel):
    """分析结果响应模型"""
    strategy_id: str = Field(..., description="策略ID")
    strategy_name: str = Field(..., description="策略名称")
    strategy_category: str = Field(..., description="策略分类")
    metrics: AnalysisMetrics = Field(default_factory=AnalysisMetrics, description="分析指标")
    signals: Optional[List[Dict[str, Any]]] = Field(None, description="交易信号列表")
    positions: Optional[List[Dict[str, Any]]] = Field(None, description="持仓建议")
    summary: str = Field(default="", description="分析摘要")
    chart_data: Optional[Dict[str, Any]] = Field(None, description="图表数据")


# ============================================================
# 文件上传相关模型
# ============================================================

class UploadResponse(BaseModel):
    """文件上传响应模型"""
    filename: str = Field(..., description="文件名")
    rows: int = Field(..., description="数据行数")
    columns: int = Field(..., description="数据列数")
    column_names: List[str] = Field(default_factory=list, description="列名列表")
    preview: List[Dict[str, Any]] = Field(default_factory=list, description="数据预览（前5行）")
    data_types: Dict[str, str] = Field(default_factory=dict, description="各列数据类型")


# ============================================================
# AI聊天相关模型
# ============================================================

class ChatRequest(BaseModel):
    """AI聊天请求模型"""
    message: str = Field(..., description="用户消息")
    context: Optional[str] = Field(default=None, description="上下文信息")
    strategy_id: Optional[str] = Field(default=None, description="关联策略ID")


class ChatResponse(BaseModel):
    """AI聊天响应模型"""
    reply: str = Field(..., description="AI回复内容")
    timestamp: str = Field(..., description="响应时间戳")


# ============================================================
# 通用响应模型
# ============================================================

class APIResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
