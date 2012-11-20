from django.template import Context, loader, RequestContext 
from django.http import HttpResponse
from settings import HOME_URL
from userprofiles.forms import MessageForm
from userprofiles.models import Message

def contact(request):
	context_dict = {}
	context_dict['homeURL'] = HOME_URL
	if request.user.is_authenticated():
		form = MessageForm(initial={'email': request.user.email,})
	else:
		form = MessageForm()

	if request.POST:
		form = MessageForm(request.POST)
		if form.is_valid():
			# NOTE: Contact form does not yet email admin. Fix this. 
			#subject = 'Message from user:' + request.POST['topic']
			#message = request.POST['message']
			#sender = request.POST['sender']
			#reciever_list = []
			#for u in User.objects.filter(is_superuser = True):
			#	reciever_list.append(u)
			#send_mail(subject, message, sender, reciever_list, fail_silently=False) Need to fix this line so that email is sent properly. 
			message_obj = Message(topic = form.cleaned_data['topic'], message = form.cleaned_data['message'], sender = form.cleaned_data['sender'], active = True)
			message_obj.save()
			context_dict['success_message'] = "Your message has been sent. We will make sure to get back to you as soon as possible."
	context_dict['form'] = form 
	template = loader.get_template('userprofiles/contact.html')
	context = RequestContext(request, context_dict)
	return HttpResponse(template.render(context))

def plagiarism(request):
	context_dict = {}
	context_dict['homeURL'] = HOME_URL
	template = loader.get_template('plagiarism.html')
	context = RequestContext(request, context_dict)
	return HttpResponse(template.render(context))
	