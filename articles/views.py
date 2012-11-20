from django.template import Context, loader, RequestContext 
from django.http import HttpResponse 
from articles.models import Article, Tag, Discipline, ArticleTagM2M, ArticleDisciplineM2M, ArticleUser_ratingM2M, Publication
from articles.upload_handlers import handle_uploaded_article
from articles.upload_form import UploadFileForm, EditFileForm
from userprofiles.models import UserProfile
from settings import DISCIPLINE_CHOICES, HOME_URL
from haystack.views import SearchView
from django.contrib.auth.models import User
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.utils import simplejson
from django.shortcuts import get_object_or_404
import string

'''
Defines all the views associated with viewing, uploading, editing and removing articles. The CivilPress.org homepage view is also defined here by the index() function. 
'''

def base_context():
	'''
	This function generates context which is used by pretty much every view.
	'''
	disciplines = []
	for dobj in Discipline.objects.all():
		disciplines.append(dobj.discipline_name)
	disciplines.sort()
	popular_tags = Tag.objects.all().order_by('-count')[:20]
	homeURL = HOME_URL
	base_article_container = "articles/base_article_container.html" # location of template to use for regular article containers
	return {'disciplines' : disciplines, 'popular_tags' : popular_tags,'homeURL':homeURL, 'base_article_container' : base_article_container,}

def index(request):
	'''
	This view is responsible for constructing the home page. 
	'''
	context_dict = base_context()
	articles_latest = Article.objects.all().order_by('-upload_date') 
	articles_popular = Article.objects.all().order_by('-rating', '-upload_date')
	# articles_featured = Article.objects.filter(featured = True).order_by('-upload_date')
	context_dict.update({'articles_latest' : articles_latest, 'articles_popular' : articles_popular})
	template = loader.get_template('base.html')
	# RequestContext used so that STATIC_URL is available (among other things). 	
	context = RequestContext(request, context_dict ) 
	if request.is_ajax():
		# The django-endless-pagination app is used to paginate each of the tabs on the home page (featured, latest, highest rated). Each has seperate 
		# pagination. They are differentiated by the 'querystring_key' variable in the GET request, with the value of this variable determined in the 
		# respective page templates for each of these tabs. See http://django-endless-pagination.readthedocs.org/en/latest/multiple_pagination.html for 
		# a full breakdown of what is going on.  
		#if request.GET.get('querystring_key') == 'page':			   
       			#template = loader.get_template('articles/featured_articles_page.html')
		if request.GET.get('querystring_key') == 'latest_page':			   
       			template = loader.get_template('articles/latest_articles_page.html')
		if request.GET.get('querystring_key') == 'highest_rated_page':			   
       			template = loader.get_template('articles/highest_rated_articles_page.html')
	context_dict['more_articles_btn_text'] = 'More articles'			
	return HttpResponse(template.render(context))

def view_article(request, article_pk, article_slug):
	'''
	Constructs the view_article page. 
	'''
	context_dict = base_context()
	article = None 
	# Get article to view
	article = get_object_or_404(Article, pk = article_pk, slug = article_slug)
	article.number_of_views += 1
	# 'r' is the user's rating of this article. 
	if request.POST.get('r'):
		# This if statement does not cause a redirect if ajax is used to update user ratings. Instead, redirection to login if user is not authenticated is handled in the template.
		if not request.user.is_authenticated():
			return HttpResponseRedirect(('login/?next=' + article.get_absolute_url()))  
		else:  
			# NOTE: This if statement is possibly unnecessary, though it does stop users from sending GET requests to this page with huge numbers.   
			if int(request.POST.get('r')) in [0,1,2,3,4,5,6,7,8,9,10]:
				new_rating = request.POST.get('r')
				a_ur_relationship = ArticleUser_ratingM2M.objects.get_or_create(user = request.user.profile
				, rated_article=article)
				a_ur_relationship[0].rating = new_rating
				a_ur_relationship[0].save()							
				article.update_rating()
	# If user has already rated this article, create 'user_rating' variable so that we can prefill the star rating on the page with the user's rating. 
	if request.user.is_authenticated():  
		if article in request.user.profile.rated_articles.all():
			a_ur_relationship = ArticleUser_ratingM2M.objects.get(user = request.user.profile, rated_article = article)
			context_dict['user_rating'] = a_ur_relationship.rating
	# Article is saved to maintain updates to number_of_views and average user rating. 
	article.save(False)
	context_dict['article'] = article
	template = loader.get_template('articles/view_article_flexpaper.html')
	context = RequestContext(request, context_dict)
	return HttpResponse(template.render(context))

