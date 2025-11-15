# SSL Certificate Setup for Windows - Sports Betting App

This guide covers setting up SSL certificates on Windows for the sports betting application.

## Option 1: Self-Signed Certificates (Development & Local Testing)

### Using PowerShell (Recommended for Windows)

1. **Open PowerShell as Administrator**

2. **Create SSL Directory**
```powershell
# Navigate to your project directory
cd C:\Users\cigba\sports_app

# Create SSL directories
New-Item -ItemType Directory -Force -Path "nginx\ssl"
New-Item -ItemType Directory -Force -Path "frontend\ssl"
```

3. **Generate Self-Signed Certificate using PowerShell**
```powershell
# Generate certificate for localhost and your local IP
$cert = New-SelfSignedCertificate -DnsName "localhost", "127.0.0.1", "your-local-ip" -CertStoreLocation "cert:\LocalMachine\My" -KeyAlgorithm RSA -KeyLength 2048 -Provider "Microsoft RSA SChannel Cryptographic Provider" -KeyUsage KeyEncipherment, DigitalSignature -NotAfter (Get-Date).AddYears(2)

# Export certificate with private key
$pwd = ConvertTo-SecureString -String "changeme123" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "nginx\ssl\localhost.pfx" -Password $pwd

# Convert PFX to PEM format (requires OpenSSL)
# Install OpenSSL for Windows first: https://slproweb.com/products/Win32OpenSSL.html
```

4. **Convert PFX to PEM (if OpenSSL is installed)**
```powershell
# Extract private key
openssl pkcs12 -in nginx\ssl\localhost.pfx -nocerts -out nginx\ssl\privkey.pem -nodes -passin pass:changeme123

# Extract certificate
openssl pkcs12 -in nginx\ssl\localhost.pfx -clcerts -nokeys -out nginx\ssl\fullchain.pem -passin pass:changeme123

# Create chain file (same as fullchain for self-signed)
Copy-Item nginx\ssl\fullchain.pem nginx\ssl\chain.pem
```

### Alternative: Using OpenSSL for Windows

1. **Install OpenSSL for Windows**
   - Download from: https://slproweb.com/products/Win32OpenSSL.html
   - Or use Chocolatey: `choco install openssl`
   - Or use Windows Subsystem for Linux (WSL)

2. **Generate Certificate using OpenSSL**
```cmd
# Create SSL directory
mkdir nginx\ssl

# Generate private key
openssl genrsa -out nginx\ssl\privkey.pem 2048

# Create certificate signing request configuration
echo [req] > nginx\ssl\cert.conf
echo distinguished_name = req_distinguished_name >> nginx\ssl\cert.conf  
echo x509_extensions = v3_req >> nginx\ssl\cert.conf
echo prompt = no >> nginx\ssl\cert.conf
echo [req_distinguished_name] >> nginx\ssl\cert.conf
echo CN = localhost >> nginx\ssl\cert.conf
echo [v3_req] >> nginx\ssl\cert.conf
echo keyUsage = keyEncipherment, dataEncipherment >> nginx\ssl\cert.conf
echo extendedKeyUsage = serverAuth >> nginx\ssl\cert.conf
echo subjectAltName = @alt_names >> nginx\ssl\cert.conf
echo [alt_names] >> nginx\ssl\cert.conf
echo DNS.1 = localhost >> nginx\ssl\cert.conf
echo DNS.2 = *.localhost >> nginx\ssl\cert.conf
echo IP.1 = 127.0.0.1 >> nginx\ssl\cert.conf

# Generate self-signed certificate
openssl req -new -x509 -key nginx\ssl\privkey.pem -out nginx\ssl\fullchain.pem -days 365 -config nginx\ssl\cert.conf

# Create chain file
copy nginx\ssl\fullchain.pem nginx\ssl\chain.pem
```

## Option 2: Let's Encrypt with Windows (Production)

### Using Certbot for Windows

1. **Install Certbot**
```powershell
# Using Chocolatey (install Chocolatey first if needed)
choco install certbot

# Or download from: https://certbot.eff.org/instructions?ws=other&os=windows
```

2. **Get Certificate (Domain Required)**
```cmd
# Stop any service using port 80
docker-compose stop nginx frontend

# Generate certificate (replace your-domain.com)
certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Certificates will be saved to: C:\Certbot\live\your-domain.com\
```

