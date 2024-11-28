import jwt

from datetime import datetime
from .secret_key import SECRET_KEY

CUSTOMER_PATH = "http://localhost:5000"
INVENTORY_PATH = "http://localhost:5001"
ADMIN_PATH = "http://localhost:5005"
LOG_PATH = "http://localhost:5006"

def extract_auth_token(authenticated_request):
    '''
    Extract Authentication Token.
    '''
    auth_header = authenticated_request.headers.get('Authorization')
    if auth_header:
        return auth_header.split(" ")[1]
    else:
        return None


def decode_token(token):
    '''
    Decode Authentication Token.
    '''
    payload = jwt.decode(token, SECRET_KEY, 'HS256')
    return payload['id']

def create_token(user_id):
    """
    Create a user token.

    Requires:
        user id (int)

    Returns:
        JWT Token
    """
    
    payload = {
        'iat': datetime.utcnow(),
        'id': user_id
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm='HS256'
    )
