# Self-Hosting WeeKI

This guide will help you set up and run WeeKI (Wee, Kunstig Intelligens) on your own infrastructure.

## Quick Start with Docker Compose

The easiest way to get started with self-hosting WeeKI is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/pynezz/WeeKI.git
cd WeeKI

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your preferred settings

# Start the service
docker-compose up -d

# Check the service is running
docker-compose ps
curl http://localhost:8000/health
```

Your WeeKI instance will be available at `http://localhost:8000`.

## Installation Methods

### 1. Docker Compose (Recommended)

**Prerequisites:**
- Docker Engine 20.10+
- Docker Compose 2.0+

**Steps:**
```bash
# Start in development mode
docker-compose up -d

# Start in production mode with nginx
docker-compose --profile production up -d

# View logs
docker-compose logs -f weeki

# Stop services
docker-compose down
```

### 2. Docker Only

```bash
# Build the image
docker build -t weeki:latest .

# Run the container
docker run -d \
  --name weeki \
  -p 8000:8000 \
  -e WEEKI_SECRET_KEY=your-secret-key \
  -v weeki_data:/app/data \
  weeki:latest
```

### 3. Python Virtual Environment

**Prerequisites:**
- Python 3.8+
- pip

**Steps:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install WeeKI
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env file

# Run the server
weeki serve
```

## Configuration

### Environment Variables

WeeKI is configured using environment variables with the `WEEKI_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `WEEKI_HOST` | `0.0.0.0` | Server host address |
| `WEEKI_PORT` | `8000` | Server port |
| `WEEKI_DEBUG` | `false` | Enable debug mode |
| `WEEKI_SECRET_KEY` | `change-me-in-production` | Secret key for sessions |
| `WEEKI_DATABASE_URL` | `sqlite:///./weeki.db` | Database connection URL |
| `WEEKI_MAX_AGENTS` | `10` | Maximum concurrent agents |
| `WEEKI_AGENT_TIMEOUT` | `300` | Agent timeout in seconds |
| `WEEKI_LOG_LEVEL` | `INFO` | Logging level |
| `WEEKI_OPENAI_API_KEY` | `None` | OpenAI API key (optional) |
| `WEEKI_ANTHROPIC_API_KEY` | `None` | Anthropic API key (optional) |

### Configuration Files

Use the provided environment templates:

- `.env.example` - Example configuration
- `.env.development` - Development settings
- `.env.production` - Production settings

Copy the appropriate file to `.env` and customize as needed.

## Security Considerations

### Production Deployment

1. **Change the secret key**: Generate a secure random string for `WEEKI_SECRET_KEY`
2. **Use HTTPS**: Set up SSL/TLS certificates (nginx configuration included)
3. **Firewall**: Restrict access to necessary ports only
4. **Environment isolation**: Use Docker or virtual environments
5. **Regular updates**: Keep dependencies and base images updated

### API Keys

Store external API keys securely:

```bash
# Use environment variables
export WEEKI_OPENAI_API_KEY="your-key"

# Or add to .env file
echo "WEEKI_OPENAI_API_KEY=your-key" >> .env
```

## Networking

### Ports

- **8000**: WeeKI API server (default)
- **80/443**: HTTP/HTTPS (when using nginx proxy)

### Reverse Proxy Setup

For production deployments, use the included nginx configuration:

```bash
# Enable production profile with nginx
docker-compose --profile production up -d
```

## Storage

### Database

WeeKI uses SQLite by default for simplicity. For production:

```bash
# SQLite (default)
WEEKI_DATABASE_URL=sqlite:///./data/weeki.db

# PostgreSQL (requires additional setup)
WEEKI_DATABASE_URL=postgresql://user:pass@localhost:5432/weeki

# MySQL (requires additional setup)
WEEKI_DATABASE_URL=mysql://user:pass@localhost:3306/weeki
```

### Persistent Data

When using Docker, ensure data persistence:

```bash
# Named volume (recommended)
-v weeki_data:/app/data

# Bind mount
-v /host/path/data:/app/data
```

## Monitoring and Maintenance

### Health Checks

WeeKI includes health check endpoints:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/tasks
```

### Logs

Access logs for troubleshooting:

```bash
# Docker Compose
docker-compose logs -f weeki

# Docker container
docker logs -f weeki

# Direct installation
weeki serve --debug
```

### Updates

Keep your WeeKI installation updated:

```bash
# Docker
docker-compose pull
docker-compose up -d

# Python installation
git pull
pip install -e .
```

## Scaling

### Horizontal Scaling

For high-traffic deployments:

1. **Load balancer**: Use nginx or similar to distribute requests
2. **Multiple instances**: Run multiple WeeKI containers behind a load balancer
3. **Shared database**: Use PostgreSQL or MySQL for shared state
4. **Container orchestration**: Deploy with Kubernetes or Docker Swarm

### Vertical Scaling

Adjust resource limits:

```yaml
# docker-compose.yml
services:
  weeki:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure port 8000 is available
2. **Permission errors**: Check file permissions and Docker user setup
3. **Database errors**: Verify database URL and permissions
4. **API key errors**: Confirm external API keys are valid

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Environment variable
WEEKI_DEBUG=true

# Command line
weeki serve --debug
```

### Support

For issues and support:

- Check the [GitHub Issues](https://github.com/pynezz/WeeKI/issues)
- Review logs with `--debug` flag
- Verify configuration with `weeki config`

## API Documentation

Once running, access the interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`