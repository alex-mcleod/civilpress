from django.contrib import admin
from articles.models import *

'''
Classes and functions related to the article model admin site. Most are self explanatory. 
'''

class ArticleTagM2MInline(admin.TabularInline):
    	model = ArticleTagM2M
    	extra = 3

class ArticleDisciplineM2MInline(admin.TabularInline):
    	model = ArticleDisciplineM2M
    	extra = 3

class PublicationArticleM2MInline(admin.TabularInline):
    	model = PublicationArticleM2M
	fk_name = 'publication'
    	extra = 3

class ArticleRatingInline(admin.StackedInline):
	model = ArticleUser_ratingM2M
	extra = 3

class SubDisciplineInline(admin.StackedInline):
	model = Discipline
	extra = 3

class ArticleRatingAdmin(admin.ModelAdmin):
	fields = ['user', 'rated_article', 'rating']
	list_display = ('user', 'rated_article', 'rating')

# A simple function to save all the objects selected. Allows overriden save() methods to run. 
def save_selected(modeladmin, request, queryset):
    for obj in queryset:
	obj.save()

class ArticleAdmin(admin.ModelAdmin):
    	fields = ['title','slug','user','file_field','content','prompt','subject_submitted_for','summary','academic_level','academic_institution','word_limit','number_of_views','rating','number_of_ratings','primary_discipline','featured']
    	list_display = ('title', 'author', 'user', 'upload_date','academic_level', 'primary_discipline')
    	inlines = [ArticleTagM2MInline,ArticleDisciplineM2MInline,ArticleRatingInline]
	readonly_fields = ['primary_discipline', 'author','slug', 'content']
	search_fields = ['title', 'author']
	actions = [save_selected]

class PublicationAdmin(admin.ModelAdmin):
    	fields = ['title','slug','user','file_field','cover','volume','issue','content','number_of_views','rating','number_of_ratings','primary_discipline']
    	list_display = ('title', 'user', 'upload_date','primary_discipline')
    	inlines = [ArticleTagM2MInline,ArticleDisciplineM2MInline,PublicationArticleM2MInline]
	readonly_fields = ['primary_discipline','slug', 'content']
	search_fields = ['title']
	actions = [save_selected]

# Deletes any relationships between a model object and articles. Sort of redundant now but used to be necessary before deleting the object. 
def clean_article_relationships(modeladmin, request, queryset):
	for obj in queryset:
		for relation in obj.article_relationships.all():
			relation.delete()

# Useful for removing unused tags and disciplines from the database. 
def delete_selected_if_count_is_zero(modeladmin, request, queryset):
	for obj in queryset:
		if obj.count == 0:
			obj.delete()

class TagAdmin(admin.ModelAdmin):
    	fields = ['tag_name','count']
    	readonly_fields=['count',]
    	inlines = [ArticleTagM2MInline]
	list_display = ('tag_name','count')
	actions = [save_selected,clean_article_relationships, delete_selected_if_count_is_zero]
	search_fields = ['tag_name']

class DisciplineAdmin(admin.ModelAdmin):
    	fields = ['discipline_name','parent','count']
    	readonly_fields=['count',]
	list_display = ('discipline_name','count')
    	inlines = [ArticleDisciplineM2MInline, SubDisciplineInline]
	actions = [save_selected,clean_article_relationships,delete_selected_if_count_is_zero]
	search_fields = ['discipline_name']
 
admin.site.register(Article, ArticleAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Discipline, DisciplineAdmin)
admin.site.register(ArticleUser_ratingM2M, ArticleRatingAdmin)
