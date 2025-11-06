# Database Connection Error Fix

## Error: "SSL connection has been closed unexpectedly"

This error occurs when PostgreSQL connections are lost or timeout. Here's how to fix it:

### ✅ Solution 1: Update Database Session (DONE)

The `backend/app/db/session.py` has been updated with:

-   `pool_pre_ping=True` - Verifies connections before use
-   `pool_recycle=300` - Recycles connections every 5 minutes
-   Connection pool settings to manage connections better

### ✅ Solution 2: Update DATABASE_URL

Check your `backend/.env` file and update the DATABASE_URL:

#### Option A: Disable SSL (for local development)

```env
DATABASE_URL=postgresql://postgres:your_password@localhost/invoice_db?sslmode=disable
```

#### Option B: Use proper SSL mode

```env
DATABASE_URL=postgresql://postgres:your_password@localhost/invoice_db?sslmode=prefer
```

#### Option C: If using cloud database (like Neon, Supabase, etc.)

```env
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
```

### 🔄 After Updating

1. **Stop the backend server** (Ctrl+C)
2. **Restart the backend**:
    ```powershell
    cd backend
    .\venv\Scripts\activate
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    ```

### 🧪 Test the Connection

Try logging in again. If you still get errors:

#### Check PostgreSQL is Running

```powershell
# Check if PostgreSQL service is running
Get-Service -Name postgresql*
```

#### Test Database Connection

```powershell
# Test connection manually
cd backend
.\venv\Scripts\activate
python -c "from app.db.session import engine; engine.connect(); print('✓ Database connected!')"
```

### 🔍 Other Possible Issues

#### Issue 1: PostgreSQL Not Running

**Solution**: Start PostgreSQL service

```powershell
# Start PostgreSQL service (run as Administrator)
Start-Service postgresql-x64-15  # Replace with your version
```

#### Issue 2: Wrong Database Credentials

**Solution**: Verify your `.env` file has correct:

-   Username
-   Password
-   Database name
-   Host (usually `localhost`)
-   Port (usually `5432`)

#### Issue 3: Database Doesn't Exist

**Solution**: Create the database

```sql
-- Connect to PostgreSQL and run:
CREATE DATABASE invoice_db;
```

Then run migrations:

```powershell
cd backend
alembic upgrade head
```

### 📝 Quick Fix Script

Create this file as `backend/test_db.py`:

```python
from app.db.session import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✓ Database connection successful!")
        print(f"✓ Result: {result.fetchone()}")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
```

Run it:

```powershell
cd backend
python test_db.py
```

### 🎯 Recommended DATABASE_URL Format

For local PostgreSQL (most common):

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/invoice_db?sslmode=disable
```

Replace:

-   `postgres` - your PostgreSQL username
-   `your_password` - your PostgreSQL password
-   `invoice_db` - your database name
-   `5432` - PostgreSQL port (default)

### ⚠️ Still Having Issues?

1. **Check PostgreSQL logs**:
    - Windows: `C:\Program Files\PostgreSQL\15\data\log\`
2. **Verify user has permissions**:

    ```sql
    GRANT ALL PRIVILEGES ON DATABASE invoice_db TO postgres;
    ```

3. **Try using SQLite instead** (temporary for testing):

    ```env
    # In backend/.env
    DATABASE_URL=sqlite:///./test.db
    ```

    Then update `backend/app/db/session.py`:

    ```python
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
        pool_pre_ping=True,
        pool_recycle=300,
    )
    ```

### 🆘 Last Resort

If nothing works, let me know:

1. Your PostgreSQL version
2. Where PostgreSQL is installed (local/cloud)
3. The exact DATABASE_URL you're using (hide password)
4. PostgreSQL service status
