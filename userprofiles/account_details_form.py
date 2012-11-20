from django import forms
from userprofiles.models import UserProfile
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.extras.widgets import SelectDateWidget
import datetime

'''
This form is used for editing user profile information. Facebook registration plugin is used for
account creation. 
'''

now = datetime.datetime.now()
# Construct a list of all years up to and including current year. Note: Inefficient. This list only needs to be generated once a year. 
BIRTH_YEAR_CHOICES = []
for year in reversed(range(1900,now.year+1)):
	BIRTH_YEAR_CHOICES.append(str(year))

class UserModelForm(ModelForm): 
    class Meta:
        model = User
	exclude = ('username','password','email','last_login','date_joined')

class ProfileModelForm(ModelForm):
	class Meta:
		model = UserProfile
		exclude = ('user',)
		widgets = {
            'dob': SelectDateWidget(years=BIRTH_YEAR_CHOICES),
       			 }


