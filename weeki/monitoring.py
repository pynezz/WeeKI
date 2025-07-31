"""Monitoring and metrics collection for WeeKI."""

import asyncio
import logging
import psutil
from datetime import datetime
from typing import Dict, Any, Optional

from .database import db_manager, SystemMetrics, Task, Agent


class SystemMonitor:
    """System monitoring and metrics collection."""
    
    def __init__(self):
        self.logger = logging.getLogger("monitor")
        self._monitoring_task: Optional[asyncio.Task] = None
        self._stop_monitoring = False
    
    async def start_monitoring(self, interval: int = 60):
        """Start system monitoring."""
        self.logger.info(f"Starting system monitoring with {interval}s interval")
        self._stop_monitoring = False
        self._monitoring_task = asyncio.create_task(self._monitor_loop(interval))
    
    async def stop_monitoring(self):
        """Stop system monitoring."""
        self.logger.info("Stopping system monitoring")
        self._stop_monitoring = True
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_loop(self, interval: int):
        """Main monitoring loop."""
        while not self._stop_monitoring:
            try:
                await self._collect_metrics()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_metrics(self):
        """Collect and store system metrics."""
        try:
            async with db_manager.get_async_session() as session:
                # Get task statistics
                from sqlalchemy import select, func, and_
                
                # Count tasks by status
                pending_count = await session.scalar(
                    select(func.count(Task.id)).where(Task.status == "pending")
                ) or 0
                
                completed_count = await session.scalar(
                    select(func.count(Task.id)).where(Task.status == "completed")
                ) or 0
                
                failed_count = await session.scalar(
                    select(func.count(Task.id)).where(Task.status == "failed")
                ) or 0
                
                # Get active agents count
                active_agents = await session.scalar(
                    select(func.count(Agent.id)).where(Agent.is_active == True)
                ) or 0
                
                # Calculate average processing time for completed tasks in last hour
                one_hour_ago = datetime.utcnow().replace(microsecond=0)
                one_hour_ago = one_hour_ago.replace(
                    hour=one_hour_ago.hour - 1 if one_hour_ago.hour > 0 else 23
                )
                
                avg_processing_time = await session.scalar(
                    select(func.avg(Task.processing_time)).where(
                        and_(
                            Task.status == "completed",
                            Task.completed_at >= one_hour_ago
                        )
                    )
                )
                
                # Get system resource usage
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # Create metrics record
                metrics = SystemMetrics(
                    active_agents=active_agents,
                    pending_tasks=pending_count,
                    completed_tasks=completed_count,
                    failed_tasks=failed_count,
                    avg_processing_time=float(avg_processing_time) if avg_processing_time else None,
                    memory_usage=memory_percent,
                    cpu_usage=cpu_percent
                )
                
                session.add(metrics)
                await session.commit()
                
                self.logger.debug(f"Collected metrics: agents={active_agents}, "
                                f"pending={pending_count}, completed={completed_count}, "
                                f"failed={failed_count}, cpu={cpu_percent}%, "
                                f"memory={memory_percent}%")
                
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        try:
            async with db_manager.get_async_session() as session:
                from sqlalchemy import select, func, desc
                
                # Get latest metrics
                latest_metrics = await session.scalar(
                    select(SystemMetrics).order_by(desc(SystemMetrics.timestamp)).limit(1)
                )
                
                # Get task counts
                total_tasks = await session.scalar(select(func.count(Task.id))) or 0
                pending_tasks = await session.scalar(
                    select(func.count(Task.id)).where(Task.status == "pending")
                ) or 0
                active_agents = await session.scalar(
                    select(func.count(Agent.id)).where(Agent.is_active == True)
                ) or 0
                
                # System resources
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                status = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "system": {
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_available_gb": round(memory.available / (1024**3), 2),
                        "disk_percent": disk.percent,
                        "disk_free_gb": round(disk.free / (1024**3), 2)
                    },
                    "agents": {
                        "active": active_agents,
                        "total_registered": await session.scalar(select(func.count(Agent.id))) or 0
                    },
                    "tasks": {
                        "total": total_tasks,
                        "pending": pending_tasks,
                        "completed": await session.scalar(
                            select(func.count(Task.id)).where(Task.status == "completed")
                        ) or 0,
                        "failed": await session.scalar(
                            select(func.count(Task.id)).where(Task.status == "failed")
                        ) or 0
                    }
                }
                
                if latest_metrics:
                    status["metrics"] = {
                        "last_updated": latest_metrics.timestamp.isoformat(),
                        "avg_processing_time": latest_metrics.avg_processing_time
                    }
                
                return status
                
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global monitor instance
system_monitor = SystemMonitor()