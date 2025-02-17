# contributing
thanks for contributing!

## tech stack
our core tech stack includes:

- FastAPI for the API framework
- uv for dependency management
- PostgreSQL + PGVector for our database (via Supabase)
- Prefect for workflow orchestration
- Python 3.12+

## development setup
### prerequisites

- Python 3.12 or higher
- env vars for supabase
- [uv](https://github.com/astral-sh/uv) for dependency management

### first-time setup

#### 1 .clone the repo:

```bash
git clone https://github.com/gupt-ai/mew.git
cd mew
```

#### 2. create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows use: `.venv\Scripts\activate`
```

#### 3. install dependencies with uv:

```bash
uv pip install -e ".[dev]"
```

#### 4. set up your environment variables:

fill in your .env with:
```bash
# Database
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mew
```

(ask @ahhcash or @aatish for the env vars)


### running locally

1. start the dev server:

```bash
uvicorn server:app --reload --port 8080
```
or via

```bash
python server.py
```

2. api will be available at http://localhost:8080
3. check http://localhost:8080/docs for the interactive API documentation

### development workflow
#### **code style**
we use ruff for linting and formatting:
```bash
ruff check .
ruff format .
```

#### **type checking**
mypy helps us catch type-related issues early:
```bash
mypy .
```

#### **branch strategy**

1. create a branch for your feature/fix
2. make your changes
3. ensure all checks pass
4. submit a PR

### project structure
```bash
mew/
├── app/                 # main application code
│   ├── api/            # API routes and endpoints
│   │   └── routes/     # route handlers
│   ├── core/           # core configuration and utilities
│   ├── models/         # data models and schemas
│   └── services/       # business logic
├── tests/              # test directory (coming soon)
└── scripts/            # utility scripts
```
