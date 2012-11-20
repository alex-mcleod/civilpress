from django.contrib.auth.decorators import login_required
from django.contrib.comments.models import Comment
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib import comments
from django.http import Http404
from django.http import HttpResponseRedirect

'''
This view allows users to remove their own comments from the site. Comments are not deleted, 
instead their is_public field is set to False. 
'''
@login_required
def remove_own_comment(request, message_id):
    comment = get_object_or_404(comments.get_model(), pk=message_id,
            site__pk=settings.SITE_ID)
    if comment.user == request.user:
        comment.is_public = False
        comment.save()
    if request.GET.get('next'):
	return HttpResponseRedirect(request.GET.get('next'))
    return HttpResponseRedirect('/') 