def remove_article(request, article_pk, article_slug):
	''' 
	View which handles removal of articles from CivilPress.org.
	'''
	context_dict = base_context() 
	article_to_delete = get_object_or_404(Article, pk = article_pk, slug = article_slug)
	if not request.user.is_authenticated():
		raise Http404
	if not request.user == article_to_delete.user:
		raise Http404
	# If user clicks delete, 'action' field will send 'delete' and the article will be removed from CivilPress.org when this view is reloaded. 
	if request.POST.get('action') == 'delete':
		article_to_delete.delete()
		return HttpResponseRedirect('/') 
	context_dict['article'] = article_to_delete	
	template = loader.get_template('articles/edit_or_delete_article.html')
	context = RequestContext(request, context_dict)
	return HttpResponse(template.render(context))
		

def edit_article(request, article_pk, article_slug):
	'''
	Allows users to edit their own articles when they are logged in. 
	NOTE: Make sure that article is only saved one time when a change is made (it used to be saved several times within this view).  
	'''
	context_dict = base_context() 
	article_to_edit = get_object_or_404(Article, pk = article_pk, slug = article_slug)
	if not request.user.is_authenticated():
		raise Http404
	if not request.user == article_to_edit.user:
		raise Http404
	# If there is a POST request, then change details of article.
	if request.method == 'POST':
		form = EditFileForm(request.POST)
		if not request.POST.get('anonymous'): # If anonymous box is unchecked, then null value will be sent causing integrity error when article is saved (as BooleanFields do not accept null values). 
			anonymous = 0
		else:
			anonymous = request.POST.get('anonymous')
		if form.is_valid():
			article_to_edit.title = request.POST.get('title')
			article_to_edit.prompt = request.POST.get('prompt')
			article_to_edit.subject_submitted_for = request.POST.get('subject_submitted_for')
			article_to_edit.academic_institution = request.POST.get('academic_institution')
			article_to_edit.academic_level = request.POST.get('academic_level')
			article_to_edit.grade = request.POST.get('grade')
			article_to_edit.anonymous = anonymous
			# Exception will be raised if no word_limit is given (as int('') will raise an error). Really, django should insert '' as None in the database, but for some
			# reason it does not do this when ModelForm is used. It will, however, do this when the admin site is used. Note: Future versions of django could fix this
			# issue.
			word_limit = request.POST.get('word_limit')
			try:
				word_limit = int(word_limit)
			except:
				word_limit = None
			article_to_edit.word_limit = word_limit
			# Article is saved before tag and discipline relationships are created as these relationships can be saved independently of the entire article.
			article_to_edit.save()
			# Strips initial string of tags.
			tags = request.POST.get('tags').strip() 
			if tags != '':			    	 
				tags = tags.split(',')
				tags_stripped = []
				# Strips individual tags.
				for t in tags: 
					if t != '': 
						tags_stripped.append(t.strip())
				tags = tags_stripped
				tags_temp = tags
				tags = []
				for t in tags_temp:
					t_lower = t.lower()
					t_lower_nopunc = ''
					for letter in t_lower:
						if letter in string.punctuation:
							letter = ''
						t_lower_nopunc += letter
					tags.append(t_lower_nopunc)
				# This loop creates tag relationships if they are added to the article.	    		
				for t in tags: 
					tObj = Tag.objects.get_or_create(tag_name = t)
					t_a_relationship = ArticleTagM2M.objects.get_or_create(article=article_to_edit, tag=tObj[0])
					t_a_relationship[0].save()
			# This loop deletes tag relationships if they are removed from the tag list. Will happen even if request.POST.get('tags') is empty.
			for article_tag in article_to_edit.tags.all():  				
				if article_tag.tag_name not in tags:
					t_a_relationship = ArticleTagM2M.objects.get(article=article_to_edit, tag = article_tag) 
					t_a_relationship.delete() 
			# request.POST.get('discipline') holds the primary key (not the name) of the selected discipline. 
			discipline = request.POST.get('discipline')
			if discipline != '':
				dObj = Discipline.objects.get_or_create(pk = discipline)
				# If discipline is changed, then delete old discipline article relationship and create new.
				if dObj not in article_to_edit.disciplines.all():
					if article_to_edit.disciplines.all().exists():
						d_a_relationship = ArticleDisciplineM2M.objects.get(article=article_to_edit, discipline = article_to_edit.disciplines.all()[0])
						d_a_relationship.delete() 
					d_a_relationship = ArticleDisciplineM2M.objects.get_or_create(article=article_to_edit, discipline = dObj[0])
					d_a_relationship[0].save()
			# If there is no discipline, then simply delete old discipline-article relationship.
			else:	 		 
				if article_to_edit.disciplines.all().exists():
					d_a_relationship = ArticleDisciplineM2M.objects.get(article=article_to_edit, discipline = article_to_edit.disciplines.all()[0])
					d_a_relationship.delete()
	# If there is no post request, will prefill form on this page. 
	else:		
		# If no disciplines have been selected, then an exception will be raised. 
		try:
			form = EditFileForm(initial={'title': article_to_edit.title, 'prompt':article_to_edit.prompt, 'discipline': article_to_edit.disciplines.all()[0].pk, 'tags':article_to_edit.tag_list(),'academic_institution': article_to_edit.academic_institution, 'subject_submitted_for':article_to_edit.subject_submitted_for, 'academic_level': article_to_edit.academic_level, 'anonymous' : article_to_edit.anonymous,'grade' : article_to_edit.grade, 'word_limit' : article_to_edit.word_limit
			})
		except:
			form = EditFileForm(initial={'title': article_to_edit.title, 'anonymous' : article_to_edit.anonymous, 'prompt':article_to_edit.prompt, 'tags':article_to_edit.tag_list(),'academic_institution': article_to_edit.academic_institution, 'subject_submitted_for':article_to_edit.subject_submitted_for, 'academic_level': article_to_edit.academic_level, 'grade' : article_to_edit.grade, 'word_limit' : article_to_edit.word_limit
			})				
  	context_dict['form'] = form					
	context_dict['article'] = article_to_edit
	# 'action' variable is used by the template to decide whether to show an edit or delete form.
	context_dict['action'] = 'edit'  
	template = loader.get_template('articles/edit_or_delete_article.html')
	context = RequestContext(request, context_dict)
	return HttpResponse(template.render(context))

