from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from app.api.v1 import api_router
from app.services.mcp_adapter import mcp_adapter
from app.core.config import settings
from app.core.logger import setup_logging
from app.db.session import SessionLocal
from app.db.init_db import init_db
import asyncio

# 初始化日志
setup_logging()

# 初始化数据库
db = SessionLocal()
try:
    init_db(db)
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

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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