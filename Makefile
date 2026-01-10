IMAGE_NAME ?= streamoid-marketplace
DOCKERFILE ?= docker/Dockerfile

.PHONY: build run test local-run

build:
	docker build -f $(DOCKERFILE) -t $(IMAGE_NAME) .

run:
	python streamoid/manage.py runserver 0.0.0.0:8000

test:
	python streamoid/manage.py test
