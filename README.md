# Glenigan's Technical Test

The technical test is to provide an API endpoint from a given SQLite database. In this case, I've chosen to use Flask and SQLAlchemy.

The reason for choosing Flask is that it's a lightweight and minimalistic framework that makes it a perfect match for this kind of task. Whilst for SQLAlchemy, it's basically the de facto standard for interacting with SQL databases with Python.

The database is an SQLite database, and the database file is provided in the `glenigan.db` file. The database is placed in the project root directory.

## Prerequisites

- Python (3.13.5+)
- pip (25.1.1+)
- Docker (optional)

## How to Run

### With Docker

```bash
docker compose up
```

### Without Docker

```bash
# 1. Create a virtual environment (most recommended way to run a Python application locally)
python3 -m venv venv
source venv/bin/activate

# 2. Install the dependencies
pip install -r requirements.txt

# 3. Start the Rest API locally
python run.py
```

The API will be available at `http://localhost:5000`.

## Running Tests

```bash
# With Docker
docker compose run --rm test

# Without Docker
python -m pytest tests/ -v
```

## API Reference

### `GET /projects`

Returns paginated projects for a given area, sorted by value (highest first), then alphabetically by name.

| Parameter  | Type    | Required | Default | Description                 |
|------------|---------|----------|---------|-----------------------------|
| `area`     | string  | ✅       | —       | Area to filter projects by  |
| `page`     | integer | ❌       | 1       | Page number (1-based)       |
| `per_page` | integer | ❌       | 10      | Results per page            |

### Example Requests

```bash
# Basic request with defaults
curl "http://localhost:5000/projects?area=Manchester"

# Custom pagination
curl "http://localhost:5000/projects?area=Manchester&page=2&per_page=5"
```

### Example Response

```json
{
  "area": "Manchester",
  "page": 1,
  "per_page": 10,
  "total": 123,
  "projects": [
    {
      "project_name": "Manchester Bridge Phase 2",
      "project_start": "2025-05-16 00:00:00",
      "project_end": "2026-02-28 00:00:00",
      "company": "NorthBuild Ltd",
      "description": "Major road expansion project in Manchester focusing on civil and structural work.",
      "project_value": 4832115
    }
  ]
}
```

### Error Responses

| Status | Scenario                                    |
|--------|---------------------------------------------|
| 400    | Missing `area` parameter                    |
| 400    | Invalid `page` or `per_page` (non-numeric, zero, negative) |
| 404    | No projects found for the given area        |
| 500    | Database / internal server error            |

All errors return JSON: `{"error": "description"}`.

## Assumptions
- `description` defaults to an empty string when `NULL` in the database.
- A project may appear in multiple areas; the query filters to the requested area only.

## Tradeoffs & Limitations

- **No caching**: Caching this kind of request can save the database from being hit on every request, whilst also fastening the response time. A caching layer (e.g. Redis) could be added for real use-cases.
- **SQLite**: SQLite is suitable for this case but would not scale to high-concurrency production workloads. Swapping to PostgreSQL/MySQL will definitely be required for actual production use-cases.