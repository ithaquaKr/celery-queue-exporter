# Makefile for celery-queue-exporter development

# Color codes for pretty output
BLUE := \033[1;34m
GREEN := \033[1;32m
RED := \033[1;31m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# Detect OS for cross-platform compatibility
ifeq ($(OS),Windows_NT)
	PYTHON := python
	RM := rmdir /s /q
	MKDIR := mkdir
	VENV_BIN := .venv\Scripts
else
	PYTHON := python3
	RM := rm -rf
	MKDIR := mkdir -p
	VENV_BIN := .venv/bin
endif

# Project settings
PROJECT_NAME := celery-queue-exporter
VENV_PATH := .venv
DOCKER_COMPOSE := docker compose -f docker/docker-compose.yml

.PHONY: help setup clean test test-unit test-e2e lint format type-check build docker-build docs docs-serve dev-env dev-env-down update-deps

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "$(BLUE)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

setup: ## Set up development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	$(PYTHON) -m venv $(VENV_PATH)
	$(VENV_BIN)/uv pip install -e ".[dev]"
	$(VENV_BIN)/pre-commit install
	@echo "$(GREEN)Development environment setup complete!$(NC)"

clean: ## Clean up build artifacts and temporary files
	@echo "$(BLUE)Cleaning up...$(NC)"
	$(RM) build dist *.egg-info .pytest_cache .coverage .mypy_cache .ruff_cache
	@echo "$(GREEN)Cleanup complete!$(NC)"

test: test-unit test-e2e ## Run all tests

test-unit: ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(VENV_BIN)/pytest tests/unit -v

test-e2e: ## Run end-to-end tests
	@echo "$(BLUE)Running end-to-end tests...$(NC)"
	$(VENV_BIN)/pytest tests/e2e -v

lint: ## Run code linting
	@echo "$(BLUE)Running linters...$(NC)"
	$(VENV_BIN)/ruff check .
	@echo "$(GREEN)Linting complete!$(NC)"

format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	$(VENV_BIN)/ruff format .
	@echo "$(GREEN)Formatting complete!$(NC)"

type-check: ## Run type checking
	@echo "$(BLUE)Running type checking...$(NC)"
	$(VENV_BIN)/mypy exporter
	@echo "$(GREEN)Type checking complete!$(NC)"

build: clean ## Build Python package
	@echo "$(BLUE)Building package...$(NC)"
	$(VENV_BIN)/uv pip build
	@echo "$(GREEN)Build complete!$(NC)"

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t $(PROJECT_NAME) -f docker/Dockerfile .
	@echo "$(GREEN)Docker build complete!$(NC)"

docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	cd docs && $(VENV_BIN)/mkdocs build
	@echo "$(GREEN)Documentation build complete!$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Starting documentation server...$(NC)"
	cd docs && $(VENV_BIN)/mkdocs serve

dev-env: ## Start development environment with Docker Compose
	@echo "$(BLUE)Starting development environment...$(NC)"
	./scripts/dev-setup.sh
	@echo "$(GREEN)Development environment is ready!$(NC)"
	@echo "$(YELLOW)Services:$(NC)"
	@echo "  - Celery Queue Exporter: http://localhost:9808/metrics"
	@echo "  - RabbitMQ Management: http://localhost:15672 (guest/guest)"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - Grafana: http://localhost:3000 (admin/admin)"

dev-env-down: ## Stop development environment
	@echo "$(BLUE)Stopping development environment...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)Development environment stopped!$(NC)"

update-deps: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	$(VENV_BIN)/uv pip compile --upgrade pyproject.toml -o uv.lock
	$(VENV_BIN)/uv pip sync uv.lock
	@echo "$(GREEN)Dependencies updated!$(NC)"

# Release targets
release-patch: ## Create a patch release
	@echo "$(BLUE)Creating patch release...$(NC)"
	$(VENV_BIN)/bump2version patch
	@echo "$(GREEN)Patch release created!$(NC)"

release-minor: ## Create a minor release
	@echo "$(BLUE)Creating minor release...$(NC)"
	$(VENV_BIN)/bump2version minor
	@echo "$(GREEN)Minor release created!$(NC)"

release-major: ## Create a major release
	@echo "$(BLUE)Creating major release...$(NC)"
	$(VENV_BIN)/bump2version major
	@echo "$(GREEN)Major release created!$(NC)"
