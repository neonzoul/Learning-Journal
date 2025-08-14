# Deployment Guide

This directory contains deployment configurations and scripts for the Accounting Automation Backend.

## Quick Start

1. **Copy environment configuration:**
   ```bash
   cp .env.example .env
   ```

2. **Configure required environment variables in `.env`:**
   ```bash
   # Required - N8N Integration
   N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/receipt-processing
   N8N_API_KEY=your-n8n-api-key-here
   
   # Required - Security
   CALLBACK_SECRET_TOKEN=your-secret-callback-token-here
   ```

3. **Validate configuration:**
   ```bash
   python scripts/validate_config.py
   ```

4. **Deploy with Docker Compose:**
   ```bash
   ./scripts/deploy.sh
   ```

## Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `N8N_WEBHOOK_URL` | N8N webhook endpoint for receipt processing | `https://n8n.example.com/webhook/receipt-processing` |
| `N8N_API_KEY` | API key for N8N authentication | `your-secure-api-key` |
| `CALLBACK_SECRET_TOKEN` | Secret token for callback authentication | `your-32-char-secret-token` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `DATABASE_URL` | `sqlite:///./job_logs.db` | Database connection URL |
| `LOG_LEVEL` | `INFO` | Logging level |
| `VERIFY_SSL` | `true` | Enable SSL certificate verification |
| `DEBUG` | `false` | Enable debug mode |
| `MAX_FILE_SIZE` | `10485760` | Maximum upload file size (bytes) |
| `QUEUE_DEFAULT_TIMEOUT` | `300` | Job timeout in seconds |

## Deployment Options

### Option 1: Docker Compose (Recommended)

The Docker Compose setup includes:
- Redis server for queue management
- Main application server
- Background worker process
- Automatic health checks
- Volume persistence

```bash
cd deployment
docker-compose up -d
```

### Option 2: Manual Deployment

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Redis server:**
   ```bash
   redis-server
   ```

3. **Validate configuration:**
   ```bash
   python scripts/validate_config.py
   ```

4. **Start the application:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

5. **Start worker process:**
   ```bash
   python rq_worker.py
   ```

## Configuration Validation

The application includes comprehensive configuration validation:

### Startup Validation
- Required environment variables are set
- URLs are properly formatted
- Database directory is writable
- SSL certificates are valid (if using HTTPS)

### Runtime Validation
- Redis connection with retry logic
- Database connectivity
- N8N webhook accessibility

### Manual Validation
```bash
python scripts/validate_config.py
```

## SSL Configuration

### Production (HTTPS)
```bash
VERIFY_SSL=true
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/receipt-processing
```

### Development (HTTP/Self-signed certificates)
```bash
VERIFY_SSL=false
N8N_WEBHOOK_URL=http://localhost:5678/webhook/receipt-processing
```

## Monitoring and Health Checks

### Health Check Endpoints
- **Application Health:** `GET /health`
- **Queue Status:** `GET /monitoring/queue`
- **Application Metrics:** `GET /monitoring/metrics`

### RQ Dashboard
- **URL:** `http://localhost:8000/rq`
- **Features:** Queue monitoring, job status, worker management

### Docker Health Checks
```bash
# Check container health
docker-compose ps

# View health check logs
docker-compose logs app
```

## Troubleshooting

### Common Issues

1. **Configuration Validation Failed**
   ```bash
   # Check environment variables
   python scripts/validate_config.py
   
   # Verify .env file exists and is properly formatted
   cat .env
   ```

2. **Redis Connection Failed**
   ```bash
   # Check Redis server status
   redis-cli ping
   
   # Check Redis URL format
   echo $REDIS_URL
   ```

3. **N8N Webhook Not Accessible**
   ```bash
   # Test webhook URL
   curl -I $N8N_WEBHOOK_URL
   
   # Check SSL certificate (if HTTPS)
   openssl s_client -connect your-n8n-host:443
   ```

4. **Database Permission Issues**
   ```bash
   # Check database directory permissions
   ls -la $(dirname $DATABASE_URL)
   
   # Create directory if needed
   mkdir -p $(dirname $DATABASE_URL)
   ```

### Log Analysis

```bash
# View application logs
docker-compose logs -f app

# View worker logs
docker-compose logs -f worker

# View Redis logs
docker-compose logs -f redis
```

### Performance Tuning

1. **Redis Configuration**
   - Adjust memory limits in `docker-compose.yml`
   - Configure persistence settings
   - Monitor queue depth

2. **Worker Scaling**
   ```bash
   # Scale worker processes
   docker-compose up -d --scale worker=3
   ```

3. **Application Scaling**
   ```bash
   # Scale application instances
   docker-compose up -d --scale app=2
   ```

## Security Considerations

### Production Checklist
- [ ] Strong `CALLBACK_SECRET_TOKEN` (32+ characters)
- [ ] Secure `N8N_API_KEY`
- [ ] SSL verification enabled (`VERIFY_SSL=true`)
- [ ] Specific CORS origins (not `*`)
- [ ] Firewall rules configured
- [ ] Regular security updates

### Token Generation
```bash
# Generate secure callback token
openssl rand -hex 32

# Generate secure API key
openssl rand -base64 32
```

## Backup and Recovery

### Database Backup
```bash
# SQLite backup
cp job_logs.db job_logs.db.backup

# PostgreSQL backup (if using)
pg_dump $DATABASE_URL > backup.sql
```

### Redis Backup
```bash
# Redis backup
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb backup/
```

## Updates and Maintenance

### Application Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose up -d
```

### Dependency Updates
```bash
# Update requirements
pip-compile requirements.in

# Rebuild containers
docker-compose build --no-cache
```