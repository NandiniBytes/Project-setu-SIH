# 🚀 Project Setu - Healthcare Platform Deployment Guide

## 🏥 Overview

Project Setu is a revolutionary healthcare terminology integration platform that bridges traditional Indian medicine (AYUSH) with modern global healthcare standards. This guide provides comprehensive deployment instructions for various environments.

---

## 🎯 Quick Start Deployment

### Option 1: Docker Compose (Recommended for Testing)

```bash
# Clone the repository
git clone https://github.com/NandiniBytes/Project-setu-SIH.git
cd "Project setu SIH"

# Create environment file
cp env.example .env
# Edit .env with your configuration

# Deploy with Docker Compose
chmod +x deploy.sh
./deploy.sh latest docker

# Access the application
# Frontend: http://localhost:8501
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Install dependencies
cd project_setu
pip install -r requirements.txt

# Start backend (Terminal 1)
python run_fastapi.py

# Start frontend (Terminal 2)
streamlit run streamlit_beautiful.py
```

---

## 🏗️ Production Deployment Options

### 1. 🐳 Docker Compose Production

#### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

#### Deployment Steps

```bash
# 1. Prepare environment
cp env.example .env
nano .env  # Configure production values

# 2. Deploy application
./deploy.sh latest docker

# 3. Deploy monitoring stack (optional)
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# 4. Access services
# Application: http://your-domain.com
# Monitoring: http://your-domain.com:3000 (Grafana)
# Metrics: http://your-domain.com:9090 (Prometheus)
```

#### Production Environment Variables

```bash
# Application
ENV=production
SECRET_KEY=your-256-bit-secret-key
DATABASE_URL=postgresql://user:pass@db:5432/project_setu

# WHO API (for live ICD-11 data)
WHO_CLIENT_ID=your-who-client-id
WHO_CLIENT_SECRET=your-who-client-secret

# ABHA Integration (Indian Health ID)
ABHA_API_URL=https://dev.abdm.gov.in
ABHA_CLIENT_ID=your-abha-client-id
ABHA_CLIENT_SECRET=your-abha-client-secret

# Monitoring
SMTP_USER=alerts@yourdomain.com
SMTP_PASSWORD=your-smtp-password
SLACK_WEBHOOK_URL=your-slack-webhook
```

### 2. ☸️ Kubernetes Deployment

#### Prerequisites
- Kubernetes 1.20+
- kubectl configured
- Helm 3.0+ (optional)
- Load balancer (for cloud deployments)

#### Deployment Steps

```bash
# 1. Create namespace
kubectl create namespace healthcare

# 2. Create secrets
kubectl create secret generic project-setu-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=secret-key="your-secret-key" \
  --from-literal=who-client-id="your-who-id" \
  --from-literal=who-client-secret="your-who-secret" \
  -n healthcare

# 3. Deploy application
kubectl apply -f deploy/kubernetes/deployment.yaml

# 4. Check deployment
kubectl get pods -n healthcare
kubectl get services -n healthcare

# 5. Access application
kubectl port-forward svc/project-setu-frontend-service 8501:8501 -n healthcare
```

#### Kubernetes Configuration

```yaml
# Custom values for production
apiVersion: v1
kind: ConfigMap
metadata:
  name: project-setu-config
  namespace: healthcare
data:
  ENV: "production"
  BACKEND_URL: "http://project-setu-backend-service:8000"
  LOG_LEVEL: "INFO"
```

### 3. 🌐 AWS ECS Deployment

#### Prerequisites
- AWS CLI configured
- ECS Cluster created
- ECR repositories created
- RDS database (optional)
- Application Load Balancer

#### Deployment Steps

```bash
# 1. Build and push images to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

docker build -t project-setu-backend .
docker build -t project-setu-frontend -f Dockerfile.streamlit .

docker tag project-setu-backend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/project-setu-backend:latest
docker tag project-setu-frontend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/project-setu-frontend:latest

docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/project-setu-backend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/project-setu-frontend:latest

# 2. Create ECS service
aws ecs create-service \
  --cluster project-setu-cluster \
  --service-name project-setu-service \
  --task-definition project-setu-healthcare \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"

# 3. Deploy using script
./deploy.sh latest aws
```

### 4. 🔷 Azure Container Instances

#### Prerequisites
- Azure CLI installed
- Azure Container Registry
- Azure Database for PostgreSQL (optional)

#### Deployment Steps

```bash
# 1. Login to Azure
az login

# 2. Create resource group
az group create --name project-setu-rg --location eastus

# 3. Build and push images
az acr build --registry projectsetuacr --image project-setu-backend:latest .
az acr build --registry projectsetuacr --image project-setu-frontend:latest -f Dockerfile.streamlit .

# 4. Deploy using Azure DevOps pipeline
# Use deploy/azure/azure-pipelines.yml

# 5. Create container instances
az container create \
  --resource-group project-setu-rg \
  --name project-setu-backend \
  --image projectsetuacr.azurecr.io/project-setu-backend:latest \
  --ports 8000 \
  --dns-name-label project-setu-api
```

### 5. 🟣 Heroku Deployment

