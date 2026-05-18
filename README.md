<div align="center">
  <img src="./frontend/public/logo/vymed_logo.png" alt="Vymed Logo" width="120" height="120" />
  <h1 align="center">Vymed</h1>
  <p align="center">
    <strong>Pharmaceutical Provenance on the Stellar Blockchain</strong>
  </p>
  <p align="center">
    Eliminating counterfeit medicine in emerging markets through transparent, tamper-proof, and privacy-conscious supply chain verification.
  </p>
  <p align="center">
    <a href="#features">Features</a> •
    <a href="#how-it-works">How It Works</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#getting-started">Getting Started</a> •
    <a href="#project-structure">Project Structure</a> •
    <a href="#contributing">Contributing</a> •
    <a href="#license">License</a>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/blockchain-Stellar-7B1FA2?style=flat-square" alt="Stellar" />
    <img src="https://img.shields.io/badge/frontend-React%20%7C%20TypeScript-61DAFB?style=flat-square" alt="React/TypeScript" />
    <img src="https://img.shields.io/badge/backend-Python%20%7C%20FastAPI-009688?style=flat-square" alt="Python/FastAPI" />
    <img src="https://img.shields.io/badge/database-PostgreSQL-336791?style=flat-square" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/cache-Redis-DC382D?style=flat-square" alt="Redis" />
    <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License" />
    <img src="https://img.shields.io/badge/status-MVP-yellow?style=flat-square" alt="MVP Status" />
  </p>
</div>

---

## 📋 Table of Contents

