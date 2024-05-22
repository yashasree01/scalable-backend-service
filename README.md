# Scalable Backend Service

High-concurrency backend service with optimized database queries and efficient request handling.

## Structure

```
src/
├── api/           # API routes
├── models/        # Pydantic models
├── services/      # Business logic
└── utils/         # Utilities
tests/
└── ...
```

## Quick Start

```bash
pip install -r requirements.txt
uvicorn src.main:app --workers 4
```

## Features

- Async request handling
- Database connection pooling
- Rate limiting
- Comprehensive error handling
- Input validation
