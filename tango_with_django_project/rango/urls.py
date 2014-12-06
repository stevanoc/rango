from django.conf.urls import patterns, url
from rango import views

urlpatterns = patterns('',
			url(r'^$', views.index, name='index'),
			url(r'^index.php', views.index, name='indexphp'),
			url(r'^about/$', views.about, name='about'),
			url(r'^add_category/$', views.add_category, name='add_category'),
			url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
			url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
			url(r'^register/$', views.register, name='register'),
			url(r'^login/$', views.user_login, name='login'),
			url(r'^logout/$', views.user_logout, name='logout'),
			url(r'^restricted/$', views.restricted, name='restricted'),
			url(r'^search/$', views.search, name='search'),
			url(r'^goto/$', views.redirecting, name='gotoredirect'),
			url(r'^goto/(?P<page_id>[\w\-]+)/$', views.track_url, name='goto'),
			url(r'^add_profile/$', views.register_profile, name='register_profile'),
			url(r'^profile/$', views.profile, name='profile'),
			url(r'^like_category/$', views.like_category, name='like_category'),
			url(r'^suggest_category/$', views.suggest_category, name='suggest_category'),
)