class ArticleSearchView(SearchView):
    '''
    Used to construct the search page. Inherits from Haystack's SearchView. 
    '''
    def __name__(self):
        return "SearchViewBaseContext"

    def extra_context(self):
        extra = super(ArticleSearchView, self).extra_context()
	# Include base_context in search page so that we can show disciplines and tags in the sidebar. 
	self.context_dict = base_context()
	extra.update(self.context_dict)
	# article_set holds the search results so that they can be manipulated independently of the default pagination used by haystack. NOTE: This is perhaps
	# inefficient as the results are calculated by haystack THEN rearranged into the article_set list (this could be done in one loop). 	
	article_set = [] 
	for article in self.results:
		article_set.append(article.object)
	extra['article_set'] = article_set
        return extra

    def create_response(self):
	# overriden method. Addition of ajax functionality for endless pagination. This method is simply a COPY of the original, with the if self.request.is_ajax() part added.
	# endless pagination uses the article_set constructed in extra_context().  
        """
        Generates the actual HttpResponse to send back to the user.
        """
        #(paginator, page) = self.build_page() Uncomment this line to use the default Haystack pagination. Endless pagination is currently being used, making this line redundant. 

        context = {
            'query': self.query,
            'form': self.form,
            #'page': page,
            #'paginator': paginator,
            'suggestion': None,
        }

        if self.results and hasattr(self.results, 'query') and self.results.query.backend.include_spelling:
            context['suggestion'] = self.form.get_suggestion()

        context.update(self.extra_context())
	# simply changes the template if this is an AJAX request. This is required for endless pagination. Else statement is necessary as otherwise self.template will remain 'search_articles_page.html' after a single ajax request is made, meaning future searches will always use this template to show the whole search page, not just the new search results requested by endless pagination. 
	if self.request.is_ajax():	
		self.template = 'search/search_articles_page.html'
	else:
		self.template = 'search/search.html'

        return render_to_response(self.template, context, context_instance=self.context_class(self.request))

