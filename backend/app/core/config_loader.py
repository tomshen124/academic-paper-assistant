"""
配置加载器，用于加载模块化配置文件
"""

from typing import Dict, Any, Optional
import yaml
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_dir: str = None):
        """初始化配置加载器
        
        Args:
            config_dir: 配置文件目录，默认为项目根目录下的config目录
        """
        # 确定配置目录
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # 默认使用项目根目录下的config目录
            self.config_dir = Path(__file__).parents[3] / "config"
        
        if not self.config_dir.exists():
            raise FileNotFoundError(f"配置目录不存在: {self.config_dir}")
        
        # 环境配置
        self.environment = os.environ.get("ENVIRONMENT", "development")
        
        # 配置数据
        self.config: Dict[str, Any] = {}
        
        # 加载配置
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        # 加载默认配置
        default_config_path = self.config_dir / "default.yaml"
        if not default_config_path.exists():
            raise FileNotFoundError(f"默认配置文件不存在: {default_config_path}")
        
        with open(default_config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 加载环境特定配置
        env_config_path = self.config_dir / f"{self.environment}.yaml"
        if env_config_path.exists():
            with open(env_config_path, 'r', encoding='utf-8') as f:
                env_config = yaml.safe_load(f)
                self._update_dict(self.config, env_config)
        
        # 加载模块配置
        self._load_module_configs()
    
    def _load_module_configs(self):
        """加载模块配置文件"""
        if "modules" not in self.config:
            logger.warning("未找到模块配置路径")
            return
        
        for module_name, module_path in self.config["modules"].items():
            module_config_path = self.config_dir / module_path
            if not module_config_path.exists():
                logger.warning(f"模块配置文件不存在: {module_config_path}")
                continue
            
            with open(module_config_path, 'r', encoding='utf-8') as f:
                module_config = yaml.safe_load(f)
                self._update_dict(self.config, module_config)
    
    def _update_dict(self, d: dict, u: dict) -> dict:
        """递归更新字典"""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._update_dict(d.get(k, {}), v)
            else:
                d[k] = v
        return d
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键，支持点号分隔的路径，如"app.name"
            default: 默认值，当配置不存在时返回
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

# 创建全局配置加载器实例
config_loader = ConfigLoader()
