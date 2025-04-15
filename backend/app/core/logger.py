import logging
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings

# 日志文件路径
# 使用项目根目录下的logs目录
LOG_PATH = Path(__file__).parents[3] / "logs"
LOG_PATH.mkdir(parents=True, exist_ok=True)

# 日志格式
LOG_FORMAT = settings.LOG_FORMAT

# 创建一个拦截器，将标准库日志重定向到loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # 获取对应的 loguru 级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找调用者
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging():
    """配置日志系统"""
    # 移除默认的处理器
    logger.remove()

    # 添加控制台输出
    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level=settings.LOG_LEVEL,
        colorize=True
    )

    # 添加文件输出
    logger.add(
        LOG_PATH / "app.log",
        format=LOG_FORMAT,
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )

    # 添加错误日志
    logger.add(
        LOG_PATH / "error.log",
        format=LOG_FORMAT,
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )

    # 添加LLM调用日志
    logger.add(
        LOG_PATH / "llm.log",
        format=LOG_FORMAT,
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        filter=lambda record: "llm" in record["extra"]
    )

    # 拦截所有标准库日志
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 配置第三方库的日志级别
    for logger_name in ["uvicorn", "uvicorn.error", "fastapi", "litellm"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

def get_logger(name):
    """获取命名日志器"""
    return logger.bind(name=name)

# 创建LLM日志器
def get_llm_logger(name):
    """获取LLM日志器"""
    return logger.bind(name=name, llm=True)