# 🍕 Food Inventory Management System - Backend

FastAPI backend with automatic inventory deduction and PostgreSQL support.

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

## ✨ Features

### 🏪 Core Functionality
- **Raw Materials Management**: Track ingredients with units, quantities, and thresholds
- **Food Items & Recipes**: Create menu items with ingredient requirements
- **Order Processing**: Atomic inventory deduction with transaction safety
- **Stock Monitoring**: Real-time availability checking and low stock alerts

### 🔧 Technical Features
- **Dual Database Support**: SQLite for development, PostgreSQL for production
- **Atomic Transactions**: Guaranteed inventory consistency
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Type Safety**: Full Pydantic validation
- **Error Handling**: Comprehensive error responses

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (for production)

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <backend-repo-url>
   cd food-inventory-backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Database Setup**
   ```bash
   # Development (SQLite) - automatic
   python seed_data.py
   
   # Production (PostgreSQL)
   # Set DATABASE_URL in .env first
   alembic upgrade head
   python seed_data.py
   ```

4. **Start Server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. **Access API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/              # Configuration
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   ├── routers/           # API endpoints
│   └── utils/             # Utilities
├── alembic/               # Database migrations
├── tests/                 # Test files
├── requirements.txt       # Dependencies
├── seed_data.py          # Sample data
└── migrate_to_postgresql.py  # Migration tool
```

## 🗄️ Database Configuration

### Development (SQLite)
```env
DATABASE_URL=sqlite:///./food_inventory.db
ENVIRONMENT=development
```

### Production (PostgreSQL)
```env
DATABASE_URL=postgresql://user:password@host:port/database
ENVIRONMENT=production
```

## 🔄 Critical Business Logic

### Inventory Deduction Algorithm
```python
# Atomic transaction ensures data consistency
def create_order(db: Session, order_data: OrderCreate):
    with db.begin():
        # 1. Validate inventory availability
        # 2. Create order record
        # 3. Deduct raw materials atomically
        # 4. Rollback on any failure
```

### Key Features
- **Atomic Transactions**: All-or-nothing inventory updates
- **Concurrent Safety**: Handles multiple simultaneous orders
- **Rollback Protection**: Automatic rollback on failures
- **Real-time Validation**: Pre-order inventory checking

## 📊 API Endpoints

### Raw Materials
- `GET /api/raw-materials/` - List all materials
- `POST /api/raw-materials/` - Create material
- `GET /api/raw-materials/{id}` - Get material details
- `PUT /api/raw-materials/{id}` - Update material
- `DELETE /api/raw-materials/{id}` - Delete material
- `GET /api/raw-materials/low-stock` - Get low stock items

### Food Items
- `GET /api/food-items/` - List all food items
- `POST /api/food-items/` - Create food item with recipe
- `GET /api/food-items/{id}` - Get food item details
- `DELETE /api/food-items/{id}` - Delete food item

### Orders (Critical)
- `POST /api/orders/check-inventory` - Validate order availability
- `POST /api/orders/` - Create order with inventory deduction
- `GET /api/orders/` - List all orders
- `GET /api/orders/{id}` - Get order details
- `PATCH /api/orders/{id}/cancel` - Cancel order
- `PATCH /api/orders/{id}/complete` - Complete order

## 🚀 Deployment

### Render Deployment

1. **Create PostgreSQL Database**
   - Go to Render Dashboard
   - Create PostgreSQL service
   - Note connection details

2. **Deploy Web Service**
   - Connect GitHub repository
   - Set environment variables:
     - `ENVIRONMENT=production`
     - `DATABASE_URL` (from database)
   - Deploy

3. **Initialize Database**
   ```bash
   # In Render shell
   python seed_data.py
   ```

### Environment Variables
```env
# Required
DATABASE_URL=postgresql://...
ENVIRONMENT=production

# Optional
SECRET_KEY=your-secret-key
```

## 🧪 Testing

### Run Tests
```bash
# Unit tests
python -m pytest

# System test
python test_system.py

# PostgreSQL connection test
python test_postgresql.py postgresql://...
```

### Test Coverage
- Raw material CRUD operations
- Food item creation with recipes
- Order processing with inventory deduction
- Error handling and edge cases

## 🔧 Development Tools

### Database Migration
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Migrate from SQLite to PostgreSQL
python migrate_to_postgresql.py postgresql://...
```

### Code Quality
```bash
# Format code
black .

# Type checking
mypy app/

# Linting
flake8 app/
```

## 📊 Monitoring

### Health Checks
- `GET /health` - System status and database type
- `GET /` - API information and features

### Logging
- Request/response logging
- Database query logging (debug mode)
- Error tracking and reporting

## 🔐 Security

- **Input Validation**: Pydantic schemas for all inputs
- **SQL Injection Protection**: SQLAlchemy ORM
- **CORS Configuration**: Environment-specific origins
- **Environment Variables**: Secure credential management

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection**
   ```bash
   # Check connection
   python test_postgresql.py <database_url>
   
   # Verify environment
   curl http://localhost:8000/health
   ```

2. **Migration Issues**
   ```bash
   # Reset migrations
   alembic downgrade base
   alembic upgrade head
   ```

3. **Import Errors**
   ```bash
   # Check Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

## 📈 Performance

### Database Optimization
- Connection pooling for PostgreSQL
- Proper indexes on foreign keys
- Query optimization with joins
- Transaction management

### API Performance
- Async/await support
- Response caching headers
- Efficient serialization
- Minimal database queries

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🔗 Related

- **Frontend Repository**: [food-inventory-frontend](link-to-frontend-repo)
- **API Documentation**: Available at `/docs` endpoint
- **Deployment Guide**: See deployment section above
