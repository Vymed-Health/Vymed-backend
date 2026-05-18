# Contributing to Vymed

🎉 **First off, thank you for considering contributing to Vymed!** 🎉

Vymed is an open-source pharmaceutical provenance platform on the Stellar
blockchain, and we welcome contributors from all backgrounds — whether you
are a blockchain developer, a pharmaceutical supply chain expert, a UI/UX
designer, or someone with fresh ideas.

This guide is especially relevant if you discovered Vymed through
**drips.network**, a decentralized protocol for funding open-source work.
We accept contributions via standard GitHub workflows and hope to
participate in **Drips** for funded bounties and grants in the future.

> **Table of Contents**
> - [Code of Conduct](#code-of-conduct)
> - [Ways to Contribute](#ways-to-contribute)
> - [Funding via Drips Network](#funding-via-drips-network)
> - [Getting Started](#getting-started)
> - [Development Workflow](#development-workflow)
> - [Project Structure](#project-structure)
> - [Style Guides](#style-guides)
> - [Testing](#testing)
> - [Pull Request Process](#pull-request-process)
> - [Reporting Issues](#reporting-issues)
> - [Community](#community)

---

## Code of Conduct

This project adheres to the [Contributor Covenant](https://www.contributor-covenant.org/)
code of conduct. By participating, you are expected to uphold this code.
Please report unacceptable behaviour to the project maintainers.

---

## Ways to Contribute

There are many ways to contribute beyond writing code:

| Area | Examples |
|------|----------|
| **🐛 Bug Reports** | Open a GitHub issue with steps to reproduce |
| **💡 Feature Ideas** | Start a Discussion or add a Feature Request |
| **📝 Documentation** | Improve README, add API docs, write tutorials |
| **🌐 Translations** | Help localise the frontend UI strings |
| **🎨 UI/UX** | Design improvements, accessibility, motion |
| **🔒 Security** | Penetration testing, threat modelling |
| **🧪 Testing** | Write tests, automate QA, test on real devices |
| **📦 Smart Contracts** | Soroban contract improvements, new features |
| **🔗 Integrations** | GS1 parsers, new barcode formats, pharmacy APIs |

---

## Funding via Drips Network

Vymed is exploring **Drips Network** — a protocol that lets you fund
open-source work with **DAI/stablecoins** split across dependencies.

Once the project is accepted on Drips, contributors will be able to
find funded issues and receive payouts after merged PRs. Stay tuned
for updates!

---

## Getting Started

### 1. Fork & Clone

```bash
git clone https://github.com/<your-username>/Vymed.git
cd Vymed
```

### 2. Choose Your Area

Decide whether you want to work on:

- **Frontend** (`frontend/`) — React + TypeScript + Tailwind CSS
- **Backend** (`backend/`) — Python + FastAPI
- **Smart Contracts** (`contracts/`) — Rust (Soroban) or Python scripts

### 3. Set Up Your Environment

#### Frontend

```bash
cd frontend
pnpm install
pnpm run dev        # → http://localhost:5173
```

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

#### Soroban Smart Contract

```bash
cd contracts/batch_registry
cargo test          # Run unit tests
cargo build --release --target wasm32-unknown-unknown
```

> **Note:** Rust + `wasm32-unknown-unknown` target + `soroban-cli` are
> required. See the [contracts README](./contracts/README.md) for full
> setup instructions.

### 4. (Optional) Docker — Full Stack

```bash
docker compose -f backend/infra/docker-compose.yml up -d
```



---

## Development Workflow

### Branch Naming

Use descriptive branch names with a prefix:

| Prefix | Example |
|--------|---------|
| `feat/` | `feat/soroban-batch-transfer` |
| `fix/` | `fix/scan-throttle-race-condition` |
| `docs/` | `docs/api-verify-endpoint` |
| `test/` | `test/rate-limiter-edge-cases` |
| `refactor/` | `refactor/stellar-service` |
| `chore/` | `chore/update-deps` |

### Commit Messages

We use **Conventional Commits**:

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

Examples:

```
feat(contract): add batch_registry Soroban contract
fix(backend): correct Redis TTL key format
docs(readme): add Drips funding section
test(contract): add provenance event tests
```

### Workflow Steps

1. **Pick an issue** — comment to self-assign
2. **Create a branch** — `git checkout -b feat/my-feature`
3. **Make changes** — write code, add tests, update docs
4. **Run tests** — ensure everything passes
5. **Commit** — use conventional commit format
6. **Push** — `git push origin feat/my-feature`
7. **Open a Pull Request** — see [PR Process](#pull-request-process)

---

## Project Structure

```
vymed/
├── frontend/                  # React + TypeScript + Tailwind
│   ├── src/
│   │   ├── app/               # Views & components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── store/             # Zustand state
│   │   └── styles/            # Global CSS
│   └── ...
├── backend/                   # Python + FastAPI
│   ├── src/
│   │   ├── api/               # REST endpoints
│   │   ├── core/              # Config, DB, security
│   │   ├── models/            # SQLAlchemy ORM
│   │   ├── schemas/           # Pydantic validation
│   │   └── services/          # Business logic
│   └── ...
├── contracts/                 # Smart contracts & scripts
│   ├── batch_registry/        # Soroban Rust contract
│   ├── scripts/               # Python Stellar SDK scripts
│   └── tests/                 # Python unit tests
├── .github/workflows/         # CI/CD pipelines
├── CONTRIBUTING.md            # You are here
└── README.md                  # Project overview
```

---

## Style Guides

### Rust (Soroban)

- Follow the [Soroban SDK conventions](https://soroban.stellar.org/docs)
- Use `rustfmt` and `clippy`:
  ```bash
  cargo fmt
  cargo clippy -- -D warnings
  ```
- Document all public items with `///` doc comments
- Every function that can fail should return `Result<_, ContractError>`

### Python (Backend / Scripts)

- **PEP 8** with a line length of 88 (Black-compatible)
- Use type hints everywhere
- Format with Black: `black backend/`
- Sort imports with isort: `isort backend/`
- Lint with Ruff: `ruff check backend/`

### TypeScript / React (Frontend)

- **Prettier** for formatting: `pnpm run format`
- **ESLint** for linting: `pnpm run lint`
- Use named exports over default exports
- Prefer functional components with hooks over class components

---

## Testing

We take testing seriously — new features should come with tests.

### Smart Contract Tests

```bash
cd contracts/batch_registry
cargo test                  # All unit tests
cargo test -- --nocapture   # With stdout output
```

### Backend Tests

```bash
cd backend
pytest                                # All tests
pytest tests/test_verify.py -v        # Single file, verbose
pytest --cov=src --cov-report=term    # With coverage
```

### Frontend Tests

```bash
cd frontend
pnpm run test         # Vitest runner
```

### CI Checks

All PRs are tested on **GitHub Actions** (see `.github/workflows/`).
Make sure your branch passes CI before requesting review.

---

## Pull Request Process

1. **Create a draft PR** early so others can see your progress
2. **Fill out the PR template** — link the issue, describe changes
3. **Ensure tests pass** — CI will run automatically
4. **Request a review** — at least one maintainer approval required
5. **Squash & merge** — maintainer will squash your commits into one

### PR Checklist

Before submitting, verify:

- [ ] Code follows style guides (rustfmt, Black, Prettier)
- [ ] Tests added/updated and passing
- [ ] Documentation updated (README, API docs)
- [ ] No regression in existing functionality
- [ ] Commit messages follow Conventional Commits
- [ ] PR title follows `<type>(<scope>): <description>` format

### What Happens Next?

| Step | Who | Description |
|------|-----|-------------|
| 1 | Maintainer | Review within 48 hours |
| 2 | Contributor | Address feedback |
| 3 | Maintainer | Approve & merge |
| 4 | Bot | Deploy to staging |
| 5 | Maintainer | Release notes |

---

## Reporting Issues

### Bug Reports

Open a [GitHub Issue](https://github.com/vrickish/Vymed/issues) with:

- **Summary** — brief description
- **Steps to Reproduce** — numbered list
- **Expected vs Actual** — what you expected vs what happened
- **Environment** — OS, browser, version, network
- **Screenshots** — if applicable

### Security Issues

For security vulnerabilities, **do not open a public issue**. Instead,
email the maintainers directly or use GitHub's private vulnerability
reporting feature.

---

## Community

| Channel | Purpose |
|---------|---------|
| [GitHub Discussions](https://github.com/vrickish/Vymed/discussions) | Ideas, questions, general chat |
| [Issue Tracker](https://github.com/vrickish/Vymed/issues) | Bug reports, feature requests |
| (Coming soon — Drips Network) | Funded bounties & grants |

### Recognition

All contributors are listed in the project's release notes and the
`CONTRIBUTORS.md` file. Drips-funded contributions are also recorded
on the Drips ledger for permanent attribution.

---

*Thank you for helping us eliminate counterfeit medicine — one batch at a time.* 💊✨
