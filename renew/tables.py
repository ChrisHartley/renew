import django_tables as tables

class PropertyTable(tables.MemoryTable):
		parcel = tables.Column(verbose_name="Parcel Number")
		streetAddress = tables.Column(verbose_name="Street Address")
		zipcode = tables.Column(verbose_name="Zipcode")
		nsp = tables.Column(verbose_name="NSP")
		structureType = tables.Column(verbose_name="Structure Type")
		cdc = tables.Column(verbose_name="CDC")
		zone = tables.Column(verbose_name="Zoned")

