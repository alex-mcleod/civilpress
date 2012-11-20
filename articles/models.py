import os
from articles.format_checker import *
from django.db import models
from django.contrib import admin
from userprofiles.models import UserProfile
from settings import DISCIPLINE_CHOICES, EDUCATION_LEVEL_CHOICES, GRADE_CHOICES, ANON_CHOICES
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.contrib.auth.models import User
from articles.convert_document import convert_document, pdf_to_swf
from settings import MEDIA_ROOT
import string
import shutil
from django.template.defaultfilters import slugify
import sys, traceback
import inspect
from manage import who_is_caller
'''
########## Article model definitions ############
Alexander McLeod <alxmcleod@gmail.com> 
This script defines every model and function related to the displaying and categorisation of articles on Civilpress.
#################################################
'''

'''
Article class: 
This is, of course, the class which defines the Article database model. 
It contains definitions for each of the fields associated with an article, and also for the functions responsible for 
creating or manipulating that information (e.g. the article's URL).
'''
class Article(models.Model):
	
    class Meta:
	# The title and authorial user for each article must be unique or else there will be URL conflicts.
	unique_together = ('title','user') 

    # This class can be used by templates to order articles. Methods in templates cannot take arguments, leading to the necessity of these functions. 
    class order:
	def by_date():
		return Article.objects.all().order_by('-upload_date')
	
	def by_rating():
		return Article.objects.all().order_by('-rating')

    # Serves the same purpose as the order class. 
    class filter_and_order:
	def by_featured():
		return Article.objects.filter(featured = True).order_by('-upload_date')
			     
    def __init__(self, *args, **kwargs): 
            super(Article, self).__init__(*args, **kwargs) 
	    # Each time an article is accessed in the database, it's current file_field is held onto so 
	    # that the file is not re-converted if the file_field is not changed (as this would be completely redundant).
	    self.original_file_field = self.file_field		
								 
    # Called whenever the name of an Article object is accessed (e.g. when every article in the database is listed).  
    # It returns the title of the article, as opposed to the default non-sensical unicode name. 
    def __unicode__(self):
        return self.title

    # Constructs a file location for articles when they are uploaded.
    # The file location syntax is "root/articles/{{username}}/{{article title without punctuation or spaces}}/{{original filename without punctuation or spaces}}.
    # It is possible that removing spaces and punctuation is unnecessary. It is done as a precautionary measure as spaces can cause problems when files 
    # are accessed using the system shell via python (particularly when using command prompt in Windows). 
    def article_file_name(instance, filename):
	filename_no_punc = ''
	for letter in filename:
		if letter != '.':
			if letter in string.punctuation:
				letter = ''
		filename_no_punc += letter
	filename_no_punc = filename_no_punc.replace(' ','_')
	title = instance.title
	title_no_punc = ''
	for letter in title:
		if letter in string.punctuation:
			letter = ''
		title_no_punc += letter
	title_no_punc = title_no_punc.replace(' ','_')
    	return ('/').join([instance.__class__.__name__ + 's', instance.user.username, title_no_punc, filename_no_punc])

    def get_absolute_url(self):
    	return "/articles/%i/%s/" % (self.pk, self.slug)

    title = models.CharField(max_length=200)
    # The url stub of the article (not including civilpress.org/{{username}}/). 
    # It is constructed in the save method using the title and primary key of the article (to ensure uniqueness).
    slug = models.SlugField(max_length = 300, null = True, blank = True)  
    upload_date = models.DateTimeField(auto_now_add=True)
    # The location of the file associated with the article. It uses a custom field ('ContentTypeRestrictedFileField'). 
    # See the documentation for this field type by checking the location of it's definition in the import statements at the top of this script.
    # Note: '.pdf' files are currently not accepted because the 'self.convert_article' method creates an undreadable file if we try to convert from
    # '.pdf' to '.pdf'. The 'self.save()' method currently trys to convert every document into '.pdf' (regardless of its format), so allowing '.pdf's to be uploaded
    # will currently cause problems. This could be fixed relatively easily by having the filetype of 'self.file_field' checked in 'self.save()'.
    file_field = ContentTypeRestrictedFileField(upload_to=article_file_name, content_types=['application/msword','application/vnd.oasis.opendocument.text','application/vnd.openxmlformats-officedocument.wordprocessingml.document',],max_upload_size=2621440)
    # Used to check whether file_field has been changed. Set in __init__ method.
    original_file_field = None
    # Holds the text content of the article. This means that the text of the article can be indexed and searched by the search engine. 
    # This field is set in the the save method.  
    content = models.TextField(default='',blank=True)
    # This is the authorial user associated with the article (its creator). 
    user = models.ForeignKey(User, related_name = 'articles', blank = True, null=True)
    # The name of the user who authored this article. It is set in the save method. 
    author = models.CharField(max_length=200,default='',blank=True)
    # Currently only set to the first 700 letters of 'self.content' and displayed when articles are listed on CivilPress.
    # Note: Could give users the ability to write their own article summaries in future.  
    summary = models.TextField('summary of article contents (max. 500 characters)',max_length = 700, blank=True,default='')
    prompt = models.CharField('Topic/prompt of article (max. 1000 characters)',max_length = 1000,default='',blank=True)
    subject_submitted_for = models.CharField('Title of subject submitted for',max_length = 50,default='',blank=True)
    academic_level = models.CharField('Academic level submitted during',max_length=50, choices=EDUCATION_LEVEL_CHOICES,default='None',blank=True)
    academic_institution = models.CharField('Academic institute submitted to',max_length=100,blank=True)
    grade = models.CharField('Grade recieved', max_length = 20, choices = GRADE_CHOICES, blank = True, null = True, default = '')
    word_limit = models.IntegerField(null = True, blank = True)
    number_of_views = models.IntegerField(default=0, blank = True)
    rating = models.DecimalField('Average rating out of ten', max_digits=4, decimal_places=2,default=0, blank = True)
    number_of_ratings = models.IntegerField(default=0, blank= True)
    # primary_discipline = models.CharField(max_length = 50, default = '',blank=True)
    # This field is only of use to the Publication class which extends this class. It is placed here so that it can make use of 
    # the article_file_name method in this class. 
    cover = models.ImageField(upload_to=article_file_name, null = True, blank = True)
    # Instead of just adding each rating of an article to an overall total (which is then divided by the number of ratings to get
    # an average rating); each invidiual user rating for each article is saved using the ArticleUser_ratingM2M model. This means that
    # users need to log in to rate articles and that the may only rate each article once. That way people can't rate articles multiple times. 
    user_ratings = models.ManyToManyField(UserProfile, related_name = 'rated_articles', through = 'ArticleUser_ratingM2M', blank = True, null = True)
    featured = models.BooleanField() 
    # anonymous = models.NullBooleanField(blank=True, null=True, choices = ANON_CHOICES)
    anonymous = models.BooleanField()

    # Replaces the primary_discipline field which used to be set during save(). NOTE: Slightly less efficient than saving this information in a field, but
    # does mean that the entire article doesn't need to be saved every time the primary_discipline is changed.  
    def primary_discipline(self):
	if self.disciplines.exists():
		return self.disciplines.all()[0].discipline_name
	else:
	        return '' 

    # This method returns a list of every tag associated with this article. 
    def tag_list(self):
	tag_string = ''
	for tag in self.tags.all():
		tag_string += tag.tag_name + ', '

	return tag_string

    # Updates the 'rating' field of the article by adding up all the user ratings associated with it and
    # dividing this total by the number of user ratings. Save method must be called after using this method
    # if changes are to be permanent. 
    def update_rating(self):
	avg_total = 0
	self.number_of_ratings = 0	
	for r in self.user_rating_relationship.all():
		avg_total += r.rating
		self.number_of_ratings += 1
	self.rating = float(avg_total) / float(self.number_of_ratings)

    # Returns a list of every discipline associated with this article. Not really used anywhere so can probably be removed. 
    def discipline_list(self):
	discipline_list = []
	for d in self.disciplines.all():
		discipline_list.append(d)
	return discipline_list

    # Currently, only ONE discipline used by the site for each article. However, the discipline-article relationship is 
    # a many-to-many one, therefore multiple disciplines could, in future, be associated with each article. For now though,
    # this function is used to set the 'primary_discipline' field which is the only place where discipline data is drawn from
    # by the site.
    # Note: It could possibly be more efficient to just access the first discipline of an article when it is called for rather than
    # setting the primary_discipline here and saving it. Also, should think about allowing articles to have multiply disciplines in future. 
    def set_primary_discipline(self):
	if self.disciplines.exists():
		disList = self.disciplines.all()
		primary_discipline = disList[0]
		self.primary_discipline = primary_discipline.discipline_name
	else:
	        self.primary_discipline = ''

    # This is a wrapper for the 'convert_document' and 'pdf_to_swf' functions which are imported into this script.
    # It's arguments are the 'format' to convert in to and whether or not to delete the original file from which the
    # new, converted file is created from ('delete_old'). 'Convert_document' ultimately uses OpenOffice to convert the document,
    # while 'pdf_to_swf' uses 'SWFTools' to perform conversion. 
    # Note: This function will produce an unreadable file if a .pdf is converted into a .pdf. Perhaps an exception should be
    # raised if this is attempted?  
    def convert_article(self,format,delete_old):
	# Holds the length of the file extension (e.g. '.docx' or .'doc') so that this can be removed from the final filename.
	# Otherwise, the filename will end up being something like 'some_document.doc.docx' as opposed to 'some_document.docx'. 
	ext_length = 0
	# Works backwards through the filename counting the number of letters until the first fullstop. Holds this value in ext_length. 
	for letter in self.file_field.name[::-1]:
		if letter == '.':
			ext_length += 1
			break
		ext_length += 1
	file_new = self.file_field.name[:-ext_length] + format
	file_in = r'"%s/%s"' % (MEDIA_ROOT, self.file_field.name)
	file_out = r'"%s/%s"' % (MEDIA_ROOT, file_new)	
	if format != ".swf":
		convert_document(file_in, file_out)
	else:
		pdf_to_swf(file_in, file_out)
	if delete_old == True:
		# [1:-1] as otherwise quotes will be captured and error will be raised.
		os.remove(file_in[1:-1]) 
	# Points the file_field to the new location of the file. MEDIA_ROOT not included.  
 	return file_new  
	
    # Overriden save method. The convert argument determines whether or not the file located in 'file_field' should be 
    # converted to .swf (which is the file format which all articles on CivilPress are saved as). Default is True. 
    def save(self, convert = True,*args, **kwargs):
	print '>>> Log: <',self.title,'> saved.', '>>> Caller:',who_is_caller()
	
	if self.id is None:
		# Slug is constructed. NOTE: Slug is only generated on first save of article. This means that any changes to the title of the article will not be reflected in the
		# URL. 
		self.slug = slugify(self.title)
	# Set convert to false if 'file_field' has not been changed AND if this is NOT the first save of the object.
        if self.id is not None and (self.file_field == self.original_file_field or self.file_field == None):  
		convert = False
	# Call the "real" save() method IF this article does not yet have a primary key (i.e. if this is the article's first save). 
	# This method is called here so that a primary key can be generated for the article. This primary key is used to generate 'URLtitle' below. 
	# Note: This is inefficient. It may be wise to remove the primary key from 'URLtitle' altogether and rely on the the
	# unique_together = ('title','user') of this model to ensure that the article's URL will be entirely unique. Alternatively, the
	# primary key value could be determined some other way (without saving the entire model). 
	if self.id is None:
		super(Article, self).save(*args, **kwargs)
 
	# Construct a string to set as 'self.URLtitle' using the title of the article (with no punctuation or spaces) and it's primary key. 
	# Set self.author to the authorial user's first and last name. 
	self.author = self.user.first_name + ' ' + self.user.last_name
	# If convert is True, article is first converted to a text file. This text file is then opened
	# and its contents are saved under 'self.content'. This makes sure that the text content of the article is
	# indexable and searchable by the search engine (i.e. via the indexing and searching of the 'self.content' field).
	# The file is then converted into a '.pdf' and then into a '.swf'. This is necessary as the 'convert_document' function
	# cannot convert documents to '.swf' and the 'pdf_to_swf' function only converts from '.pdf' to '.swf'. 
	# Note: Extreme inefficiency here. Three conversions take place, and only two of them are really necessary (perhaps even one). 
	# Finding a way to a document directly into '.swf' without initial conversion to '.pdf' could improve efficiency dramatically. 
	# If the text content of this file could then be read in without a conversion to '.txt', then efficiency could be further improved.   	
	if convert == True:
		article_as_txt = self.convert_article('.txt', False)
		article_as_txt_path = r"%s/%s" % (MEDIA_ROOT, article_as_txt)
		article_as_txt = open(article_as_txt_path, 'r')
		# Note: Use of 'latin-1' was the result of trial and error. This decode method could cause bugs in future (particularly
		# if people try to upload documents containing foreign characters). 
		self.content = article_as_txt.read().decode('latin-1')
		article_as_txt.close()
		# Txt file is deleted as its contents are held in 'self.content'.
		os.remove(article_as_txt_path)
		# Original file is now converted to '.pdf'. Original file is also kept as a precautionary measure as we may need to convert
		# it into other formats at a later date (and converting from '.swf' is tough). 
		# Note: Could save space by deleting this file if needed.  
		self.file_field = self.convert_article('.pdf', False)
		# '.swf' created from the '.pdf'. '.pdf' is deleted ('deleted_old' argument is set to True) as it is now wasting space. 
		self.file_field = self.convert_article('.swf', True)
	# Sets 'self.summary' to the first 700 words of 'self.content', or equals 'self.content' if 'self.content' is less than 700 characters in length.  
	if len(self.content)>700:
		self.summary = self.content[0:700] 

	else:
		self.summary = self.content 
	# Ellipsis added to end of summary for aesthetic purposes.
	self.summary += '...'
	# Finally, the "real" save method is called so that all the field values we just changed are saved. 
        super(Article, self).save(*args, **kwargs)
 
