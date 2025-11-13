# Kingshot Hero API developer instructions

Welcome to the Kingshot Hero API developer instructions! This document provides guidelines and best practices for developers working with the Kingshot Hero API.

# Project Context

The Kingshot Hero API is a FastAPI-based application that interacts with a Supabase database to manage and retrieve data related to heroes, skills, expeditions, and exclusive gear. The API is designed to provide efficient and reliable access to this data for various clients. It is structured with clear separation of concerns, utilizing repositories for database interactions and schemas for data validation and serialization.

- FastAPI used for building the API and serving endpoints.
- Supabase as the backend database for storing hero-related data.
- Pydantic schemas for data validation and serialization.

# Coding Standards

- Follow PEP 8 guidelines for Python code style.
- Use type hints for function signatures to improve code readability and maintainability.
- Write clear and concise docstrings for all functions and classes.
- Ensure proper error handling using FastAPI's HTTPException for client errors.
- Use dependency injection for managing database connections and other shared resources.
- `uv` is used as package manager and task runner.

# Repository Structure

- `src/routes/`: Contains FastAPI route definitions for various endpoints.
- `src/db/repositories/`: Contains repository classes for database interactions.
- `src/schemas/`: Contains Pydantic models for request and response data structures.
- `src/dependencies.py`: Contains dependency injection functions for shared resources like the Supabase client.

# Do and Don'ts

## Do

- Do use the repository pattern for database interactions to keep routes clean and focused on request handling.
- Do validate incoming request data using Pydantic models.
- Do write unit tests for new features and bug fixes.
- Do use asynchronous programming practices to ensure scalability and performance.
- Do document new endpoints and significant code changes in this file.
- Do add filters and pagination to endpoints that return large datasets.
- Do re read the Supabase documentation when unsure about database operations.
- Do use the Context7 mcp for fetching documentation of libraries and frameworks.

## Don't

- Don't hardcode database queries in route handlers; always use repository methods.
- Don't ignore error handling; always provide meaningful error messages to clients.
- Don't expose sensitive information in API responses.
- Don't forget to update documentation when making changes to the API.

# Example Code Snippets

## Dependency Injection Example

```python
from src.dependencies import get_supabase_client
from supabase import Client
def get_stats_repository(supabase: Client = Depends(get_supabase_client)) -> StatsRepository:
    return StatsRepository(supabase)
```
