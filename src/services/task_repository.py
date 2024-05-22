from typing import List, Optional, AsyncIterator
from datetime import datetime
import asyncio
from collections import defaultdict

from ..models import Task, TaskStatus, Priority


class TaskRepository:
    def __init__(self):
        self._storage: dict[str, Task] = {}
        self._lock = asyncio.Lock()
        self._counter = 0

    async def create(self, task: Task) -> Task:
        async with self._lock:
            self._storage[task.id] = task
            self._counter += 1
        return task

    async def get(self, task_id: str) -> Optional[Task]:
        return self._storage.get(task_id)

    async def get_all(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[Priority] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[Task], int]:
        async with self._lock:
            filtered = list(self._storage.values())
            
            if status:
                filtered = [t for t in filtered if t.status == status]
            if priority:
                filtered = [t for t in filtered if t.priority == priority]
            
            total = len(filtered)
            filtered.sort(key=lambda x: x.created_at, reverse=True)
            tasks = filtered[skip:skip + limit]
        
        return tasks, total

    async def update(self, task_id: str, task: Task) -> Optional[Task]:
        async with self._lock:
            if task_id not in self._storage:
                return None
            task.updated_at = datetime.utcnow()
            self._storage[task_id] = task
        return task

    async def delete(self, task_id: str) -> bool:
        async with self._lock:
            if task_id not in self._storage:
                return False
            del self._storage[task_id]
            return True

    async def count(self) -> int:
        async with self._lock:
            return self._counter

    async def stats(self) -> dict:
        async with self._lock:
            status_counts = defaultdict(int)
            priority_counts = defaultdict(int)
            
            for task in self._storage.values():
                status_counts[task.status] += 1
                priority_counts[task.priority] += 1
            
            return {
                "total": len(self._storage),
                "by_status": dict(status_counts),
                "by_priority": dict(priority_counts)
            }