# This exception class is used by the Article_postDelete function below. 
class DirectoryNoLongerExists(BaseException):
    pass

# This method will be called after an article is deleted. Django's signal system is used here to determine when this happens. 
# This method simply deletes the file directory associated with the article (i.e. the original file and '.swf' file associated with the article').
# Note: Be careful with this function, it could easily delete files which are not associated with the deleted article.  	
def Article_postDelete(sender, instance, **kwargs):
	file_to_delete = r'"%s/%s"' % (MEDIA_ROOT, instance.file_field.name)
	file_split = file_to_delete.split('/')
	file_to_delete = ''
	for segment in file_split[0:-1]:
		# This makes sure that the folder containing the article is deleted. 
		file_to_delete += segment + '/' 	
	try:
		# This function allows you to delete a folder. 
		shutil.rmtree(file_to_delete[1:-1]) 
	except: 
		raise DirectoryNoLongerExists("Exception in articles.models.Article_postDelete: The directory for instance.file_field.name no longer exists. This probably means that it was already deleted when the delete method was called for an article with the same title and user. This exception can most likely be ignored.") 

# This function call ensures that the Article_postDelete function defined above is called whenever an Article object is deleted. 
post_delete.connect(Article_postDelete, sender = Article)
  
'''
ArticleUser_ratingM2M class:
This model holds all the information pertaining to the relationship between non-authorial users of an article and the article. 
Currently, it only holds a user's rating of the article (out of 10). This is a many-to-many relationship (articles can be rated by
multiple users and users can rate multiple articles). 
Note: The 'Article.user_rating' field operates through this class. To access information in this class (i.e. the rating value), make sure
to use the related name listed here for the article object ('user_rating_relationship') instead of 'user_rating' as (I am pretty sure) using 'user_rating'
will not work. That said, perhaps 'user_rating' could be removed? Or perhaps the related_name value for 'self.rated_article' is unnecessary? This would avoid confusion
when accessing rating information. 
'''
class ArticleUser_ratingM2M(models.Model):
	class Meta:
		verbose_name = 'Article-user_rating relationship'
		# Articles can only be rated once per user. If multiple ratings are allowed, there will be bugs when rating information is accessed. 
		unique_together = ('rated_article','user')

	rated_article = models.ForeignKey('Article', null = True, related_name = 'user_rating_relationship')
	user = models.ForeignKey(UserProfile, null = True, related_name = 'rated_article_relationship') 
	rating = models.IntegerField(null = True, blank = True)  

