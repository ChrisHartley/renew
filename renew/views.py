from django.template import Context, loader
from renew.models import Property
from renew.models import propertyInquiry
from renew.models import Zipcode
from renew.models import Zoning
from renew.models import CDC
from renew.forms import SearchForm
from renew.forms import PropertyInquiryForm
from renew.forms import ApplicationForm
from renew.tables import PropertyTable # used for table display of search results
from renew.tables import PropertyStatusTable


from django.http import HttpResponse
from django.http import HttpResponseBadRequest

from django.contrib.gis.geos import GEOSGeometry
from django.core.mail import send_mail

#from django_tables2   import RequestConfig

#shotgun approach
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.shortcuts import get_object_or_404 

from vectorformats.Formats import Django, GeoJSON    # used for geojson display of search results
import csv # used for csv return of search results
import xlsxwriter # switching to XLSX
import StringIO

# to build query
from django.db.models import Q
import operator

from django.contrib.gis.geos import GEOSGeometry # used for centroid calculation
import json
from django.core import serializers

# login requirements 
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django_tables2_reports.config import RequestConfigReport as RequestConfig

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
		if 'homestead_only' in request.GET and request.GET['homestead_only']:
			homestead_only = request.GET.__getitem__('homestead_only')
			queries.append(Q(homestead_only=homestead_only))
		if 'bep_demolition' in request.GET and request.GET['bep_demolition']:
			bep_demolition = request.GET.__getitem__('bep_demolition')
			queries.append(Q(bep_demolition=bep_demolition))
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
			try:
				properties = Property.objects.filter(reduce(operator.and_, queries))
			except:
				pass # search engines keep sending malformed queries with no search criteria so we want to just return everything in that case
			if returnType == "html":				
				return render(request, 'renew/table1_template.html', {'table': properties})
			if returnType == "csv": 	
				response = HttpResponse(content_type='text/csv')
				response['Content-Disposition'] = 'attachment; filename="renew-properties.csv"'
				writer = csv.writer(response)
				writer.writerow(["Parcel Number", "Street Address", "Zipcode", "Structure Type", "CDC", "Zoned", "NSP", "Licensed Urban Garden", "Quiet Title", "Sidelot Eligible", "Homestead Only", "BEP Demolition Slated", "Parcel Area ft^2", "Status", "Price", "Lat/Lon"])
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
					if row.homestead_only:
						hstdValue = "Yes"
					else:
						hstdValue = "No"
					if row.bep_demolition:
						bepDemolition = "Yes"
					else:
						bepDemolition = "No"

					writer.writerow([row.parcel, row.streetAddress, row.zipcode, row.structureType, row.cdc, row.zone, nspValue, ugValue, qtValue, slValue, hstdValue, bepDemolition, row.area, row.status, row.price, GEOSGeometry(row.geometry).centroid])
				return response	
		
#			if returnType == "xlsx":
#				output = StringIO.StringIO()
#				workbook = xlsxwriter.Workbook(output, {'in_memory': True})
#				worksheet = workbook.add_worksheet('Properties')
#				bold = workbook.add_format({'bold': True})

#				#writer.writerow(["Parcel Number", "Street Address", "Zipcode", "Structure Type", "CDC", "Zoned", "NSP", "Licensed Urban Garden", "Quiet Title", "Sidelot Eligible", "Parcel Size ft^2", "Status", "Lat/Lon"])
#				worksheet.write_row('A1',["Parcel Number", "Street Address", "Zipcode", "Structure Type", "CDC", "Zoned", "NSP", "Licensed Urban Garden", "Quiet Title", "Parcel Size ft^2", "Status", "Price", "Lat/Lon"],bold)
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
		pass
	djf = Django.Django(geodjango='geometry', properties=['streetAddress', 'parcel', 'status', 'structureType', 'sidelot_eligible', 'homestead_only', 'price'])
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


