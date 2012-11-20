from django.contrib.auth.models import User, check_password

class EmailAuthBackend(object): # from http://www.micahcarrick.com/django-email-authentication.html --- Allows users to login using email address. Comment out AUTHENTICATION_BACKENDS = ('backends.EmailAuthBackend',) in settings.py to return to default setting (user logs in using username). 
    """
    Email Authentication Backend
    
    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """
    
    def authenticate(self, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None 

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
