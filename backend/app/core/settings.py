from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import yaml
from pathlib import Path

class Settings(BaseSettings):
    """应用配置管理"""

    # 基础配置
    CONFIG_PATH: str = Field(
        default="app/core/config/default.yaml",
        description="配置文件路径"
    )
    ENV: str = Field(default="development", description="运行环境")

    # 配置数据
    _config: Dict[str, Any] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        # 加载默认配置
        config_path = Path(self.CONFIG_PATH)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path) as f:
            self._config = yaml.safe_load(f)

        # 加载环境特定配置
        env_config_path = config_path.parent / f"{self.ENV}.yaml"
        if env_config_path.exists():
            with open(env_config_path) as f:
                env_config = yaml.safe_load(f)
                self._config = self._merge_configs(self._config, env_config)

    @staticmethod
    def _merge_configs(base: Dict, override: Dict) -> Dict:
        """递归合并配置"""
        for key, value in override.items():
            if (
                key in base
                and isinstance(base[key], dict)
                and isinstance(value, dict)
            ):
                base[key] = Settings._merge_configs(base[key], value)
            else:
                base[key] = value
        return base

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value or default

    @property
    def app_name(self) -> str:
        return self.get('app.name', '学术论文辅助平台')

    @property
    def debug(self) -> bool:
        return self.get('app.debug', False)

    @property
    def database_url(self) -> str:
        """构建数据库URL"""
        return (
            f"postgresql://{self.get('database.user')}:"
            f"{self.get('database.password')}@"
            f"{self.get('database.host')}/"
            f"{self.get('database.name')}"
        )

    @property
    def cache_config(self) -> Dict[str, Any]:
        return self.get('cache', {})


    @property
    def ai_config(self) -> Dict[str, Any]:
        return self.get('ai', {})

# 全局设置实例
settings = Settings()