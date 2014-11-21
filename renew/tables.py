import django_tables as tables
import django_tables2 as tables2

from django_tables2_reports.tables import TableReport


from renew.models import Property

class PropertyTable(tables.MemoryTable):
		parcel = tables.Column(verbose_name="Parcel Number")
		streetAddress = tables.Column(verbose_name="Street Address")
		zipcode = tables.Column(verbose_name="Zipcode")
		nsp = tables.Column(verbose_name="NSP")
		structureType = tables.Column(verbose_name="Structure Type")
		cdc = tables.Column(verbose_name="CDC")
		zone = tables.Column(verbose_name="Zoned")

#class PropertyStatusTable(tables2.Table):
class PropertyStatusTable(TableReport):
	class Meta:
		model = Property
		attrs = {"class": "paleblue"}
		fields = ("parcel", "streetAddress", "zipcode", "structureType", "applicant", "status", )
