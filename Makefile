# Harborline Freight monorepo — developer shortcuts
SHELL := /bin/bash
ENV ?= staging
COMPOSE ?= docker compose

.PHONY: help up down logs seed test test-api test-web lint scan tf-plan tf-apply

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

up: ## Start the local stack
	$(COMPOSE) up -d --build

down: ## Stop the local stack
	$(COMPOSE) down

logs: ## Tail api + worker logs
	$(COMPOSE) logs -f api worker

seed: ## Load demo data into the local database
	cd api && python ../scripts/seed_dev_data.py

test: test-api test-web ## Run all tests

test-api:
	cd api && python -m pytest -q

test-web:
	cd web && npm test --silent

lint: ## ruff + eslint
	ruff check api scripts
	cd web && npm run lint

scan: ## Secret scan: working tree + full git history
	gitleaks dir . --no-banner --redact
	gitleaks git . --no-banner --redact

tf-plan: ## terraform plan (ENV=staging)
	cd infra/terraform/$(ENV) && terraform init -input=false && terraform plan -out=tfplan

tf-apply: ## terraform apply a saved plan (ENV=staging)
	cd infra/terraform/$(ENV) && terraform apply tfplan
