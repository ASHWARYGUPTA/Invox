# Invox Backend2 Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER BROWSER                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │               Next.js Frontend (Port 3000)                   │ │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────────────────┐ │ │
│  │  │   Pages    │  │ Components  │  │   API Utils          │ │ │
│  │  │            │  │             │  │  - backendFetch()    │ │ │
│  │  │ - signin   │  │ - NavBar    │  │  - getCurrentUser()  │ │ │
│  │  │ - dashboard│  │ - Sidebar   │  │  - updateProfile()   │ │ │
│  │  └────────────┘  └─────────────┘  └──────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────────┘ │
└───────────────────────┬───────────────────────┬─────────────────────┘
                        │                       │
                        │ OAuth Flow            │ API Calls
                        │                       │ (JWT Token)
                        ▼                       ▼
        ┌───────────────────────┐   ┌─────────────────────────────┐
        │      NextAuth         │   │   FastAPI Backend           │
        │   (Port 3000/api)     │   │     (Port 8001)             │
        │                       │   │                             │
        │  ┌─────────────────┐  │   │  ┌───────────────────────┐ │
        │  │   Callbacks     │◄─┼───┼─►│   API Endpoints        │ │
        │  │                 │  │   │  │                        │ │
        │  │ - signIn()      │  │   │  │ /auth/oauth/callback  │ │
        │  │ - jwt()         │  │   │  │ /auth/verify-email    │ │
        │  │ - session()     │  │   │  │ /users/me             │ │
        │  └─────────────────┘  │   │  └───────────────────────┘ │
        └───────┬───────────────┘   └─────────┬───────────────────┘
                │                             │
                │ OAuth Redirect              │ Database Queries
                │                             │
                ▼                             ▼
    ┌───────────────────────┐     ┌─────────────────────────────────┐
    │   Google OAuth        │     │      PostgreSQL Database        │
    │                       │     │         (Port 5432)             │
    │  - Client ID          │     │                                 │
    │  - Client Secret      │     │  ┌───────────────────────────┐ │
    │  - User Profile       │     │  │   Tables                  │ │
    │  - Access Tokens      │     │  │                           │ │
    └───────────────────────┘     │  │  - users                  │ │
                                  │  │  - accounts               │ │
                                  │  │  - sessions               │ │
                                  │  │  - verification_tokens    │ │
                                  │  └───────────────────────────┘ │
                                  └─────────────────────────────────┘
```

## Authentication Flow Diagram

```
┌─────────┐                                                         ┌─────────┐
│         │                                                         │         │
│  USER   │                                                         │ GOOGLE  │
│         │                                                         │  OAUTH  │
└────┬────┘                                                         └────┬────┘
     │                                                                   │
     │ 1. Click "Sign in with Google"                                   │
     │────────────────────────────►┌──────────────┐                     │
     │                             │   NextAuth   │                     │
     │                             │              │                     │
     │                             │ 2. Redirect  │                     │
     │                             │    to Google ├────────────────────►│
     │                             └──────────────┘                     │
     │                                                                   │
     │                                                    3. Authenticate│
     │                                                       & Authorize │
     │                                                                   │
     │                             ┌──────────────┐                     │
     │                             │   NextAuth   │◄────────────────────┤
     │                             │              │ 4. Return with      │
     │                             │              │    OAuth tokens     │
     │                             └──────┬───────┘                     │
     │                                    │                             │
     │                                    │ 5. signIn callback          │
     │                                    │    triggers                 │
     │                                    ▼                             │
     │                             ┌──────────────┐                     │
     │                             │   FastAPI    │                     │
     │                             │   Backend    │                     │
     │                             │              │                     │
     │                             │ POST /oauth/ │                     │
     │                             │    callback  │                     │
     │                             │              │                     │
     │                             │ 6. Create/   │                     │
     │                             │    Update    │                     │
     │                             │    User      │                     │
     │                             │              │                     │
     │                             └──────┬───────┘                     │
     │                                    │                             │
     │                                    │ 7. Return JWT               │
     │                                    ▼                             │
     │                             ┌──────────────┐                     │
     │                             │  PostgreSQL  │                     │
     │                             │              │                     │
     │                             │  [User Data] │                     │
     │                             │              │                     │
     │                             └──────────────┘                     │
     │                                                                   │
     │ 8. Session with JWT token                                        │
     │◄────────────────────────────────                                 │
     │                                                                   │
     │ 9. Make API calls with JWT                                       │
     │─────────────────────────────────►┌──────────────┐               │
     │                                   │   FastAPI    │               │
     │                                   │   Backend    │               │
     │                                   │              │               │
     │                                   │ Verify JWT   │               │
     │ 10. Return data                   │ & Process    │               │
     │◄──────────────────────────────────┤              │               │
     │                                   └──────────────┘               │
     │                                                                   │
```

## Request Flow for Protected Endpoint

```
┌─────────────────┐
│  Frontend Page  │
│  (Dashboard)    │
└────────┬────────┘
         │
         │ 1. User visits dashboard
         │
         ▼
┌─────────────────────────────┐
│  getSession()               │
│  - Get NextAuth session     │
│  - Extract backendToken     │
└────────┬────────────────────┘
         │
         │ 2. Call backend API
         │    with JWT token
         │
         ▼
┌─────────────────────────────┐
│  backendFetch('/users/me')  │
│  Headers:                   │
│  Authorization: Bearer JWT  │
└────────┬────────────────────┘
         │
         │ 3. HTTP Request
         │
         ▼
┌─────────────────────────────┐
│  FastAPI Backend            │
│  Endpoint: GET /users/me    │
└────────┬────────────────────┘
         │
         │ 4. Extract token from header
         │
         ▼
