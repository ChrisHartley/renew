from django.forms import ModelForm
from django import forms
from renew.models import Property
from renew.models import Zipcode
from renew.models import CDC
from renew.models import Zoning


class SearchForm(ModelForm):
	zipcode =  forms.ModelMultipleChoiceField(queryset=Zipcode.objects.all().order_by('name'), widget=forms.SelectMultiple)
	cdc = forms.ModelMultipleChoiceField(queryset=CDC.objects.all().order_by('name'), widget=forms.SelectMultiple)
	zone = forms.ModelMultipleChoiceField(queryset=Zoning.objects.filter(id__in=Property.objects.distinct('zone').values('zone').filter(propertyType__exact='lb')).order_by('name'), widget=forms.SelectMultiple)
	structureType = forms.ModelMultipleChoiceField(queryset=Property.objects.distinct('structureType').value('structureType').order_by('structureType'), widget=forms.SelectMultiple)
	minsize = forms.IntegerField(label="Minimum parcel size in square feet")
	maxsize = forms.IntegerField(label="Maximum parcel size in square feet")
	class Meta:
		model = Property
		fields = ['parcel', 'streetAddress', 'nsp', 'structureType', 'cdc', 'zone', 'zipcode']




