from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional

from ..models import (
    Task,
    TaskCreate,
    TaskUpdate,
    TaskListResponse,
    TaskStatus,
    Priority,
    ErrorResponse,
)
from ..services import TaskService, TaskRepository


router = APIRouter(prefix="/tasks", tags=["tasks"])

task_repository = TaskRepository()
task_service = TaskService(task_repository)


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate):
    return await task_service.create_task(task_data)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[Priority] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    tasks, total, pages = await task_service.list_tasks(
        status=status,
        priority=priority,
        page=page,
        page_size=page_size
    )
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str):
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: str, task_data: TaskUpdate):
    task = await task_service.update_task(task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    deleted = await task_service.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")


@router.get("/stats/overview")
async def get_task_stats():
    return await task_service.get_stats()
