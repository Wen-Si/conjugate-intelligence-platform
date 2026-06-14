"""
FastAPI 主应用模块
共轭智能平台后端服务 - 包含用户认证、文件上传、策略分析、AI聊天等API
"""

import os
import shutil
import tempfile
from datetime import datetime
from typing import Optional, List, Dict, Any

import pandas as pd
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 导入自定义模块
from models import (
    UserRegister, UserLogin, TokenResponse, UserInfo,
    StrategyListResponse, StrategyInfo,
    AnalyzeRequest, AnalysisResult, AnalysisMetrics,
    UploadResponse, ChatRequest, ChatResponse,
    APIResponse
)
from auth import (
    authenticate_user, register_user, create_access_token,
    verify_token, get_user
)
from strategies import (
    get_all_strategies, get_strategy_by_id,
    get_strategies_by_category, get_categories
)

# ============================================================
# FastAPI 应用实例
# ============================================================

app = FastAPI(
    title="共轭智能平台 API",
    description="金融策略分析与AI智能投顾后端服务",
    version="1.0.0",
)

# CORS 中间件配置 - 允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],           # 允许所有HTTP方法
    allow_headers=["*"],           # 允许所有请求头
)

# ============================================================
# 智谱AI配置
# ============================================================

ZHIPU_API_KEY = "325d6fa364954d2e871c30ba95b553bd.KBdQdqgJgELJBhnv"

# 上传文件存储目录
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# JWT 依赖注入
# ============================================================

async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    从请求头中提取并验证JWT Token，返回当前用户信息

    Args:
        authorization: Authorization请求头，格式为 "Bearer <token>"

    Returns:
        dict: 用户信息字典

    Raises:
        HTTPException: Token无效或缺失时抛出401错误
    """
    if authorization is None:
        raise HTTPException(status_code=401, detail="未提供认证Token")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token格式错误，应为 'Bearer <token>'")
    token = authorization.split(" ")[1]
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Token无效或已过期")
    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


# ============================================================
# 首页和健康检查
# ============================================================

@app.get("/", tags=["系统"])
async def root():
    """API根路径，返回服务信息"""
    return {
        "service": "共轭智能平台 API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============================================================
# 用户认证 API
# ============================================================

@app.post("/api/register", response_model=APIResponse, tags=["用户认证"])
async def register(user_data: UserRegister):
    """
    用户注册接口

    - **username**: 用户名（3-50字符）
    - **email**: 邮箱地址
    - **password**: 密码（6-128字符）
    """
    existing_user = get_user(user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = register_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
    )
    if user is None:
        raise HTTPException(status_code=500, detail="注册失败，请稍后重试")

    # 注册成功后自动生成Token
    token = create_access_token(data={"sub": user["username"]})

    return APIResponse(
        success=True,
        message="注册成功",
        data={
            "access_token": token,
            "token_type": "bearer",
            "username": user["username"],
            "email": user["email"],
        }
    )


@app.post("/api/login", response_model=APIResponse, tags=["用户认证"])
async def login(user_data: UserLogin):
    """
    用户登录接口

    - **username**: 用户名
    - **password**: 密码
    """
    user = authenticate_user(user_data.username, user_data.password)
    if user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(data={"sub": user["username"]})

    return APIResponse(
        success=True,
        message="登录成功",
        data={
            "access_token": token,
            "token_type": "bearer",
            "username": user["username"],
            "email": user["email"],
        }
    )


@app.get("/api/me", response_model=APIResponse, tags=["用户认证"])
async def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前登录用户信息（需要认证）"""
    return APIResponse(
        success=True,
        message="获取成功",
        data={
            "id": current_user["id"],
            "username": current_user["username"],
            "email": current_user["email"],
        }
    )


# ============================================================
# Excel文件上传 API
# ============================================================

@app.post("/api/upload", response_model=APIResponse, tags=["文件管理"])
async def upload_excel(file: UploadFile = File(...)):
    """
    上传Excel文件并解析数据

    支持格式：.xlsx, .xls, .csv
    返回文件基本信息、列名、数据类型和前5行预览
    """
    # 验证文件类型
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    allowed_extensions = {".xlsx", ".xls", ".csv"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {file_ext}，仅支持 {', '.join(allowed_extensions)}"
        )

    # 保存上传文件到临时目录
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(save_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 读取Excel/CSV文件
        if file_ext == ".csv":
            df = pd.read_csv(save_path, encoding="utf-8")
        else:
            df = pd.read_excel(save_path, engine="openpyxl")

        # 获取数据基本信息
        rows, cols = df.shape
        column_names = df.columns.tolist()

        # 获取各列数据类型
        data_types = {}
        for col in column_names:
            dtype_str = str(df[col].dtype)
            data_types[col] = dtype_str

        # 获取前5行预览数据（转为字典列表）
        preview_df = df.head(5)
        # 处理NaN值
        preview_df = preview_df.where(pd.notnull(preview_df), None)
        preview = preview_df.to_dict(orient="records")

        return APIResponse(
            success=True,
            message=f"文件上传成功: {file.filename}",
            data={
                "filename": file.filename,
                "rows": rows,
                "columns": cols,
                "column_names": column_names,
                "data_types": data_types,
                "preview": preview,
                "file_path": save_path,
            }
        )
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="文件内容为空")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="文件解析失败，请检查文件格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理错误: {str(e)}")


# ============================================================
# 策略列表 API
# ============================================================

