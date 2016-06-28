from app import app , db , lm
from itsdangerous import URLSafeTimedSerializer


def generate_confirmation_token(email):
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
	return serializer.dumps(email, salt=app.config['CONFIRM_SALT'])

def generate_passwordRecovery_token(email):
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
	return serializer.dumps(email,salt=app.config['PASSWORD_RECOVERY_SALT'])

#expiration 300 seconds
def get_confirm_token(token, expiration=300):
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
	try:
		email = serializer.loads(token,
			salt=app.config['CONFIRM_SALT'],
			max_age=expiration)
	except:
		return False
	return email

def get_passwordRecovery_token(token, expiration=300):
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
	try:
		email = serializer.loads(token,
			salt=app.config['PASSWORD_RECOVERY_SALT'],
			max_age=expiration)
	except:
		return False
	return email

