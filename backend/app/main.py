from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1 import api_router
from app.services.mcp_adapter import mcp_adapter
from app.core.config import settings
from app.core.logger import setup_logging
from app.db.session import SessionLocal
from app.db.init_db import init_db
from app.core.middleware import LoggingMiddleware, UserIDMiddleware
import asyncio

# 初始化日志
setup_logging()

# 初始化数据库
db = SessionLocal()
try:
    # 创建数据库表
    from app.db.base import Base
    from app.db.session import engine
    Base.metadata.create_all(bind=engine)

    # 如果配置了初始化超级用户，则创建超级用户
    if settings.config.get("database", {}).get("init_superuser", False):
        from app.db.init_db import create_first_superuser
        create_first_superuser(db)
        print("Initialized superuser")
except Exception as e:
    print(f"Error initializing database: {e}")
finally:
    db.close()

app = FastAPI(
    title="学术论文辅助平台",
    description="基于FastAPI的学术论文辅助平台后端服务",
    version="1.0.0",
    docs_url=None,  # 禁用默认的 swagger-ui
    redoc_url=None  # 禁用默认的 redoc
)

# 中间件配置

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 本地开发环境
        "http://127.0.0.1:3000",  # 本地IP开发环境
        "http://localhost:5173",  # Vite默认开发环境
        "http://127.0.0.1:5173",  # Vite默认IP开发环境
        "http://192.168.159.155:3000",  # 前端开发环境
        "http://192.168.159.155:8000",  # 后端开发环境
        "http://localhost:8000",  # 后端开发环境
        "http://127.0.0.1:8000",  # 后端开发环境
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 添加用户ID中间件
app.add_middleware(UserIDMiddleware)

# 添加日志中间件
app.add_middleware(LoggingMiddleware)

# 注册API路由
app.include_router(api_router, prefix="/api/v1")

# 初始化MCP适配器
@app.on_event("startup")
async def startup_event():
    if settings.get('mcp.enabled', False):
        try:
            # 异步初始化MCP适配器
            asyncio.create_task(mcp_adapter.initialize())
        except Exception as e:
            print(f"MCP适配器初始化失败: {str(e)}")

@app.get("/")
async def root():
    return {"message": "欢迎使用学术论文辅助平台"}

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
    )