IMAGE_NAME ?= streamoid-marketplace
DOCKERFILE ?= docker/Dockerfile
PYTHONPATH ?= streamoid
export PYTHONPATH

.PHONY: build run test local-run migrations migrate help

help: ## Show available Makefile targets with descriptions
	@echo "Available targets:"
	@grep -Eh '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-30s %s\n", $$1, $$2}'
	@echo ""


build: ## Build the Docker image.
	docker build -f $(DOCKERFILE) -t $(IMAGE_NAME) .


run: ## Run the Django development server.
	python streamoid/manage.py runserver 0.0.0.0:8000


test: ## Run the Django development server locally with auto-reload.
	pytest


migrations: ## Generate the new database migrations.
	python streamoid/manage.py makemigrations


migrate: ## Apply database migrations.
	python streamoid/manage.py migrate
