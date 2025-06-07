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

# Docker multi-platform settings
DOCKER_REGISTRY ?=
DOCKER_TAG ?= latest
DOCKER_PLATFORMS := linux/amd64,linux/arm64
DOCKER_BUILDER := $(PROJECT_NAME)-builder
DOCKERFILE_PATH := docker/Dockerfile

# Detect current platform for local builds
CURRENT_PLATFORM := $(shell docker version --format '{{.Server.Os}}/{{.Server.Arch}}')

# Default target
.DEFAULT_GOAL := help

##@ Other
.PHONY: help
help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(YELLOW)Usage:$(NC)\n  make $(BLUE)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development
setup: ## Set up development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	$(PYTHON) -m venv $(VENV_PATH)
	$(VENV_BIN)/uv pip install -e ".[dev]"
	$(VENV_BIN)/pre-commit install
	@echo "$(GREEN)Development environment setup complete!$(NC)"

clean: ## Clean up build artifacts, docker buildx resources and temporary files
	@echo "$(BLUE)Cleaning up...$(NC)"
	@echo "$(BLUE)Cleaning up python temporary files ..."
	$(RM) .pytest_cache .coverage .mypy_cache .ruff_cache
	@echo "$(BLUE)Cleaning up Docker buildx resources...$(NC)"
	@if docker buildx ls | grep -q $(DOCKER_BUILDER); then \
		docker buildx rm $(DOCKER_BUILDER); \
		echo "$(GREEN)Buildx builder $(DOCKER_BUILDER) removed$(NC)"; \
	fi
	@echo "$(GREEN)Cleanup complete!$(NC)"

lint: ## Run code linting
	@echo "$(BLUE)Running linters...$(NC)"
	$(VENV_BIN)/ruff check .
	@echo "$(GREEN)Linting complete!$(NC)"

format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	$(VENV_BIN)/ruff format .
	@echo "$(GREEN)Formatting complete!$(NC)"

##@ Build
docker-build: ## Build Docker image for current platform only (fast)
	@echo "$(BLUE)Building Docker image for current platform ($(CURRENT_PLATFORM))...$(NC)"
	docker build -t $(DOCKER_REGISTRY)/$(PROJECT_NAME):$(DOCKER_TAG) -f $(DOCKERFILE_PATH) .
	@echo "$(GREEN)Docker build complete!$(NC)"

docker-multi: ## Build multi-platform Docker images
	@echo "$(BLUE)Setting up Docker buildx for multi-platform builds...$(NC)"
	@if ! docker buildx ls | grep -q $(DOCKER_BUILDER); then \
		echo "$(YELLOW)Creating new buildx builder: $(DOCKER_BUILDER)$(NC)"; \
		docker buildx create --name $(DOCKER_BUILDER) --platform $(DOCKER_PLATFORMS) --use; \
	else \
		echo "$(YELLOW)Using existing buildx builder: $(DOCKER_BUILDER)$(NC)"; \
		docker buildx use $(DOCKER_BUILDER); \
	fi
	@docker buildx inspect --bootstrap
	@echo "$(GREEN)Docker buildx setup complete!$(NC)"
	@echo "$(BLUE)Building multi-platform Docker images...$(NC)"
	@echo "$(YELLOW)Platforms: $(DOCKER_PLATFORMS)$(NC)"
	docker buildx build \
		--platform $(DOCKER_PLATFORMS) \
		--tag $(DOCKER_REGISTRY)/$(PROJECT_NAME):$(DOCKER_TAG) \
		--file $(DOCKERFILE_PATH) \
		--load \
		.
	@echo "$(GREEN)Multi-platform Docker build complete!$(NC)"

docker-push: ## Push images to registry
	@if [ -z "$(DOCKER_REGISTRY)" ]; then \
		echo "$(RED)Error: DOCKER_REGISTRY is not set. Use: make docker-push DOCKER_REGISTRY=your-registry/$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Pushing images to registry $(DOCKER_REGISTRY)...$(NC)"
	docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME):$(DOCKER_TAG)
	@echo "$(GREEN)Docker push complete!$(NC)"

docker-info: ## Show Docker build configuration
	@echo "$(BLUE)Docker Build Configuration:$(NC)"
	@echo "  Project Name: $(GREEN)$(PROJECT_NAME)$(NC)"
	@echo "  Docker Tag: $(GREEN)$(DOCKER_TAG)$(NC)"
	@echo "  Registry: $(GREEN)$(DOCKER_REGISTRY)$(NC)"
	@echo "  Platforms: $(GREEN)$(DOCKER_PLATFORMS)$(NC)"
	@echo "  Builder: $(GREEN)$(DOCKER_BUILDER)$(NC)"
	@echo "  Current Platform: $(GREEN)$(CURRENT_PLATFORM)$(NC)"
	@echo "  Dockerfile: $(GREEN)$(DOCKERFILE_PATH)$(NC)"
