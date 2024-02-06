def create_success_response(data):
    return {
        "status": "success", 
        "data": data
    }

def create_error_response(message, status_code=400):
    return {
        "status": "error",
        "message": message,
        "status_code": status_code  
    }
