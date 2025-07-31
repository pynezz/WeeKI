"""Configuration management for WeeKI."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="WEEKI_"
    )
    
    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    
    # API configuration
    api_title: str = Field(default="WeeKI API", description="API title")
    api_version: str = Field(default="0.1.0", description="API version")
    api_description: str = Field(
        default="AI Agent Orchestration System API",
        description="API description"
    )
    
    # Security
    secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key for session management"
    )
    
    # Database configuration
    database_url: str = Field(
        default="sqlite:///./weeki.db",
        description="Database connection URL"
    )
    
    # Agent configuration
    max_agents: int = Field(default=10, description="Maximum number of concurrent agents")
    agent_timeout: int = Field(default=300, description="Agent timeout in seconds")
    
    # External services
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )


# Global settings instance
settings = Settings()