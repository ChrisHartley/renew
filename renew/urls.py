from django.conf.urls import patterns, include, url
from django.contrib.gis import admin

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

	url(r'show/$', 'renew.views.showMap'),
	url(r'ajax/$', 'renew.views.showMapAjax'),
	url(r'search/$', 'renew.views.search'),
	url(r'search-form/$', 'renew.views.search_form'),
	url(r'application_status/$', 'renew.views.showApplicationStatus'),
	url(r'lookup_street_address/$', 'renew.views.getAddressFromParcel'),
	url(r'property_inquiry/$', 'renew.views.showPropertyInquiry'),
	url(r'lookup_possible_street_addresses/$', 'renew.views.getMatchingAddresses'),
	url(r'application/$', 'renew.views.showApplicationForm'),

   # Uncomment the next line to enable the admin:
   # url(r'^admin/', include(admin.site.urls)),
)