@app.get("/api/strategies", response_model=APIResponse, tags=["策略管理"])
async def list_strategies(category: Optional[str] = None):
    """
    获取策略列表

    - **category**: 可选，按分类筛选（股票策略/债券策略/期权策略/期货策略）
    """
    if category:
        strategies = get_strategies_by_category(category)
    else:
        strategies = get_all_strategies()

    categories = get_categories()

    return APIResponse(
        success=True,
        message=f"获取策略列表成功，共 {len(strategies)} 个策略",
        data={
            "total": len(strategies),
            "categories": categories,
            "strategies": strategies,
        }
    )


@app.get("/api/strategies/{strategy_id}", response_model=APIResponse, tags=["策略管理"])
async def get_strategy_detail(strategy_id: str):
    """
    获取单个策略详情

    - **strategy_id**: 策略唯一标识
    """
    strategy = get_strategy_by_id(strategy_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail=f"策略不存在: {strategy_id}")

    return APIResponse(
        success=True,
        message="获取策略详情成功",
        data=strategy.to_dict(),
    )


# ============================================================
# 策略分析执行 API
# ============================================================

@app.post("/api/analyze", response_model=APIResponse, tags=["策略分析"])
async def analyze_strategy(request: AnalyzeRequest):
    """
    执行策略分析

    - **strategy_id**: 策略ID
    - **data**: Excel数据（字典列表格式）
    - **parameters**: 可选，自定义分析参数
    """
    # 验证策略是否存在
    strategy = get_strategy_by_id(request.strategy_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail=f"策略不存在: {request.strategy_id}")

    # 验证数据是否为空
    if not request.data:
        raise HTTPException(status_code=400, detail="分析数据不能为空")

    try:
        # 将字典列表转换为 DataFrame
        df = pd.DataFrame(request.data)

        # 提取自定义参数
        custom_params = request.parameters or {}

        # 执行策略分析
        analysis_result = strategy.analyze(df, **custom_params)

        # 检查是否返回错误
        if isinstance(analysis_result, dict) and "error" in analysis_result:
            return APIResponse(
                success=False,
                message=analysis_result["error"],
                data=None,
            )

        # 构建分析结果
        result = AnalysisResult(
            strategy_id=strategy.id,
            strategy_name=strategy.name,
            strategy_category=strategy.category,
            metrics=AnalysisMetrics(**analysis_result) if analysis_result else AnalysisMetrics(),
            summary=f"策略 [{strategy.name}] 分析完成。"
                    f"年化收益率: {analysis_result.get('annualized_return', 'N/A')}%, "
                    f"最大回撤: {analysis_result.get('max_drawdown', 'N/A')}%, "
                    f"夏普比率: {analysis_result.get('sharpe_ratio', 'N/A')}, "
                    f"波动率: {analysis_result.get('volatility', 'N/A')}%",
            chart_data={
                "metrics": analysis_result,
                "strategy_name": strategy.name,
                "category": strategy.category,
            }
        )

        return APIResponse(
            success=True,
            message=f"策略分析完成: {strategy.name}",
            data=result.model_dump(),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"数据分析错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析执行错误: {str(e)}")


# ============================================================
# AI聊天 API
# ============================================================

@app.post("/api/chat", response_model=APIResponse, tags=["AI聊天"])
async def chat_with_ai(request: ChatRequest):
    """
    AI聊天接口 - 调用智谱GLM-4-Flash模型

    - **message**: 用户消息
    - **context**: 可选，上下文信息
    - **strategy_id**: 可选，关联策略ID
    """
    try:
        import zhipuai

        # 初始化智谱AI客户端
        client = zhipuai.ZhipuAI(api_key=ZHIPU_API_KEY)

        # 构建系统提示词
        system_prompt = (
            "你是共轭智能平台的AI投资顾问助手。你拥有丰富的金融投资知识，"
            "涵盖股票、债券、期权、期货等多个领域。"
            "请用专业但通俗易懂的语言回答用户的问题。"
            "当涉及具体投资建议时，请提醒用户投资有风险，决策需谨慎。"
        )

        # 如果关联了策略，添加策略上下文
        if request.strategy_id:
            strategy = get_strategy_by_id(request.strategy_id)
            if strategy:
                system_prompt += (
                    f"\n\n当前讨论的策略是: {strategy.name}（{strategy.category}）\n"
                    f"策略描述: {strategy.description}\n"
                    f"策略优势: {', '.join(strategy.advantages)}\n"
                    f"策略风险: {', '.join(strategy.risks)}"
                )

        # 如果有额外上下文
        if request.context:
            system_prompt += f"\n\n用户提供的上下文信息: {request.context}"

        # 调用智谱AI API
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message},
            ],
            temperature=0.7,
            max_tokens=2048,
        )

        # 提取回复内容
        reply = response.choices[0].message.content

        return APIResponse(
            success=True,
            message="AI回复成功",
            data={
                "reply": reply,
                "timestamp": datetime.now().isoformat(),
                "model": "glm-4-flash",
            }
        )

    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="zhipuai库未安装，请执行: pip install zhipuai"
        )
    except Exception as e:
        error_msg = str(e)
        # 如果API调用失败，返回友好的错误信息
        return APIResponse(
            success=False,
            message=f"AI服务暂时不可用: {error_msg}",
            data={
                "reply": "抱歉，AI服务暂时不可用，请稍后重试。如果问题持续存在，请联系管理员。",
                "timestamp": datetime.now().isoformat(),
                "model": "glm-4-flash",
            }
        )


# ============================================================
# 启动入口
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