┌─────────────────────────────┐
│  Dependency: get_current_   │
│             user()          │
│  - Verify JWT signature     │
│  - Extract user_id          │
│  - Query database           │
└────────┬────────────────────┘
         │
         │ 5. Database query
         │
         ▼
┌─────────────────────────────┐
│  PostgreSQL                 │
│  SELECT * FROM users        │
│  WHERE id = ?               │
└────────┬────────────────────┘
         │
         │ 6. Return user data
         │
         ▼
┌─────────────────────────────┐
│  FastAPI Endpoint           │
│  Return JSON response       │
└────────┬────────────────────┘
         │
         │ 7. HTTP Response
         │
         ▼
┌─────────────────────────────┐
│  Frontend                   │
│  - Receive user data        │
│  - Update UI                │
└─────────────────────────────┘
```

## Database Schema Relationships

```
┌─────────────────────────────────────┐
│             users                   │
│─────────────────────────────────────│
│ id (PK)               VARCHAR       │
│ name                  VARCHAR       │
│ email                 VARCHAR UNIQUE│
│ email_verified        TIMESTAMP     │
│ image                 VARCHAR       │
│ created_at            TIMESTAMP     │
│ updated_at            TIMESTAMP     │
└──────────────┬──────────────────────┘
               │
               │ 1:N
               │
      ┌────────┴────────────┐
      │                     │
      ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│    accounts     │   │    sessions     │
│─────────────────│   │─────────────────│
│ id (PK)         │   │ id (PK)         │
│ user_id (FK) ───┤   │ user_id (FK) ───┤
│ type            │   │ session_token   │
│ provider        │   │ expires         │
│ provider_acc_id │   │ created_at      │
│ access_token    │   │ updated_at      │
│ refresh_token   │   └─────────────────┘
│ expires_at      │
│ token_type      │
│ scope           │
│ id_token        │
│ session_state   │
│ created_at      │
│ updated_at      │
└─────────────────┘

┌──────────────────────────────┐
│    verification_tokens       │
│──────────────────────────────│
│ identifier (PK)              │
│ token (PK)                   │
│ expires                      │
└──────────────────────────────┘
```

## Module Dependencies

```
app/
│
├── main.py
│   ├─► core/config.py
│   ├─► db/session.py
│   └─► api/v1/api.py
│
├── api/
│   ├── deps.py
│   │   ├─► core/security.py
│   │   ├─► db/session.py
│   │   ├─► models/user.py
│   │   └─► services/auth.py
│   │
│   └── v1/
│       ├── api.py
│       │   └─► endpoints/*
│       │
│       └── endpoints/
│           ├── auth.py
│           │   ├─► db/session.py
│           │   ├─► services/auth.py
│           │   ├─► core/security.py
│           │   └─► schemas/user.py
│           │
│           └── users.py
│               ├─► api/deps.py
│               ├─► db/session.py
│               ├─► services/auth.py
│               ├─► schemas/user.py
│               └─► models/user.py
│
├── core/
│   ├── config.py
│   │   └─► pydantic_settings
│   │
│   └── security.py
│       ├─► jose (JWT)
│       ├─► passlib (bcrypt)
│       └─► core/config.py
│
├── db/
│   ├── base.py
│   │   ├─► sqlalchemy
│   │   └─► models/user.py
│   │
│   └── session.py
│       ├─► sqlalchemy
│       └─► core/config.py
│
├── models/
│   └── user.py
│       ├─► sqlalchemy
│       └─► db/base.py
│
├── schemas/
│   └── user.py
│       └─► pydantic
│
└── services/
    └── auth.py
        ├─► sqlalchemy
        ├─► models/user.py
        └─► schemas/user.py
```

## Technology Stack

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                         │
│  ┌───────────────────────────────────────────────┐  │
│  │  Next.js 14  │  React 18  │  TypeScript       │  │
│  ├───────────────────────────────────────────────┤  │
│  │  NextAuth.js │  TailwindCSS │  Shadcn/ui     │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                         │
                         │ HTTP/REST
                         │
┌─────────────────────────────────────────────────────┐
│                    BACKEND                          │
│  ┌───────────────────────────────────────────────┐  │
│  │  FastAPI      │  Pydantic   │  Python 3.9+   │  │
│  ├───────────────────────────────────────────────┤  │
│  │  SQLAlchemy   │  Alembic    │  python-jose   │  │
│  ├───────────────────────────────────────────────┤  │
│  │  Uvicorn      │  Passlib    │  HTTPx         │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                         │
                         │ SQL
                         │
┌─────────────────────────────────────────────────────┐
│                   DATABASE                          │
│  ┌───────────────────────────────────────────────┐  │
│  │           PostgreSQL 12+                      │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## File Organization

```
Invox/
│
├── app/                         # Next.js Frontend
│   ├── api/auth/[...nextauth]/  # NextAuth configuration
│   ├── dashboard/               # Protected pages
│   └── ...
│
├── backend2/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/                 # API routes
│   │   ├── core/                # Configuration
│   │   ├── db/                  # Database
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   └── main.py              # App entry point
│   │
│   ├── alembic/                 # Database migrations
│   ├── .env                     # Environment variables
│   ├── requirements.txt         # Python dependencies
│   └── *.md                     # Documentation
│
├── lib/                         # Shared utilities
│   └── api/backend.ts           # Backend API client
│
├── types/                       # TypeScript types
│   └── next-auth.d.ts           # NextAuth types
│
└── .env.local                   # Frontend environment
```

---

**For more details, see:**

- IMPLEMENTATION_SUMMARY.md - Complete feature list
- SETUP_GUIDE.md - Detailed setup instructions
- QUICK_REFERENCE.md - Common commands
- README.md - Project overview
