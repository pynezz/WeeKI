#!/bin/bash
# WeeKI Self-Hosting Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENV_FILE=".env"
COMPOSE_FILE="docker-compose.yml"
PRODUCTION=false

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    cat << EOF
WeeKI Self-Hosting Deployment Script

Usage: $0 [OPTIONS] COMMAND

Commands:
    install     Install and start WeeKI
    start       Start WeeKI services
    stop        Stop WeeKI services
    restart     Restart WeeKI services
    update      Update WeeKI to latest version
    logs        Show service logs
    status      Show service status
    backup      Backup WeeKI data
    restore     Restore WeeKI data from backup

Options:
    -p, --production    Use production configuration
    -h, --help         Show this help message

Environment:
    ENV_FILE           Environment file to use (default: .env)
    COMPOSE_FILE       Docker compose file to use (default: docker-compose.yml)

Examples:
    $0 install                 # Install with default settings
    $0 -p install             # Install with production settings
    $0 start                  # Start services
    $0 logs                   # View logs
    $0 backup /path/to/backup # Backup data

EOF
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_info "Dependencies check passed."
}

setup_environment() {
    if [ ! -f "$ENV_FILE" ]; then
        if [ "$PRODUCTION" = true ]; then
            log_info "Creating production environment file..."
            cp .env.production "$ENV_FILE"
        else
            log_info "Creating environment file from example..."
            cp .env.example "$ENV_FILE"
        fi
        
        # Generate secure secret key
        SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "change-me-$(date +%s)")
        sed -i "s/change-me-in-production/$SECRET_KEY/g" "$ENV_FILE"
        
        log_warn "Environment file created at $ENV_FILE"
        log_warn "Please review and update the configuration as needed."
    else
        log_info "Environment file already exists: $ENV_FILE"
    fi
}

install_weeki() {
    log_info "Installing WeeKI..."
    
    check_dependencies
    setup_environment
    
    log_info "Building and starting WeeKI services..."
    if [ "$PRODUCTION" = true ]; then
        docker-compose --profile production build
        docker-compose --profile production up -d
    else
        docker-compose build
        docker-compose up -d
    fi
    
    log_info "Waiting for services to be ready..."
    sleep 10
    
    if curl -s http://localhost:8000/health > /dev/null; then
        log_info "WeeKI installed successfully!"
        log_info "Access your instance at: http://localhost:8000"
        log_info "API documentation: http://localhost:8000/docs"
    else
        log_error "Installation may have failed. Check logs with: $0 logs"
        exit 1
    fi
}

start_services() {
    log_info "Starting WeeKI services..."
    if [ "$PRODUCTION" = true ]; then
        docker-compose --profile production up -d
    else
        docker-compose up -d
    fi
    log_info "Services started."
}

stop_services() {
    log_info "Stopping WeeKI services..."
    docker-compose down
    log_info "Services stopped."
}

restart_services() {
    log_info "Restarting WeeKI services..."
    stop_services
    start_services
}

update_weeki() {
    log_info "Updating WeeKI..."
    
    # Pull latest changes
    git pull origin main
    
    # Rebuild and restart
    if [ "$PRODUCTION" = true ]; then
        docker-compose --profile production build
        docker-compose --profile production up -d
    else
        docker-compose build
        docker-compose up -d
    fi
    
    log_info "WeeKI updated successfully."
}

show_logs() {
    docker-compose logs -f weeki
}

show_status() {
    log_info "WeeKI Service Status:"
    docker-compose ps
    
    echo
    log_info "Health Check:"
    if curl -s http://localhost:8000/health | jq . 2>/dev/null; then
        log_info "Service is healthy"
    else
        log_warn "Service may not be responding"
    fi
}

backup_data() {
    BACKUP_PATH=${1:-"./backup-$(date +%Y%m%d-%H%M%S)"}
    log_info "Creating backup at: $BACKUP_PATH"
    
    mkdir -p "$BACKUP_PATH"
    
    # Backup database and configuration
    docker-compose exec -T weeki tar -czf - /app/data | tar -xzf - -C "$BACKUP_PATH" --strip-components=2
    cp "$ENV_FILE" "$BACKUP_PATH/"
    
    log_info "Backup completed: $BACKUP_PATH"
}

restore_data() {
    BACKUP_PATH=$1
    if [ -z "$BACKUP_PATH" ] || [ ! -d "$BACKUP_PATH" ]; then
        log_error "Please provide a valid backup directory path."
        exit 1
    fi
    
    log_warn "This will overwrite existing data. Continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log_info "Restore cancelled."
        exit 0
    fi
    
    log_info "Restoring from backup: $BACKUP_PATH"
    
    # Stop services
    stop_services
    
    # Restore data
    docker run --rm -v weeki_data:/data -v "$BACKUP_PATH":/backup alpine sh -c "rm -rf /data/* && cp -r /backup/* /data/"
    
    # Restore configuration
    if [ -f "$BACKUP_PATH/.env" ]; then
        cp "$BACKUP_PATH/.env" "$ENV_FILE"
    fi
    
    # Start services
    start_services
    
    log_info "Restore completed."
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--production)
            PRODUCTION=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        install)
            COMMAND="install"
            shift
            ;;
        start)
            COMMAND="start"
            shift
            ;;
        stop)
            COMMAND="stop"
            shift
            ;;
        restart)
            COMMAND="restart"
            shift
            ;;
        update)
            COMMAND="update"
            shift
            ;;
        logs)
            COMMAND="logs"
            shift
            ;;
        status)
            COMMAND="status"
            shift
            ;;
        backup)
            COMMAND="backup"
            BACKUP_ARG="$2"
            shift 2
            ;;
        restore)
            COMMAND="restore"
            RESTORE_ARG="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Execute command
case $COMMAND in
    install)
        install_weeki
        ;;
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    update)
        update_weeki
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    backup)
        backup_data "$BACKUP_ARG"
        ;;
    restore)
        restore_data "$RESTORE_ARG"
        ;;
    *)
        log_error "No command specified."
        show_help
        exit 1
        ;;
esac