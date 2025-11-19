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

## ALWAYS

- ALWAYS use the repository pattern for database interactions to keep routes clean and focused on request handling.
- ALWAYS validate incoming request data using Pydantic models.
- ALWAYS write unit tests for new features and bug fixes.
- ALWAYS use asynchronous programming practices to ensure scalability and performance.
- ALWAYS document new endpoints and significant code changes in this file.
- ALWAYS add filters and pagination to endpoints that return large datasets.
- ALWAYS re read the Supabase documentation when unsure about database operations.
- ALWAYS use the Context7 mcp for fetching documentation of libraries and frameworks.
- ALWAYS follow security best practices, such as sanitizing inputs and using HTTPS.
- ALWAYS use Python 3.13 compatible syntax and libraries.
- ALWAYS fix linting errors and failing tests before continuing.

## NEVER

- NEVER hardcode database queries in route handlers; always use repository methods.
- NEVER ignore error handling; always provide meaningful error messages to clients.
- NEVER expose sensitive information in API responses.
- NEVER forget to update documentation in the code when making changes to the API.

# Example Code Snippets

## Dependency Injection Example

```python
from src.dependencies import get_supabase_client
from supabase import Client
def get_stats_repository(supabase: Client = Depends(get_supabase_client)) -> StatsRepository:
    return StatsRepository(supabase)
```
