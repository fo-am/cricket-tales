from django.conf.urls import patterns, url
from django.conf.urls import include

from crickets import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^movie/(?P<pk>\d+)/$', views.MovieView.as_view(), name='movie'),
    url(r'^player/(?P<pk>\d+)/$', views.player, name='player'),
    url(r'^tutorial/', views.tutorial, name='tutorial'),
    url(r'^about/', views.about, name='about'),
#    url(r'^suck/', views.suck, name='suck'),
    url(r'^spit_event/', views.spit_event, name='spit_event'),
    url(r'^update_house/', views.update_house, name='update_house'),
    url(r'^register/', views.register, name='register'),
    url(r'^login/$', views.logmein, name='login'),
    url(r'^logout/$', views.logmeout, name='logout'),
    url(r'^random_movie/$', views.random_movie, name='random_movie'),
    url(r'^house_builder/(?P<id>\d+)/$', views.house_builder, name='house_builder'),
    url(r'^random_burrow_movie/(?P<id>\d+)/$', views.random_burrow_movie, name='random_burrow_movie'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)
