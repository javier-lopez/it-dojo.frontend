from itsdangerous import URLSafeTimedSerializer

from app import app

def generate_confirmation_token(data):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(data, salt='email-confirm')

def confirm_token(token, expiration=3600): #1 hour
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='email-confirm',
            max_age=expiration
        )
    except:
        return False
    return email




