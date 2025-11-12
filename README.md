# **Lëb Lango API – Digital Dictionary & Cultural Library**

**Powered by Kakebe Technologies 🇺🇬**

Preserving, digitizing, and modernizing the **Lango language and culture** through technology.

---

## **Overview**

The **Lëb Lango API** is a full-stack, production-ready backend system built to power the  **Lëb Lango Dictionary** ,  **Cultural Library** , and related linguistic AI models.

It serves as the foundation for Lango digital translation tools, AI training datasets, and cultural preservation applications.

This API enables developers, linguists, and contributors to:

* Search and explore dictionary entries in Lëb Lango.
* Submit and manage cultural and literary content.
* Upload bulk data (CSV/JSON) for faster digitization.
* Track language usage analytics and contributor activity.
* Build modern mobile/web apps that integrate the Lango language into everyday digital experiences.

---

## **Core Features**

### Dictionary & Language Data

* Public dictionary search (`/api/public/v1/dictionary/search/`)
* Individual entry lookups (`/api/public/v1/dictionary/entry/<id>/`)
* Auto-suggest, lemma variants, and indexed fields
* Bulk dictionary import (CSV/JSON) for large datasets

### Library System

* Library submission and tracking endpoints
* Admin approval workflows for submitted content
* Library categories, events, and author tracking
* Support for local literature and cultural archives

### Authentication & Access Control

* JWT-based authentication (using SimpleJWT)
* Sign-up, login, refresh, and verify tokens
* Role-based permissions (`IsStaffUser`, `IsModerator`, etc.)
* Contributor and admin dashboards for moderation

### Analytics & Query Insights

* Logs all dictionary and library search queries
* Query health summary for "no results" detection
* Optional analytics visualization endpoints
* User activity tracking (views, downloads, submissions)

### System & DevOps

* Dockerized environment for isolated deployment
* Redis caching and Celery-ready background task structure
* PostgreSQL database with indexed and optimized queries
* Health checks (`/`, `/api/healthz/`) for monitoring
* API documentation via Swagger (`/api/docs/`) and Schema (`/api/schema/`)

### Performance & Reliability

* Global throttling for authenticated vs anonymous users
* Built-in pagination and ordering for heavy data endpoints
* Configurable error handler returning consistent JSON
* Fuzzy search with PostgreSQL Trigram (`pg_trgm`)
* OpenAPI 3.0 documentation ready for external integrations

## **Tech Stack**

| Layer                       | Technology                                    |
| --------------------------- | --------------------------------------------- |
| **Backend Framework** | Django 5.x, Django REST Framework             |
| **Database**          | PostgreSQL (optimized with pg_trgm & indexes) |
| **Caching & Queue**   | Redis (ready for Celery/async tasks)          |
| **Authentication**    | SimpleJWT (token-based access)                |
| **Containerization**  | Docker & Docker Compose                       |
| **Documentation**     | Swagger UI + OpenAPI Schema                   |
| **Deployment-ready**  | Render / Railway / AWS ECS compatible         |
| **Language**          | Python 3.11                                   |
| **Environment**       | `.env`with secrets + Docker volumes         |

## **Setup & Installation**

### Using Docker (Recommended)

<pre class="overflow-visible!" data-start="4302" data-end="4926"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span># 1. Clone repository</span><span>
git </span><span>clone</span><span> https://github.com/kakebetech/leblango.git
</span><span>cd</span><span> leblango

</span><span># 2. Copy environment variables</span><span>
</span><span>cp</span><span> .env.example .</span><span>env</span><span>

</span><span># 3. Build and start containers</span><span>
docker compose up --build

</span><span># 4. Run migrations</span><span>
docker compose </span><span>exec</span><span> leblango_backend_app python manage.py makemigrations
docker compose </span><span>exec</span><span> leblango_backend_app python manage.py migrate

</span><span># 5. (Optional) Create admin user</span><span>
docker compose </span><span>exec</span><span> leblango_backend_app python manage.py createsuperuser

</span><span># 6. Access system</span><span>
</span><span># API root</span><span>
http://localhost:6200/
</span><span># Swagger docs</span><span>
http://localhost:6200/api/docs/
</span><span># Admin panel</span><span>
http://localhost:6200/admin/</span></span></code></div></div></pre>

## **API Endpoints**

### **System**

| Method | Endpoint          | Description        |
| ------ | ----------------- | ------------------ |
| GET    | `/`             | System home status |
| GET    | `/api/healthz/` | Health check       |
| GET    | `/api/schema/`  | OpenAPI schema     |
| GET    | `/api/docs/`    | Swagger UI         |

### **Dictionary**

| Method | Endpoint                                     | Description       |
| ------ | -------------------------------------------- | ----------------- |
| GET    | `/api/public/v1/dictionary/search/?q=word` | Search dictionary |
| GET    | `/api/public/v1/dictionary/entry/<id>/`    | Get single entry  |
| POST   | `/api/admin/import/dictionary/csv/`        | Bulk upload CSV   |
| POST   | `/api/admin/import/dictionary/json/`       | Bulk upload JSON  |

### **Library**

| Method | Endpoint                                         | Description           |
| ------ | ------------------------------------------------ | --------------------- |
| GET    | `/api/library/search/?q=`                      | Search library        |
| POST   | `/api/library/submit/`                         | Submit new entry      |
| POST   | `/api/library/track/`                          | Track views/downloads |
| POST   | `/api/admin/library/submissions/<id>/approve/` | Approve submission    |
| POST   | `/api/admin/library/submissions/<id>/reject/`  | Reject submission     |

### **Analytics**

