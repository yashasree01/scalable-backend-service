import pytest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services import TaskRepository, TaskService
from src.models import Task, TaskCreate, TaskUpdate, TaskStatus, Priority


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def repository():
    return TaskRepository()


@pytest.fixture
async def service(repository):
    return TaskService(repository)


@pytest.mark.asyncio
async def test_create_task(service):
    task_data = TaskCreate(
        title="Test Task",
        description="Test Description",
        priority=Priority.HIGH
    )
    task = await service.create_task(task_data)
    
    assert task.title == "Test Task"
    assert task.priority == Priority.HIGH
    assert task.id is not None


@pytest.mark.asyncio
async def test_get_task(service):
    task_data = TaskCreate(title="Get Test", priority=Priority.MEDIUM)
    created = await service.create_task(task_data)
    
    retrieved = await service.get_task(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.title == "Get Test"


@pytest.mark.asyncio
async def test_list_tasks_pagination(service):
    for i in range(10):
        await service.create_task(TaskCreate(title=f"Task {i}"))
    
    tasks, total, pages = await service.list_tasks(page=1, page_size=5)
    
    assert len(tasks) == 5
    assert total == 10
    assert pages == 2


@pytest.mark.asyncio
async def test_filter_tasks_by_status(service):
    await service.create_task(TaskCreate(title="Task 1", status=TaskStatus.PENDING))
    await service.create_task(TaskCreate(title="Task 2", status=TaskStatus.COMPLETED))
    await service.create_task(TaskCreate(title="Task 3", status=TaskStatus.PENDING))
    
    tasks, total, _ = await service.list_tasks(status=TaskStatus.PENDING)
    
    assert total == 2
    assert all(t.status == TaskStatus.PENDING for t in tasks)


@pytest.mark.asyncio
async def test_update_task(service):
    created = await service.create_task(TaskCreate(title="Original"))
    
    updated = await service.update_task(
        created.id,
        TaskUpdate(title="Updated", status=TaskStatus.COMPLETED)
    )
    
    assert updated is not None
    assert updated.title == "Updated"
    assert updated.status == TaskStatus.COMPLETED
    assert updated.updated_at > created.updated_at


@pytest.mark.asyncio
async def test_delete_task(service):
    created = await service.create_task(TaskCreate(title="To Delete"))
    deleted = await service.delete_task(created.id)
    
    assert deleted is True
    
    retrieved = await service.get_task(created.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_get_stats(service):
    await service.create_task(TaskCreate(title="Task 1", priority=Priority.HIGH))
    await service.create_task(TaskCreate(title="Task 2", priority=Priority.LOW))
    await service.create_task(TaskCreate(title="Task 3", priority=Priority.HIGH))
    
    stats = await service.get_stats()
    
    assert stats["total"] == 3
    assert stats["by_priority"]["high"] == 2
    assert stats["by_priority"]["low"] == 1
