from django.conf.urls import patterns, include, url
from django.contrib.gis import admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

	url(r'show/$', 'renew.views.showMap'),
	url(r'ajax/$', 'renew.views.showMapAjax'),
	url(r'search/$', 'renew.views.search'),
	url(r'search-form/$', 'renew.views.search_form'),

)


