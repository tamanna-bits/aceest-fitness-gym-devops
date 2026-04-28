# ACEest Fitness & Gym API

A simple **Flask-based REST API** for managing gym members.
This project demonstrates a **CI/CD-ready Python service** using **Poetry, Docker, Jenkins, and GitHub Actions** with automated testing.

---

# Project Overview

The API allows:

- Checking service status
- Adding gym members
- Fetching all registered members

Example endpoints:

| Method | Endpoint   | Description          |
| ------ | ---------- | -------------------- |
| GET    | `/`        | Health check         |
| POST   | `/members` | Add a new member     |
| GET    | `/members` | Retrieve all members |

---

# Tech Stack

- Python 3.11
- Flask
- Poetry (Dependency Management)
- Pytest (Testing)
- Docker
- Jenkins (CI pipeline)
- GitHub Actions (CI integration)

---

# Project Structure

```
.
├── app/
│   └── routes.py
├── tests/
│   └── test_api.py
├── Dockerfile
├── Jenkinsfile
├── pyproject.toml
├── poetry.lock
└── README.md
```

---

# Local Setup & Execution

## 1. Clone the Repository

```bash
git@github.com:<user_name>/aceest-fitness-gym-devops.git
cd aceest-fitness-gym-api
```

---

## 2. Install Poetry

Install Poetry if not already installed:

```bash
pip install poetry
```

Verify installation:

```bash
poetry --version
```

---

## 3. Install Dependencies

```bash
poetry config virtualenvs.create false
poetry install
```

---

## 4. Run the Application

```bash
source venv/bin/activate
python main.py
```

Server will start on:

```
http://localhost:5000
```

---

# API Usage Examples

## Check API

```bash
curl http://localhost:5000/
```

Response:

```json
{
  "message": "ACEest Fitness & Gym API Running"
}
```

---

## Add Member

```bash
curl -X POST http://localhost:5000/members \
-H "Content-Type: application/json" \
-d '{
"name": "Alex",
"age": 25,
"membership": "Gold"
}'
```

---

## Get Members

```bash
curl http://localhost:5000/members
```

---

# Running Tests Manually

Tests are written using **Pytest** .

Run tests locally:

```bash
source venv/bin/activate
pytest -v
```

Example output:

```
test_home PASSED
test_add_member PASSED
test_get_members PASSED
```

---

# Running with Docker

## Build Docker Image

```bash
docker build -t aceest-fitness-gym-devops .
```

## Run Container

```bash
docker run -p 5000:5000 aceest-fitness-gym-devops
```

The API will be available at:

```
http://localhost:5000
```

---

# Jenkins CI Pipeline

The repository contains a **Jenkinsfile** that automates the CI process.

## Pipeline Stages

### 1. Checkout

Pulls the latest code from the Git repository.

```
checkout scm
```

---

### 2. Install Dependencies & Run Tests (Docker)

Runs tests inside a **Python 3.11 Docker container** .

Steps:

1. Start Python container
2. Install Poetry
3. Install dependencies
4. Execute tests using Pytest

```
poetry install
poetry run pytest -v
```

This ensures:

- Clean environment
- Consistent builds
- Dependency isolation

---

### 3. Build Docker Image

If tests pass, Jenkins builds the production Docker image:

```
docker build -t aceest-fitness-gym-devops:latest .
```

---

### Jenkins Pipeline Flow

```
Code Push
     │
     ▼
Jenkins Trigger
     │
     ▼
Checkout Repository
     │
     ▼
Install Dependencies
     │
     ▼
Run Tests (Pytest)
     │
     ▼
Build Docker Image
     │
     ▼
Pipeline Success / Failure
```

---

# GitHub Actions Integration (Concept)

A similar CI process can run using **GitHub Actions** .

Typical workflow:

`.github/workflows/ci.yml`

Pipeline logic:

1. Trigger on `push` or `pull_request`
2. Setup Python
3. Install Poetry
4. Install dependencies
5. Run tests
6. Build Docker image

Example steps:

```
- Checkout code
- Setup Python 3.11
- Install Poetry
- poetry install
- pytest
- docker build
```

---

# CI/CD Benefits

This setup provides:

- Automated testing
- Consistent build environment
- Faster feedback for developers
- Dockerized deployment ready for cloud

---

# Future Improvements

- Add database (PostgreSQL / MongoDB)
- Implement authentication
- Add member update & delete endpoints
- Deploy using Kubernetes or AWS ECS
- Add code coverage reporting

---

# Author

Tamanna Bindra BITS_ID (2022us70002)
