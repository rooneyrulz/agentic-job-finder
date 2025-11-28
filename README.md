# Job Finder API - Production-Ready Setup

## 🏗️ Project Structure

```
job-finder-api/
│
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (create from .env.example)
├── .gitignore                   # Git ignore file
├── README.md                    # Project documentation
│
├── app/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Settings and configuration
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   │
│   └── services/
│       ├── __init__.py
│       ├── scraper.py          # BrightData scraper
│       ├── llm_service.py      # Groq LLM service
│       └── job_agent.py        # LangGraph agent workflow
│
└── tests/
    ├── __init__.py
    ├── test_api.py
    └── test_agent.py
```

## 🚀 Setup Instructions

### 1. Clone and Setup Environment

```bash
# Create project directory
mkdir job-finder-api && cd job-finder-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the environment template
cp example.env .env

# Edit .env and add your API keys:
# - BRIGHTDATA_API_KEY (from https://brightdata.com)
# - GROQ_API_KEY (from https://console.groq.com)
nano .env
```

### 3. Create Directory Structure

```bash
# Create app directories
mkdir -p app/core app/models app/services tests

# Create __init__.py files
touch app/__init__.py
touch app/core/__init__.py
touch app/models/__init__.py
touch app/services/__init__.py
touch tests/__init__.py
```

### 4. Run the Application

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Access API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📡 API Endpoints

### 1. Search Jobs (Main Endpoint)

**POST** `/api/v1/jobs/search`

```json
{
  "keywords": "Senior Python Developer",
  "location": "Remote",
  "job_type": "full_time",
  "experience_level": "senior",
  "limit": 10,
  "preferences": {
    "min_salary": 120000,
    "required_skills": ["Python", "FastAPI", "Docker"],
    "exclude_companies": []
  }
}
```

**Response:**
```json
{
  "success": true,
  "query": "Senior Python Developer",
  "total_found": 10,
  "jobs": [
    {
      "job_id": "linkedin_123456",
      "title": "Senior Python Developer",
      "company": "Tech Corp",
      "location": "Remote",
      "job_type": "Full-time",
      "description": "...",
      "requirements": ["5+ years Python", "FastAPI experience"],
      "salary_range": "$120k - $180k",
      "posted_date": "2024-11-20",
      "apply_url": "https://linkedin.com/jobs/123456",
      "source": "LinkedIn",
      "match_score": 92.5,
      "match_reason": "Strong alignment with Python expertise...",
      "key_highlights": ["Remote-first culture", "Competitive salary"]
    }
  ],
  "search_metadata": {
    "sources": ["LinkedIn", "Glassdoor"],
    "processing_time_seconds": 3.5,
    "total_scraped": 50,
    "analyzed_count": 25,
    "final_count": 10
  },
  "timestamp": "2024-11-24T10:30:00Z"
}
```

### 2. Get Recommendations

**POST** `/api/v1/jobs/recommend`

Same request/response format as search endpoint.

### 3. Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "message": "All systems operational",
  "version": "1.0.0"
}
```

## 🧪 Testing with Postman

### Import Collection

Create a new Postman collection with these requests:

1. **Health Check**
   - Method: GET
   - URL: `http://localhost:8000/health`

2. **Search Jobs - Basic**
   - Method: POST
   - URL: `http://localhost:8000/api/v1/jobs/search`
   - Body (JSON):
   ```json
   {
     "keywords": "Python Developer",
     "location": "Remote",
     "limit": 5
   }
   ```

3. **Search Jobs - Advanced**
   - Method: POST
   - URL: `http://localhost:8000/api/v1/jobs/search`
   - Body (JSON):
   ```json
   {
     "keywords": "Machine Learning Engineer",
     "location": "San Francisco, CA",
     "job_type": "full_time",
     "experience_level": "senior",
     "limit": 10,
     "preferences": {
       "min_salary": 150000,
       "required_skills": ["Python", "TensorFlow", "PyTorch"],
       "exclude_companies": ["Company X"]
     }
   }
   ```

## 🔧 Configuration Options

### Job Types
- `full_time`
- `part_time`
- `contract`
- `internship`
- `remote`
- `hybrid`
- `any`

### Experience Levels
- `entry`
- `junior`
- `mid`
- `senior`
- `lead`
- `executive`
- `any`

### Groq LLM Models (Free)
- `mixtral-8x7b-32768` (default - fast and capable)
- `llama-3.3-70b-versatile` (high quality)
- `gemma2-9b-it` (lightweight)
- `llama-3.1-8b-instant` (fastest)

Change in `.env`:
```
GROQ_MODEL=llama-3.3-70b-versatile
```

## 🏗️ Architecture Highlights

### LangGraph Workflow Nodes

1. **validate_input** - Input validation and normalization
2. **scrape_jobs** - Concurrent scraping from LinkedIn & Glassdoor
3. **analyze_jobs** - AI-powered job analysis with Groq LLM
4. **rank_and_filter** - Scoring, ranking, and filtering
5. **format_response** - Final response formatting

### Key Features

✅ **Async/Await** - Full async support for high performance
✅ **LangGraph State Management** - Robust workflow orchestration
✅ **Pydantic Validation** - Type-safe request/response
✅ **Structured LLM Output** - JSON schema validation
✅ **Error Handling** - Comprehensive error handling and logging
✅ **Retry Logic** - Automatic retry for failed scraping
✅ **Concurrent Scraping** - Parallel data fetching
✅ **AI-Powered Matching** - Intelligent job recommendations
✅ **Scalable Design** - Ready for production deployment

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use environment variables** - All secrets in `.env`
3. **API key rotation** - Rotate keys regularly
4. **Rate limiting** - Configure in production
5. **Input validation** - Pydantic handles this automatically

## 📊 Monitoring & Logging

Logs include:
- Request/response tracking
- Scraping success/failure
- LLM analysis performance
- Error tracking with stack traces

View logs in console when running with `--log-level info`

## 🚢 Production Deployment

### Using Docker (Recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t job-finder-api .
docker run -p 8000:8000 --env-file .env job-finder-api
```

### Using systemd (Linux)

Create service file: `/etc/systemd/system/job-finder.service`
```ini
[Unit]
Description=Job Finder API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/job-finder-api
Environment="PATH=/opt/job-finder-api/venv/bin"
EnvironmentFile=/opt/job-finder-api/.env
ExecStart=/opt/job-finder-api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

[Install]
WantedBy=multi-user.target
```

## 📈 Performance Tips

1. **Increase workers**: `uvicorn main:app --workers 4`
2. **Enable caching**: Implement Redis for response caching
3. **Database**: Add PostgreSQL for persistent storage
4. **CDN**: Use CDN for static assets
5. **Load balancer**: Use Nginx for production

## 🐛 Troubleshooting

### API Key Errors
- Verify keys in `.env`
- Check key permissions on BrightData/Groq dashboards

### Import Errors
- Ensure all `__init__.py` files exist
- Check Python path: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`

### Scraping Failures
- Verify BrightData subscription is active
- Check API rate limits
- Review BrightData dataset IDs

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Groq API Documentation](https://console.groq.com/docs)
- [BrightData Documentation](https://docs.brightdata.com/)

## 🤝 Contributing

This is a production-ready template. Customize as needed:
- Add authentication (JWT, OAuth)
- Implement caching (Redis)
- Add database (PostgreSQL, MongoDB)
- Enhance error handling
- Add comprehensive tests

## 📄 License

MIT License - Feel free to use in your projects!