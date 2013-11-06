from django.forms import ModelForm
from django import forms
from renew.models import Property
from renew.models import Zipcode
from renew.models import CDC
from renew.models import Zoning


class SearchForm(ModelForm):
	zipcode =  forms.ModelMultipleChoiceField(queryset=Zipcode.objects.all().order_by('name'), widget=forms.SelectMultiple, help_text="The 5 digit zipcode.", label='Zipcode')
	cdc = forms.ModelMultipleChoiceField(queryset=CDC.objects.all().order_by('name'), widget=forms.SelectMultiple, help_text="The Community Development Corporation boundries the property falls within.", label='CDC')
	zone = forms.ModelMultipleChoiceField(queryset=Zoning.objects.filter(id__in=Property.objects.distinct('zone').values('zone').filter(propertyType__exact='lb')).order_by('name'), widget=forms.SelectMultiple, help_text="The zoning of the property.", label='Zoning')
	structureType = forms.ModelMultipleChoiceField(queryset=Property.objects.distinct('structureType').order_by('structureType').filter(propertyType__exact='lb').values_list('structureType', flat=True), widget=forms.SelectMultiple, help_text='As classified by the Assessor.', label='Structure Type')
	minsize = forms.IntegerField(label="Minimum parcel size", help_text='Area is in square feet.')
	maxsize = forms.IntegerField(label="Maximum parcel size", help_text='Area is in square feet.')
	class Meta:
		model = Property
		fields = ['parcel', 'streetAddress', 'nsp', 'structureType', 'cdc', 'zone', 'zipcode']



