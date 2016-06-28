from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session
from json import dumps
import json, urllib.request as urllib2

#http://stackoverflow.com/questions/12179271/python-classmethod-and-staticmethod-for-beginner

#https://github.com/miguelgrinberg/flask-oauth-example/blob/master/oauth.py

class OAuthSignIn(object):
    #It's a dict, contains all provider class
    #e.g providers = {'Facebook': FacebookSignIn,'Google':googleSignIn}
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    #for Facebook it will return : 
    #http://localhost:5000/callback/facebook
    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    #return the class of the provider_name 
    #e.g: if provider_name = facebook, it will return 
    #FacebookSignIn class defined below
    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                subclass = provider_class()
                self.providers[subclass.provider_name] = subclass
        return self.providers[provider_name]



class FacebookSignIn(OAuthSignIn):
    
    #in OAuth2Service , there is not request_token
    #and service.get_authorize_url() dosen't take
    #request_token as argument
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    #it's redirect the user to facebook page and he will be 
    #ask to allow our app for use his information
    #to register him with in our app 
    def authorize(self):
       	return redirect(self.service.get_authorize_url(
            scope='email,publish_actions',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    #link:http://rauth.readthedocs.io/en/latest/api/#rauth.OAuth2Service.get_auth_session
    #get_auth_session(data=data)
    #Gets an access token, 
    #intializes a new authenticated session with the access token. 
    #Returns an instance of session_obj.
    def callback(self):
    	if 'code' not in request.args:
    		return None
    	oauth_session = self.service.get_auth_session(
    		data={'code': request.args['code'],
    		      'grant_type': 'authorization_code',
    		      'redirect_uri': self.get_callback_url()}
    		)
    	me = oauth_session.get('v2.2/me?fields=id,email,first_name,last_name,name').json()
    	access_token = getattr(oauth_session, 'access_token')
    	logOutProvider_url = 'https://www.facebook.com/logout.php?access_token='+access_token+'&confirm=1&next=http://localhost:5000/'
    	user_info = {
    				 'logOutProvider_url':logOutProvider_url,
    	             'social_network':'facebook',
    	             'username':'facebook$'+me.get('id'),
    	             'email':me.get('email'),
    	             'firstname':me.get('first_name'),
    	             'lastname':me.get('last_name')
    	             }
    	return user_info


class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        googleinfo = urllib2.urlopen('https://accounts.google.com/.well-known/openid-configuration').read()
        google_params = json.loads(googleinfo.decode('utf-8'))
        self.service = OAuth2Service(
            name='Google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            access_token_url=google_params.get('token_endpoint'),
            authorize_url=google_params.get('authorization_endpoint'),
            base_url=google_params.get('userinfo_endpoint'),
            
        )

    
    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None
        oauth_session = self.service.get_auth_session(
                data={'code': request.args['code'],
                      'grant_type': 'authorization_code',
                      'redirect_uri': self.get_callback_url()
                     },
                decoder = json.loads
        )
        client_info = oauth_session.get('https://www.googleapis.com/oauth2/v1/userinfo?alt=json').json()
        #client_email = oauth_session.get('https://www.googleapis.com/userinfo/email?alt=json').json()
        logOutProvider_url ='https://www.google.com/accounts/Logout?continue=https://appengine.google.com/_ah/logout?continue=http://localhost:5000/'
        return {
			'logOutProvider_url':logOutProvider_url,
			'social_network':'google',
			'username':'google$'+client_info['id'],
			'email':client_info['email'],
			'firstname':client_info['given_name'],
			'lastname':client_info['family_name']}



#def dump_obj(obj):
#	target = open("/Users/daniel/Desktop/data1.txt",'w')
#	for attr in dir(obj):
#		target.write(attr)
#		target.write(str(getattr(obj, attr)))
#	target.close()

#target = open("/Users/daniel/Desktop/data1.txt",'w')
#target.write(json.dumps(oauth_session))
#target.close()