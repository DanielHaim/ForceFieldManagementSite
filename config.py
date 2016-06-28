import os

basedir = os.path.abspath(os.path.dirname(__file__))
#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'sqlalchemy_table.db')

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'sqlalchemy_table.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

#config for csrf attack , token and session
WTF_CSRF_ENABLED = True
SECRET_KEY = b'EPj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Ym'

#config for token
CONFIRM_SALT = "activation_link_salt"
PASSWORD_RECOVERY_SALT = "password_recovery_salt"

#config for send email
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = "danielmoisehaim@gmail.com"
MAIL_PASSWORD = ""
MAIL_ASCII_ATTACHMENTS = True
ADMINS = ['danielmoisehaim@gmail.com']


#config for OAuth 
GOOGLE_ID = '77946648146-ehvbe7met5kpr13poc8cqbl0ehvfdabi.apps.googleusercontent.com'
FACEBOOK_ID = '1266250030074001'

OAUTH_CREDENTIALS= {
    'google': {
        'id': GOOGLE_ID,
        'secret': 'MaL4sRSJI5CksvDikFG-6cnL'
    },
    'facebook':{
    	'id':FACEBOOK_ID,
    	'secret': '4fec2ff3b674530b053d2b08837635d1'

    }
}

#config for upload file
UPLOAD_FOLDER = os.path.join(basedir,'app/static/files/')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','db'])

