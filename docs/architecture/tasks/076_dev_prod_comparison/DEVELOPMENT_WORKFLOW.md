# 🚀 Development Workflow Guide

## 📋 **Current Architecture Overview**

### **Backend (API) - Containerized ✅**

- **Container**: `personal_assistant_api` (dev) / `personal_assistant_api_prod` (prod)
- **Port**: 8000 (exposed)
- **Technology**: FastAPI (Python)
- **Status**: Fully containerized and working

### **Frontend - Mixed Setup ⚠️**

- **Technology**: React + TypeScript + Vite
- **Development**: Runs on port 3001 with proxy to API
- **Production**: Static files served by nginx
- **Issue**: Missing nginx configuration for frontend serving

### **Infrastructure Services - Containerized ✅**

- **Database**: PostgreSQL 15.14
- **Cache**: Redis 7
- **Reverse Proxy**: Nginx
- **Monitoring**: Prometheus + Grafana + Loki
- **Workers**: Celery workers and scheduler

---

## 🔄 **Recommended Development Workflow**

### **Phase 1: Local Development Setup**

#### **1. Backend Development**

```bash
# Start backend services
cd docker
docker-compose -f docker-compose.dev.yml up -d postgres redis api worker scheduler

# Check status
docker ps | grep personal_assistant

# View logs
docker logs personal_assistant_api -f
```

#### **2. Frontend Development**

```bash
# Start frontend development server
cd src/apps/frontend
npm install
npm run dev

# Frontend runs on http://localhost:3001
# Proxies API calls to http://localhost:8000
```

#### **3. Full Stack Development**

```bash
# Terminal 1: Backend services
cd docker && docker-compose -f docker-compose.dev.yml up -d

# Terminal 2: Frontend development
cd src/apps/frontend && npm run dev

# Access:
# Frontend: http://localhost:3001
# API: http://localhost:8000
# Database: localhost:5432
```

### **Phase 2: Testing & Validation**

#### **1. Backend Testing**

```bash
# Run backend tests
cd src
python -m pytest tests/ -v

# Run specific test suites
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
```

#### **2. Frontend Testing**

```bash
# Run frontend tests
cd src/apps/frontend
npm run test
npm run test:coverage
```

#### **3. End-to-End Testing**

```bash
# Test full stack integration
cd tests/e2e
python -m pytest -v
```

### **Phase 3: Production Simulation**

#### **1. Build Frontend for Production**

```bash
# Build frontend static files
cd src/apps/frontend
npm run build

# This creates dist/ folder with static files
```

#### **2. Test Production-like Environment**

```bash
# Start production-like environment
cd docker
docker-compose -f docker-compose.prod.yml up -d

# Test production endpoints
curl http://localhost/api/health
curl http://localhost/  # Should serve frontend
```

---

## 🛠️ **Development Scripts Needed**

### **1. Quick Start Script**

```bash
#!/bin/bash
# scripts/dev-start.sh

echo "🚀 Starting Personal Assistant Development Environment..."

# Start backend services
cd docker
docker-compose -f docker-compose.dev.yml up -d postgres redis api worker scheduler loki

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker ps --format "table {{.Names}}\t{{.Status}}"

echo "✅ Backend services started!"
echo "🌐 API available at: http://localhost:8000"
echo "📊 Monitoring at: http://localhost:3000 (Grafana)"
echo "📝 Logs at: http://localhost:3100 (Loki)"

echo ""
echo "🎯 Next steps:"
echo "1. Start frontend: cd src/apps/frontend && npm run dev"
echo "2. Access frontend: http://localhost:3001"
```

### **2. Frontend Development Script**

```bash
#!/bin/bash
# scripts/frontend-dev.sh

echo "🎨 Starting Frontend Development..."

cd src/apps/frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start development server
echo "🚀 Starting Vite development server..."
npm run dev
```

### **3. Full Stack Test Script**

```bash
#!/bin/bash
# scripts/test-full-stack.sh

echo "🧪 Running Full Stack Tests..."

# Backend tests
echo "🔧 Running backend tests..."
cd src
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v

# Frontend tests
echo "🎨 Running frontend tests..."
cd apps/frontend
npm run test:run

# E2E tests
echo "🌐 Running E2E tests..."
cd ../../tests/e2e
python -m pytest -v

echo "✅ All tests completed!"
```

