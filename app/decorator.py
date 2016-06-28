from threading import Thread


# target recoit une fonction a executer dans son Thread
def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


#tres bon lien pour les decorateurs en python
#http://gillesfabio.com/blog/2010/12/16/python-et-les-decorateurs/