def upload(request):
    '''
    Handless uploading files to CivilPress.org. NOTE: The actual file format of the uploaded file is currently not checked! This is a big security loophole. 
    '''
    if not request.user.is_authenticated():
	return HttpResponseRedirect('/login/?next=/upload/')
    context_dict = base_context()
    if request.method == 'POST':
	 # Must add user to request.POST, as otherwise the unique constraint on article user and title will not be run (as technically no user is associated with the article in request.POST initially, therefore unique constraint is ignored by django. 
        request.POST['user'] = request.user.id
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
           # handle_uploaded_article(request.FILES['file'], form.title) --- NOTE: NEED TO DO SOMETHING LIKE THIS TO VALIDATE FILE!
	    # Exception will be raised if no word_limit is given (as int('') will raise an error). Really, django should insert '' as None in the database, but for some
	    # reason it does not do this when ModelForm is used. It will, however, do this when the admin site is used. Note: Future versions of django could fix this
	    # issue.
	    word_lim = request.POST.get('word_limit')
	    try:
		word_lim = int(word_lim)
	    except:
		word_lim = None
	    # Check if articles was submitted to an academic institution (selected using the 'select' select box). If not, then don't include this information when creating this article. That way, 
	    # information which is automatically added to the form like 'academic institution' are not included if the article was not submmitted to an academic institute. 
	    if not request.POST.get('anonymous'): # If anonymous box is unchecked, then null value will be sent causing integrity error when article is saved (as BooleanFields do not accept null values). 
		request.POST['anonymous'] = 0
	    if request.POST.get('select') == "1":
	    		article = Article(
				title = request.POST.get('title'), 
				user = request.user,
				file_field = request.FILES['file_field'],
				prompt = request.POST.get('prompt'),
				subject_submitted_for = request.POST.get('subject_submitted_for'),
				academic_institution = request.POST.get('academic_institution'),
				academic_level = request.POST.get('academic_level'),	
				grade = request.POST.get('grade'),
				word_limit = word_lim,
				anonymous = request.POST.get('anonymous')
				)
	    else:
			article = Article(
				title = request.POST.get('title'), 
				user = request.user, 
				file_field = request.FILES['file_field'],
				anonymous = request.POST.get('anonymous'),
				)
	    article.save()
            # Strips initial string of tags. NOTE: This exact sequence is also performed by the edit_article view. Should probably be made into a function. 
	    tags = request.POST.get('tags').strip() 
	    tags = tags.split(',')
	    tags_stripped = []
	    for t in tags:
		if t != '':
			# Strips individual tags.
			tags_stripped.append(t.strip()) 
	    tags = tags_stripped
	    # Create tag_article relationships. 
	    for t in tags:
		t_lower = t.lower()
		t_lower_nopunc = ''
		for letter in t_lower:
			if letter in string.punctuation:
				letter = ''
			t_lower_nopunc += letter
		tObj = Tag.objects.get_or_create(tag_name = t_lower_nopunc)
		t_a_relationship = ArticleTagM2M(article=article, tag=tObj[0])
		t_a_relationship.save()
	    # Try and create article_discipline relationship. Note: Try statement could perhaps be replaced by a check that request.POST.get('discipline') has been selected. 
	    try:
		    discipline = request.POST.get('discipline')
		    dObj = Discipline.objects.get_or_create(pk = discipline)
		    d_a_relationship = ArticleDisciplineM2M(article=article, discipline = dObj[0])
		    d_a_relationship.save()
	    except:
		print 'Exception in article.views.upload: Tried to get or create discipline for ArticleDisciplineM2M and was unable to do so. This probably means that no discipline was specified in the form.' 

            return HttpResponseRedirect(article.get_absolute_url())
    # Prefill some of the form with details from ther user's account.
    else:
        form = UploadFileForm(initial={'academic_institution': request.user.profile.institute_enrolled_in, 'academic_level': request.user.profile.academic_level, 'user' : request.user.id})
    context_dict['form'] = form
    template = loader.get_template('articles/upload.html')	
    context = RequestContext(request, context_dict )
    return HttpResponse(template.render(context))

def publications(request):
        '''
	Publication view. NOTE: This view is unfinished.
	'''
	context_dict = base_context()
	context_dict['publications'] = Publication.objects.all() 
	template = loader.get_template('articles/publications_coming_soon.html')
	context = RequestContext(request, context_dict)
	return HttpResponse(template.render(context)) 



	
