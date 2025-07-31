"""Database models and setup for WeeKI."""

import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    create_engine, Column, String, Text, DateTime, Integer, 
    Boolean, JSON, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from .config import settings

Base = declarative_base()


class Task(Base):
    """Task model for persistent storage."""
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True)
    directive = Column(Text, nullable=False)
    context = Column(JSON, default=dict)
    status = Column(String(20), default="pending")
    message = Column(Text, default="")
    result = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    processing_time = Column(Float, nullable=True)
    assigned_agent = Column(String(100), nullable=True)
    

class Agent(Base):
    """Agent model for tracking agent state."""
    __tablename__ = "agents"
    
    id = Column(String(100), primary_key=True)
    type = Column(String(20), nullable=False)  # orchestrator, specialist, utility
    domain = Column(String(50), nullable=True)  # For specialist agents
    specialty = Column(String(50), nullable=True)  # For utility agents
    is_active = Column(Boolean, default=False)
    tasks_processed = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.utcnow)
    

class SystemMetrics(Base):
    """System metrics for monitoring."""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    active_agents = Column(Integer, default=0)
    pending_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    avg_processing_time = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    cpu_usage = Column(Float, nullable=True)


class DatabaseManager:
    """Database connection and session management."""
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        
    def initialize(self):
        """Initialize database connections."""
        # Convert SQLite URL for async if needed
        db_url = settings.database_url
        async_db_url = db_url
        
        if db_url.startswith("sqlite:///"):
            async_db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        
        # Synchronous engine
        self.engine = create_engine(
            db_url,
            echo=settings.debug,
            pool_pre_ping=True
        )
        
        # Asynchronous engine
        self.async_engine = create_async_engine(
            async_db_url,
            echo=settings.debug,
            pool_pre_ping=True
        )
        
        # Session factories
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )
        
        self.AsyncSessionLocal = async_sessionmaker(
            bind=self.async_engine,
            expire_on_commit=False
        )
    
    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(bind=self.engine)
    
    async def create_tables_async(self):
        """Create all tables asynchronously."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    def get_session(self) -> Session:
        """Get a synchronous database session."""
        return self.SessionLocal()
    
    def get_async_session(self):
        """Get an asynchronous database session."""
        return self.AsyncSessionLocal()
    
    async def close(self):
        """Close database connections."""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()