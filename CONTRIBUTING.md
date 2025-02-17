# contributing
thanks for contributing!

## tech stack
our core tech stack includes:

- gRPC with grpclib for our server framework
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

#### 1. clone the repo:

```bash
git clone https://github.com/gupt-ai/mew.git
cd mew
```

#### 2. create a virtual environment:

```bash
uv venv -p 3.12 --seed
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
SECRET_KEY=secret_key_goes_here
```

(ask @ahhcash or @aatish for the env vars)

### running locally

1. start the gRPC server:

```bash
python server.py
```

2. server will be available on port 50051

### development workflow
#### **code style**
we use ruff for linting and formatting:
```bash
ruff check .
ruff format .
```

#### **type checking**
mypy helps us catch type-related issues early: (we aren't type safe yet 😢)
```bash
mypy .
```

#### **generated code**
proto stubs are generated automatically and shouldn't be committed. run:
```bash
python scripts/gen_proto.py
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
│   ├── core/           # core configuration and utilities
│   ├── models/         # data models and schemas
│   ├── proto/          # protobuf definitions
│   │   ├── health/     # health check proto
│   │   └── user/       # user service proto
│   └── services/       # gRPC service implementations
├── tests/              # test directory (coming soon)
└── scripts/            # utility scripts
```