from django.forms import ModelForm
from django import forms
from renew.models import Property
from renew.models import Zipcode
from renew.models import CDC
from renew.models import Zoning


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
	class Meta:
		model = Property
		#fields = ['parcel', 'streetAddress', 'nsp', 'structureType', 'cdc', 'zone', 'zipcode', 'sidelot_eligible']
		fields = ['parcel', 'streetAddress', 'nsp', 'structureType', 'cdc', 'zone', 'zipcode', 'sidelot_eligible', 'homestead_only']



