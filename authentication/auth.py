import jwt

# Use JWT for authentication instead of sessions
def login(username, password):
    # Authenticate user
    token = jwt.encode({
        "username": username, 
        "exp": datetime.utcnow() + timedelta(days=1)  
    }, app.config["SECRET_KEY"])
    
    return {"token": token}

def protected_route(function):
    @wraps(function)
    def wrap(*args, **kwargs):
        token = request.headers.get("Authorization") 
        try:
            jwt.decode(token, app.config["SECRET_KEY"])
            return function(*args, **kwargs)
        except:
            return "Invalid token", 401
    return wrap
# JWT based authentication instead of sessions

def create_token(user):
    """Generates a JSON Web Token for the user"""
    token = jwt.encode({'username': user.username}, SECRET_KEY, algorithm='HS256')
    return token

def validate_token(token):
    """Validates if the JWT token is valid"""
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return data
    except:
        return None
# Auth routes and token handling

from flask import app


@app.route('/login', methods=['POST'])
def login():
    # Validate credentials and return JWT
    
@app.route('/protected')
@require_auth
def protected():
    # Protected endpoint