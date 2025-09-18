#!/bin/bash

# Project Setu - Healthcare Platform Deployment Script
# Supports multiple deployment targets: Docker, Kubernetes, AWS, Azure, Heroku

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="project-setu"
VERSION=${1:-latest}
DEPLOYMENT_TARGET=${2:-docker}

echo -e "${BLUE}🏥 Project Setu Healthcare Platform Deployment${NC}"
echo -e "${BLUE}=================================================${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if [ "$DEPLOYMENT_TARGET" = "kubernetes" ] && ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    if [ "$DEPLOYMENT_TARGET" = "heroku" ] && ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI is not installed. Please install Heroku CLI first."
        exit 1
    fi
    
    print_status "Prerequisites check passed ✅"
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build backend image
    print_status "Building backend image..."
    docker build -t ${PROJECT_NAME}-backend:${VERSION} -f Dockerfile .
    
    # Build frontend image
    print_status "Building frontend image..."
    docker build -t ${PROJECT_NAME}-frontend:${VERSION} -f Dockerfile.streamlit .
    
    print_status "Docker images built successfully ✅"
}

# Deploy with Docker Compose
deploy_docker() {
    print_status "Deploying with Docker Compose..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        cp env.example .env
        print_warning "Please edit .env file with your production values before running again."
        exit 1
    fi
    
    # Deploy with docker-compose
    docker-compose up -d
    
    print_status "Deployment completed! ✅"
    print_status "Backend API: http://localhost:8000"
    print_status "Frontend App: http://localhost:8501"
    print_status "API Docs: http://localhost:8000/docs"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    print_status "Deploying to Kubernetes..."
    
    # Create namespace
    kubectl create namespace healthcare --dry-run=client -o yaml | kubectl apply -f -
    
    # Create secrets (you need to create these manually)
    print_warning "Please ensure you have created the required secrets:"
    print_warning "kubectl create secret generic project-setu-secrets --from-literal=database-url=... --from-literal=secret-key=..."
    
    # Apply deployments
    kubectl apply -f deploy/kubernetes/deployment.yaml
    
    print_status "Kubernetes deployment completed! ✅"
    print_status "Check status with: kubectl get pods -n healthcare"
}

# Deploy to Heroku
deploy_heroku() {
    print_status "Deploying to Heroku..."
    
    # Check if Heroku app exists
    if ! heroku apps:info $PROJECT_NAME-backend &> /dev/null; then
        print_status "Creating Heroku apps..."
        heroku create $PROJECT_NAME-backend
        heroku create $PROJECT_NAME-frontend
    fi
    
    # Set environment variables
    heroku config:set ENV=production -a $PROJECT_NAME-backend
    heroku config:set SECRET_KEY=$(openssl rand -hex 32) -a $PROJECT_NAME-backend
    
    # Deploy backend
    git subtree push --prefix=project_setu heroku main
    
    print_status "Heroku deployment completed! ✅"
    print_status "Backend: https://$PROJECT_NAME-backend.herokuapp.com"
    print_status "Frontend: https://$PROJECT_NAME-frontend.herokuapp.com"
}

# Deploy to AWS ECS
deploy_aws() {
    print_status "Deploying to AWS ECS..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install AWS CLI first."
        exit 1
    fi
    
    # Build and push to ECR
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
    
    docker tag ${PROJECT_NAME}-backend:${VERSION} 123456789012.dkr.ecr.us-east-1.amazonaws.com/${PROJECT_NAME}-backend:${VERSION}
    docker tag ${PROJECT_NAME}-frontend:${VERSION} 123456789012.dkr.ecr.us-east-1.amazonaws.com/${PROJECT_NAME}-frontend:${VERSION}
    
    docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/${PROJECT_NAME}-backend:${VERSION}
    docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/${PROJECT_NAME}-frontend:${VERSION}
    
    # Update ECS service
    aws ecs update-service --cluster project-setu-cluster --service project-setu-service --force-new-deployment
    
    print_status "AWS ECS deployment completed! ✅"
}

# Main deployment logic
main() {
    check_prerequisites
    build_images
    
    case $DEPLOYMENT_TARGET in
        docker)
            deploy_docker
            ;;
        kubernetes|k8s)
            deploy_kubernetes
            ;;
        heroku)
            deploy_heroku
            ;;
        aws)
            deploy_aws
            ;;
        *)
            print_error "Unknown deployment target: $DEPLOYMENT_TARGET"
            print_status "Supported targets: docker, kubernetes, heroku, aws"
            exit 1
            ;;
    esac
    
    print_status "🎉 Project Setu deployment completed successfully!"
    print_status "Your healthcare platform is now running and ready to serve patients!"
}

# Run main function
main
