from random import choice
import hashlib
import urllib2
import json
import base64
import hmac
from django.http import Http404
from django.http import HttpResponseRedirect
from django.template import Context, loader, RequestContext 
from django.http import HttpResponse
from articles.views import base_context
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import settings
from settings import HOME_URL
from settings import EDUCATION_LEVEL_CHOICES
from userprofiles.account_details_form import UserModelForm, ProfileModelForm
from django.core.mail import send_mail
from userprofiles.forms import MessageForm
from userprofiles.models import Message
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import UserCreationForm

def create_account(request):
	context_dict = base_context()
	JSON_ELC = str(EDUCATION_LEVEL_CHOICES) # JSON_ELC is a version of EDUCATION_LEVEL_CHOICES converted into a format useable by the Facebook registration plugin (converts from tuple to dictionary). 
	JSON_ELC_LIST = JSON_ELC[:-1].split(',')
	JSON_ELC = '{'
	for index in range(0,len(JSON_ELC_LIST),2):
		key = JSON_ELC_LIST[index][2:]
		value = JSON_ELC_LIST[index+1][:-1]
		JSON_ELC += key + ':' + value + ','

	JSON_ELC += '}'
	context_dict['EDUCATION_LEVEL_CHOICES'] = mark_safe(JSON_ELC) # Mark_safe is used to stop django auto-escaping quotation marks. 

	if request.is_ajax():
		response = {'username':True, 'email' : False}
		try:
			User.objects.get(username = request.GET['username'])
		except:
			response['username'] = False

		return HttpResponse(json.dumps(response), mimetype="application/json")
	  
		
	template = loader.get_template('userprofiles/create_account.html')
	context = RequestContext(request, context_dict)
        
	return HttpResponse(template.render(context)) 

def parse_signed_request(signed_request, app_secret): # From http://www.rkblog.rk.edu.pl/w/p/facebook-aided-registration-django/
    """Return dictionary with signed request data.
    Code taken from https://github.com/facebook/python-sdk"""
    try:
      l = signed_request.split('.', 2)
      encoded_sig = str(l[0])
      payload = str(l[1])
    except IndexError:
      raise ValueError("'signed_request' malformed")
    
    sig = base64.urlsafe_b64decode(encoded_sig + "=" * ((4 - len(encoded_sig) % 4) % 4))
    data = base64.urlsafe_b64decode(payload + "=" * ((4 - len(payload) % 4) % 4))

    data = json.loads(data)

    if data.get('algorithm').upper() != 'HMAC-SHA256':
      raise ValueError("'signed_request' is using an unknown algorithm")
    else:
      expected_sig = hmac.new(app_secret, msg=payload, digestmod=hashlib.sha256).digest()

    if sig != expected_sig:
      raise ValueError("'signed_request' signature mismatch")
    else:
      return data

@csrf_exempt
def register_user(request): # From http://www.rkblog.rk.edu.pl/w/p/facebook-aided-registration-django/
	"""
	Register a user from Facebook-aided registration form
	"""
	if request.POST:
		if 'signed_request' in request.POST:
			# parse and check data
			data = parse_signed_request(request.POST['signed_request'], settings.FACEBOOK_APP_SECRET)
			
			# lets try to check if user exists based on username or email
			try:
				check_user = User.objects.get(username=data['registration']['username'])
			except:
				pass
			else:
				return HttpResponseRedirect('/')
			
			try:
				check_user = User.objects.get(email=data['registration']['email'])
			except:
				pass
			else:
				return HttpResponseRedirect('/')
			
			form = UserCreationForm(data = {'password1':data['registration']['password'],'password2':data['registration']['password'],'username':data['registration']['username'], 'email':data['registration']['email']})
			print "FORM ERRORS:", form.errors
			# Form validation is performed by JavaScript on the create account page, however if that fails then validation here makes sure that no form errors hit the database. 
			if form.is_valid():
				# user does not exist. We create an account
				# in this example I assume that he will login via Facebook button or RPXnow
				# so no password is needed for him - using random password to make Django happy
				#randompass = ''.join([choice('1234567890qwertyuiopasdfghjklzxcvbnm') for i in range(7)])
				name_list = data['registration']['name'].split(' ')
				if len(name_list) > 1:
					first_name = name_list[0]
					last_name = name_list[-1]
				else:
					first_name = name_list[0]
					last_name = ''
				#username = data['registration']['email'].split('@')[0]
				try:
					user = User.objects.create_user(data['registration']['username'], data['registration']['email'], data['registration']['password'])
				except Exception as e: 
					print e
			
				user.save()

				user.first_name = first_name
				user.last_name = last_name
				user.save()

                     	#user.profile = UserProfile.objects.get_or_create(user=user)
				profile = user.profile # Must be accessed in this fashion (as opposed to just calling user.profile.suchandsuch to change values). 
				print data['registration']['birthday']
				dob = data['registration']['birthday']
				if dob[1] == '/' and dob[3] == '/': # 1/1/1111
					dob = dob[4:] + '-' + dob[0] + '-' + dob[2]    
				elif dob[1] == '/' and dob[4] == '/': # 1/11/1111
					dob = dob[5:] + '-' + dob[0] + '-' + dob[2:4]
				elif dob[2] == '/' and dob[4] == '/': # 11/1/1111
					dob = dob[5:] + '-' + dob[0:2] + '-' + dob[3]
				elif dob[2] == '/' and dob[5] == '/': #11/11/1111
					dob = dob[6:] + '-' + dob[0:2] + '-' + dob[3:5] 
				print dob 
				profile.dob = dob
				profile.location = data['registration']['location']['name']
				profile.institute_enrolled_in = data['registration']['academic_institute']['name']
				profile.course_enrolled_in = data['registration']['course']
				profile.academic_level = data['registration']['year_level']
				profile.save()

				# Logout the current user before logging in the new user. 
				if request.user.is_authenticated():
					logout(request)

				user = authenticate(username=data['registration']['email'], password=data['registration']['password'])
				if user is not None:
					# save in user profile his facebook id. In this case for RPXNow login widget
					#fbid = 'http://www.facebook.com/profile.php?id=%s' % data['user_id']
					#r = RPXAssociation(user=user, identifier=fbid)
					#r.save()
	
					login(request, user)
				return HttpResponseRedirect('/')
			
	return HttpResponseRedirect('/create_account')