- [About Vymed](#about-vymed)
- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Features](#features)
- [How It Works](#how-it-works)
- [User Journeys](#user-journeys)
- [Tech Stack](#tech-stack)
- [Architecture Overview](#architecture-overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Smart Contract](#smart-contract)
- [Security & Anti-Fraud](#security--anti-fraud)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Community](#community)
- [License](#license)

---

## 🧬 About Vymed

**Vymed** is an open-source, mobile-first pharmaceutical provenance platform built on the **Stellar Blockchain**. It provides a transparent, tamper-proof, and privacy-conscious ledger for tracking medication from manufacturer to patient.

By leveraging Stellar's low transaction fees (~$0.00001 per operation) and ~5-second settlement time, Vymed makes pharmaceutical verification accessible, affordable, and instant — even in the most resource-constrained environments.

### 🌍 Mission

> *To create a trustless verification layer that is free for the end-user, cost-effective for the manufacturer, and secure against systemic abuse — ultimately saving lives by eliminating counterfeit medicine.*

---

## ⚠️ The Problem

In emerging markets across **Africa, Southeast Asia, and South America**, counterfeit medicine is a life-threatening crisis:

- **1 in 10** medical products in developing countries are substandard or falsified (WHO)
- Existing supply chain solutions require digital wallets and cryptocurrency for "gas fees"
- Patients lack the tools to verify whether their medication is authentic
- Distributors need privacy protections for their trade secrets
- Batch recalls are slow, manual, and often fail to reach end consumers

---

## ✅ The Solution

Vymed addresses these challenges through four core innovations:

| Innovation | Description |
|------------|-------------|
| **Zero-Cost Verification** | Manufacturer-sponsored Fee Bump transactions mean patients never pay to verify |
| **Privacy-First Transparency** | Masked identity protocol protects distributor trade secrets while maintaining audit trails |
| **Nested Scanning** | Scan a carton to automatically update all internal bottles — no individual scanning needed |
| **Instant Recall Alerts** | Batch-specific clawback notifications pushed directly to users' smartphones |

---

## ✨ Features

### 🔍 For Patients (End Users)
- **Free Verification** — Scan any GS1 DataMatrix or QR code at no cost
- **Instant Results** — Green (Authentic), Yellow (Warning), or Red (Counterfeit/Recall) in under 5 seconds
- **Offline Mode** — Store-and-forward queue for low-connectivity zones
- **Privacy Preserved** — No personal data required to verify medication

### 🏭 For Manufacturers
- **Batch Minting** — Register new drug batches as unique Stellar assets
- **Parent-Child Mapping** — Define carton-to-bottle relationships (e.g., 1 carton = 50 bottles)
- **Recall Management** — Use Stellar's clawback feature for instant batch recalls
- **Scan Analytics** — Dashboard with heatmaps and verification metrics

### 🚚 For Distributors
- **Masked Identity** — Appear as "Verified Distributor 08" on the public ledger
- **Bulk Scanning** — Scan cartons to update entire pallets in one transaction
- **Chain of Custody** — Full audit trail without exposing trade secrets

### 🛡️ Security Features
- **Scan Throttling** — Max 3 scans per 10 minutes per unique bottle (Redis-based)
- **Fee Bump Sponsorship** — All transactions wrapped in manufacturer-signed Fee Bumps
- **Clawback Enabled** — Batch-level recall capability via Stellar's AUTH_CLAWBACK_ENABLED flag
- **Device Binding** — Rate limiting tied to Device ID for anti-spoofing

---

## 🔄 How It Works

### Verification Flow

```mermaid
sequenceDiagram
    participant Patient
    participant App as Vymed Mobile App
    participant API as FastAPI Backend
    participant Redis as Redis Cache
    participant Stellar as Stellar Blockchain

    Patient->>App: Scan GS1 DataMatrix
    App->>App: Decode Unit_ID + Device_ID
    App->>API: POST /verify (Unit_ID, Device_ID)
    
    API->>Redis: Check throttle:{unit_id}:{device_id}
    Redis-->>API: Scan count (0-3)
    
    alt Scan Count > 3
        API-->>App: 429 Security Warning
        App-->>Patient: ⚠️ Yellow Warning
    else Scan Count ≤ 3
        API->>API: Construct Stellar Transaction
        API->>API: Sign Fee Bump (Manufacturer Key)
        API->>Stellar: Submit Transaction
        Stellar-->>API: Ledger Confirmation (~5s)
        API->>Redis: Increment scan count
        API-->>App: Provenance Result
        App-->>Patient: ✅ Green (Authentic) or ❌ Red (Counterfeit)
    end
```

### Supply Chain Flow

```mermaid
graph LR
    M[Manufacturer] -->|Mint Batch| S[Stellar Asset]
    S -->|Scan Carton| D1[Distributor A]
    D1 -->|Alias: Verified Dist. 01| D2[Distributor B]
    D2 -->|Alias: Verified Dist. 08| P[Pharmacy]
    P -->|Patient Scans| V[Verification]
    
    style M fill:#6366F1,color:#fff
    style S fill:#10B981,color:#fff
    style D1 fill:#F59E0B,color:#fff
    style D2 fill:#F59E0B,color:#fff
    style P fill:#6366F1,color:#fff
    style V fill:#10B981,color:#fff
```

---

## 👤 User Journeys

### A. The Manufacturer (Genesis)

1. Registers a new drug batch via the Manufacturer Dashboard
2. Defines the parent-child relationship (e.g., 1 Carton = 50 Bottles)
3. Mints the batch as a unique Stellar asset with clawback flags
4. Prints GS1 DataMatrix codes for packaging

### B. The Distributor (Handoff)

1. Receives a pallet or carton at the warehouse
2. Scans the **Carton QR** using the Vymed app
3. The app automatically updates ownership/status of all 50 internal bottles on-chain
4. Identity is logged as an alias (e.g., "Verified Distributor 08") to protect trade secrets

### C. The Patient (Verification)

1. Scans the individual bottle at the pharmacy counter
2. **Green Status:** *"Authentic. Produced by [Manufacturer Name]. 4 Verified Handoffs."*
3. **Red Status:** *"Warning: Origin not verified"* or *"RECALLED: Do not consume."*

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, TypeScript, Tailwind CSS v4 | High-performance, type-safe, mobile-first UI |
| **Animation** | Framer Motion (motion/react) | Smooth, weightless transitions |
| **State Management** | Zustand | Lightweight offline queue management |
| **Backend** | Python 3.11+, FastAPI | High-concurrency async API for blockchain operations |
| **Blockchain** | Stellar (Mainnet/Testnet) | Low fees, native asset support, Fee Bump transactions |
| **Database** | PostgreSQL | Relational integrity for parent-child batch mappings |
| **Cache** | Redis | Sub-millisecond throttling for security (3 scans / 10 mins) |
| **Mobile Bridge** | Capacitor or PWA | Native camera API access for GS1 DataMatrix scanning |
| **Containerization** | Docker & Docker Compose | Consistent development and deployment environments |
| **CI/CD** | GitHub Actions | Lint → Test → Build → Deploy pipeline |

---

## 🏗️ Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           React PWA / Capacitor Mobile App            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │  │
│  │  │ Scanner  │  │  Result  │  │  Manufacturer    │   │  │
│  │  │  UI      │  │  Card    │  │  Dashboard       │   │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS / REST API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Verify  │  │  Batch   │  │  Recall  │  │  Auth    │   │
│  │  Route   │  │  Routes  │  │  Routes  │  │  Routes  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │             │              │          │
│  ┌────▼──────────────▼─────────────▼──────────────▼─────┐   │
│  │              Core Services Layer                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │   │
│  │  │  Stellar │  │  Rate    │  │  Alias Manager   │   │   │
│  │  │  Service │  │  Limiter │  │  (Identity Mask) │   │   │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│  PostgreSQL  │  │    Redis     │  │  Stellar Horizon  │
│  (Metadata)  │  │  (Throttle)  │  │  (Blockchain)     │
└──────────────┘  └──────────────┘  └──────────────────┘
```

### Data Flow

1. **Scanning**: Client decodes GS1 DataMatrix into a Unit_ID
2. **Request**: Client sends Unit_ID and Device_ID to FastAPI
3. **Throttling**: FastAPI checks Redis; if count > 3, return 429 (Security Warning)
4. **Sponsorship**: FastAPI constructs a Stellar Transaction, signs it with the Manufacturer's key as the Fee Payer, and submits it
5. **Result**: UI displays Green (Verified), Yellow (Warning/Throttled), or Red (Counterfeit/Recall)

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and **pnpm** (for frontend)
- **Python** 3.11+ and **pip** (for backend)
- **PostgreSQL** 14+ (for metadata storage)
- **Redis** 7+ (for rate limiting)
- **Docker** & **Docker Compose** (optional, for containerized setup)
- **Stellar Testnet Account** (for development)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/your-org/vymed.git
cd vymed
```

#### 2. Frontend Setup

```bash
cd frontend
pnpm install
pnpm run dev
```

The frontend will be available at `http://localhost:5173`.

#### 3. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

#### 4. Database Setup

```bash
# Create the PostgreSQL database
createdb vymed

# Run migrations
cd backend
alembic upgrade head
```

#### 5. Docker Setup (Alternative)

```bash
docker compose -f backend/infra/docker-compose.yml up -d
```

This will start all services: frontend, backend, PostgreSQL, and Redis.

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Stellar Configuration
STELLAR_NETWORK=TESTNET
STELLAR_HORIZON_URL=https://horizon-testnet.stellar.org
MANUFACTURER_SECRET_KEY=SCXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
MANUFACTURER_PUBLIC_KEY=GCXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/vymed

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
RATE_LIMIT_MAX_SCANS=3
RATE_LIMIT_WINDOW_SECONDS=600
API_KEY=your-api-key-here

# App
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## 📁 Project Structure

```
vymed/
├── backend/                          # FastAPI Backend
│   ├── src/
│   │   ├── api/                      # API Routes
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── verify.py         # POST /verify endpoint
│   │   │   │   ├── batches.py        # Batch management endpoints
│   │   │   │   ├── recalls.py        # Recall/clawback endpoints
│   │   │   │   └── auth.py           # Authentication endpoints
│   │   │   └── deps.py               # Dependency injection
│   │   ├── core/                     # Core Configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # App configuration
│   │   │   ├── security.py           # Rate limiting & auth
│   │   │   └── database.py           # Database connection
│   │   ├── models/                   # SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── batch.py              # Batch model
│   │   │   ├── distributor_alias.py  # Distributor alias model
│   │   │   └── scan_log.py           # Scan audit log model
│   │   ├── schemas/                  # Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   ├── verify.py             # Verification request/response
│   │   │   ├── batch.py              # Batch schemas
│   │   │   └── recall.py             # Recall schemas
│   │   ├── services/                 # Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── stellar_service.py    # Stellar SDK operations
│   │   │   ├── rate_limiter.py       # Redis-based throttling
│   │   │   ├── alias_manager.py      # Identity masking
│   │   │   └── batch_service.py      # Batch management logic
│   │   └── main.py                   # FastAPI app entry point
│   ├── migrations/                   # Alembic migrations
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   ├── tests/                        # Test suite
│   │   ├── __init__.py
│   │   ├── test_verify.py
│   │   ├── test_rate_limiter.py
│   │   └── test_stellar_service.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                         # React/TypeScript Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── App.tsx               # Main app with view routing
│   │   │   └── components/
│   │   │       ├── LandingPage.tsx    # Public landing/home
│   │   │       ├── Scanner.tsx        # Camera scanner interface
│   │   │       ├── VerificationResult.tsx  # Green/Yellow/Red result
│   │   │       ├── ManufacturerDashboard.tsx  # Manufacturer portal
│   │   │       ├── BatchManagement.tsx  # Batch CRUD interface
│   │   │       ├── AnalyticsDashboard.tsx  # Scan analytics
│   │   │       ├── LoadingShimmer.tsx  # Blockchain loading state
│   │   │       ├── ThemeToggle.tsx    # Light/Dark mode toggle
│   │   │       └── ui/               # Reusable UI components
│   │   ├── hooks/                    # Custom React hooks
│   │   │   ├── useStellar.ts
│   │   │   └── useOfflineQueue.ts
│   │   ├── store/                    # Zustand state management
│   │   │   └── offlineQueue.ts
│   │   ├── styles/                   # Global styles & theme
│   │   │   ├── globals.css
│   │   │   ├── theme.css
│   │   │   └── fonts.css
│   │   └── main.tsx                  # Entry point
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── postcss.config.mjs
│   └── Dockerfile
│
├── contracts/                        # Stellar Smart Contracts
│   ├── scripts/
│   │   ├── mint_batch.py             # Batch minting script
│   │   ├── setup_sponsorship.py      # Fee Bump setup
│   │   └── clawback_recall.py        # Recall/clawback script
│   ├── tests/
│   │   ├── test_mint.py
│   │   └── test_sponsorship.py
│   └── README.md
│
├── docs/                             # Documentation
│   ├── Vymed Architecture.md
│   ├── Vymed Product Definition.md
│   ├── Vymed Project Brief.md
│   └── Vymed UI_UX & Frontend Specification.md
│
│
├── .github/                          # GitHub configuration
│   └── workflows/
│       ├── frontend.yml              # Frontend CI/CD
│       └── backend.yml               # Backend CI/CD
│
├── .gitignore
├── LICENSE
└── README.md                         # You are here
```

---

## 📡 API Reference

### Verification Endpoints

| Method | Endpoint | Description | Rate Limited |
|--------|----------|-------------|--------------|
| `POST` | `/api/v1/verify` | Verify a medication unit | Yes (3/10min) |
| `GET`  | `/api/v1/verify/{unit_id}` | Get verification history | No |

### Batch Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/batches` | Register a new batch | Yes |
| `GET`  | `/api/v1/batches/{batch_id}` | Get batch details | Yes |
| `POST` | `/api/v1/batches/{batch_id}/map` | Map parent-child relationships | Yes |

### Recall Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/recalls` | Initiate a batch recall | Yes |
| `GET`  | `/api/v1/recalls/{recall_id}` | Get recall status | Yes |

### Example: Verify a Medication

```bash
curl -X POST http://localhost:8000/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{
    "unit_id": "GS1-ABC123XYZ",
    "device_id": "device-uuid-here"
  }'
```

**Response (Verified):**

```json
{
  "status": "verified",
  "batch_id": "BATCH-2026-05-001",
  "manufacturer": "PharmaCorp Ltd.",
  "handoffs": 4,
  "last_verified": "2026-05-02T14:30:00Z",
  "expiry_date": "2027-05-01",
  "transaction_hash": "a1b2c3d4e5f6..."
}
```

**Response (Counterfeit/Recall):**

```json
{
  "status": "recalled",
  "batch_id": "BATCH-2026-05-001",
  "reason": "Quality control failure - Batch recalled by manufacturer",
  "alert_level": "critical"
}
```

---

## 📜 Smart Contract

Vymed leverages Stellar's native blockchain features rather than traditional smart contracts. The core logic is implemented through:

### Stellar Asset Configuration

- **Asset Code**: 4-12 alphanumeric characters per batch
- **Issuer Flags**: `AUTH_CLAWBACK_ENABLED` enabled for batch-level recalls
- **Fee Sponsorship**: All verification transactions wrapped in Fee Bump transactions

### Key Operations

| Operation | Description | Stellar Feature |
|-----------|-------------|-----------------|
| **Batch Minting** | Create a unique asset for each drug batch | `ChangeTrust` + `Payment` |
| **Verification** | Record a scan event on-chain | `Payment` (0.0000001 XLM) |
| **Ownership Transfer** | Update distributor chain of custody | `SetTrustLineFlags` |
| **Batch Recall** | Revoke all outstanding units | `Clawback` |
| **Fee Sponsorship** | Manufacturer pays for patient scans | `Fee Bump Transaction` |

### Scripts

```bash
# Mint a new batch
python contracts/scripts/mint_batch.py \
  --asset-code "BATCH001" \
  --issuer-secret "SC..." \
  --amount 1000

# Setup fee sponsorship
python contracts/scripts/setup_sponsorship.py \
  --sponsor-secret "SC..." \
  --sponsored-key "GC..."

# Execute a recall
python contracts/scripts/clawback_recall.py \
  --asset-code "BATCH001" \
  --issuer-secret "SC..."
```

---

## 🛡️ Security & Anti-Fraud

### Rate Limiting

- **Mechanism**: Redis-based sliding window counter
- **Key Format**: `throttle:{unit_id}:{device_id}`
- **Threshold**: Maximum 3 scans per 10 minutes per unique bottle
- **TTL**: 600 seconds (auto-expires)
- **Action**: Exceeding threshold triggers a security warning (Yellow status)

### Fee Bump Sponsorship

- All verification transactions are wrapped in a **Fee Bump** signed by the Manufacturer account
- Patients never need to hold XLM or pay transaction fees
- The Manufacturer account maintains a minimal XLM balance for sponsorship

### Clawback Protection

- Each batch asset is issued with `AUTH_CLAWBACK_ENABLED` flag
- In the event of a recall, the manufacturer can claw back all outstanding units
- The app automatically detects clawed-back assets and displays a Red alert

### Privacy Protection

- Distributor identities are masked using cryptographic aliases
- The public ledger shows "Verified Distributor 08" instead of the actual Stellar public key
- Full audit trail maintained without exposing trade secrets

---

## 🚢 Deployment

### Docker Compose (Local/Staging)

```bash
docker compose -f backend/infra/docker-compose.yml up -d
```

### Production Deployment

| Component | Service | Configuration |
|-----------|---------|---------------|
| **Frontend** | AWS S3 + CloudFront | Static site hosting with CDN |
| **Backend** | AWS App Runner | Auto-scaling containerized API |
| **Database** | AWS RDS (PostgreSQL) | Managed, multi-AZ deployment |
| **Cache** | AWS ElastiCache (Redis) | Managed, cluster mode disabled |
| **Secrets** | AWS Secrets Manager | Manufacturer secret key storage |

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/backend.yml
name: Backend CI/CD
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t vymed-backend ./backend
      - run: docker push ${{ secrets.REGISTRY }}/vymed-backend
```

---

## 🗺️ Roadmap

### Phase 1 — MVP (Current) 🟢
- [x] Frontend UI (React/TypeScript) — Scanner, Result Card, Landing Page
- [x] Design system — "Whisper" aesthetic with glassmorphism
- [ ] Stellar asset minting for batch IDs
- [ ] Fee Bump transaction sponsorship
- [ ] Basic scan verification flow

### Phase 2 — Supply Chain Logic 🔄
- [ ] Parent-Child inheritance (Carton → Bottle)
- [ ] Distributor identity masking (Alias Manager)
- [ ] Batch management dashboard
- [ ] PostgreSQL schema for batch metadata

### Phase 3 — Security & Mobile 📱
- [ ] Redis-based scan throttling
- [ ] Offline store-and-forward queue
- [ ] GS1 DataMatrix camera integration
- [ ] Push notification system for recalls

### Phase 4 — Production & Scale 🚀
- [ ] Open-source release
- [ ] Pilot program with regional pharmacies
- [ ] Performance optimization (< 5s scan-to-result)
- [ ] Comprehensive test suite
- [ ] Security audit

---

## 🤝 Contributing

We welcome contributions from the community! Whether you're a blockchain developer, a pharmaceutical supply chain expert, or a UI/UX designer, there's a place for you in the Vymed project.

### Getting Started

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- **Code Style**: Follow PEP 8 (Python) and ESLint/Prettier (TypeScript)
- **Testing**: Write tests for all new features
- **Documentation**: Update docs for any API changes
- **Commits**: Use conventional commit messages (`feat:`, `fix:`, `docs:`, etc.)

### Areas Needing Help

- Stellar blockchain integration and optimization
- GS1 DataMatrix barcode parsing
- Mobile PWA/Capacitor camera integration
- UI/UX refinements for the "Whisper" aesthetic
- Documentation and translations
- Security auditing and penetration testing

---

## 💬 Community

- **Discussions**: [GitHub Discussions](https://github.com/your-org/vymed/discussions)
- **Issues**: [GitHub Issues](https://github.com/your-org/vymed/issues)
- **Twitter/X**: [@vymed](https://twitter.com/vymed)
- **Discord**: [Join our Discord](https://discord.gg/vymed)

### Code of Conduct

This project adheres to the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct. By participating, you are expected to uphold this code.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](./LICENSE) for more information.

```
MIT License

Copyright (c) 2026 Vymed Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

<div align="center">
  <p>
    <strong>Vymed</strong> — <em>Trust in every dose. Transparency in every scan.</em>
  </p>
  <p>
    Made with ❤️ for global health integrity.
  </p>
</div>
