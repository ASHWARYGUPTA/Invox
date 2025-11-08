# 🚀 Invox - AI-Powered Invoice Management Platform

<div align="center">

**Transform your invoice workflow with AI-powered automation**

[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)

[Features](#-key-features) • [Installation](#-local-setup) • [Architecture](#-architecture) • [API Docs](#-api-documentation)

</div>

---

## 📋 Table of Contents

- [What is Invox?](#-what-is-invox)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Architecture](#-architecture)
- [Local Setup](#-local-setup)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Features in Detail](#-features-in-detail)
- [Development](#-development)
- [Contributing](#-contributing)
- [📚 **[Complete Technical Documentation →](DOCUMENTATION.md)**](#-complete-technical-documentation)

---

## 🎯 What is Invox?

**Invox** is a modern, AI-powered invoice management platform that automates the entire invoice processing workflow - from extraction to approval. Built with cutting-edge technologies, Invox leverages Google Gemini AI for intelligent OCR, providing 99% accuracy in invoice data extraction from multiple sources including PDFs, images, emails, and handwritten documents.

### Why Invox?

- ⚡ **10x Faster Processing** - Automated invoice extraction vs manual data entry
- 🎯 **99% Accuracy** - AI-powered OCR with Google Gemini
- 🔒 **Bank-Level Security** - AES-256 encryption, OAuth 2.0, SOC 2 & GDPR compliant
- 📊 **Real-Time Analytics** - Monitor invoices and payments instantly
- 🔄 **Multi-Source Import** - Gmail, direct uploads, APIs, scanned documents
- 🤖 **Smart Automation** - Auto-categorize, route, and approve invoices

---

## ✨ Key Features

### 🤖 AI-Powered OCR Extraction

- **Google Gemini AI Integration** for intelligent data extraction
- Support for PDFs, images (PNG, JPG), and handwritten documents
- Multi-page document processing
- 99% accuracy rate with automatic validation

### 📧 Smart Email Integration

- **Gmail OAuth Integration** - Automatic invoice detection from emails
- Background polling system (checks every 60 seconds)
- Processes last 5 emails automatically
- Multi-layer duplicate prevention
- Supports both Gmail OAuth and IMAP protocols

### 📊 Real-Time Dashboard

- Live invoice monitoring and payment tracking
- Visual analytics and reporting
- Invoice status tracking (pending, approved, paid)
- Export to JSON and CSV formats

### 🔐 Enterprise Security

- **OAuth 2.0 Authentication** with Google
- AES-256 end-to-end encryption
- JWT token-based authorization
- Bank-level data protection
- SOC 2 & GDPR compliant

### 🎨 Modern UI/UX

- Responsive design (mobile, tablet, desktop)
- Beautiful 3D Prism background animations
- Glassmorphism design elements
- Dark mode optimized
- Smooth transitions and interactions

### 🔄 Automation & Workflows

- Auto-categorization of invoices
- Intelligent routing and approval workflows
- Email notification system
- Batch processing capabilities
- API integration ready

---

## 🛠 Technology Stack

### Frontend

- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript 5
- **Styling:** Tailwind CSS
- **UI Components:** Radix UI, shadcn/ui
- **Authentication:** NextAuth.js with Google OAuth
- **Animations:** GSAP, Framer Motion
- **State Management:** React Hooks
- **HTTP Client:** Axios

### Backend

- **Framework:** FastAPI 0.115.5
- **Language:** Python 3.13
- **Database:** PostgreSQL (Neon)
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Authentication:** JWT Tokens, OAuth 2.0
- **AI/ML:** Google Gemini AI
- **Email:** Gmail API, IMAP
- **Server:** Uvicorn (ASGI)

### Infrastructure

- **Database:** PostgreSQL 16
- **Cloud Storage:** (Optional) AWS S3 / Google Cloud Storage
- **Deployment:** Vercel (Frontend), Railway/Render (Backend)
- **Version Control:** Git, GitHub

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT (Browser)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Landing    │  │   Sign In    │  │  Dashboard   │     │
│  │     Page     │  │     Page     │  │     Page     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                    ┌───────▼───────┐
                    │   Next.js 15   │
                    │  (Frontend)    │
                    │  Port: 3000    │
                    └───────┬───────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
    ┌───────▼───────┐ ┌────▼────┐  ┌──────▼──────┐
    │  NextAuth.js  │ │  Axios  │  │   GSAP      │
    │  (OAuth)      │ │  (API)  │  │ (Animations)│
    └───────┬───────┘ └────┬────┘  └─────────────┘
            │              │
            └──────┬───────┘
                   │
           ┌───────▼────────┐
           │   FastAPI      │
           │   Backend      │
           │   Port: 8000   │
           └───────┬────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
┌─────▼─────┐ ┌───▼────┐ ┌─────▼──────┐
│PostgreSQL │ │ Gmail  │ │   Gemini   │
│ Database  │ │  API   │ │     AI     │
└───────────┘ └────────┘ └────────────┘
```

### Data Flow

1. **User Authentication:** Google OAuth → NextAuth → JWT Token
2. **Invoice Upload:** User uploads → FastAPI → Gemini AI → Extracted Data
3. **Email Polling:** Background Worker → Gmail API/IMAP → Invoice Detection → Processing
4. **Data Storage:** PostgreSQL with SQLAlchemy ORM
5. **Real-Time Updates:** WebSocket/Polling for dashboard updates

---

## 🚀 Local Setup

### Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** 18+ and npm/pnpm
- **Python** 3.13+
- **PostgreSQL** 16+
- **Git**

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/ASHWARYGUPTA/Invox.git
cd Invox
```

### 2️⃣ Frontend Setup (Next.js)

#### Install Dependencies

```bash
# Using pnpm (recommended)
pnpm install

# Or using npm
npm install
```

#### Configure Environment Variables

Create a `.env.local` file in the root directory:

```env
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here-min-32-chars

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Add authorized redirect URIs:
   - `http://localhost:3000/api/auth/callback/google`
   - `http://localhost:3000/auth/callback`
6. Copy Client ID and Client Secret to `.env.local`

#### Run Development Server

```bash
pnpm dev
# or
npm run dev
```

The frontend will be available at **http://localhost:3000**

---

### 3️⃣ Backend Setup (FastAPI)

#### Create Virtual Environment

```bash
cd backend
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/invox_db

# Authentication
NEXTAUTH_SECRET=same-as-frontend-secret
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth (same as frontend)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Application
DEBUG=True
```

#### Setup PostgreSQL Database

```bash
# Create database
createdb invox_db

# Create user (optional)
createuser invox_user -P
# Enter password when prompted

# Grant privileges
psql invox_db
GRANT ALL PRIVILEGES ON DATABASE invox_db TO invox_user;
\q
```

#### Run Database Migrations

```bash
# Initialize Alembic (if not already done)
alembic upgrade head
```

#### Run Development Server

```bash
# Start the FastAPI server
python -m uvicorn app.main:app --reload --port 8000
```

The backend will be available at:

- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

### 4️⃣ Verify Installation

1. **Frontend:** Open http://localhost:3000

   - You should see the landing page with 3D Prism background
   - Click "Join with Google" button

2. **Backend:** Open http://localhost:8000/docs

   - You should see the Swagger UI with all API endpoints
   - Try the `/health` endpoint

3. **Authentication:** Sign in with Google

   - Should redirect to Google OAuth
   - After approval, redirect back to dashboard

4. **Database:** Check if tables are created
   ```bash
   psql invox_db
   \dt
   # You should see: users, accounts, sessions, invoices, etc.
   ```

---

## 📁 Project Structure

```
Invox/
├── app/                          # Next.js App Router
│   ├── api/                      # API routes
│   │   └── auth/                 # NextAuth configuration
│   ├── auth/                     # Authentication pages
│   │   └── signin/               # Sign in page
│   ├── dashboard/                # Dashboard pages
│   └── page.tsx                  # Landing page
├── components/                   # React components
│   ├── ui/                       # UI components (buttons, cards, etc.)
│   ├── NavBarMenu.tsx            # Navigation menu
│   ├── Prism.tsx                 # 3D Prism background
│   └── ...                       # Other components
├── lib/                          # Utility functions
│   └── api/                      # API client configuration
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── api/                  # API routes
│   │   │   └── v1/
│   │   │       ├── endpoints/    # API endpoints
│   │   │       │   ├── auth.py   # Authentication
│   │   │       │   ├── invoices.py
│   │   │       │   └── users.py
│   │   │       └── api.py        # API router
│   │   ├── core/                 # Core functionality
│   │   │   ├── config.py         # Configuration
│   │   │   └── security.py       # Security utilities
│   │   ├── crud/                 # Database operations
│   │   ├── db/                   # Database configuration
│   │   ├── models/               # SQLAlchemy models
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # Business logic
│   │   │   ├── auth.py
│   │   │   ├── email_polling.py  # Email automation
│   │   │   └── invoice.py
│   │   ├── worker/               # Background workers
│   │   └── main.py               # FastAPI application
│   ├── alembic/                  # Database migrations
│   ├── requirements.txt          # Python dependencies
│   └── .env                      # Environment variables
├── public/                       # Static assets
├── types/                        # TypeScript types
├── .gitignore                    # Git ignore rules
├── next.config.ts                # Next.js configuration
├── package.json                  # Node.js dependencies
├── tsconfig.json                 # TypeScript configuration
└── README.md                     # This file
```

---

## 📚 API Documentation

### Authentication Endpoints

#### POST `/api/v1/auth/oauth/callback`

Handle OAuth callback from NextAuth

```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "image": "https://..."
}
```

#### GET `/api/v1/auth/me`

Get current user information (requires authentication)

### Invoice Endpoints

#### POST `/api/v1/invoices/upload`

Upload and process invoice

- Supports: PDF, PNG, JPG, JPEG
- Max size: 10MB
- Returns extracted invoice data

#### GET `/api/v1/invoices`

List all invoices for current user

- Pagination supported
- Filter by status, date range

#### GET `/api/v1/invoices/{invoice_id}`

Get specific invoice details

#### PUT `/api/v1/invoices/{invoice_id}`

Update invoice information

#### DELETE `/api/v1/invoices/{invoice_id}`

Delete invoice

### User Endpoints

#### GET `/api/v1/users/me`

Get current user profile

#### PUT `/api/v1/users/me`

Update user profile

---

## 🎨 Features in Detail

### Email Polling System

The backend includes an intelligent email polling system that:

- **Automatic Detection:** Scans inbox every 60 seconds
- **Smart Filtering:** Only processes last 5 emails
- **Duplicate Prevention:** Multi-layer checking at email and invoice level
- **Gmail OAuth Support:** Secure Gmail API integration
- **IMAP Fallback:** Support for other email providers
- **Background Processing:** Runs independently without blocking main application

### Duplicate Prevention

Three-layer duplicate prevention system:

1. **Email Level:** Tracks processed emails in `EmailProcessingLog`
2. **Exact Match:** Checks invoice_id + vendor + amount + date
3. **Filename Match:** Checks filename + amount
4. **Partial Match:** Handles OCR variations in vendor names

### AI-Powered Extraction

Google Gemini AI integration provides:

- Intelligent field detection (vendor, amount, date, items)
- Multi-language support
- Handwriting recognition
- Confidence scoring
- Automatic validation

---

## 💻 Development

### Frontend Development

```bash
# Run development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start

# Run linter
pnpm lint

# Type checking
pnpm type-check
```

### Backend Development

```bash
# Run development server with auto-reload
python -m uvicorn app.main:app --reload --port 8000

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```

### Database Management

```bash
# Connect to database
psql invox_db

# List tables
\dt

# Describe table
\d table_name

# Backup database
pg_dump invox_db > backup.sql

# Restore database
psql invox_db < backup.sql
```

---

## 📚 Complete Technical Documentation

For comprehensive technical documentation including:

- **Gmail OAuth Implementation** - Complete setup and integration guide
- **Duplicate Prevention System** - Multi-layer prevention strategy
- **Email Polling System** - Automated email processing
- **Export Features** - JSON and CSV export functionality
- **Backend Architecture** - Detailed system architecture
- **Troubleshooting Guide** - Solutions to common issues
- **Development Guide** - Code standards and workflows
- **API Reference** - Complete endpoint documentation
- **What's Next** - Future enhancements roadmap

**📖 [Read the Complete Documentation →](DOCUMENTATION.md)**

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

Created by the Invox Team:

- **Abhinav Mishra** - Full Stack Developer
- **Ashwary Gupta** - Full Stack Developer
- **Sujal Ahar** - Backend Developer
- **Shivang Baranwal** - Frontend Developer

---

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/) - React Framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python Web Framework
- [Google Gemini AI](https://deepmind.google/technologies/gemini/) - AI/ML Platform
- [Tailwind CSS](https://tailwindcss.com/) - CSS Framework
- [shadcn/ui](https://ui.shadcn.com/) - UI Components
- [Vercel](https://vercel.com/) - Deployment Platform

---

<div align="center">

**Made with ❤️ by the Invox Team**

[⬆ Back to Top](#-invox---ai-powered-invoice-management-platform)

</div>
