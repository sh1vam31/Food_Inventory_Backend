# PostgreSQL Connection Guide

This guide explains how to connect your backend to PostgreSQL, both locally and in production.

## 🗄️ Database URL Options

### Internal vs External Database

**Internal Database (Recommended for Production)**
- Database hosted on the same platform as your backend (e.g., Render PostgreSQL + Render Web Service)
- Faster connection (same data center)
- Lower latency
- Often cheaper or free
- Automatic backups and maintenance

**External Database**
- Database hosted on a different platform (e.g., AWS RDS, Google Cloud SQL, Supabase)
- More flexibility in database provider
- Can be shared across multiple applications
- May have higher latency
- Usually more expensive

## 🚀 Production Setup Options

### Option 1: Render PostgreSQL (Recommended)

**Advantages:**
- Same platform as your backend
- Free tier available
- Automatic backups
- Easy setup and management
- Internal network connection (faster)

**Setup:**
1. Create PostgreSQL database on Render
2. Connect to your web service
3. Database URL is automatically provided

**Database URL Format:**
```
postgresql://username:password@internal-host:5432/database_name
```

### Option 2: External PostgreSQL Services

#### Supabase (Popular Choice)
```env
DATABASE_URL=postgresql://postgres:password@db.supabase.co:5432/postgres
```

#### AWS RDS
```env
DATABASE_URL=postgresql://username:password@your-db.region.rds.amazonaws.com:5432/database_name
```

#### Google Cloud SQL
```env
DATABASE_URL=postgresql://username:password@your-ip:5432/database_name
```

#### Railway
```env
DATABASE_URL=postgresql://postgres:password@containers-us-west-1.railway.app:5432/railway
```

## 🔧 Local Development Setup

### Option 1: Local PostgreSQL Installation

**Install PostgreSQL:**
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Create Database:**
```bash
# Create user and database
sudo -u postgres createuser --interactive your_username
sudo -u postgres createdb food_inventory_dev
```

**Local Database URL:**
```env
DATABASE_URL=postgresql://your_username:password@localhost:5432/food_inventory_dev
```

### Option 2: Docker PostgreSQL

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: food_inventory_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Start:**
```bash
docker-compose up -d
```

**Database URL:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/food_inventory_dev
```

### Option 3: Cloud Development Database

Use a free cloud PostgreSQL for development:

**Supabase (Free Tier):**
1. Sign up at supabase.com
2. Create new project
3. Get connection string from settings

**Railway (Free Tier):**
1. Sign up at railway.app
2. Create PostgreSQL service
3. Get connection string

## 🔄 Migration from SQLite

### Automatic Migration
```bash
# Run the migration script
python migrate_to_postgresql.py "postgresql://user:pass@host:port/db"
```

### Manual Migration
1. Export SQLite data
2. Create PostgreSQL tables
3. Import data using SQL scripts

## ⚙️ Environment Configuration

### Development (.env)
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/food_inventory_dev
ENVIRONMENT=development
```

### Production (Render Environment Variables)
```env
DATABASE_URL=postgresql://user:pass@internal-host:5432/food_inventory_prod
ENVIRONMENT=production
```

## 🔍 Testing Connection

### Test Script
```bash
# Test PostgreSQL connection
python test_postgresql.py "postgresql://user:pass@host:port/db"
```

### Manual Test
```python
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://user:pass@host:port/db")
with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(result.fetchone())
```

## 📊 Performance Considerations

### Connection Pooling
Your backend automatically configures connection pooling:
```python
# Automatic configuration in database.py
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connections
    pool_recycle=300,        # Recycle every 5 minutes
    echo=False               # Set to True for debugging
)
```

### Optimization Tips
- Use connection pooling (already configured)
- Enable query logging for debugging
- Monitor connection usage
- Use database indexes (already configured)

## 🔐 Security Best Practices

### Connection Security
- Always use SSL in production
- Use environment variables for credentials
- Rotate passwords regularly
- Limit database user permissions

### Network Security
- Use internal networks when possible
- Whitelist IP addresses if needed
- Enable database firewall rules

## 💰 Cost Comparison

### Free Tiers
- **Render PostgreSQL**: 1GB storage, 1 month retention
- **Supabase**: 500MB storage, 2 projects
- **Railway**: 1GB storage, $5 credit monthly

### Paid Tiers
- **Render**: $7/month (25GB storage)
- **Supabase**: $25/month (8GB storage)
- **AWS RDS**: $15-50/month (varies by instance)

## 🚀 Recommended Setup

### For Development
```env
# Local PostgreSQL or Docker
DATABASE_URL=postgresql://postgres:password@localhost:5432/food_inventory_dev
```

### For Production
```env
# Render PostgreSQL (recommended)
DATABASE_URL=postgresql://user:pass@internal-host:5432/food_inventory_prod
```

## 🔧 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if PostgreSQL is running
   - Verify host and port
   - Check firewall settings

2. **Authentication Failed**
   - Verify username and password
   - Check user permissions
   - Ensure database exists

3. **SSL Required**
   - Add `?sslmode=require` to connection string
   - Use proper SSL certificates

### Debug Commands
```bash
# Test connection
psql "postgresql://user:pass@host:port/db"

# Check database status
curl http://localhost:8000/health

# View logs
# Check your platform's logging system
```

Your backend will automatically detect PostgreSQL and configure itself accordingly! 🎉