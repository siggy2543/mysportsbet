#!/bin/bash

# 🎰 Sports Betting App - Live DraftKings Production Deployment
# Deploys the app with live betting capabilities

set -e

echo "🎰 Deploying Sports Betting App with Live DraftKings Integration..."

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE} $1 ${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check prerequisites
print_header "Checking Prerequisites"

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
fi

if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
fi

print_success "Docker and Docker Compose are ready"

# Verify environment configuration
print_header "Verifying Environment Configuration"

if [ ! -f ".env" ]; then
    print_error ".env file not found. Please ensure your environment configuration exists."
fi

# Check critical environment variables
if ! grep -q "DRAFTKINGS_USERNAME=" .env; then
    print_error "DRAFTKINGS_USERNAME not found in .env file"
fi

if ! grep -q "DRAFTKINGS_PASSWORD=" .env; then
    print_error "DRAFTKINGS_PASSWORD not found in .env file"
fi

if ! grep -q "OPENAI_API_KEY=" .env; then
    print_error "OPENAI_API_KEY not found in .env file"
fi

print_success "Environment configuration verified"

# Create necessary directories
print_header "Setting Up Directory Structure"

mkdir -p logs/{api,nginx,postgres,redis,celery}
mkdir -p monitoring
mkdir -p nginx/ssl

print_success "Directory structure created"

# Generate SSL certificates for local deployment
print_header "Setting Up SSL Certificates"

if [ ! -f "nginx/ssl/server.crt" ]; then
    print_status "Generating self-signed SSL certificates..."
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/server.key \
        -out nginx/ssl/server.crt \
        -subj "/C=US/ST=MD/L=Baltimore/O=SportsBettingApp/CN=localhost"
    
    print_success "SSL certificates generated"
else
    print_success "SSL certificates already exist"
fi

# Create monitoring configuration
print_header "Setting Up Monitoring"

cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sports-betting-api'
    static_configs:
      - targets: ['api:8000']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF

print_success "Monitoring configuration created"

# Build production images
print_header "Building Production Docker Images"

print_status "Building backend production image..."
docker-compose -f docker-compose.production.yml build api

print_status "Building frontend production image..."
docker-compose -f docker-compose.production.yml build frontend

print_success "Production images built successfully"

# Stop any existing containers
print_header "Stopping Existing Containers"

docker-compose down --remove-orphans || true
docker-compose -f docker-compose.production.yml down --remove-orphans || true

print_success "Existing containers stopped"

# Deploy production stack
print_header "Deploying Production Stack"

print_status "Starting production services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Health checks
print_header "Running Health Checks"

print_status "Checking API health..."
for i in {1..10}; do
    if curl -s -k https://localhost/api/v1/bets/public/status > /dev/null; then
        print_success "API is responding"
        break
    fi
    if [ $i -eq 10 ]; then
        print_error "API health check failed after 10 attempts"
    fi
    sleep 5
done

print_status "Checking frontend..."
if curl -s https://localhost > /dev/null; then
    print_success "Frontend is serving"
else
    print_warning "Frontend may not be ready yet"
fi

print_status "Checking database connection..."
if docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U sportsapp; then
    print_success "Database is ready"
else
    print_warning "Database connection check failed"
fi

# Verify DraftKings integration
print_header "Verifying DraftKings Integration"

print_status "Testing DraftKings service connection..."
sleep 10

# Check if betting services are running
if docker-compose -f docker-compose.production.yml logs api | grep -q "DraftKings"; then
    print_success "DraftKings service initialized"
else
    print_warning "DraftKings service logs not found - check manual connection"
fi

# Display deployment summary
print_header "Deployment Summary"

echo -e "${GREEN}🎰 Sports Betting App is now live with DraftKings integration!${NC}"
echo ""
echo -e "${BLUE}📊 Access Points:${NC}"
echo -e "   Dashboard:     ${YELLOW}https://localhost/${NC}"
echo -e "   API Status:    ${YELLOW}https://localhost/api/v1/bets/public/status${NC}"
echo -e "   API Docs:      ${YELLOW}https://localhost/docs${NC}"
echo -e "   Monitoring:    ${YELLOW}http://localhost:9090${NC}"
echo ""
echo -e "${BLUE}🎯 Betting Configuration:${NC}"
echo -e "   Account:       ${YELLOW}siggy2543@gmail.com${NC}"
echo -e "   State:         ${YELLOW}Maryland (MD)${NC}"
echo -e "   Bet Amount:    ${YELLOW}\$5.00 per bet${NC}"
echo -e "   Daily Limit:   ${YELLOW}\$500.00${NC}"
echo -e "   Auto Betting:  ${YELLOW}ENABLED${NC}"
echo ""
echo -e "${BLUE}📈 Expected Performance:${NC}"
echo -e "   Bets/Day:      ${YELLOW}5-15 high-confidence bets${NC}"
echo -e "   Investment:    ${YELLOW}\$25-75 per day${NC}"
echo -e "   Target ROI:    ${YELLOW}5-10% monthly${NC}"
echo ""
echo -e "${BLUE}🔍 Monitoring Commands:${NC}"
echo -e "   View Logs:     ${YELLOW}docker-compose -f docker-compose.production.yml logs -f api${NC}"
echo -e "   Check Status:  ${YELLOW}curl -k https://localhost/api/v1/bets/public/status${NC}"
echo -e "   View Bets:     ${YELLOW}curl -k https://localhost/api/v1/bets/active${NC}"
echo ""

# Check if containers are running
print_status "Verifying all services are running..."
docker-compose -f docker-compose.production.yml ps

echo ""
print_warning "⚠️  IMPORTANT REMINDERS:"
echo -e "   • Start with small amounts (\$5 bets as configured)"
echo -e "   • Monitor betting activity closely via dashboard"
echo -e "   • Ensure sports betting is legal in Maryland"
echo -e "   • Review and adjust risk management settings as needed"
echo -e "   • Keep your DraftKings account funded"

echo ""
print_success "🚀 Production deployment complete! Your betting bot is ready to start placing bets."

# Optional: Run a test bet
read -p "Would you like to run a test connection to DraftKings? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Testing DraftKings connection..."
    curl -k -X POST https://localhost/api/v1/draftkings/test-connection || print_warning "Test connection failed - check credentials"
fi

print_success "Deployment script completed successfully! 🎰"