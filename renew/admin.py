from renew.models import Property
from renew.models import Zipcode
from renew.models import CDC
from renew.models import Zoning
from django.contrib.gis import admin

class PropertyAdmin(admin.OSMGeoAdmin):
	list_display = ('parcel', 'streetAddress', 'zipcode', 'cdc', 'zone')
	#list_filter = ['cdcArea']
	search_fields = ['parcel', 'streetAddress']
	#search_fields = ['parcel', '_zipcode', 'cdcArea', 'streetAddress', 'zone' ]
 
class ZipcodeAdmin(admin.OSMGeoAdmin):
	list_display = ('name', 'area')

class CDCAdmin(admin.OSMGeoAdmin):
	list_display = ('name', 'area')

class ZoningAdmin(admin.OSMGeoAdmin):
	list_display = ('name', 'area')

admin.site.register(Property, PropertyAdmin)
admin.site.register(Zipcode, ZipcodeAdmin)
admin.site.register(CDC, CDCAdmin)
admin.site.register(Zoning, ZoningAdmin)
