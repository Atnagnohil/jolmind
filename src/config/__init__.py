from src.config.loader import AppConfig, load_config

config: AppConfig = load_config()

__all__ = ["config", "AppConfig", "load_config"]