### **4. Production Build Script**

```bash
#!/bin/bash
# scripts/build-production.sh

echo "🏗️ Building for Production..."

# Build frontend
echo "🎨 Building frontend..."
cd src/apps/frontend
npm run build

# Copy frontend to nginx html directory
echo "📁 Copying frontend to nginx..."
cp -r dist/* ../../docker/nginx/html/

# Build Docker images
echo "🐳 Building Docker images..."
cd ../../docker
docker-compose -f docker-compose.prod.yml build

echo "✅ Production build complete!"
echo "🚀 Deploy with: docker-compose -f docker-compose.prod.yml up -d"
```

---

## 🔧 **Missing Configuration Fixes**

### **1. Fix Nginx Frontend Serving**

Create `/docker/nginx/conf.d/locations/frontend.conf`:

```nginx
# Frontend static files
location / {
    root /usr/share/nginx/html;
    try_files $uri $uri/ /index.html;
    index index.html;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
}

# API routes (already exists in api.conf)
location /api/ {
    proxy_pass http://api_backend;
    # ... existing proxy configuration
}
```

### **2. Update Docker Compose for Development**

Add frontend volume mount to dev nginx:

```yaml
# In docker-compose.dev.yml
nginx:
  volumes:
    - ./nginx/html:/usr/share/nginx/html:ro # Add this line
    - ./nginx/ssl/dev:/etc/nginx/ssl:ro
    - ./nginx/logs:/var/log/nginx
    - ./nginx/conf.d:/etc/nginx/conf.d:ro
```

---

## 📊 **Development Environment Comparison**

| Component       | Development                 | Production               | Status          |
| --------------- | --------------------------- | ------------------------ | --------------- |
| **Backend API** | Container (port 8000)       | Container (port 8000)    | ✅ Working      |
| **Frontend**    | Vite dev server (port 3001) | Nginx static files       | ⚠️ Needs config |
| **Database**    | Container (port 5432)       | Container (port 5432)    | ✅ Working      |
| **Redis**       | Container (port 6379)       | Container (port 6379)    | ✅ Working      |
| **Nginx**       | Container (ports 8081/8445) | Container (ports 80/443) | ✅ Working      |
| **Monitoring**  | Grafana (port 3000)         | Grafana (port 3000)      | ✅ Working      |
| **Logging**     | Loki (port 3100)            | Loki (port 3100)         | ✅ Working      |

---

## 🎯 **Recommended Workflow Steps**

### **Daily Development:**

1. **Start Backend**: `./scripts/dev-start.sh`
2. **Start Frontend**: `./scripts/frontend-dev.sh`
3. **Develop**: Make changes, test locally
4. **Test**: `./scripts/test-full-stack.sh`

### **Before Production Deploy:**

1. **Build**: `./scripts/build-production.sh`
2. **Test Production**: `docker-compose -f docker-compose.prod.yml up -d`
3. **Validate**: Test all endpoints and functionality
4. **Deploy**: Push to production environment

### **Key Differences to Address:**

1. **Frontend Serving**: Fix nginx configuration
2. **Port Consistency**: Standardize port usage
3. **Environment Variables**: Ensure all required vars are set
4. **SSL Certificates**: Configure proper SSL for production

---

## 🚨 **Critical Issues to Fix**

### **High Priority:**

1. **Nginx Frontend Configuration**: Add location block for static files
2. **Frontend Build Process**: Ensure dist/ files are copied to nginx
3. **Environment Variables**: Sync all required variables between dev/prod

### **Medium Priority:**

1. **Development Scripts**: Create automation scripts
2. **Port Standardization**: Consistent port usage
3. **SSL Configuration**: Proper certificate handling

### **Low Priority:**

1. **Frontend Container**: Consider containerizing frontend for dev
2. **Hot Reloading**: Improve development experience
3. **Documentation**: Update setup guides

---

This workflow ensures a smooth development-to-production pipeline with proper testing and validation at each stage.