def	showApplications(request):
	config = RequestConfig(request)
	soldProperties = Property.objects.all().filter(status__exact='Sold').order_by('status', 'applicant')
	approvedProperties = Property.objects.all().filter(status__istartswith='Sale').order_by('status', 'applicant')
	soldTable = PropertyStatusTable(soldProperties, prefix="1-")
	approvedTable = PropertyStatusTable(approvedProperties, prefix="2-")
	config.configure(soldTable)
	config.configure(approvedTable)
	return render(request, 'renew/app_status_template.html', {'soldTable': soldTable, 'approvedTable': approvedTable, 'title': 'applications & sale activity'})


def getAddressFromParcel(request):
	response_data = {}
	if 'parcel' in request.GET and request.GET['parcel']:
		parcelNumber = request.GET.__getitem__('parcel')
		try:
			SearchResult = Property.objects.get(parcel__exact=parcelNumber)
		except Property.DoesNotExist:
			return HttpResponse("No such parcel in our inventory", content_type="text/plain")
		response_data['streetAddress'] = SearchResult.streetAddress
		response_data['structureType'] = SearchResult.structureType
		response_data['status'] = SearchResult.status
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	if 'streetAddress' in request.GET and request.GET['streetAddress']:
		streetAddress = request.GET.__getitem__('streetAddress')
		try:
			SearchResult = Property.objects.get(streetAddress__iexact=streetAddress)
		except Property.DoesNotExist:
			return HttpResponse("No such address in our inventory", content_type="text/plain") 
		return HttpResponse(SearchResult.parcel)
	return HttpResponse("Please submit a search term")


# Given a street name, return a json object with all the properties in inventory 
def getMatchingAddresses(request):
#	response_data = {}
	if 'street_name' in request.GET and request.GET['street_name']:
		street_name = request.GET.__getitem__('street_name')
		try:
			SearchResult = Property.objects.filter(streetAddress__icontains=street_name)
		except Property.DoesNotExist:
			return HttpResponse("No such properties in our inventory", content_type="text/plain")

		response_data = serializers.serialize('json', SearchResult, fields=('parcel','streetAddress'))
		return HttpResponse(response_data, content_type="application/json")
	return HttpResponse("Please submit a search term")


# Displays form template for property inquiry submissions, and saves those submissions
def showPropertyInquiry(request):
	form = PropertyInquiryForm(request.POST or None)
	parcelNumber = False
	if request.method == 'POST':
		form = PropertyInquiryForm(request.POST)
		if form.is_valid():
			form.save()
			parcelNumber = form.cleaned_data['parcel']
			ChosenProperty = Property.objects.get(parcel__iexact=parcelNumber)
			message_body = 'Applicant: ' + form.cleaned_data['applicant_name'] + '\n' + 'Parcel: ' + form.cleaned_data['parcel'] + '\nAddress: ' + ChosenProperty.streetAddress + '\nStatus: ' + ChosenProperty.status
			send_mail('New Property Inquiry', message_body, 'chris.hartley@renewindianapolis.org',
    ['chris.hartley@renewindianapolis.org'], fail_silently=False)
	return render_to_response('renew/property_inquiry.html', {
		'form': form,
		'parcel': parcelNumber
	}, context_instance=RequestContext(request))


# show all property inquiries
@method_decorator(login_required)
def propertyInquries(request):
		propertyInquries = propertyInquiry.objects.all().order_by('timestamp')
		return render_to_response('renew/property_inquiry_admin.html', {
			'propertyInquiries': propertyInquries
		}, context_instance=RequestContext(request))


def showApplicationForm(request):
	form = ApplicationForm(request.POST or None)
	if request.method == 'POST':
		form = ApplicationForm(request.POST, request.FILES)
		try:
			selected_property = Property.objects.get(parcel=request.POST['Parcel'])
		except Property.DoesNotExist:
			selected_property = None
		if form.is_valid():
			form_saved = form.save(commit=False)			# this is necessary so we can set the Property based on the parcel number inputed
			form_saved.Property = selected_property
			form_saved.save()
	return render_to_response('renew/application-template.html', {
		'form': form,
	}, context_instance=RequestContext(request))


