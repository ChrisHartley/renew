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

	propertyType = models.CharField(choices=PROPERTY_TYPES, max_length=2)

	parcel = models.CharField(max_length=7, unique=True)	
	streetAddress = models.CharField(max_length=255)
	nsp = models.NullBooleanField(default=False, null=True)
	structureType = models.CharField(max_length=20, null=True, blank=True)

	cdc = models.ForeignKey(CDC, blank=True, null=True)
	zone = models.ForeignKey(Zoning, blank=True, null=True)
	zipcode = models.ForeignKey(Zipcode, blank=True, null=True)

	@property
	def _zipcode(self):
		return Zipcode.objects.get(id=self.zipcode).name

	area = models.FloatField()
		
	def __unicode__(self):
		return '%s' % (self.parcel)



