# LebLango API (Django REST Framework)

A production-grade API for the **Lëb Lango Dictionary and Cultural Library**, developed by **Kakebe Technologies** to preserve and digitize the Lango language using modern AI and translation systems.

---

## Features

- RESTful Dictionary API (`/api/public/v1/dictionary/search`)
- Library content management and tracking
- JWT Authentication (login, refresh, verify)
- Admin moderation and approval
- Swagger (`/api/docs/`) & ReDoc (`/api/redoc/`)
- Health checks (`/api/healthz`, `/api/health`)
- Throttling, pagination, caching, analytics logging
- Optional fuzzy search (pg_trgm for partial matches)

---

## Setup

```bash
git clone https://github.com/<your-org>/leblango.git
cd leblango
cp .env.example .env
docker compose up --build
docker compose exec backend python manage.py migrate
```
