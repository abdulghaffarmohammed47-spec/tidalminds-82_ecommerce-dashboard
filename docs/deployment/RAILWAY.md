# Railway deployment

This repository contains separate React and FastAPI services. Deploy both from
the same GitHub repository, with the PostgreSQL and Redis services in the same
Railway project. MongoDB may be hosted separately (for example, on MongoDB
Atlas).

## Create the services

1. Create a Railway project and connect this GitHub repository.
2. Add a PostgreSQL service and a Redis service. The PostgreSQL instance must
   provide the `vector` extension used by the Alembic migrations.
3. Add a backend service from this repository:
   - Root directory: `/backend`
   - Dockerfile path: `Dockerfile.railway`
   - Generate a public domain only if you want to call the API directly; the
     frontend uses the backend's private network address.
4. Add a frontend service from this repository:
   - Root directory: `/frontend`
   - Dockerfile path: `Dockerfile.railway`
   - Generate a public domain for the storefront.

## Configure variables

Set these on the backend service using Railway's variable references:

| Variable | Value |
|---|---|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` |
| `MONGO_URL` | MongoDB connection URI |
| `MONGO_DB` | MongoDB database name |
| `JWT_SECRET` | A newly generated, high-entropy secret |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` |
| `PORT` | `8000` |

The backend accepts Railway's `postgres://` and `postgresql://` connection URL
formats and converts them to the async SQLAlchemy driver format. The backend
container applies Alembic migrations before starting Uvicorn. A failed
migration prevents the service from starting.

Set these on the frontend service:

| Variable | Value |
|---|---|
| `BACKEND_URL` | `http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:8000` |

Replace `Postgres`, `Redis`, and `backend` in the references if your Railway
service names differ. The frontend Nginx server uses Railway's injected `PORT`,
serves the Vite build, proxies `/api/*` and `/health*` to the backend, and
provides SPA route fallback.

Generate a secret locally rather than reusing the development value:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Do not commit production connection strings or secrets. Set the production
`CORS_ORIGINS` to any additional trusted browser origins if the API is accessed
outside the same-origin frontend proxy.

## Deploy and verify

Deploy PostgreSQL and Redis first, then the backend, and finally the frontend.
The first backend deploy runs the database migrations. Check the backend's
`/health` endpoint and the storefront's home, product, search, login, cart, and
checkout routes. Seed demo catalog data only when desired; this project uses
synthetic data and its checkout payment provider is simulated, not a live
payment processor.

Railway account access and production secrets are required to create the live
services. Keep database backups enabled before accepting real customer data.
