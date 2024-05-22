from fastapi import Depends, HTTPException, Query
from fastapi.testclient import TestClient
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import app
from src.models import TaskCreate, TaskUpdate, TaskStatus, Priority

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "uptime_seconds" in data


def test_create_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "priority": "high",
            "status": "pending"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["priority"] == "high"
    assert "id" in data


def test_create_task_validation():
    response = client.post(
        "/tasks",
        json={"title": "", "priority": "high"}
    )
    assert response.status_code == 422


def test_list_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "total" in data
    assert "page" in data


def test_list_tasks_with_filters():
    response = client.get("/tasks?status=pending&priority=high&page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10


def test_get_task_not_found():
    response = client.get("/tasks/non-existent-id")
    assert response.status_code == 404


def test_update_task_not_found():
    response = client.put(
        "/tasks/non-existent-id",
        json={"title": "Updated"}
    )
    assert response.status_code == 404


def test_delete_task_not_found():
    response = client.delete("/tasks/non-existent-id")
    assert response.status_code == 404


def test_task_crud_integration():
    create_response = client.post(
        "/tasks",
        json={
            "title": "Integration Test Task",
            "description": "Testing CRUD operations",
            "priority": "medium"
        }
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    
    update_response = client.put(
        f"/tasks/{task_id}",
        json={"status": "in_progress"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "in_progress"
    
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204
    
    get_deleted = client.get(f"/tasks/{task_id}")
    assert get_deleted.status_code == 404
