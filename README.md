# Streamoid Marketplace

Backend service for onboarding seller files, defining marketplace schemas, and mapping seller data into marketplace templates. Built with Django + DRF, with MinIO for file storage.

## System design

### Components
- **API**: Django REST Framework with schema via drf-spectacular.
- **Storage**:
  - **Local**: SQLite by default (`db.sqlite3`).
  - **Production/Docker**: MySQL (configured in `production.py`).
- **Object store**: MinIO for seller file uploads.
- **Background Tasks**: A lightweight cron server (`django-crontab`) handles background tasks for the MVP.
- **Apps**:
  - `seller`: Sellers and their uploaded files (CSV/XLSX).
  - `marketplace`: Marketplace definitions and template schemas.
  - `mapping`: Links seller file headers to marketplace template keys (Transformation engine).

### Environment Configuration
The project uses `DJANGO_ENV` to switch between `local` and `production` settings.
- **Local**: Loads `.env.local`. Default DB is SQLite.
- **Production**: Loads `.env` and Docker secrets. Default DB is MySQL.

### Data model (DB schema)
All models include `created_at` and `updated_at` timestamps via `BaseModel`.

- **Seller**
  - `id`, `name`, `bucket_name`
- **SellerFiles**
  - `id`, `seller_id`, `name`, `type`, `path`, `rows_count`, `headers`, `sample_rows`
- **Marketplace**
  - `id`, `name`
- **MarketplaceTemplate**
  - `id`, `marketplace_id`, `template` (JSON validation schema)
- **Mappings**
  - `id`, `marketplace_template_id`, `seller_file_id`, `mappings` (Header-to-key map)

### Marketplace template format
Templates are JSON objects where each key defines a validation rule for a marketplace field.

Example:
```
{
  "productName": { "type": "string", "maxLength": 150, "required": true },
  "brand": { "type": "string", "required": true },
  "gender": { "type": "enum", "choices": ["Men", "Women", "Boys", "Girls", "Unisex"] },
  "mrp": { "type": "number", "min": 0, "required": true },
  "price": { "type": "number", "min": 0, "max": "$mrp", "required": true },
  "images": { "type": "array", "items": { "type": "url" } },
  "sku": { "type": "string", "unique": true, "required": true }
}
```

Notes:
- `max`/`min` can reference other fields using `$fieldName`.
- `array` fields accept multiple values from mapped rows.

## API documentation

Base URL: `/api/v1`

OpenAPI:
- `/api/schema/` (OpenAPI Spec)
- `/api/docs/` (Swagger UI - **Includes Request Snippets/cURL**)

### Authentication

The API is configured to support Bearer token authentication. 

> [!NOTE]
> In this MVP, authentication is handled at the service level. The instructions below describe how to generate a token that follows the standard Bearer pattern.

To create a bearer token:
1. Create a Django user:
   ```bash
   python streamoid/manage.py createsuperuser
   ```
2. Encode the `username:password` string in Base64.
3. Use the result in the `Authorization` header:
   `Authorization: Bearer <base64_encoded_string>`

### Response envelope
Single item:
```
{
  "code": 200,
  "data": {},
  "errors": {},
  "message": "Success"
}
```

List response (pagination fields always included):
```
{
  "code": 200,
  "data": [],
  "errors": {},
  "message": "Success",
  "total_page_number": 1,
  "total_count": 2
}
```

Pagination:
- `page_number` and `page_size` must be provided together.

## Setup and usage

### Local setup
1. **Initialize Environment**:
   ```bash
   uv sync
   ```
2. **Database Migrations**:
   ```bash
   make migrate
   ```
3. **Run Development Server**:
   ```bash
   make run
   ```
   Access at `http://localhost:8000`.

### Makefile Targets
A `Makefile` is provided for common tasks:
| Target | Description |
| :--- | :--- |
| `make run` | Run the Django development server locally |
| `make test` | Run unit tests with `pytest` |
| `make migrations` | Generate new database migrations |
| `make migrate` | Apply database migrations |
| `make build` | Build the Docker image |
| `make compose-up` | Start services via Docker Compose |
| `make compose-down` | Stop services via Docker Compose |
| `make compose-destroy`| Stop services and **delete all data** (DB/MinIO) |
| `make zip` | Package code into `data.zip` for submission |

### Docker (Compose)
From the repo root:
```bash
make compose-up
```

Notes:
- The container uses `config.settings.production`.
- MinIO console: `http://localhost:9001` (Credentials: `minioadmin` / `minioadmin`).
- Database: MySQL is used within Docker. Persistent data is stored in Docker volumes.

### Development Utilities
- **Run Tests**: `make test`
- **Linting**: Ruff is used (configured in `pyproject.toml`).
- **Submit Code**: `make zip` generates a `data.zip` excluding unnecessary files.

---

*Note on Cron*: For the MVP, background tasks are handled via `django-crontab`. Ensure the cron thread is running or use `make run` which includes the scheduler if configured.
