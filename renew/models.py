from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError



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

class Neighborhood_Association(Overlay):
	contact_first_name = models.CharField(max_length=255)
	contact_last_name = models.CharField(max_length=255)
	contact_phone = models.CharField(max_length=255)
	contact_email_address = models.CharField(max_length=255)
	last_updated = models.DateField()

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
	sidelot_eligible = models.BooleanField(default=False, help_text="If the property is currently elgibile for the side-lot program")
	#sidelot_eligible = models.CharField(max_length=255, null=True, blank=True, help_text="If the property is currently elgibile for the side-lot program")
	price = models.DecimalField(max_digits=8, decimal_places=2, help_text="The price of the property", null=True)
	area = models.FloatField(help_text="The parcel area in square feet")
	applicant = models.CharField(max_length=255, null=True, help_text="Name of current applicant for status page")
	homestead_only = models.BooleanField(default=False, help_text="Only available for homestead applications")
	bep_demolition = models.BooleanField(default=False, help_text="Slated for demolition under the Blight Elimination Program")

	class Meta:
		verbose_name_plural = "properties"
	
	def __unicode__(self):
		return '%s' % (self.parcel)



class propertyInquiry(models.Model):
	parcel = models.CharField(max_length=7, blank=False, null=False)
	applicant_name = models.CharField(max_length=255, blank=False, null=False)
	applicant_email_address = models.EmailField(blank=False, null=False)
	applicant_phone = models.CharField(max_length=15, blank=False, null=False)
	timestamp = models.DateTimeField(auto_now_add=True)
	Property = models.ForeignKey(Property, blank=True, null=True)


	def clean(self):
		try: 
			structureType = Property.objects.get(parcel=self.parcel).structureType
			status = Property.objects.get(parcel=self.parcel).status
		except Property.DoesNotExist:
			raise ValidationError('That parcel is not in our inventory')
		if structureType == 'Vacant Lot':
			raise ValidationError('Our records show this is a vacant lot and so you can not submit a property inquiry. If our data are incorrect, please email us at chris.hartley@renewindianapolis.org so we can correct our data and set up a showing.')
		if (status == 'Sold' or 'Sale approved by MDC' in status):
			raise ValidationError('This parcel has been sold or is approved for sale and is no longer available from Renew Indianapolis.')	
	
	class Meta:
		verbose_name_plural = "property inquiries"
		

def content_file_name(instance, filename):
	return '/'.join(['applications', instance.Applicant, instance.Property.streetAddress, filename])


	
class Application(models.Model):

	Applicant = models.EmailField()

	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	APPLICATION_TYPES = ( ('hms', 'Homestead'), ('std', 'Standard') ) 
	STATUS_TYPES = ( ('w', 'Withdrawn'), ('h', 'On Hold'), ('a', 'Active'), ('c', 'Complete') ) 

#	Applicant = models.ForeignKey(User)


	application_type = models.CharField(choices=APPLICATION_TYPES, max_length=3, verbose_name='application type', help_text="If you will live in this property as your primary residence chose Homestead, otherwise chose Standard")

	Property = models.ForeignKey('Property') # pull from renew_property
	is_rental = models.CharField(max_length=255, help_text="Will this property be a rental or owner occupied?", null=False, blank=False)
	planned_improvements = models.TextField(max_length=5120, help_text="Describe the improvements you plan to make to the property", null=False, blank=False) 
	long_term_ownership = models.CharField(max_length=255, help_text="Who will own the property long-term?", null=False, blank=False)
	team_members = models.TextField(max_length=5120, help_text="What contractors, property managers, construction managers, or others will be part of this work? What experience do they have?", null=False, blank=False)
	estimated_cost = models.PositiveIntegerField(blank=False)
	source_of_financing = models.TextField(max_length=5120, help_text="What sources of financing will you use?", blank=False)
	grant_funds = models.TextField(max_length=5120, help_text="List grants you plan to utilize. Note whether they are committed, applied for, or planned.", blank=False)
	scope_of_work = models.FileField(upload_to=content_file_name) # pdf
	proof_of_funds = models.FileField(upload_to='proof_of_funds/%Y/%m/%d') # pdf or jpg, png attachment 
	neighborhood_notification = models.FileField(upload_to=property(content_file_name)) # pdf
	timeline = models.TextField(max_length=5120, help_text="Tell us your anticipated timeline for this project", blank=False)

	hearing_rc	= models.DateField(help_text="When was the application heard by the Review Committee?", blank=True, null=True)
	hearing_bd	= models.DateField(help_text="When was the application heard by the Board of Directors?", blank=True, null=True)
	hearing_dmd = models.DateField(help_text="When was the application heard by the Department of Metropolitan Development?", blank=True, null=True)
	hearing_mdc = models.DateField(help_text="When was the application heard by Metropolitan Development Commission?", blank=True, null=True)	

	decision_rc = models.NullBooleanField(help_text="Approved by Review Committee?", blank=True)
	decision_bd = models.NullBooleanField(help_text="Approved by Board of Directors?", blank=True)
	decision_dmd = models.NullBooleanField(help_text="Approved by Department of Metropolitan Development?", blank=True)
	decision_mdc = models.NullBooleanField(help_text="Approved by Metropolitan Development Commission?", blank=True)

	sold = models.BooleanField(help_text="Has the property been sold by Renew Indianapolis?", null=False, default=False)
	status = models.CharField(max_length=1, choices=STATUS_TYPES, help_text="What is the internal status of this application?", null=True) 
	created_timestamp = models.DateTimeField(auto_now_add=True)
	staff_recommendation = models.CharField(max_length=255, help_text="Staff recommendation to Review Comittee", null=True)
	staff_summary = models.TextField(max_length=5120, help_text="Staff summary of application for Review Committee", null=True)
	staff_pof_total = models.IntegerField(help_text="Total funds demonstrated", null=True)

