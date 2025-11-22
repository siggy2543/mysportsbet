@echo off
echo Setting up SSL certificates for Windows...

REM Create SSL directory if it doesn't exist
if not exist "nginx\ssl" mkdir nginx\ssl
if not exist "frontend\ssl" mkdir frontend\ssl

echo Generating SSL certificates...

REM Generate private key
openssl genrsa -out nginx\ssl\server.key 2048

REM Generate certificate
openssl req -new -x509 -key nginx\ssl\server.key -out nginx\ssl\server.crt -days 365 -subj "/C=US/ST=MD/L=Baltimore/O=SportsBettingApp/CN=localhost"

if exist nginx\ssl\server.crt (
    echo [SUCCESS] SSL certificates generated successfully
    
    REM Copy certificates to frontend
    copy nginx\ssl\server.crt frontend\ssl\
    copy nginx\ssl\server.key frontend\ssl\
    
    echo [SUCCESS] SSL certificates copied to frontend
    echo SSL setup completed successfully!
) else (
    echo [ERROR] Failed to generate SSL certificates
    exit /b 1
)