#### Prerequisites
- Heroku CLI installed
- Heroku account

#### Deployment Steps

```bash
# 1. Login to Heroku
heroku login

# 2. Create applications
heroku create project-setu-backend
heroku create project-setu-frontend

# 3. Set environment variables
heroku config:set ENV=production -a project-setu-backend
heroku config:set SECRET_KEY=$(openssl rand -hex 32) -a project-setu-backend

# 4. Deploy using script
./deploy.sh latest heroku

# 5. Open applications
heroku open -a project-setu-backend
heroku open -a project-setu-frontend
```

---

## 🔧 Configuration Guide

### Database Configuration

#### PostgreSQL (Recommended for Production)
```bash
# Connection string
DATABASE_URL=postgresql://username:password@host:5432/database_name

# Connection pool settings (handled automatically)
# - Pool size: 20 connections
# - Max overflow: 30 connections
# - Connection recycling: 1 hour
```

#### MySQL Support
```bash
DATABASE_URL=mysql://username:password@host:3306/database_name
```

#### SQLite (Development Only)
```bash
DATABASE_URL=sqlite:///./project_setu.db
```

### Security Configuration

#### HTTPS/SSL Setup
```bash
# For production, use SSL certificates
# Place certificates in ssl/ directory
# Update nginx.conf for HTTPS configuration

# Generate self-signed certificates for testing
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem
```

#### CORS Configuration
```python
# In production, restrict CORS origins
CORS_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

### API Integration

#### WHO ICD-11 API Setup
```bash
# 1. Register at https://icd.who.int/icdapi
# 2. Get client credentials
# 3. Set environment variables
WHO_CLIENT_ID=your_client_id
WHO_CLIENT_SECRET=your_client_secret
WHO_API_URL=https://id.who.int
```

#### ABHA Integration (Indian Health ID)
```bash
# 1. Register with ABDM
# 2. Get sandbox/production credentials
# 3. Configure environment
ABHA_API_URL=https://dev.abdm.gov.in  # or prod URL
ABHA_CLIENT_ID=your_abha_client_id
ABHA_CLIENT_SECRET=your_abha_client_secret
```

---

## 📊 Monitoring & Observability

### Metrics & Monitoring

#### Prometheus + Grafana Stack
```bash
# Deploy monitoring stack
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Access dashboards
# Grafana: http://localhost:3000 (admin/admin123)
# Prometheus: http://localhost:9090
# AlertManager: http://localhost:9093
```

#### Key Metrics to Monitor
- **Response Time**: API response times < 200ms
- **Error Rate**: HTTP 5xx errors < 1%
- **Database Connections**: Active connections < 80
- **Memory Usage**: System memory < 90%
- **Disk Space**: Available space > 10%

### Logging

#### Centralized Logging with Loki
```bash
# Logs are automatically collected by Promtail
# View logs in Grafana Explore
# Query examples:
{job="project-setu-backend"} |= "ERROR"
{job="project-setu-frontend"} |= "health"
```

#### Application Logs
- **Backend**: `/app/logs/fastapi.log`
- **Frontend**: Streamlit console output
- **Audit**: Database audit table
- **Security**: Authentication logs

### Alerting

#### Critical Alerts
- Healthcare system down (1 minute)
- High error rate (> 10% for 3 minutes)
- Database connection failures
- Security breaches

#### Notification Channels
- Email notifications
- Slack integration
- SMS for critical alerts
- PagerDuty integration (optional)

---

## 🔒 Security Considerations

### Production Security Checklist

#### Infrastructure Security
- [ ] Use HTTPS/TLS encryption
- [ ] Configure firewall rules
- [ ] Enable VPC/network isolation
- [ ] Use secrets management
- [ ] Regular security updates

#### Application Security
- [ ] Strong JWT secret keys
- [ ] Input validation enabled
- [ ] Rate limiting configured
- [ ] CORS properly restricted
- [ ] Security headers enabled

#### Healthcare Compliance
- [ ] PHI data encryption
- [ ] Audit logging enabled
- [ ] Access controls configured
- [ ] HIPAA compliance measures
- [ ] Data backup procedures

#### ABHA Integration Security
- [ ] Secure API credentials
- [ ] Token refresh handling
- [ ] User consent management
- [ ] Audit trail compliance

---

## 🧪 Testing Deployment

### Health Checks

#### Application Health
```bash
# Backend health check
curl http://localhost:8000/health

# Frontend health check
curl http://localhost:8501/_stcore/health

# Database connectivity
curl http://localhost:8000/api/health/database
```

#### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API endpoints
ab -n 1000 -c 10 http://localhost:8000/api/CodeSystem/\$lookup?system=NAMASTE&code=NAMC001

# Test frontend
ab -n 100 -c 5 http://localhost:8501/
```

### Demo Scenarios

#### Authentication Testing
```bash
# Test ABHA login
curl -X POST http://localhost:8000/api/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=12-3456-7890-1234&password=testpassword"
```

