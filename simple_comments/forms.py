from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.comments.forms import CommentDetailsForm, COMMENT_MAX_LENGTH

'''
Custom form used instead of the standard comments form. 
NOTE: In future, could add Javascript which deletes the initial form value (i.e. 'Type your comment here') when the
field is clicked on. 
'''
class SimpleCommentForm(CommentDetailsForm):
    # Call to ModelForm constructor
    def __init__(self, *args, **kwargs):
        super(SimpleCommentForm, self).__init__(*args, **kwargs) 
        self.fields['comment'].widget.attrs['cols'] = 143
        self.fields['comment'].widget.attrs['rows'] = 5
	# Add a CSS class to the comment field for styling purposes. 
	self.fields['comment'].widget.attrs.update({'class' : 'text_area'})
	self.fields['comment'].initial = 'Type your comment here.'

    # Email field customised so that it is no longer required. 
    email = forms.EmailField(label=_("Email address"), required=False)
    # Comment field with custom error messages.
    comment       = forms.CharField(label=_('Comment'), widget=forms.Textarea,
                                    max_length=COMMENT_MAX_LENGTH, error_messages={'required': u'You have not entered a valid comment. '})

def get_form():
    return CommentForm