'''
Publication class:
This class holds information about publications. Fairly self explanatory. 
This class uses the 'cover' field in the Article class (of which this is a child). 
'''
class Publication(Article):
    # These are the articles which are contained in this publication. This field is really just optional. 
    articles = models.ManyToManyField(Article, related_name = 'publications', blank = True, null = True, through = 'PublicationArticleM2M') 
    volume = models.IntegerField(null = True, blank = True)
    issue = models.IntegerField(null = True, blank = True)

'''
PublicationArticleM2M class:
Fairly straightforward here. Note: Keeping information about the relationship between publications and
articles could be userful in future. Users could generate their own publications by selecting groups of articles,
or information about which publications an article is featured in could be displayed in the article's details. 
'''
class PublicationArticleM2M(models.Model):
	class Meta:
		verbose_name = 'Publication-Article relationship'
	article = models.ForeignKey(Article, null = True, related_name = 'publication_relationship')
	publication = models.ForeignKey(Publication, null = True, related_name = 'article_relationship')

'''
Tag class:
Holds information about tags, including the number of times a tag has been used and the articles which use it. 
'''
class Tag(models.Model):
    	def __unicode__(self):
        	return self.tag_name

	class Meta:
		ordering = ['tag_name']
	
	tag_name = models.CharField(max_length=50, unique = True)
	count = models.IntegerField("Number of articles associated with this tag", default = 0)
	articles = models.ManyToManyField(Article, blank=True, related_name = 'tags', through='ArticleTagM2M')
	
	def update_count(self):
		self.count = self.articles.count()

	def save(self, *args, **kwargs):
		# The "real" save method is called initially, so that 'self.tag_name' can be accessed in the next line. 
		# Note: This is extremely inefficient. It would be best to find another way to access 'self.tag_name' (if, indeed, 
		# it actually cannot be accessed otherwise). 
		super(Tag, self).save(*args, **kwargs)
		# Any punctuation is removed from self.tag_name and it is converted into lower case. 
		tag_lower = self.tag_name.lower()		
		tag_lower_nopunc = ''
		for letter in tag_lower:
			if letter in string.punctuation:
				letter = ''
			tag_lower_nopunc += letter
		self.tag_name = tag_lower_nopunc
		# self.update_count is called everytime the tag is saved so that any changes to the articles associated with this tag are reflected in self.count. 		
		self.update_count()
		# Call the "real" save() method again. Makes sure changes made by update_count are saved.
		super(Tag, self).save(*args, **kwargs) 

