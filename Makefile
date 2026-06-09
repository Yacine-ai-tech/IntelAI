# IntelAI — single cloud app. (The old multi-service platform Makefile lives in OmniIntelOS.)
.PHONY: help dev run test build deploy-info

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n",$$1,$$2}'

dev: ## Studio dev: app-only container with hot reload (Neon DB via .env)
	docker compose -f docker-compose.dev.yml up --build

run: ## Local full stack: app + bundled Postgres
	docker compose up --build

test: ## Run the test suite
	python -m pytest tests/ -q

build: ## Build the app image
	docker build -t intelai:latest .

deploy-info: ## How IntelAI deploys
	@echo "IntelAI deploys as ONE cloud service built from the Dockerfile (see railway.toml)."
	@echo "Railway/Fly: connect the repo; set env vars POSTGRES_URL, GROQ_API_KEY,"
	@echo "ANTHROPIC_API_KEY, TAVILY_API_KEY, SECRET_KEY. Frontend deploys separately (Vercel/Netlify)."
