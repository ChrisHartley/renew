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
import xlsxwriter # switching to XLSX
import StringIO

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
		if 'sidelot_eligible' in request.GET and request.GET['sidelot_eligible']:
			sidelot_eligible = request.GET.__getitem__('sidelot_eligible')
			queries.append(Q(sidelot_eligible=sidelot_eligible))
		if 'searchArea' in request.GET and request.GET['searchArea']:
			searchArea = request.GET.__getitem__('searchArea')
			try: 
				searchGeometry = GEOSGeometry(searchArea, srid=900913)
			except Exception: 
				pass
			else:
				queries.append(Q(geometry__within=searchGeometry))
		if 'returnType' in request.GET and request.GET['returnType']:
			returnType = request.GET.__getitem__('returnType')
			if returnType == "html":
				properties = Property.objects.filter(reduce(operator.and_, queries)).order_by('zipcode')	
	 			propertiesTable = PropertyTable(properties, order_by='parcel')
				return render(request, 'renew/table1_template.html', {'table': properties})
			if returnType == "csv": 	
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="renew-properties.csv"'
				writer = csv.writer(response)
				#writer.writerow(["Parcel Number", "Street Address", "Zipcode", "Structure Type", "CDC", "Zoned", "NSP", "Licensed Urban Garden", "Quiet Title", "Sidelot Eligible", "Area ft^2", "Status", "Lat/Lon"])
				writer.writerow(["Parcel Number", "Street Address", "Zipcode", "Structure Type", "CDC", "Zoned", "NSP", "Licensed Urban Garden", "Quiet Title", "Parcel Area ft^2", "Status", "Price", "Lat/Lon"])
				properties = Property.objects.filter(reduce(operator.and_, queries)).order_by('zipcode')				
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
					if row.sidelot_eligible:
						slValue = "Yes"
					else:
						slValue = "No"

					writer.writerow([row.parcel, row.streetAddress, row.zipcode, row.structureType, row.cdc, row.zone, nspValue, ugValue, qtValue, row.area, row.status, row.price, GEOSGeometry(row.geometry).centroid])
				return response	
		
#			if returnType == "xlsx":
#				output = StringIO.StringIO()
#				workbook = xlsxwriter.Workbook(output, {'in_memory': True})
#				worksheet = workbook.add_worksheet('Properties')
#				bold = workbook.add_format({'bold': True})

#				#writer.writerow(["Parcel Number", "Street Address", "Zipcode", "Structure Type", "CDC", "Zoned", "NSP", "Licensed Urban Garden", "Quiet Title", "Sidelot Eligible", "Area ft^2", "Status", "Lat/Lon"])
#				worksheet.write_row('A1',["Parcel Number", "Street Address", "Zipcode", "Structure Type", "CDC", "Zoned", "NSP", "Licensed Urban Garden", "Quiet Title", "Area ft^2", "Status", "Price", "Lat/Lon"],bold)
#				properties = Property.objects.filter(reduce(operator.and_, queries)).order_by('zipcode')				
#				rowNumber = 1
#				for row in properties:
#					if row.nsp:
#						nspValue = "Yes"
#					else:
#						nspValue = "No"
#					if row.urban_garden:
#						ugValue = "Yes"
#					else:
#						ugValue = "No"
#					if row.quiet_title_complete:
#						qtValue = "Yes"
#					else:
#						qtValue = "No"
#					if row.sidelot_eligible:
#						slValue = "Yes"
#					else:
#						slValue = "No"

#					#worksheet.write_row(rowNumber, 0, [row.parcel, row.streetAddress, row.zipcode, row.structureType, row.cdc, row.zone, nspValue, ugValue, qtValue, row.area, row.status, row.price, GEOSGeometry(row.geometry).centroid])
#					worksheet.write_row(rowNumber, 0, [row.parcel, row.streetAddress, nspValue, ugValue, qtValue, row.area, row.status])
#					print rowNumber
#					rowNumber += 1
#				workbook.close()
#				output.seek(0)
#				response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#				response['Content-Disposition'] = 'attachment; filename="renew-properties.xlsx"'
#				return response	

	try:
		properties = Property.objects.filter(reduce(operator.and_, queries))
	except:
		return HttpResponseBadRequest()
	djf = Django.Django(geodjango='geometry', properties=['streetAddress', 'parcel', 'status', 'structureType', 'sidelot_eligible', 'price'])
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

def	showApplicationStatus(request):
	properties = Property.objects.all().exclude(status__exact='Available').order_by('status').order_by('status', 'applicant')
	if 'statusType' in request.GET and request.GET['statusType']:
		statusType = request.GET.__getitem__('statusType')
		if statusType == 'Sold':		
			properties = Property.objects.all().exclude(status__exact='Available').filter(status__istartswith='Sold').order_by('applicant')
		if statusType == 'Approved':
			properties = Property.objects.all().exclude(status__exact='Available').filter(status__istartswith='Sale').order_by('status', 'applicant')
	return render(request, 'renew/app_status_template.html', {'table': properties})

