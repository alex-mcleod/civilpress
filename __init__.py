from django.contrib.auth.models import User

User._meta.get_field_by_name('email')[0]._unique = True # Makes sure that email field for users is unique. 


