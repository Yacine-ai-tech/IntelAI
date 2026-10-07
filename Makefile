# IntelAI — single cloud app.
.PHONY: help dev run test seed eval build deploy-info

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n",$$1,$$2}'

dev: ## Local dev: app-only container with hot reload (Neon DB via .env)
	docker compose -f docker-compose.dev.yml up --build

run: ## Local full stack: app + bundled Postgres
	docker compose up --build

test: ## Run the test suite
	python -m pytest tests/ -q

seed: ## Seed deterministic demo data (KPIs + knowledge docs) into Postgres
	python -m src.data.seed

eval: ## Run the RAG prompt-eval (groundedness/recall gate)
	python -m src.data.rag_eval

build: ## Build the app image
	docker build -t intelai:latest .

deploy-info: ## How IntelAI deploys
	@echo "IntelAI deploys as a containerized service built from the Dockerfile."
	@echo "Production backend runs on Contabo VPS behind Caddy/Cloudflare Edge with Neon Postgres & Qdrant."
	@echo "Frontend deploys separately to Vercel (https://intelai-ui-2026.vercel.app)."
