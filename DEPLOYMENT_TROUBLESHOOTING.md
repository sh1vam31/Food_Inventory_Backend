# Deployment Troubleshooting Guide

## Common Deployment Issues and Solutions

### 1. ModuleNotFoundError: No module named 'pydantic_settings'

**Error:**
```
ModuleNotFoundError: No module named 'pydantic_settings'
```

**Solution:**
This happens because `pydantic_settings` is a separate package in Pydantic v2.

**Fixed in requirements.txt:**
```
pydantic-settings>=2.0.0
```

### 2. Python Version Compatibility

**Error:**
```
Python version compatibility issues
```

**Solution:**
Ensure you're using Python 3.11+ in production.

**Render Configuration:**
```yaml
# render.yaml
envVars:
  - key: PYTHON_VERSION
    value: 3.11.0
```

### 3. Database Connection Issues

**Error:**
```
Connection refused / Database connection failed
```

**Solutions:**

1. **Check DATABASE_URL format:**
   ```env
   # Correct format for PostgreSQL
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

2. **Verify environment variables are set in Render:**
   - `DATABASE_URL` (from PostgreSQL service)
   - `ENVIRONMENT=production`

3. **Check database service is running:**
   - Go to Render dashboard
   - Verify PostgreSQL service is active
   - Check connection string is correct

### 4. Import Path Issues

**Error:**
```
ModuleNotFoundError: No module named 'app'
```

**Solution:**
Ensure your start command is correct:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 5. Missing Dependencies

**Error:**
```
ModuleNotFoundError: No module named 'xyz'
```

**Solution:**
Update requirements.txt with all dependencies:
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
alembic>=1.12.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
pydantic>=2.6.0
pydantic-settings>=2.0.0
psycopg2-binary>=2.9.0
```

## Deployment Checklist

### Before Deployment:
- [ ] All dependencies in requirements.txt
- [ ] Environment variables configured
- [ ] Database service created
- [ ] Code pushed to GitHub

### Render Configuration:
- [ ] **Build Command**: `pip install -r requirements.txt`
- [ ] **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] **Environment**: `Python 3`
- [ ] **Python Version**: `3.11.0`

### Environment Variables:
- [ ] `DATABASE_URL` (connected from PostgreSQL service)
- [ ] `ENVIRONMENT=production`

### After Deployment:
- [ ] Check service logs for errors
- [ ] Test health endpoint: `https://your-service.onrender.com/health`
- [ ] Initialize database: `python seed_data.py` (in Render shell)

## Testing Your Deployment

### 1. Health Check
```bash
curl https://your-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "API is running",
  "database": "PostgreSQL",
  "environment": "production"
}
```

### 2. API Endpoints
```bash
# Test raw materials endpoint
curl https://your-backend.onrender.com/api/raw-materials/

# Test API documentation
# Visit: https://your-backend.onrender.com/docs
```

### 3. Database Connection
```bash
# In Render shell
python -c "
from app.database import engine
with engine.connect() as conn:
    print('Database connected successfully')
"
```

## Common Render Issues

### 1. Build Timeout
**Solution:** Optimize requirements.txt, remove unused dependencies

### 2. Memory Issues
**Solution:** Upgrade to paid plan or optimize code

### 3. Cold Starts
**Solution:** Use paid plan for always-on service

### 4. Environment Variables Not Loading
**Solution:** 
- Check spelling in Render dashboard
- Restart service after adding variables
- Use Render's "Connect Database" feature

## Debugging Steps

### 1. Check Render Logs
- Go to your service in Render dashboard
- Click "Logs" tab
- Look for specific error messages

### 2. Test Locally First
```bash
# Test with production-like settings
export DATABASE_URL="postgresql://..."
export ENVIRONMENT="production"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Verify Dependencies
```bash
# Check if all imports work
python -c "
from app.main import app
from app.core.config import settings
print('All imports successful')
"
```

## Quick Fixes

### Fix 1: Update requirements.txt
```bash
# Add missing pydantic-settings
echo "pydantic-settings>=2.0.0" >> requirements.txt
git add requirements.txt
git commit -m "Fix: Add pydantic-settings dependency"
git push origin main
```

### Fix 2: Force Rebuild
- Go to Render dashboard
- Click "Manual Deploy" → "Deploy latest commit"
- Or push a small change to trigger rebuild

### Fix 3: Check Python Version
```yaml
# In render.yaml or environment variables
PYTHON_VERSION: 3.11.0
```

## Support Resources

- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Pydantic Docs**: https://docs.pydantic.dev/

## Contact

If issues persist:
1. Check Render community forum
2. Review deployment logs carefully
3. Test locally with production settings
4. Verify all environment variables are set correctly

Your backend should now deploy successfully! 🚀