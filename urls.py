from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from haystack.views import SearchView
from articles.search_form import ArticleSearchForm
from articles.views import ArticleSearchView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    # This URL is an alternative to the comments/delete URL. It allows users to remove their own comments, whereas the comments/delete URL only allows users to remove
    # comments if they have permission to delete comments. 
    url(r'^comments/remove/(\d+)/$',  'simple_comments.views.remove_own_comment', name='comments-remove'), 
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^articles/(?P<article_pk>\d+)/(?P<article_slug>.+)/$', 'articles.views.view_article'),
    url(r'^articles/(?P<article_pk>\d+)/(?P<article_slug>.+)/edit$', 'articles.views.edit_article'),
    url(r'^articles/(?P<article_pk>\d+)/(?P<article_slug>.+)/remove$', 'articles.views.remove_article'),
    url(r'^$', 'articles.views.index'),
    url(r'^search/$', ArticleSearchView(searchqueryset=None, form_class=ArticleSearchForm, template='search/search.html',), name ='haystack_search'),
    url(r'^create_account/$', 'userprofiles.views.create_account'),
    url(r'^create_account/register/$', 'userprofiles.views.register_user'),
    url(r'^logout/$', 'userprofiles.views.logout_view'),
    url(r'^upload/$', 'articles.views.upload'),
    url(r'^login/$', 'userprofiles.views.login_view'),
    url(r'^account/$', 'userprofiles.views.account'),
    url(r'^publications/$', 'articles.views.publications'),
    url(r'^contact/$', 'views.contact'),
    url(r'^plagiarism/$', 'views.plagiarism'),


) 

# Add URL patterns for static files. 
urlpatterns += staticfiles_urlpatterns()


