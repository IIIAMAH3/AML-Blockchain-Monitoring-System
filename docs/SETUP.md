# Setup Instructions for New Developers

## Prerequisites
- Python 3.12+
- PostgreSQL 16+ (for Windows: https://www.postgresql.org/download/windows/)
- Git

## Windows Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd aml-blockchain-monitoring
```

### 2. Create your local .env file
```bash
copy .env.example .env
```

### 3. Edit .env with YOUR local settings
- Open `.env` with your favorite editor (Notepad, VS Code, etc.)
- Update:
  - `DB_PASSWORD` - Your PostgreSQL password
  - `SECRET_KEY` - Run to generate: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
  - `DEBUG` - Keep as `True` for development

### 4. Create PostgreSQL database

**Option A: Using pgAdmin (GUI)**
1. Open pgAdmin (comes with PostgreSQL installer)
2. Right-click "Databases" → "Create" → "Database"
3. Name: `aml_monitoring`
4. Right-click "Login/Group Roles" → "Create" → "Login/Group Role"
   - Name: `aml_user`
   - Password: (same as `DB_PASSWORD` in `.env`)
5. Right-click user → "Properties" → "Privileges" → Set all to `Yes`

**Option B: Using Command Line**
```bash
# Open Windows Command Prompt or PowerShell
psql -U postgres

# Then run:
CREATE DATABASE aml_monitoring;
CREATE USER aml_user WITH PASSWORD 'your_password_from_.env';
ALTER ROLE aml_user SET client_encoding TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE aml_monitoring TO aml_user;
\q
```

### 5. Run setup script

**Option B: PowerShell**
```powershell
# Allow script execution (first time only):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run:
.\scripts\setup_env.ps1
```

**Option C: Manual Setup**
```bash
# Install dependencies
uv sync

# Run migrations
uv run python manage.py migrate

# Collect static files
uv run python manage.py collectstatic --noinput
```

### 6. Run development server
```bash
uv run python manage.py runserver
```

Visit: http://localhost:8000

## Linux/Mac Setup

### 1-3. Same as Windows (clone, .env, edit)

### 4. Create PostgreSQL database
```bash
sudo -u postgres psql

CREATE DATABASE aml_monitoring;
CREATE USER aml_user WITH PASSWORD 'your_password_from_.env';
ALTER ROLE aml_user SET client_encoding TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE aml_monitoring TO aml_user;
\q
```

### 5. Run setup script
```bash
bash scripts/setup_env.sh
```

### 6. Run development server
```bash
uv run python manage.py runserver
```

## .env Variables Explained

| Variable | Purpose | Example |
|----------|---------|---------|
| DB_PASSWORD | PostgreSQL password | mypassword123 |
| SECRET_KEY | Django secret key | django-insecure-abc... |
| DEBUG | Debug mode | True (dev), False (prod) |
| ALLOWED_HOSTS | Allowed hostnames | localhost,127.0.0.1 |
| DB_HOST | PostgreSQL server | localhost |
| ENVIRONMENT | dev/prod | development |

⚠️ **NEVER commit .env to Git!**

## Troubleshooting

### "psycopg2 connection refused"
- Make sure PostgreSQL service is running
- Check PostgreSQL is listening on 5432
- Verify DB_PASSWORD in .env matches PostgreSQL password

### "ModuleNotFoundError: No module named 'dotenv'"
```bash
uv add python-dotenv
uv sync
```

### "Django secret key not found"
Generate and add to .env:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## After Initial Setup

When pulling new changes:
```bash
git pull
uv sync  # Update dependencies if pyproject.toml changed
uv run python manage.py migrate  # Run any new migrations
```