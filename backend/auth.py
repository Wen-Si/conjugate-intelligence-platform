"""
认证模块
提供 JWT Token 生成和验证功能，以及密码哈希处理
"""

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

# ============================================================
# 配置常量
# ============================================================

# JWT 密钥（生产环境应从环境变量读取）
SECRET_KEY = "conjugate-intelligence-platform-secret-key-2024"
# JWT 算法
ALGORITHM = "HS256"
# Token 过期时间（天）
ACCESS_TOKEN_EXPIRE_DAYS = 7

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 模拟用户数据库（生产环境应使用真实数据库）
# 格式: {username: {"id": int, "username": str, "email": str, "hashed_password": str}}
fake_users_db: dict = {}


# ============================================================
# 密码工具函数
# ============================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码与哈希密码是否匹配

    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码

    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    对明文密码进行哈希处理

    Args:
        password: 明文密码

    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)


# ============================================================
# JWT Token 工具函数
# ============================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT 访问令牌

    Args:
        data: 要编码到 token 中的数据（通常包含 sub 字段为用户名）
        expires_delta: token 过期时间增量，默认为 ACCESS_TOKEN_EXPIRE_DAYS 天

    Returns:
        str: 编码后的 JWT token 字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    验证 JWT token 并提取用户名

    Args:
        token: JWT token 字符串

    Returns:
        Optional[str]: 验证成功返回用户名，失败返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


# ============================================================
# 用户管理函数
# ============================================================

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    验证用户凭据

    Args:
        username: 用户名
        password: 明文密码

    Returns:
        Optional[dict]: 验证成功返回用户信息字典，失败返回 None
    """
    user = fake_users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def register_user(username: str, email: str, password: str) -> Optional[dict]:
    """
    注册新用户

    Args:
        username: 用户名
        email: 邮箱地址
        password: 明文密码

    Returns:
        Optional[dict]: 注册成功返回用户信息字典，失败（用户名已存在）返回 None
    """
    if username in fake_users_db:
        return None
    hashed_password = get_password_hash(password)
    user_id = len(fake_users_db) + 1
    user = {
        "id": user_id,
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
    }
    fake_users_db[username] = user
    return user


def get_user(username: str) -> Optional[dict]:
    """
    根据用户名获取用户信息

    Args:
        username: 用户名

    Returns:
        Optional[dict]: 用户信息字典，不存在返回 None
    """
    if username in fake_users_db:
        return fake_users_db[username]
    return None
