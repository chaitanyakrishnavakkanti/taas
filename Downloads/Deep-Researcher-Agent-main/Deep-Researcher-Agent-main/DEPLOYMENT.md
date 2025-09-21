# Deployment Guide

This guide covers different ways to deploy the Deep Researcher Agent application.

## 🚀 Local Development

### Prerequisites

- Python 3.8+
- 8GB+ RAM recommended
- 2GB+ free disk space

### Quick Start

```bash
# Clone repository
git clone https://github.com/sathish0416/Deep-Researcher-Agent.git
cd Deep-Researcher-Agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python run_app.py
```

## 🐳 Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for data and embeddings
RUN mkdir -p data embeddings

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run Docker Container

```bash
# Build image
docker build -t deep-researcher-agent .

# Run container
docker run -p 8501:8501 -v $(pwd)/data:/app/data deep-researcher-agent
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  deep-researcher:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./embeddings:/app/embeddings
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## ☁️ Cloud Deployment

### Heroku

1. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```

2. **Create `Procfile`**:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

3. **Create `runtime.txt`**:
   ```
   python-3.9.7
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

### Railway

1. **Connect GitHub repository** to Railway
2. **Set environment variables**:
   - `PORT=8501`
3. **Deploy automatically** on push to main branch

### Google Cloud Run

1. **Create `Dockerfile`** (see Docker section)
2. **Build and push to Google Container Registry**:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/deep-researcher-agent
   ```
3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy --image gcr.io/PROJECT-ID/deep-researcher-agent --platform managed --region us-central1 --allow-unauthenticated
   ```

### AWS Elastic Beanstalk

1. **Create `Dockerrun.aws.json`**:
   ```json
   {
     "AWSEBDockerrunVersion": "1",
     "Image": {
       "Name": "your-account.dkr.ecr.region.amazonaws.com/deep-researcher-agent:latest",
       "Update": "true"
     },
     "Ports": [
       {
         "ContainerPort": "8501"
       }
     ]
   }
   ```

2. **Deploy using EB CLI**:
   ```bash
   eb init
   eb create
   eb deploy
   ```

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true

# AI Model Configuration
TRANSFORMERS_CACHE=/app/.cache/transformers
TORCH_HOME=/app/.cache/torch

# Application Settings
MAX_FILE_SIZE=200MB
CHUNK_SIZE=300
OVERLAP_SIZE=50
```

### Streamlit Configuration

Create `.streamlit/config.toml`:

```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

## 📊 Performance Optimization

### For Production

1. **Use GPU** if available:
   ```python
   device = 0 if torch.cuda.is_available() else -1
   ```

2. **Optimize model loading**:
   - Cache models in memory
   - Use smaller models for faster inference
   - Implement model warm-up

3. **Database optimization**:
   - Use FAISS with GPU support
   - Implement connection pooling
   - Add caching layer

4. **Memory management**:
   - Implement garbage collection
   - Use memory-efficient data structures
   - Monitor memory usage

### Scaling Considerations

- **Horizontal scaling**: Use load balancer with multiple instances
- **Caching**: Implement Redis for session storage
- **Database**: Use external vector database for large datasets
- **CDN**: Serve static assets through CDN

## 🔒 Security

### Production Security

1. **Authentication**: Add user authentication
2. **Authorization**: Implement role-based access
3. **Data encryption**: Encrypt sensitive data
4. **Input validation**: Validate all user inputs
5. **Rate limiting**: Implement API rate limiting
6. **HTTPS**: Use SSL/TLS certificates

### Security Headers

Add security headers in Streamlit config:

```toml
[server]
enableCORS = false
enableXsrfProtection = true
```

## 📈 Monitoring

### Health Checks

```python
# Add to app.py
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now()}
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Metrics

- **Response time**: Monitor query processing time
- **Memory usage**: Track memory consumption
- **Error rates**: Monitor application errors
- **User activity**: Track user interactions

## 🚨 Troubleshooting

### Common Issues

1. **Memory errors**: Increase container memory limits
2. **Model loading failures**: Check internet connection and disk space
3. **Port conflicts**: Change port in configuration
4. **Permission errors**: Check file permissions

### Debug Mode

Enable debug mode in development:

```python
import streamlit as st

if st.secrets.get("DEBUG", False):
    st.set_page_config(page_title="Debug Mode")
    # Add debug information
```

## 📚 Additional Resources

- [Streamlit Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud)
- [Docker Best Practices](https://docs.docker.com/develop/best-practices/)
- [Cloud Deployment Patterns](https://cloud.google.com/architecture)

---

**Need help with deployment?** Open an issue on GitHub or check the troubleshooting section.
