from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry

class Overlay(models.Model):
	name = models.CharField(max_length=255)
	geometry = models.MultiPolygonField(srid=4326)
	objects = models.GeoManager()

	@property
	def area(self):
		return GEOSGeometry(self.geometry).area

	def __unicode__(self):
		return '%s' % (self.name)
	
	class Meta:
		abstract = True

class Zipcode(Overlay):
	pass

class CDC(Overlay):
	CDCtype = models.CharField(max_length=50)

class Zoning(Overlay):
	pass

class Property(models.Model):

	PROPERTY_TYPES = ( ('lb', 'Landbank'), ('sp', 'County Owned Surplus') ) 

	geometry = models.MultiPolygonField(srid=4326)
	objects = models.GeoManager()

	propertyType = models.CharField(choices=PROPERTY_TYPES, max_length=2, verbose_name='property type')

	parcel = models.CharField(max_length=7, unique=True, help_text="The 7 digit local parcel number for a property, ex 1052714", verbose_name='parcel number')	
	streetAddress = models.CharField(max_length=255, help_text="Supports partial matching, so you can enter either the full street address (eg 1425 E 11TH ST) to find one property or just the street name (eg 11th st) to find all the properties on that street.", verbose_name='street address')
	nsp = models.BooleanField(default=False, help_text="If a property comes with requirements related to the Neighborhood Stabilization Program.", verbose_name='NSP')
	quiet_title_complete = models.BooleanField(default=False, help_text="If quiet title process has been completed.", verbose_name='Quiet Title Complete')
	structureType = models.CharField(max_length=255, null=True, blank=True, help_text="As classified by the Assessor", verbose_name='structure type')

	cdc = models.ForeignKey(CDC, blank=True, null=True, help_text="The Community Development Corporation boundries the property falls within.", verbose_name='CDC')
	zone = models.ForeignKey(Zoning, blank=True, null=True, help_text="The zoning of the property")
	zipcode = models.ForeignKey(Zipcode, blank=True, null=True, help_text="The zipcode of the property")
	urban_garden = models.BooleanField(default=False, help_text="If the property is currently licensed as an urban garden through the Office of Sustainability")
	status = models.CharField(max_length=255, null=True, blank=True, help_text="The property's status with Renew Indianapolis")
	area = models.FloatField(help_text="The parcel area in square feet")
		
	def __unicode__(self):
		return '%s' % (self.parcel)