def logout_view(request):
    redirect_to = None

    if request.GET and request.GET['next'] != '':
	redirect_to = request.GET['next']

    logout(request)
    if redirect_to is None:
	return HttpResponseRedirect('/')
    else:
	return HttpResponseRedirect(redirect_to)

def login_view(request):

     if request.user.is_authenticated():
	print 'USER ALREADY LOGGED IN'
	return HttpResponseRedirect(HOME_URL)
	
     context_dict = base_context()

     user = None
     redirect_to = None

     if request.GET and request.GET['next'] != '':
	redirect_to = request.GET['next']
	context_dict['redirect_to'] = redirect_to

     if request.POST:
    	   username = request.POST['username']
    	   password = request.POST['password']
    	   user = authenticate(username=username, password=password)
    	   if user is not None:
        	if user.is_active:
           		login(request, user)
			if redirect_to is None:
				return HttpResponseRedirect('/')
			else:
				return HttpResponseRedirect(redirect_to)
        	else:
            		pass# Return a 'disabled account' error message
   	   else:
		error_message = "Invalid login: Please enter a correct username and password combination. Note that both fields are case-sensitive." 
		context_dict["error_message"] = error_message
                pass# Return an 'invalid login' error message.
		
     if user != None: # Doesn't do anything currently. User is already passed to template, checked for using user.is_anonymous.
	    if request.user.is_authenticated():
	        print '--------------------------------->>>>>>>>>>>>>User:',user.first_name, user.last_name
		    #context_dict['authenticated_user'] = user
	    else:
		pass# Do something for anonymous users.


     template = loader.get_template('userprofiles/login.html')
     context = RequestContext(request, context_dict )
     return HttpResponse(template.render(context))

def account(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(HOME_URL + 'login/?next=' + HOME_URL + 'account/')

	user = request.user
	user_profile = user.profile	
	context_dict = base_context()
	
	if request.POST:
		uform = UserModelForm(request.POST)
		pform = ProfileModelForm(request.POST)
		print uform.errors
		print pform.errors
		if uform.is_valid() and pform.is_valid():

			user.first_name = uform.cleaned_data['first_name']
			user.last_name = uform.cleaned_data['last_name']
			user_profile.location = pform.cleaned_data['location']
			user_profile.dob = pform.cleaned_data['dob']
			user_profile.institute_enrolled_in = pform.cleaned_data['institute_enrolled_in']
			user_profile.course_enrolled_in = pform.cleaned_data['course_enrolled_in']
			user_profile.academic_level = pform.cleaned_data['academic_level']
			user.save()
			user_profile.save()


	uform = UserModelForm(initial={'username': user.username, 'first_name': user.first_name, 'last_name':user.last_name, 'email': user.email, }) # Form for editing basic account details.
	pform = ProfileModelForm(initial={'dob': user.profile.dob, 'location': user.profile.location, 'institute_enrolled_in':user.profile.institute_enrolled_in, 'course_enrolled_in' : user.profile.course_enrolled_in, 'academic_level' : user.profile.academic_level})

	context_dict['uform'] = uform
	context_dict['pform'] = pform
	context_dict['article_set'] = user.articles.all().order_by('-upload_date')
        template = loader.get_template('userprofiles/account.html')
        context = RequestContext(request, context_dict )


	if request.is_ajax():
		template = loader.get_template('userprofiles/account_articles_page.html')
        return HttpResponse(template.render(context))















    
