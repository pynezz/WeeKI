# WeeKI
Wee, Kunstig Intelligens - AI Agent Orchestration System

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

WeeKI is a self-hostable AI agent orchestration system designed to coordinate multiple AI agents for complex task execution.

## 🚀 Quick Start (Self-Hosting)

Get WeeKI running on your infrastructure in minutes:

```bash
# Clone the repository
git clone https://github.com/pynezz/WeeKI.git
cd WeeKI

# Quick install with Docker Compose
./deploy.sh install

# Or for production deployment
./deploy.sh -p install
```

Your WeeKI instance will be available at `http://localhost:8000` with API docs at `/docs`.

## 🏗️ Architecture

### Agent Hierarchy
- **Orchestrator Agent**: Central coordinator that distributes tasks and monitors overall progress
- **Specialist Agents**: Domain-specific agents with specialized capabilities (coding, design, research, etc.)
- **Utility Agents**: Handle routine tasks like data processing, formatting, and communication

### Decision Flow
1. You provide high-level directives to the Orchestrator
2. Orchestrator breaks down tasks and assigns to appropriate Specialist/Utility agents
3. Results flow back up through the hierarchy for your review

## 📦 Installation Options

### Docker Compose (Recommended)
```bash
docker-compose up -d
```

### Docker
```bash
docker build -t weeki .
docker run -d -p 8000:8000 weeki
```

### Python
```bash
pip install -e .
weeki serve
```

## 🔧 Configuration

WeeKI is configured through environment variables:

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
vim .env

# Key settings:
WEEKI_HOST=0.0.0.0
WEEKI_PORT=8000
WEEKI_SECRET_KEY=your-secret-key
WEEKI_OPENAI_API_KEY=your-api-key  # Optional
```

## 🌐 API Usage

### Create a Task
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{"directive": "Write a Python function to calculate fibonacci numbers"}'
```

### Check Task Status
```bash
curl "http://localhost:8000/tasks/{task_id}"
```

### Health Check
```bash
curl "http://localhost:8000/health"
```

## 📚 Documentation

- **[Self-Hosting Guide](SELF_HOSTING.md)** - Complete guide for self-hosting WeeKI
- **API Documentation** - Available at `/docs` when running
- **Configuration Reference** - See [Configuration](#-configuration) section

## 🛠️ Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black weeki/
isort weeki/

# Type checking
mypy weeki/
```

## 🚀 Deployment

### Production Deployment
```bash
# Production setup with nginx reverse proxy
./deploy.sh -p install

# Or manually with docker-compose
docker-compose --profile production up -d
```

### Management Commands
```bash
./deploy.sh status     # Check service status
./deploy.sh logs       # View logs
./deploy.sh backup     # Backup data
./deploy.sh update     # Update to latest version
```

## 🔒 Security

For production deployments:
- Change default secret keys
- Use HTTPS with SSL certificates
- Configure firewall rules
- Regular security updates
- See [Security section in Self-Hosting Guide](SELF_HOSTING.md#security-considerations)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Self-Hosting Documentation](SELF_HOSTING.md)
- 🐛 [Report Issues](https://github.com/pynezz/WeeKI/issues)
- 💬 [Discussions](https://github.com/pynezz/WeeKI/discussions)

---

**WeeKI** - Empowering self-hosted AI agent orchestration 🤖
