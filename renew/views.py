from django.template import Context, loader
from renew.models import Property
from renew.models import Zipcode
from renew.models import Zoning
from renew.models import CDC
from renew.forms import SearchForm

from django.http import HttpResponse
from django.http import HttpResponseBadRequest

from django.contrib.gis.geos import GEOSGeometry


#shotgun approach
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from vectorformats.Formats import Django, GeoJSON    # used for geojson display of search results
from renew.tables import PropertyTable # used for table display of search results
import csv # used for csv return of search results

# to build query
from django.db.models import Q
import operator

from django.contrib.gis.geos import GEOSGeometry # used for centroid calculation


@csrf_exempt
def search(request):
	queries = []
	properties = Property.objects.all()
	if request.GET.items():
		if 'searchType' in request.GET and request.GET['searchType']:
			searchType = request.GET.__getitem__('searchType')
			if searchType == "lb":
				queries.append(Q(propertyType__exact=searchType))				
			if searchType == "sp":
				queries.append(Q(propertyType__exact=searchType))
		if 'parcel' in request.GET and request.GET['parcel']:
			parcelNumber = request.GET.__getitem__('parcel')
			queries.append(Q(parcel__exact=parcelNumber))
		if 'streetAddress' in request.GET and request.GET['streetAddress']:
			streetAddress = request.GET.__getitem__('streetAddress')
			queries.append(Q(streetAddress__icontains=streetAddress))
		if 'minsize' in request.GET and request.GET['minsize']:
			minsize = request.GET.__getitem__('minsize')
			queries.append(Q(area__gte=minsize))
		if 'maxsize' in request.GET and request.GET['maxsize']:
			minsize = request.GET.__getitem__('maxsize')
			queries.append(Q(area__lte=minsize))
		if 'zipcode' in request.GET and request.GET['zipcode']:
			zipcode = request.GET.getlist('zipcode')
			queries.append(Q(zipcode__in=Zipcode.objects.filter(id__in=zipcode)))
		if 'cdc' in request.GET and request.GET['cdc']:
			cdc = request.GET.getlist('cdc')
			queries.append(Q(cdc__in=CDC.objects.filter(id__in=cdc)))
		if 'zone' in request.GET and request.GET['zone']:
			zone = request.GET.getlist('zone')
			queries.append(Q(zone__in=Zoning.objects.filter(id__in=zone)))
		if 'structureType' in request.GET and request.GET['structureType']:
			structureType = request.GET.getlist('structureType')
			queries.append(Q(structureType__in=structureType))
		if 'nsp' in request.GET and request.GET['nsp']:
			nsp = request.GET.__getitem__('nsp')
			queries.append(Q(nsp=nsp))
		if 'searchArea' in request.GET and request.GET['searchArea']:
			searchArea = request.GET.__getitem__('searchArea')
			searchGeometry = GEOSGeometry(searchArea, srid=900913)
			queries.append(Q(geometry__within=searchGeometry))
		if 'returnType' in request.GET and request.GET['returnType']:
			returnType = request.GET.__getitem__('returnType')
			if returnType == "html":
				properties = Property.objects.filter(reduce(operator.and_, queries))
	 			propertiesTable = PropertyTable(properties, order_by=request.GET.get('sort'))
				return render(request, 'renew/table1_template.html', {'table': properties})
			if returnType == "csv": 	
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="renew-properties.csv"'
				writer = csv.writer(response)
				writer.writerow(["Parcel Number", "Street Address", "Zipcode", "Structure Type", "CDC", "Zoned", "NSP", "Licensed Urban Garden", "Quiet Title", "Area ft^2", "Lat/Lon"])
				properties = Property.objects.filter(reduce(operator.and_, queries))				
				for row in properties:
					if row.nsp:
						nspValue = "Yes"
					else:
						nspValue = "No"
					if row.urban_garden:
						ugValue = "Yes"
					else:
						ugValue = "No"
					if row.quiet_title_complete:
						qtValue = "Yes"
					else:
						qtValue = "No" 
					writer.writerow([row.parcel, row.streetAddress, row.zipcode, row.structureType, row.cdc, row.zone, nspValue, ugValue, qtValue, row.area, GEOSGeometry(row.geometry).centroid])
				return HttpResponseBadRequest()	
	try:
		properties = Property.objects.filter(reduce(operator.and_, queries))
	except:
		return	
	djf = Django.Django(geodjango='geometry', properties=['streetAddress', 'parcel'])
	geoj = GeoJSON.GeoJSON()
	s = geoj.encode(djf.decode(properties))
	return HttpResponse(s)


def search_form(request):
	form = SearchForm()
	return render_to_response('renew/search-form.html', {
		'form': form,
	}, context_instance=RequestContext(request))


def showMap(request):
	form = SearchForm()
	return render_to_response('renew/map.html', {
		'form': form,
	}, context_instance=RequestContext(request))


def showMapAjax(request):
	form = SearchForm()
	return render_to_response('renew/map-ajax.html', {
		'form': form,
	}, context_instance=RequestContext(request))

