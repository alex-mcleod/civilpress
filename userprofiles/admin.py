from django.contrib import admin
from userprofiles.models import UserProfile, Message
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from articles.models import Article

class UserProfileAdmin(admin.ModelAdmin):
    fields = ['user','dob','location','institute_enrolled_in','course_enrolled_in','academic_level']
    list_display = ('user', 'institute_enrolled_in','course_enrolled_in','academic_level')

class UserProfileInline(admin.StackedInline):
   model = UserProfile
   max_num = 1
   can_delete = False



class MessageAdmin(admin.ModelAdmin):
	fields = ['date_sent','sender', 'topic', 'message', 'active'] 
	list_display = ['sender','date_sent','topic', 'active'] 
	readonly_fields = ('date_sent',)

class ArticleInline(admin.StackedInline):
	model = Article
	extra = 1
	readonly_fields = ['primary_discipline', 'author','slug']

class UserAdmin(AuthUserAdmin):
    inlines = [ UserProfileInline, ArticleInline,]

#admin.site.register(UserProfile, UserProfileAdmin)

# unregister old user admin
admin.site.unregister(User)
# register new user admin
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Message, MessageAdmin)
