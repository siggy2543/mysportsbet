@echo off
REM Sports Betting App - Windows SSL Setup Script
REM Generates self-signed SSL certificates for local development

echo.
echo ================================
echo  Sports Betting App SSL Setup
echo ================================
echo.

REM Check if OpenSSL is available
where openssl >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] OpenSSL not found in PATH
    echo.
    echo Please install OpenSSL for Windows:
    echo 1. Download from: https://slproweb.com/products/Win32OpenSSL.html
    echo 2. Or install via Chocolatey: choco install openssl
    echo 3. Or use Windows Subsystem for Linux ^(WSL^)
    echo.
    pause
    exit /b 1
)

echo [INFO] OpenSSL found, proceeding with certificate generation...

REM Create directories
if not exist "nginx\ssl" mkdir nginx\ssl
if not exist "frontend\ssl" mkdir frontend\ssl

echo [INFO] Created SSL directories

REM Generate private key
echo [INFO] Generating private key...
openssl genrsa -out nginx\ssl\privkey.pem 2048
if %errorlevel% neq 0 (
    echo [ERROR] Failed to generate private key
    pause
    exit /b 1
)

REM Create certificate configuration
echo [INFO] Creating certificate configuration...
echo [req] > nginx\ssl\cert.conf
echo distinguished_name = req_distinguished_name >> nginx\ssl\cert.conf
echo x509_extensions = v3_req >> nginx\ssl\cert.conf
echo prompt = no >> nginx\ssl\cert.conf
echo. >> nginx\ssl\cert.conf
echo [req_distinguished_name] >> nginx\ssl\cert.conf
echo CN = localhost >> nginx\ssl\cert.conf
echo. >> nginx\ssl\cert.conf
echo [v3_req] >> nginx\ssl\cert.conf
echo keyUsage = keyEncipherment, dataEncipherment >> nginx\ssl\cert.conf
echo extendedKeyUsage = serverAuth >> nginx\ssl\cert.conf
echo subjectAltName = @alt_names >> nginx\ssl\cert.conf
echo. >> nginx\ssl\cert.conf
echo [alt_names] >> nginx\ssl\cert.conf
echo DNS.1 = localhost >> nginx\ssl\cert.conf
echo DNS.2 = *.localhost >> nginx\ssl\cert.conf
echo DNS.3 = sports-betting.local >> nginx\ssl\cert.conf
echo IP.1 = 127.0.0.1 >> nginx\ssl\cert.conf
echo IP.2 = ::1 >> nginx\ssl\cert.conf

REM Generate self-signed certificate
echo [INFO] Generating self-signed certificate...
openssl req -new -x509 -key nginx\ssl\privkey.pem -out nginx\ssl\fullchain.pem -days 365 -config nginx\ssl\cert.conf
if %errorlevel% neq 0 (
    echo [ERROR] Failed to generate certificate
    pause
    exit /b 1
)

REM Create chain file
echo [INFO] Creating certificate chain...
copy nginx\ssl\fullchain.pem nginx\ssl\chain.pem >nul

REM Set file permissions (make private key read-only)
attrib +R nginx\ssl\privkey.pem

echo.
echo ================================
echo  SSL Certificate Setup Complete
echo ================================
echo.
echo Generated files:
echo - nginx\ssl\privkey.pem     (Private Key)
echo - nginx\ssl\fullchain.pem  (Certificate)
echo - nginx\ssl\chain.pem      (Certificate Chain)
echo.
echo Certificate Details:
openssl x509 -in nginx\ssl\fullchain.pem -noout -subject -dates -fingerprint

echo.
echo [SUCCESS] SSL certificates generated successfully!
echo.
echo Next Steps:
echo 1. Update your hosts file to include: 127.0.0.1 sports-betting.local
echo 2. Run: docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d
echo 3. Access your app at: https://localhost or https://sports-betting.local
echo 4. Accept the self-signed certificate warning in your browser
echo.
echo Note: For production, replace with proper SSL certificates from a CA
echo.
pause