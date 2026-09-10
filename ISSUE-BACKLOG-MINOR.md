# Vymed-backend — Minor Issues Backlog (9 Issues)

Sized strictly as **100 pts (Trivial / Good First Issue)** in Drips Wave criteria.

---

## #1: Add OpenAPI documentation and response schemas for batch verification endpoints

- **Labels**: `complexity:trivial, backend, documentation, good first issue`

- **Complexity**: `100 pts` (Trivial)


### Summary
Enrich FastAPI / NestJS Swagger documentation with detailed response schemas for medication verification.

### Requirements
- Document `/api/v1/verify/{batch_id}` with example 200, 404, and 400 responses.
- Add parameter descriptions and validation rules.
- Verify Swagger UI loads at `/docs`.

---

## #2: Enhance health check route to report database latency and cache availability

- **Labels**: `complexity:trivial, backend, code-hygiene`

- **Complexity**: `100 pts` (Trivial)


### Summary
Expand `/api/health` to report real-time database latency and Redis cache connection status.

### Requirements
- Return `{ status: "healthy", db_latency_ms: 5, cache_status: "connected", version: "1.0.0" }`.
- Ensure route fails with HTTP 503 if primary database is down.
- Add automated test verifying health check response format.

---

## #3: Document all database, JWT secret, and Stellar RPC env vars in .env.example

- **Labels**: `complexity:trivial, backend, documentation, good first issue`

- **Complexity**: `100 pts` (Trivial)


### Summary
Provide complete documentation and dummy values for all backend environment variables.

### Requirements
- Document `DATABASE_URL`, `JWT_SECRET`, `SOROBAN_RPC_URL`, and `GS1_PARSER_SECRET`.
- Include notes distinguishing Stellar Testnet vs Mainnet configurations.
- Verify server startup displays clean error messages when required variables are absent.

---

## #4: Standardize validation error response structure for medication batch registration

- **Labels**: `complexity:trivial, backend, code-hygiene`

- **Complexity**: `100 pts` (Trivial)


### Summary
Ensure all validation failures return a consistent JSON response structure across API controllers.

### Requirements
- Return standardized `{ error: "Validation Error", details: [{ field: string, issue: string }] }`.
- Ensure handler catches schema validation exceptions globally.
- Add test asserting HTTP 400 with structured validation payload on missing fields.

---

## #5: Add request logger middleware recording HTTP method, path, and duration

- **Labels**: `complexity:trivial, backend, code-hygiene`

- **Complexity**: `100 pts` (Trivial)


### Summary
Improve API traceability by logging all incoming requests with request duration in milliseconds.

### Requirements
- Log format: `[INFO] POST /api/v1/batches/register 201 - 24.5ms`.
- Ensure sensitive medical tokens and passwords are redacted from log messages.
- Verify logging works cleanly in Docker container.

---

## #6: Add Pytest / Jest unit test verifying 400 Bad Request on invalid barcode hash

- **Labels**: `complexity:trivial, backend, testing, good first issue`

- **Complexity**: `100 pts` (Trivial)


### Summary
Verify that the barcode verification endpoint rejects malformed or non-hexadecimal hash strings.

### Requirements
- Write test in `tests/verification.test.ts` testing malformed barcode hash parameter.
- Assert API returns HTTP 400 with descriptive error message.
- Ensure test passes with `npm test` or `pytest`.

---

## #7: Add package dependency audit command to CI pipeline and package scripts

- **Labels**: `complexity:trivial, backend, ci, security`

- **Complexity**: `100 pts` (Trivial)


### Summary
Configure automated security vulnerability checks on project dependencies.

### Requirements
- Add `"audit": "npm audit --audit-level=high"` in `package.json` (or `pip-audit` in `requirements-dev.txt`).
- Add audit check step to `.github/workflows/ci.yml`.
- Verify clean execution with zero high-severity vulnerabilities.

---

## #8: Document GS1 DataMatrix barcode parsing rules and regex patterns in docs/

- **Labels**: `complexity:trivial, backend, documentation`

- **Complexity**: `100 pts` (Trivial)


### Summary
Document GS1 Application Identifiers (AI 01 GTIN, AI 17 Expiration, AI 10 Batch/Lot, AI 21 Serial) in `docs/gs1-spec.md`.

### Requirements
- Explain barcode regex parsing logic and checksum verification.
- Provide sample barcode strings for testing.
- Verify documentation formatting.

---

## #9: Add quickstart instructions and API endpoint table to README.md

- **Labels**: `complexity:trivial, backend, documentation`

- **Complexity**: `100 pts` (Trivial)


### Summary
Update backend `README.md` with developer onboarding guide and complete endpoint overview.

### Requirements
- Document local Docker setup and database migration commands.
- Add summary table of REST endpoints for batches and verifications.
- Include curl examples for verifying medication batches.

---