'''
ArticleTagM2M class:
The information contained in this class isn't particularly important (in fact, it isn't really that useful). 
Its importance is that when this relationship is saved, it sends a signal which triggers the tag itself to be saved, which in
turn updates the tag's count attribute. Otherwise, tag's have to be saved manually whenever new ArticleTag relationships are created or deleted
for accurate counts.
'''
class ArticleTagM2M(models.Model):
	def __unicode__(self):
        	return 'Article-tag relationship'
	class Meta:
		verbose_name = 'Article-Tag relationship'
		unique_together = ('article','tag')

	article = models.ForeignKey(Article, null=True, related_name = 'tag_relationships')
	tag = models.ForeignKey(Tag, null=True, related_name = 'article_relationships')

# ArticleTagM2M_postSave and ArticleTagM2M_postDelete ensure that tag counts are updated whenever ArticleTag relationships are created or deleted. 
def ArticleTagM2M_postSave(sender, instance, **kwargs): 
	instance.tag.save()
post_save.connect(ArticleTagM2M_postSave, sender = ArticleTagM2M)

def ArticleTagM2M_postDelete(sender, instance, **kwargs):	
	instance.tag.save()
post_delete.connect(ArticleTagM2M_postDelete, sender = ArticleTagM2M)

'''
Discipline class:
This class serves the same purpose as the Tag class. 
Note: For the sake of brevity (and upholding the DRY principle), this class could simply inherit from
the Tag class.
'''
class Discipline(models.Model):
    	def __unicode__(self):
        	return self.discipline_name

	class Meta:
		ordering = ['discipline_name']
	
	discipline_name = models.CharField(max_length=50, unique = True)
	count = models.IntegerField("Number of articles associated with this discipline", default = 0)
	articles = models.ManyToManyField(Article, blank=True, related_name = 'disciplines', through = 'ArticleDisciplineM2M')
	# Used if this is a sub-discipline of another discipline. 
	parent = models.ForeignKey('Discipline', related_name = 'child', blank = True, null = True, default = None)
	def update_count(self):
		self.count = self.articles.count()

	def save(self, *args, **kwargs):
		# Call the "real" save() method. Makes sure self can be called on in next line.
		super(Discipline, self).save(*args, **kwargs) 
		self.update_count()
		# Call the "real" save() method. Makes sure changes made by update_count are saved.
		super(Discipline, self).save(*args, **kwargs) 
