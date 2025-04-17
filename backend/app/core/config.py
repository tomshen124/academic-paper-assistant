from typing import Dict, Any, Optional, List, Union
from pydantic import AnyHttpUrl, Field, ConfigDict
from pydantic_settings import BaseSettings
import yaml
import os
from pathlib import Path

class Settings(BaseSettings):
    # 项目基础配置
    _PROJECT_NAME: str = "学术论文辅助平台"  # 私有属性，使用属性方法获取
    API_V1_STR: str = "/api/v1"

    # 环境配置
    ENVIRONMENT: str = Field(default="development", description="运行环境")

    # YAML配置
    config: Dict[str, Any] = Field(default_factory=dict, description="YAML配置")

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # 可选配置（从.env加载，有默认值）
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="访问令牌过期时间（分钟）")

    # LLM 配置
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API密钥")
    OPENAI_API_BASE: Optional[str] = Field(None, description="OpenAI API基础URL")
    ANTHROPIC_API_KEY: Optional[str] = Field(None, description="Anthropic API密钥")
    DEEPSEEK_API_KEY: Optional[str] = Field(None, description="DeepSeek API密钥")
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEFAULT_MODEL: str = "gpt-3.5-turbo"

    # LiteLLM配置
    LITELLM_CACHE_ENABLE: bool = True
    LITELLM_CACHE_FOLDER: str = ".cache/litellm"

    # LLM 参数配置
    LLM_MAX_TOKENS: int = 2000
    LLM_TEMPERATURE: float = 0.3
    LLM_TOP_P: float = 0.9
    LLM_FREQUENCY_PENALTY: float = 0.0
    LLM_PRESENCE_PENALTY: float = 0.0

    # Token预算配置
    MAX_TOKENS_PER_REQUEST: int = 4000
    TOKEN_BUDGET_PER_PROJECT: int = 100000

    # 学术API配置
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = Field(None, description="Semantic Scholar API密钥")

    # 文本处理配置
    TEXT_MIN_LENGTH: int = 10  # 最小文本长度
    TEXT_MAX_LENGTH: int = 10000  # 最大文本长度
    TEXT_CHUNK_SIZE: int = 2000  # 文本分块大小
    TEXT_OVERLAP_SIZE: int = 200  # 文本块重叠大小

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    # 缓存配置
    CACHE_EXPIRATION: int = 3600  # 1小时

    # 异步任务配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    model_config = ConfigDict(
        case_sensitive=True,
        env_file=str(Path(__file__).parents[3] / "config" / ".env"),
        env_file_encoding="utf-8",
        extra="allow"  # 允许额外字段
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_yaml_config()

    def load_yaml_config(self):
        """加载YAML配置文件"""
        # 使用项目根目录下的config目录
        config_dir = Path(__file__).parents[3] / "config"

        # 加载默认配置
        default_config_path = config_dir / "default.yaml"
        if default_config_path.exists():
            with open(default_config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            raise FileNotFoundError(f"默认配置文件不存在: {default_config_path}")

        # 加载环境特定配置（如果存在）
        env = self.ENVIRONMENT
        env_config_path = config_dir / f"{env}.yaml"
        if env_config_path.exists():
            with open(env_config_path, 'r', encoding='utf-8') as f:
                env_config = yaml.safe_load(f)
                # 递归更新配置
                self._update_dict(self.config, env_config)

    def _update_dict(self, d: dict, u: dict) -> dict:
        """递归更新字典"""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._update_dict(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    @property
    def DEBUG(self) -> bool:
        return self.config.get("app", {}).get("debug", True)

    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        return self.config.get("cors", {}).get("allow_origins", ["*"])

    @property
    def PROJECT_NAME(self) -> str:
        return self.config.get("app", {}).get("name", "学术论文辅助平台")

    @property
    def DATABASE_USER(self) -> str:
        return os.environ.get("DATABASE_USER", "postgres")

    @property
    def DATABASE_PASSWORD(self) -> str:
        return os.environ.get("DATABASE_PASSWORD", "postgres")

    @property
    def DATABASE_HOST(self) -> str:
        return os.environ.get("DATABASE_HOST", "localhost")

    @property
    def DATABASE_PORT(self) -> str:
        return os.environ.get("DATABASE_PORT", "5432")

    @property
    def DATABASE_NAME(self) -> str:
        return os.environ.get("DATABASE_NAME", "academic_paper_assistant")

    @property
    def DATABASE_URL(self) -> str:
        """构建数据库URL"""
        return (
            f"postgresql://{self.DATABASE_USER}:"
            f"{self.DATABASE_PASSWORD}@"
            f"{self.DATABASE_HOST}:"
            f"{self.DATABASE_PORT}/"
            f"{self.DATABASE_NAME}"
        )

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，类似于字典的get方法"""
        # 先尝试从对象属性中获取
        if hasattr(self, key):
            return getattr(self, key)
        # 然后从配置字典中获取
        return self.config.get(key, default)

# 创建全局设置对象
settings = Settings()