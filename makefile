# Variables
TAG ?= latest
IMAGE_NAME = 752749714540.dkr.ecr.ap-south-1.amazonaws.com/divs/pancard-ocr

# Default goal
.DEFAULT_GOAL := help

.PHONY: run
run: ## Run the application locally with config
	@echo "Running application locally..."
	@uvicorn app.main:app --host 0.0.0.0 --port 8000

.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "Building Docker image $(IMAGE_NAME):$(TAG)..."
	@docker build -f Dockerfile -t $(IMAGE_NAME):$(TAG) .
	@echo "  Docker image $(IMAGE_NAME):$(TAG) built successfully."

.PHONY: docker-push
docker-push: ## Push Docker image to ECR
	@echo "Pushing Docker image $(IMAGE_NAME):$(TAG)..."
	@docker push $(IMAGE_NAME):$(TAG)
	@echo "  Docker image $(IMAGE_NAME):$(TAG) pushed successfully."

.PHONY: docker-login
docker-login: ## Authenticate Docker with AWS ECR
	@echo "Logging in to AWS ECR..."
	@aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 752749714540.dkr.ecr.ap-south-1.amazonaws.com
	@echo "  Logged in to AWS ECR."

.PHONY: help
help: ## Show available commands
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