'''
ArticleDisciplineM2M class:
This class serves the same purpose as the TagDisciplineM2M class.
Note: This could also simply inherit from the Tag version of this class. 
'''	 
class ArticleDisciplineM2M(models.Model):
	def __unicode__(self):
        	return 'Article-discipline relationship'
	class Meta:
		verbose_name = 'Article-discipline relationship'
		unique_together = ('article','discipline')

	discipline = models.ForeignKey(Discipline, related_name = 'article_relationships')
	article = models.ForeignKey(Article, related_name = 'discipline_relationships')

# ArticleDisciplineM2M_postSave and ArticleDisciplineM2M_postDelete use signals to
# ensure that discipline counts are updated when ArticleDiscipline relationships are 
# saved or deleted. Furthermore, it ensures that the primary_discipline field is updated for the article associated with this relationship. 		
def ArticleDisciplineM2M_postSave(sender, instance, **kwargs):
	instance.discipline.save()
#	instance.article.save(False)
post_save.connect(ArticleDisciplineM2M_postSave, sender = ArticleDisciplineM2M)

# NOTE: The exception here is only printed to the console. This could cause problems, however for the moment this is necessary as otherwise when a user trys to delete an article,
# they will get this exception. 
def ArticleDisciplineM2M_postDelete(sender, instance, **kwargs): 
	instance.discipline.save()
#	try:
#		instance.article.save(False)
#	except:
#		# This is simply printed, not raised. 
#		print DirectoryNoLongerExists("Exception in articles.models.ArticleDisciplineM2M_postDelete: Trying to save instance.article, but instance.article no longer exists. Ignore if instance.article was just deleted.")
post_delete.connect(ArticleDisciplineM2M_postDelete, sender = ArticleDisciplineM2M)

'''
This function adds introspection rules to South (the database migration manager) so that it can work with the custom field type 'ContentTypeRestrictedFileField'.
In reality, it can be placed in any script that will get run when South's 'schemamigration' function is called. 
It took a bit of trial and error to work out exactly what to use for each of the required arguments, so this probably shouldn't be messed with. 
At the moment it works fine, so it can probably just be ignored. 
'''
add_introspection_rules([
    (
        [ContentTypeRestrictedFileField],      
        [],         				
        {           				
            "content_types": ["content_types", {}],
            "max_upload_size": ["max_upload_size", {}],
        },
    ),
], ["articles\.format_checker"])
