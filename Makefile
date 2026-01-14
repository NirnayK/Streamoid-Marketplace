IMAGE_NAME ?= streamoid-marketplace
IMAGE_TAG  ?= latest
DOCKERFILE ?= docker/Dockerfile
COMPOSE_FILE ?= docker/docker-compose.yml
PLATFORM ?= linux/amd64
PYTHONPATH ?= streamoid
export PYTHONPATH

.PHONY: build run test local-run migrations migrate help compose-up compose-down compose-destroy compose-ps compose-logs

help: ## Show available Makefile targets with descriptions
	@echo "Available targets:"
	@grep -Eh '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-30s %s\n", $$1, $$2}'
	@echo ""


build: ## Build the Docker image.
	docker build --platform $(PLATFORM) -f $(DOCKERFILE) -t $(IMAGE_NAME):$(IMAGE_TAG) .


run: ## Run the Django development server.
	python streamoid/manage.py runserver 0.0.0.0:8000


test: ## Run the Django development server locally with auto-reload.
	pytest


migrations: ## Generate the new database migrations.
	python streamoid/manage.py makemigrations


migrate: ## Apply database migrations.
	python streamoid/manage.py migrate


compose-up: ## Start services using docker compose.
	docker compose -f $(COMPOSE_FILE) up -d


compose-down: ## Stop services using docker compose.
	docker compose -f $(COMPOSE_FILE) down


compose-destroy: ## Stop services and remove volumes (deletes database and minio data).
	docker compose -f $(COMPOSE_FILE) down -v


compose-ps: ## List running services using docker compose.
	docker compose -f $(COMPOSE_FILE) ps


compose-logs: ## View service logs using docker compose.
	docker compose -f $(COMPOSE_FILE) logs -f


zip: ## Generate a data.zip containing all relevant code.
	rm -f data.zip
	zip -r data.zip . -x "*.git*" "**/__pycache__/*" ".venv/*" ".pytest_cache/*" "streamoid/db.sqlite3" "streamoid/logs/*" "data.zip"
