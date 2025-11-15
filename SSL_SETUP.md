# SSL Certificate Setup for Sports Betting App

This guide covers setting up SSL certificates for the production deployment of the sports betting application.

## Option 1: Let's Encrypt (Recommended for Production)

### Prerequisites
- Domain name pointing to your server
- Server with ports 80 and 443 open
- Docker and Docker Compose installed

### Setup Steps

1. **Install Certbot**
```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# On CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

2. **Obtain SSL Certificate**
```bash
# Replace your-domain.com with your actual domain
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com
```

3. **Copy Certificates to Project**
```bash
# Create SSL directory
mkdir -p nginx/ssl/

# Copy certificates (adjust paths as needed)
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/chain.pem nginx/ssl/

# Set permissions
sudo chown $USER:$USER nginx/ssl/*
chmod 644 nginx/ssl/*.pem
```

4. **Update nginx-production.conf**
Update the server_name in `frontend/nginx-production.conf`:
```nginx
server_name your-domain.com www.your-domain.com;
```

5. **Setup Certificate Renewal**
```bash
# Add to crontab for automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## Option 2: Self-Signed Certificates (Development/Testing)

### Generate Self-Signed Certificates
```bash
# Create SSL directory
mkdir -p nginx/ssl/

# Generate private key
openssl genrsa -out nginx/ssl/privkey.pem 2048

# Generate certificate signing request
openssl req -new -key nginx/ssl/privkey.pem -out nginx/ssl/cert.csr

# Generate self-signed certificate
openssl x509 -req -days 365 -in nginx/ssl/cert.csr -signkey nginx/ssl/privkey.pem -out nginx/ssl/fullchain.pem

# Create chain file (same as fullchain for self-signed)
cp nginx/ssl/fullchain.pem nginx/ssl/chain.pem

# Clean up
rm nginx/ssl/cert.csr
```

## Option 3: Cloud Provider SSL (AWS, Cloudflare, etc.)

### AWS Application Load Balancer
1. Use AWS Certificate Manager to provision certificates
2. Configure ALB to terminate SSL
3. Use HTTP configuration in nginx (ALB handles HTTPS)

### Cloudflare
1. Enable Cloudflare proxy for your domain
2. Use "Flexible" or "Full" SSL mode
3. Use HTTP configuration in nginx (Cloudflare handles HTTPS)

## Docker Compose SSL Configuration

Update your `docker-compose.yml` to mount SSL certificates:

```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.production
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl:ro
    environment:
      - NGINX_CONFIG=production
```

## Testing SSL Configuration

1. **Check Certificate**
```bash
openssl x509 -in nginx/ssl/fullchain.pem -text -noout
```

2. **Test SSL Setup**
```bash
curl -I https://your-domain.com/health
```

3. **SSL Rating**
Test your SSL configuration at: https://www.ssllabs.com/ssltest/

## Security Best Practices

1. **File Permissions**
```bash
chmod 600 nginx/ssl/privkey.pem
chmod 644 nginx/ssl/fullchain.pem nginx/ssl/chain.pem
```

2. **Regular Updates**
- Keep certbot updated
- Monitor certificate expiration
- Update SSL ciphers regularly

3. **Security Headers**
The nginx configuration already includes:
- HSTS (HTTP Strict Transport Security)
- X-Frame-Options
- X-Content-Type-Options
- Content Security Policy

## Troubleshooting

### Common Issues

1. **Certificate Path Errors**
```bash
# Check if certificates exist
ls -la nginx/ssl/
```

2. **Permission Denied**
```bash
# Fix permissions
sudo chown -R $USER:$USER nginx/ssl/
```

3. **Domain Validation Failures**
- Ensure domain points to your server
- Check firewall settings (ports 80, 443)
- Verify DNS propagation

### Nginx Configuration Test
```bash
# Test configuration
docker-compose exec frontend nginx -t

# Reload configuration
docker-compose exec frontend nginx -s reload
```

## Production Deployment Checklist

- [ ] Domain configured and pointing to server
- [ ] SSL certificates obtained and installed
- [ ] nginx-production.conf updated with correct domain
- [ ] Docker Compose configured for SSL
- [ ] Firewall configured (ports 80, 443)
- [ ] Certificate renewal automated
- [ ] SSL configuration tested
- [ ] Security headers verified
- [ ] Backup of certificates created

## Environment Variables

Add these to your production environment:

```bash
# SSL Configuration
SSL_CERT_PATH=/etc/nginx/ssl/fullchain.pem
SSL_KEY_PATH=/etc/nginx/ssl/privkey.pem
SSL_CHAIN_PATH=/etc/nginx/ssl/chain.pem

# Domain Configuration
DOMAIN_NAME=your-domain.com
REDIRECT_HTTPS=true
```