| Method | Endpoint                                      | Description          |
| ------ | --------------------------------------------- | -------------------- |
| GET    | `/api/admin/query-health/summary/`          | Query insights       |
| GET    | `/api/admin/analytics/dictionary/overview/` | Dictionary analytics |
| GET    | `/api/admin/analytics/library/overview/`    | Library analytics    |

### **Auth**

| Method | Endpoint                   | Description       |
| ------ | -------------------------- | ----------------- |
| POST   | `/api/auth/sign-up/`     | User registration |
| POST   | `/api/auth/sign-in/`     | Login             |
| POST   | `/api/auth/jwt/create/`  | Get access token  |
| POST   | `/api/auth/jwt/refresh/` | Refresh token     |
| POST   | `/api/auth/jwt/verify/`  | Verify token      |

---

## **Permissions & Roles**

| Role                    | Capabilities                                      |
| ----------------------- | ------------------------------------------------- |
| **Anonymous**     | Public read access to dictionary & library        |
| **Contributor**   | Submit and edit personal entries                  |
| **Moderator**     | Approve or reject user submissions                |
| **Admin / Staff** | Full access to imports, analytics, and moderation |

---

## **AI & Language Model Integration**

The API supports data export for use in:

* AI language modeling and translation training
* Voice-to-text and text-to-speech systems
* Dataset generation for local language NLP research

Data sources include validated contributions from:

* The **Lango Cultural Foundation**
* Verified local linguists and teachers
* Community contributors via the submission system

---

## **Monitoring & Analytics**

* Health status: `/api/healthz/`
* Query logs: stored via `SearchQueryLog` model
* Analytics summaries via `/api/admin/query-health/summary/`
* Redis integration for caching frequent searches (optional)

---

## **Fuzzy Search (Optional)**

Enable approximate search and typo tolerance by installing PostgreSQL Trigram extension:

<pre class="overflow-visible!" data-start="7324" data-end="7360"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-sql"><span><span>CREATE</span><span> EXTENSION pg_trgm;
</span></span></code></div></div></pre>

Then enable fuzzy lookup mode in settings:

<pre class="overflow-visible!" data-start="7404" data-end="7444"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-python"><span><span>ENABLE_FUZZY_SEARCH = </span><span>True</span><span>
</span></span></code></div></div></pre>

---

## **Testing**

<pre class="overflow-visible!" data-start="7470" data-end="7653"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span># Run Django checks</span><span>
docker compose run --</span><span>rm</span><span> leblango_backend_app python manage.py check

</span><span># Run API tests</span><span>
docker compose run --</span><span>rm</span><span> leblango_backend_app python manage.py </span><span>test</span><span>
</span></span></code></div></div></pre>

---

## **Deployment**

The system is Dockerized and can be deployed easily to:

* **Render**
* **Railway**
* **AWS ECS / Fargate**
* **DigitalOcean App Platform**

Use the same Docker configuration — just ensure your environment variables match production secrets.

---

## **Contributing**

We welcome contributions from:

* Lango teachers, translators, and linguists
* Software developers interested in African language tech
* Volunteers helping to expand and refine the dataset

To contribute:

1. Fork the repository
2. Create a branch: `git checkout -b feature/add-new-word`
3. Commit and push your changes
4. Open a Pull Request

---


## **License – Apache License 2.0**

<pre class="overflow-visible!" data-start="7514" data-end="8087"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>Copyright </span><span>2025</span><span> Kakebe Technologies Ltd.

Licensed under the Apache License, Version </span><span>2.0</span><span> (the "License");
you may </span><span>not</span><span> use this file </span><span>except</span><span></span><span>in</span><span> compliance </span><span>with</span><span> the License.
You may obtain a </span><span>copy</span><span></span><span>of</span><span> the License </span><span>at</span><span>:

    http:</span><span>/</span><span>/</span><span>www.apache.org</span><span>/</span><span>licenses</span><span>/</span><span>LICENSE</span><span>-2.0</span><span>

Unless required </span><span>by</span><span> applicable law </span><span>or</span><span> agreed </span><span>to</span><span></span><span>in</span><span> writing, software
distributed under the License </span><span>is</span><span> distributed </span><span>on</span><span> an "AS IS" BASIS,
</span><span>WITHOUT</span><span> WARRANTIES </span><span>OR</span><span> CONDITIONS </span><span>OF</span><span></span><span>ANY</span><span> KIND,
either express </span><span>or</span><span> implied. See the License </span><span>for</span><span> the </span><span>specific</span><span></span><span>language</span><span>
governing permissions </span><span>and</span><span> limitations under the License.
</span></span></code></div></div></pre>

> **Note:**
>
> This license allows Kakebe Technologies to retain intellectual property rights and seek patents for innovations or derived works while allowing limited open-source collaboration and reuse under compliance with Apache 2.0 terms.

---

## **Acknowledgments**

Developed under the  **Kakebe Technologies Limited, Language Digitization Initiative** , in partnership with cultural, educational, and community stakeholders.

**Core Team:**

* 👨‍💻 **Bodo Desderio Derrick** – *Lead Developer & Systems Architect*
* 👨‍💻 **Okello Patrick** – *Assistant Developer & Database Engineer*
* 👨‍💼 **Sedrick Otolo** – *Project Director, Strategy & Partnerships*

**Cultural & Linguistic Resources:**

* **Lango Cultural Foundation** – Source of verified linguistic and cultural material used for AI model training
* **General Public Contributors** – For sharing authentic language data and cultural content used in digitization efforts

---

## **Mission Statement**

> *“To preserve the Lango language and heritage through open digital innovation — enabling future generations to learn, speak, and interact with technology in their mother tongue.”*
>
