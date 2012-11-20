from django.db import models
from django.contrib import admin
from django.db import models
from settings import EDUCATION_LEVEL_CHOICES, TOPIC_CHOICES
from django.contrib.auth.models import User



# Create your models here.

class UserProfile(models.Model):

    def __unicode__(self):
        return self.user.username

    user = models.ForeignKey(User, unique = True, related_name = 'profile')
    dob = models.DateField('Date of birth', blank = True, null = True) # Not sure if max_length refers to number of integers or length of each integer. 
    location = models.CharField('Location', max_length = 50, blank = True, null = True, default = '')

    # The following three fields will be left blank if user is not enrolled in an academic institute. 
    institute_enrolled_in = models.CharField('Academic institute currently enrolled in', max_length = 100, blank = True)
    course_enrolled_in = models.CharField('Academic course currently enrolled in', max_length = 100, blank = True)
    academic_level = models.CharField('Current year level',max_length=15, choices=EDUCATION_LEVEL_CHOICES, blank = True) 


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0]) # Makes it so that if user.profile is typed anywhere else in civilpress, a userprofile object is created for the User in question if one does not already exist.
 

class Message(models.Model):
	def _unicode_(self):
		return sender

	class Meta:
		ordering = ['-active','date_sent']

	date_sent = models.DateTimeField(auto_now_add=True)	
	message = models.TextField();
	sender = models.EmailField(max_length = 500) # Email address of user who sent message. 
	topic = models.CharField(max_length = 50, choices = TOPIC_CHOICES)
	active = models.BooleanField() # Has problem been dealt with? 
	


    
    
