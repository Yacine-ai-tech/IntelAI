# Makefile — OmniIntelOS Docker-first workflow

.PHONY: build build-all build-dev create create-all create-dev start stop status check logs dev-up dev-down tunnel tunnel-up tunnel-down cleanup automation-check

build: ## Build minimal core images (no containers started)
	./scripts/start_all.sh minimal

build-all: ## Build all images (including optional profiled services)
	./scripts/start_all.sh full

build-dev: ## Build development profile images
	docker compose --profile dev build --parallel backend-dev frontend-dev dev-proxy

create: ## Create core containers (no start)
	docker compose create postgres fastapi frontend

create-all: ## Create all standard containers (no start)
	docker compose --profile automation --profile monitoring --profile ai create postgres fastapi frontend n8n prometheus grafana omnitel-ocr omnitel-voice

create-dev: ## Create dev containers (no start)
	docker compose --profile dev create backend-dev frontend-dev dev-proxy

start: ## Start all standard services
	./scripts/start_containers.sh full

stop: ## Stop all running containers
	./scripts/stop_containers.sh

status: ## Show stack status and health
	./scripts/status.sh

check: status

cleanup: ## Deep cleanup for low storage (safe mode, keeps volumes)
	./scripts/cleanup_deep.sh

automation-check: ## Validate automation framework programmatically
	python3 ./scripts/automation_e2e.py

logs: ## Follow compose logs
	docker compose logs -f

dev-up: ## Run hot-reload development profile
	docker compose --profile dev up --remove-orphans

dev-down: ## Stop development profile
	docker compose --profile dev down

tunnel: ## Configure tunnel env defaults
	./scripts/tunnel.sh configure

tunnel-up: ## Start Cloudflare tunnel profile
	./scripts/tunnel.sh up

tunnel-down: ## Stop Cloudflare tunnel profiles
	./scripts/tunnel.sh down
