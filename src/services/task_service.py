from typing import Optional
from ..models import Task, TaskCreate, TaskUpdate, TaskStatus, Priority


class TaskService:
    def __init__(self, repository):
        self._repository = repository

    async def create_task(self, task_data: TaskCreate) -> Task:
        task = Task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            status=task_data.status,
        )
        return await self._repository.create(task)

    async def get_task(self, task_id: str) -> Optional[Task]:
        return await self._repository.get(task_id)

    async def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[Priority] = None,
        page: int = 1,
        page_size: int = 50
    ) -> tuple[list[Task], int, int]:
        skip = (page - 1) * page_size
        tasks, total = await self._repository.get_all(
            status=status,
            priority=priority,
            skip=skip,
            limit=page_size
        )
        pages = (total + page_size - 1) // page_size if total > 0 else 1
        return tasks, total, pages

    async def update_task(self, task_id: str, task_data: TaskUpdate) -> Optional[Task]:
        existing = await self._repository.get(task_id)
        if not existing:
            return None
        
        update_data = task_data.dict(exclude_unset=True)
        
        if not update_data:
            return existing
        
        updated_task = Task(
            id=existing.id,
            title=update_data.get("title", existing.title),
            description=update_data.get("description", existing.description),
            priority=update_data.get("priority", existing.priority),
            status=update_data.get("status", existing.status),
            created_at=existing.created_at,
            updated_at=existing.updated_at,
        )
        
        return await self._repository.update(task_id, updated_task)

    async def delete_task(self, task_id: str) -> bool:
        return await self._repository.delete(task_id)

    async def get_stats(self) -> dict:
        return await self._repository.stats()