#### Terminology Search
```bash
# Test medical term search
curl "http://localhost:8000/api/CodeSystem/\$lookup?system=NAMASTE&code=NAMC001"

# Test code mapping
curl "http://localhost:8000/api/ConceptMap/\$translate?system=NAMASTE&code=NAMC001&targetSystem=ICD11"
```

---

## 🚨 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000
netstat -tulpn | grep :8501

# Kill processes using ports
sudo kill -9 $(sudo lsof -t -i:8000)
sudo kill -9 $(sudo lsof -t -i:8501)
```

#### Database Connection Issues
```bash
# Check database connectivity
docker exec -it project-setu-backend python -c "
from database import engine
try:
    with engine.connect() as conn:
        result = conn.execute('SELECT 1')
        print('Database connection successful')
except Exception as e:
    print(f'Database error: {e}')
"
```

#### Memory Issues
```bash
# Check container memory usage
docker stats

# Increase memory limits in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

#### SSL Certificate Issues
```bash
# Generate new self-signed certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem \
  -subj "/C=IN/ST=Maharashtra/L=Mumbai/O=ProjectSetu/CN=localhost"
```

### Log Analysis

#### Backend Logs
```bash
# View backend logs
docker logs project-setu-backend -f

# Search for errors
docker logs project-setu-backend 2>&1 | grep ERROR

# Check specific timeframe
docker logs project-setu-backend --since="2024-01-01T00:00:00" --until="2024-01-01T23:59:59"
```

#### Database Logs
```bash
# PostgreSQL logs
docker logs postgres-container -f

# Check slow queries
docker exec -it postgres-container psql -U username -d database_name -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"
```

---

## 📈 Performance Optimization

### Database Optimization

#### Indexing Strategy
```sql
-- Create indexes for frequently queried fields
CREATE INDEX idx_namaste_code ON medical_concepts(code);
CREATE INDEX idx_namaste_display ON medical_concepts(display);
CREATE INDEX idx_mapping_source ON concept_mappings(source_code);
CREATE INDEX idx_mapping_target ON concept_mappings(target_code);
```

#### Connection Pooling
```python
# Production database settings
SQLALCHEMY_DATABASE_URI = "postgresql://user:pass@host:5432/db"
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
}
```

### Application Optimization

#### Caching Strategy
```python
# Redis caching for frequent queries
REDIS_URL = "redis://localhost:6379/0"
CACHE_TTL = 3600  # 1 hour

# Enable response caching
@lru_cache(maxsize=1000)
def get_medical_concept(code: str):
    # Cached function implementation
    pass
```

#### Load Balancing
```yaml
# nginx load balancing
upstream backend {
    server backend1:8000 weight=3;
    server backend2:8000 weight=2;
    server backend3:8000 weight=1;
}
```

---

## 🔄 Maintenance & Updates

### Regular Maintenance Tasks

#### Daily Tasks
- Monitor system health
- Check error logs
- Verify backup completion
- Review security alerts

#### Weekly Tasks
- Update security patches
- Review performance metrics
- Clean up old logs
- Test backup restoration

#### Monthly Tasks
- Update dependencies
- Review access logs
- Performance optimization
- Security audit

### Update Procedures

#### Application Updates
```bash
# 1. Backup current deployment
docker-compose exec backend python backup_database.py

# 2. Pull latest changes
git pull origin main

# 3. Rebuild and deploy
./deploy.sh latest docker

# 4. Verify deployment
curl http://localhost:8000/health
```

#### Database Migrations
```bash
# Run database migrations
docker-compose exec backend python -c "
from database_production import run_migrations
run_migrations()
"
```

---

## 📞 Support & Contact

### Getting Help

#### Documentation
- [API Documentation](http://localhost:8000/docs)
- [User Manual](project_setu/MANUAL_TESTING_SCENARIOS.md)
- [Testing Guide](project_setu/TESTING_GUIDE.md)

#### Community Support
- GitHub Issues: [Report Issues](https://github.com/NandiniBytes/Project-setu-SIH/issues)
- Discussions: [Community Forum](https://github.com/NandiniBytes/Project-setu-SIH/discussions)

#### Professional Support
- Email: nhemantjani@supervity.ai
- Healthcare Integration: Specialized support for EHR integration
- Custom Deployment: Enterprise deployment assistance

---

## 🎯 Success Metrics

### Deployment Success Indicators

#### Technical Metrics
- ✅ All services running (Backend, Frontend, Database)
- ✅ Health checks passing
- ✅ Response times < 200ms
- ✅ Error rates < 1%
- ✅ Database connections stable

#### Healthcare Metrics
- ✅ FHIR validation passing
- ✅ Terminology mappings accurate
- ✅ ABHA authentication working
- ✅ Audit logging functional
- ✅ Security compliance met

#### User Experience Metrics
- ✅ Frontend loading < 3 seconds
- ✅ Search results < 1 second
- ✅ AI diagnostics responsive
- ✅ Mobile compatibility working
- ✅ Accessibility standards met

---

**🏥 Project Setu is now ready for production deployment! Your healthcare terminology integration platform is equipped with enterprise-grade security, monitoring, and scalability features.**

*Made with ❤️ for advancing healthcare interoperability and preserving traditional medical wisdom*
