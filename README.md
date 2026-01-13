# Streamoid Marketplace

Backend service for onboarding seller files, defining marketplace schemas, and mapping seller data into marketplace templates. Built with Django + DRF, with MinIO for file storage.

## System design

### Components
- **API**: Django REST Framework with schema via drf-spectacular.
- **Storage**: SQLite by default; Docker Compose includes MySQL (not wired in by default).
- **Object store**: MinIO for seller file uploads.
- **Cron**: A lightweight cron server handles background tasks for the MVP.
- **Apps**:
  - `seller`: Sellers and their uploaded files (CSV/XLSX).
  - `marketplace`: Marketplace definitions and template schemas.
  - `mapping`: Links seller file headers to marketplace template keys.


### Data model (DB schema)
All models include `created_at` and `updated_at` timestamps via `BaseModel`.

- **Seller**
  - `id`, `name`, `bucket_name`
- **SellerFiles**
  - `id`, `seller_id`, `name`, `type`, `path`, `rows_count`, `headers`, `sample_rows`
- **Marketplace**
  - `id`, `name`
- **MarketplaceTemplate**
  - `id`, `marketplace_id`, `template`
- **Mappings**
  - `id`, `marketplace_template_id`, `seller_file_id`, `mappings`

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
- `/api/schema/` (schema)
- `/api/docs/` (Swagger UI)

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
1) Create .venv and install dependencies.
```
uv sync
```


3) Configure environment.
- Use `.env.local` for local development (loaded automatically).
- Ensure MinIO settings point to a running MinIO instance if you upload files.

4) Run migrations and start the server.
```
python streamoid/manage.py migrate
python streamoid/manage.py runserver 0.0.0.0:8000
```

Cron note:
- Ideally, a dedicated task server should be used. Something like a celery + rabbitmq/redis
- For simple MVP testing, a cron server is used instead to avoid extra moving parts.

### Docker (Compose)
From the repo root:
```
docker compose -f docker/docker-compose.yml up --build
```

Notes:
- The container uses `config.settings.production` and loads `.env` via Docker secrets.
- MinIO console: `http://localhost:9001` (default credentials `minioadmin` / `minioadmin`).
- MySQL container is included but Django defaults to SQLite unless you override `DATABASES`.

### Run unit tests
```
pytest
```

Or using Make:
```
make test
```