3. **Copy Certificates to Project**
```powershell
# Copy certificates to project directory
Copy-Item "C:\Certbot\live\your-domain.com\fullchain.pem" "nginx\ssl\"
Copy-Item "C:\Certbot\live\your-domain.com\privkey.pem" "nginx\ssl\"
Copy-Item "C:\Certbot\live\your-domain.com\chain.pem" "nginx\ssl\"
```

## Option 3: Windows Certificate Store (Advanced)

### Using IIS Manager

1. **Install IIS if not already installed**
2. **Use IIS Manager to create and manage certificates**
3. **Export certificates in PEM format**

## Docker Configuration for Windows SSL

### Update docker-compose.yml for SSL

Create `docker-compose.ssl.yml`:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend/nginx-production.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - frontend
      - api
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.production
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl:ro
    environment:
      - NGINX_SSL_ENABLED=true
    restart: unless-stopped

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    environment:
      - SSL_ENABLED=true
      - HTTPS_ONLY=true
    restart: unless-stopped
```

## Testing SSL Setup on Windows

### 1. Test Certificate Generation
```powershell
# Check if certificates exist
Get-ChildItem nginx\ssl\

# Verify certificate details
openssl x509 -in nginx\ssl\fullchain.pem -text -noout
```

### 2. Test SSL Connection
```powershell
# Test HTTPS connection
Invoke-WebRequest -Uri "https://localhost/health" -SkipCertificateCheck

# Or use curl
curl -k https://localhost/health
```

### 3. Browser Testing
- Navigate to `https://localhost`
- Accept the self-signed certificate warning (for development)
- Verify the SSL lock icon appears

## Windows-Specific SSL Commands

### PowerShell Commands for Certificate Management
```powershell
# List certificates in Windows certificate store
Get-ChildItem -Path Cert:\LocalMachine\My

# Remove a certificate
Remove-Item -Path "Cert:\LocalMachine\My\THUMBPRINT"

# Trust a self-signed certificate (run as Administrator)
Import-Certificate -FilePath "nginx\ssl\fullchain.pem" -CertStoreLocation Cert:\LocalMachine\Root
```

### Batch Script for Quick SSL Setup
Create `setup-ssl-windows.bat`:

```batch
@echo off
echo Setting up SSL certificates for Windows...

mkdir nginx\ssl 2>nul

echo Generating self-signed certificate...
openssl genrsa -out nginx\ssl\privkey.pem 2048
openssl req -new -x509 -key nginx\ssl\privkey.pem -out nginx\ssl\fullchain.pem -days 365 -subj "/CN=localhost"
copy nginx\ssl\fullchain.pem nginx\ssl\chain.pem

echo SSL certificates generated successfully!
echo Certificates location: %cd%\nginx\ssl\

pause
```

## Windows Firewall Configuration

### Allow HTTPS Traffic
```powershell
# Allow HTTPS through Windows Firewall
New-NetFirewallRule -DisplayName "Allow HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# Allow HTTP through Windows Firewall
New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
```

## Troubleshooting SSL on Windows

### Common Issues and Solutions

1. **OpenSSL not found**
   - Install OpenSSL for Windows
   - Add OpenSSL to PATH environment variable

2. **Permission denied errors**
   - Run PowerShell/Command Prompt as Administrator
   - Check file permissions on SSL directory

3. **Certificate not trusted**
   - Import certificate to Windows certificate store
   - Use `-SkipCertificateCheck` flag for testing

4. **Port 443 already in use**
   - Check what's using port 443: `netstat -ano | findstr :443`
   - Stop conflicting services

### Useful Windows Commands
```cmd
# Check what's listening on SSL ports
netstat -ano | findstr :443
netstat -ano | findstr :80

# Check certificate validity
openssl x509 -in nginx\ssl\fullchain.pem -noout -dates

# Test SSL connection
openssl s_client -connect localhost:443 -servername localhost
```

## Deployment on Windows

### Using the Windows SSL Setup Script
```powershell
# Make script executable and run
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup-ssl-windows.bat

# Deploy with SSL
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d
```

## Security Notes for Windows

1. **Certificate Storage**: Store certificates securely outside of the project directory in production
2. **Permissions**: Ensure SSL certificate files have restricted permissions
3. **Updates**: Regularly update OpenSSL and certificate management tools
4. **Backup**: Backup certificate files and private keys securely

## Next Steps After SSL Setup

1. Update your `.env` file with SSL settings
2. Test all application endpoints over HTTPS
3. Configure automatic certificate renewal (for Let's Encrypt)
4. Set up monitoring for certificate expiration
5. Configure proper security headers in nginx