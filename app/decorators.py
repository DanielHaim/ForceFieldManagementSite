from threading import Thread


# target recoit une fonction a executer dans son Thread
def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


#tres bon lien pour les decorateurs en python
#http://gillesfabio.com/blog/2010/12/16/python-et-les-decorateurs/

#je n'en ai pas besoin pour l'instant parceque je me suffit du @login_required
#mais on sait jamais donc ca creer un decorator @confirmed_user_required
def confirmed_user_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('signIn')) 
            #idealement ca doit retourner vers une page dedie a un user non confirme
        return func(*args, **kwargs)
    return decorated_function
