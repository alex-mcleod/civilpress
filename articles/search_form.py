from django import forms
from haystack.forms import SearchForm
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet, EmptySearchQuerySet
from django import forms

'''
Defines the form used by Haystack in the ArticleSearchView. Overrides the SearchForm class 
to add the ability to to search multiple queries in multiple fields. 
'''

# These are the search fields presented to the user. 
FIELD_CHOICES = (
    ('All fields', 'All fields'),
    ('Titles', 'Titles'),
    ('Authors', 'Authors'),
    ('Article bodies', 'Article bodies'),
    ('Disciplines', 'Disciplines'),
    ('Tags', 'Tags'),
    ('Academic institutions', 'Academic institutions'),
    ('Subjects','Subjects'),
    ('Prompts','Prompts'),
)

class ArticleSearchForm(SearchForm):
    # q attribute is overriden from SearchForm class.
    q = forms.CharField(required=False, label=('Search for'))  
    q_searchfield = forms.ChoiceField(required=False,choices=FIELD_CHOICES, label=('in'))
    q2 = forms.CharField(required=False, label=('Search for'))
    q2_searchfield = forms.ChoiceField(required=False,choices=FIELD_CHOICES, label=('in'))
    q3 = forms.CharField(required=False, label=('Search for'))  
    q3_searchfield = forms.ChoiceField(required=False,choices=FIELD_CHOICES, label=('in'))
    # User field is used to limit searches to only include those articles by a specific user. We could just search for the user in 
    # the Authors field, but then we might get articles written by other users with the same name. This field is hidden in the search
    # view, and is only used when users click on the author of an article's name.  
    user = forms.CharField(required=False, label = 'user') 
    # Links query variables and searchfield variables. 
    query_search_field_list = [('q','q_searchfield'), ('q2','q2_searchfield'), ('q3','q3_searchfield')]
    # These will hold the queries for each search field. 
    all_query = ''
    title_query = ''
    author_query = ''
    body_query = ''
    discipline_query = ''
    tags_query = ''
    academic_institution_query = ''
    subject_query = ''
    prompt_query = '' 
    
    def search(self):
        # First, store the SearchQuerySet (sqs) received from other processing.
	# Note: Should perhaps include code from super class and change it as necessary to permit checking of multiple queries, not just 1.
        sqs = super(ArticleSearchForm, self).search()  
	if self.is_valid():
		# Cycle through the query and search_field pairs to construct the search queries for each field (i.e. if query is 'Alexander McLeod' and searchfield is 'Authors',
		# then 'Alexander McLeod' will be added to the author_query string). NOTE: The number of if statements could be reduced to just one here if another for loop is
		# used to cycle through the different query strings (i.e. 'all_query', 'title_query' etc) and their counterparts in FIELD_CHOICES. This would improve maintainability and 
		# readability. 
		for query, search_field in self.query_search_field_list:
			# This is how to access the query passed into the form.
			if self.cleaned_data[query]:
				if self.cleaned_data[search_field] == 'All fields':
				     self.all_query +=  self.cleaned_data[query] + ' '
				elif self.cleaned_data[search_field] == 'Titles':
				     self.title_query += self.cleaned_data[query] + ' '
				elif self.cleaned_data[search_field] == 'Authors':
				     self.author_query += self.cleaned_data[query] + ' '
				elif self.cleaned_data[search_field] == 'Article bodies':
				     self.body_query += self.cleaned_data[query] + ' '
				elif self.cleaned_data[search_field] == 'Disciplines':
				     self.discipline_query += self.cleaned_data[query] + ' '
				elif self.cleaned_data[search_field] == 'Tags':
				     self.tags_query += self.cleaned_data[query] + ' '
				elif self.cleaned_data[search_field] == 'Prompts':
				     self.prompt_query += self.cleaned_data[query] + ' '
				elif self.cleaned_data[search_field] == 'Subjects':
				     self.subject_query += self.cleaned_data[query] + ' '
				elif self.cleaned_data[search_field] == 'Academic institutions':
				     self.academic_institution_query += self.cleaned_data[query] + ' '
		# Can't entirely remember what this line is for, but it is necessary. 
        	sqs = self.searchqueryset.auto_query(self.all_query)
	# For each query string, check if it is not empty and filter the sqs accordingly. NOTE: For the sake of readability and maintainability, a for loop could be used here
	# to reduce the number of if statements to one.  
	if self.title_query != '':
		sqs = sqs.filter(title = self.title_query)
	if self.author_query != '':
		sqs = sqs.filter(author = self.author_query)
	if self.body_query != '':
		sqs = sqs.filter(content = self.body_query)
	if self.discipline_query != '':
		sqs = sqs.filter(disciplines = self.discipline_query)
	if self.tags_query != '':
		sqs = sqs.filter(tags = self.tags_query)
	if self.subject_query != '':
		sqs = sqs.filter(subject = self.subject_query)
	if self.prompt_query != '':
		sqs = sqs.filter(prompt = self.prompt_query)
	if self.academic_institution_query != '':
		sqs = sqs.filter(academic_institution = self.academic_institution_query)
	if self.cleaned_data['user'] != '':		
		sqs = sqs.filter(user = self.cleaned_data['user'])
	# Finally, return the filtered sqs. 
        return sqs

    def no_query_found(self):
        """
        Determines the behavior when no query was found.

        By default, no results are returned (``EmptySearchQuerySet``).

        Should you want to show all results, override this method in your
        own ``SearchForm`` subclass and do ``return self.searchqueryset.all()``.
        """
        return EmptySearchQuerySet()
	#return self.searchqueryset.all()
