import datetime
from haystack import indexes
from articles.models import Article

'''
This class is used by Haystack whenever 'manage.py rebuild_index' or 'manage.py update_index' is run. 
It links article model fields to index fields. 
'''
class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    # This field holds all the text associated with the article (note that document=True). When all fields are 
    # being searched (i.e. no filter is being used), this is the field that is used. Use_template = True refers to the fact that
    # this field uses the template located @ templates/search/indexes/articles/article_text.txt to determine which article fields are included in this
    # index field (and how they are prepared before being included). Article fields can be more heavily weighted in search results by repeating them in this
    # template. NOTE: Proper weighting of search results is something which should be further investigated in future to improve the site. 
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='author')
    user = indexes.CharField()
    pub_date = indexes.DateTimeField(model_attr='upload_date')
    title = indexes.CharField(model_attr='title') 
    tags = indexes.CharField()
    disciplines = indexes.CharField() 
    content = indexes.CharField(model_attr='content') 
    subject = indexes.CharField(model_attr = 'subject_submitted_for')
    prompt = indexes.CharField(model_attr = 'prompt')
    academic_institution = indexes.CharField(model_attr = 'academic_institution')
    
    # Prepare functions named using the form 'prepare_{{model_field}}' are run by Haystack automatically before the associated field is indexed. 
    def prepare_tags(self, inst):
	tagsStr = ''
	if inst.tags.count() > 0:
		for t in inst.tags.all():
			tagsStr += t.tag_name + ' '		
	return tagsStr

    def prepare_disciplines(self, inst):
	disStr = ''
	if inst.disciplines.count() > 0:
		for d in inst.disciplines.all():
			disStr += d.discipline_name + ' ' 
 	return disStr 

    def prepare_user(self, inst):
	linkStr = ''
	linkStr = inst.user.username
	return linkStr

    # Currently seems to do nothing of importance, could be useful in future though. 
    def prepare(self, inst):
	self.prepared_data = super(ArticleIndex, self).prepare(inst)
	return self.prepared_data
	
    def get_model(self):
        return Article

