"""
中间件模块，用于处理请求和响应
"""
import time
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import get_api_logger, get_user_activity_logger
from app.core.context import get_current_user_id

# 创建API日志器
api_logger = get_api_logger("api_middleware")
# 创建用户活动日志器
user_activity_logger = get_user_activity_logger("user_activity")

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    日志中间件，记录所有API请求和响应
    """
    async def dispatch(self, request: Request, call_next):
        # 获取请求信息
        start_time = time.time()
        path = request.url.path
        method = request.method
        client_host = request.client.host if request.client else "unknown"

        # 获取当前用户ID
        user_id = get_current_user_id()
        user_info = f"用户ID: {user_id}" if user_id else "未认证用户"

        # 尝试从请求中获取用户ID
        if not user_id:
            # 从请求头中获取令牌
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.replace('Bearer ', '')
                try:
                    # 解析JWT令牌
                    from jose import jwt
                    from app.core.security import SECRET_KEY, ALGORITHM
                    from app.db.session import SessionLocal
                    from app.models.user import User

                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    username = payload.get("sub")
                    if username:
                        # 从数据库中获取用户ID
                        db = SessionLocal()
                        try:
                            user = db.query(User).filter(User.username == username).first()
                            if user:
                                # 设置当前用户ID
                                from app.core.context import set_current_user_id
                                set_current_user_id(user.id)
                                user_id = user.id
                                user_info = f"用户ID: {user_id} (用户名: {username})"
                        finally:
                            db.close()
                except Exception as e:
                    api_logger.warning(f"解析用户令牌失败: {str(e)}")

        # 记录请求开始
        api_logger.info(f"开始处理请求: {method} {path} - {user_info} - 客户端: {client_host}")

        # 处理请求
        try:
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 记录请求结束
            api_logger.info(f"请求处理完成: {method} {path} - 状态码: {response.status_code} - 处理时间: {process_time:.4f}秒")

            # 记录用户活动（仅记录成功的请求）
            if user_id and response.status_code < 400:
                # 获取用户名
                username = "未知用户"
                try:
                    from app.db.session import SessionLocal
                    from app.models.user import User
                    db = SessionLocal()
                    try:
                        user = db.query(User).filter(User.id == user_id).first()
                        if user:
                            username = user.username
                    finally:
                        db.close()
                except Exception as e:
                    api_logger.warning(f"获取用户名失败: {str(e)}")

                # 记录用户活动
                user_activity_logger.info(f"用户活动: 用户 {username} (ID: {user_id}) - {method} {path} - 状态码: {response.status_code}")

            return response
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            api_logger.error(f"请求处理异常: {method} {path} - 异常: {str(e)} - 处理时间: {process_time:.4f}秒")
            raise

class UserIDMiddleware(BaseHTTPMiddleware):
    """
    用户ID中间件，从请求中提取用户ID并设置到上下文中
    """
    async def dispatch(self, request: Request, call_next):
        # 重置用户ID
        from app.core.context import reset_current_user_id
        reset_current_user_id()

        # 尝试从请求中获取令牌
        token = None

        # 1. 从请求头中获取令牌
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')

        # 2. 如果请求头中没有令牌，尝试从URL参数中获取
        if not token:
            token_param = request.query_params.get('token')
            if token_param:
                token = token_param

        # 如果找到令牌，尝试解析并设置用户ID
        if token:
            try:
                # 解析JWT令牌
                from jose import jwt, JWTError
                from app.core.security import SECRET_KEY, ALGORITHM
                from app.db.session import SessionLocal
                from app.models.user import User

                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("sub")
                if username:
                    # 从数据库中获取用户ID
                    db = SessionLocal()
                    try:
                        user = db.query(User).filter(User.username == username).first()
                        if user:
                            # 设置当前用户ID
                            from app.core.context import set_current_user_id
                            set_current_user_id(user.id)
                    finally:
                        db.close()
            except JWTError as e:
                api_logger.warning(f"令牌解析错误: {str(e)}")
            except Exception as e:
                api_logger.error(f"设置用户ID失败: {str(e)}")

        # 继续处理请求
        response = await call_next(request)
        return response
