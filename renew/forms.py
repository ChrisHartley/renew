from django.forms import ModelForm
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from renew.models import Property
from renew.models import Zipcode
from renew.models import CDC
from renew.models import Zoning
from renew.models import propertyInquiry
from renew.models import Application

from django.core.exceptions import ValidationError

class SearchForm(ModelForm):
	zipcode =  forms.ModelMultipleChoiceField(queryset=Zipcode.objects.all().order_by('name'), widget=forms.SelectMultiple, help_text="The 5 digit zipcode.", label='Zipcode')
	cdc = forms.ModelMultipleChoiceField(queryset=CDC.objects.all().order_by('name'), widget=forms.SelectMultiple, help_text="The Community Development Corporation boundaries the property falls within.", label='CDC')
	zone = forms.ModelMultipleChoiceField(queryset=Zoning.objects.filter(id__in=Property.objects.distinct('zone').values('zone').filter(propertyType__exact='lb')).order_by('name'), widget=forms.SelectMultiple, help_text="The zoning of the property.", label='Zoning')
	structureType = forms.ModelMultipleChoiceField(queryset=Property.objects.distinct('structureType').order_by('structureType').filter(propertyType__exact='lb').values_list('structureType', flat=True), widget=forms.SelectMultiple, help_text='As classified by the Assessor.', label='Structure Type')
	minsize = forms.IntegerField(label="Minimum parcel size", help_text='Area is in square feet.')
	maxsize = forms.IntegerField(label="Maximum parcel size", help_text='Area is in square feet.')
	nsp = forms.ChoiceField(widget=forms.Select, label='NSP', help_text="If a property comes with requirements related to the Neighborhood Stabilization Program.", choices = (('1', 'Yes'), ('0', 'No'), ('', '') ), initial='')
	sidelot_eligible = forms.ChoiceField(widget=forms.Select, label='Side lot', help_text="If a property is eligible for the side lot program.", choices = (('1', 'Yes'), ('0', 'No'), ('', '') ), initial='')
	homestead_only = forms.ChoiceField(widget=forms.Select, label='Homestead Only', help_text="If a property is available only for homestead applications.", choices = (('1', 'Yes'), ('0', 'No'), ('', '') ), initial='')
	bep_demolition = forms.ChoiceField(widget=forms.Select, label='Slated for BEP Demolition', help_text="If a property is currently on the list for demolition using BEP funds. Demolition can be stopped if a viable plan for reuse is presented.", choices = (('1', 'Yes'), ('0', 'No'), ('', '') ), initial='')
	class Meta:
		model = Property
		#fields = ['parcel', 'streetAddress', 'nsp', 'structureType', 'cdc', 'zone', 'zipcode', 'sidelot_eligible']
		fields = ['parcel', 'streetAddress', 'nsp', 'structureType', 'cdc', 'zone', 'zipcode', 'sidelot_eligible', 'homestead_only', 'bep_demolition']

class PropertyInquiryForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(PropertyInquiryForm, self).__init__(*args, **kwargs)
		self.fields.keyOrder = ['applicant_name','applicant_email_address','applicant_phone','parcel']
		self.helper = FormHelper()
		self.helper.form_id = 'propertyInquiryForm'
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-lg-3'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.add_input(Submit('submit', 'Submit'))

	class Meta:
		model = propertyInquiry


class ApplicationForm(ModelForm):
	def validate_parcel(value):
		try:
			Property.objects.get(parcel=value)
		except Property.DoesNotExist:
			raise ValidationError("The parcel you entered does not exist in our inventory.")

	def __init__(self, *args, **kwargs):
		super(ApplicationForm, self).__init__(*args, **kwargs)
		#self.fields.keyOrder = ['Applicant','applicant_email_address','applicant_address','applicant_phone','parcel']
		self.helper = FormHelper()
		self.helper.form_id = 'ApplicationForm'
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-lg-3'
		self.helper.field_class = 'col-lg-5'
		self.helper.form_method = 'post'
		self.helper.form_action = ''
		self.helper.add_input(Submit('submit', 'Submit'))

	Parcel = forms.CharField(max_length=7, validators=[validate_parcel])


	class Meta:
		model = Application
		exclude = ("Property",)
		fields = ['Applicant','Parcel','scope_of_work','neighborhood_notification','is_rental','application_type','planned_improvements','long_term_ownership','team_members','timeline','estimated_cost','source_of_financing','grant_funds',]
		widgets = {
            'hearing_rc': forms.DateInput(attrs={'class':'datepicker'}),
            'hearing_bd': forms.DateInput(attrs={'class':'datepicker'}),
            'hearing_dmd': forms.DateInput(attrs={'class':'datepicker'}),
            'hearing_mdc': forms.DateInput(attrs={'class':'datepicker'}),

        }


class NeighborhoodAssocationSearchForm(forms.Form):
	parcel = forms.CharField(max_length=7)
	
	def __init__(self, *args, **kwargs):
		super(NeighborhoodAssocationSearchForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'propertyInquiryForm'
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-lg-3'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'get'
		self.helper.form_action = ''
		self.helper.add_input(Submit('submit', 'Submit'))


