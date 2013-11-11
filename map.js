var lon = -9590863.695045754313469;
var lat = 4835547.198063937388361;
var zoom = 12;
var map, OSMlayer, gmap, gypb, statemLayer, stamenTerrainLayer, drawControls, polyfeature, polygonLayer, searchResultsLayer, searchResults, surplusLayer;
var selectControl, selectedFeature, selectedFill, selectedLayer;
var lbStyle, lbStyleMap;
var searchArea = new Array();
var clusterStrategy = new OpenLayers.Strategy.Cluster({distance: 15, threshold: 4});

var stamenAttribution = 'Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.';


var geojson_format = new OpenLayers.Format.GeoJSON({
                    'internalProjection': new OpenLayers.Projection("EPSG:900913"),
                    'externalProjection': new OpenLayers.Projection("EPSG:4326")
});   

function toggleDraw(element) {
	if(element.value == "polygon" && element.checked) {
   		polyfeature.activate();
		alert("Click on the map to draw a corner, double click to finish");
    } else {
                polyfeature.deactivate();
            }
}

function clearDrawn() {
	polygonLayer.destroyFeatures();
}
    

function onPopupClose(evt) {
    selectControl.unselect(selectedFeature);
}

function onFeatureSelect(feature) {
    selectedFeature = feature;
	selectedLayer = feature.layer;
	selectedLayer.drawFeature(feature, {fillColor: "#ffff00", strokeColor: "black"});
    popup = new OpenLayers.Popup.FramedCloud("chicken", 
                             feature.geometry.getBounds().getCenterLonLat(),
                             null,
                             "<div style='font-size:.8em'>Parcel: " + feature.attributes.parcel +"<br>Address: " + feature.attributes.streetAddress+"</div>",
                             null, true, onPopupClose);
    feature.popup = popup;
    map.addPopup(popup);
}

function onFeatureUnselect(feature) {
    map.removePopup(feature.popup);
    feature.popup.destroy();
    feature.popup = null;
}    

function getSearchArea(){
	try{
		$('input[name=searchArea]').val(polygonLayer.features[0].geometry.toString());		
	}
	catch(err){ return; }
}


function init(){
	map = new OpenLayers.Map( 'map', {controls: [	
		new OpenLayers.Control.PanZoomBar(), 
		new OpenLayers.Control.KeyboardDefaults(), 
		new OpenLayers.Control.Navigation(),
		new OpenLayers.Control.Attribution()
	]});
	
	var ls = new OpenLayers.Control.LayerSwitcher({});
	map.addControl(ls);
	ls.maximizeControl();

	// set up basemaps
	stamenLayer = new OpenLayers.Layer.Stamen("toner", {attribution: stamenAttribution});
	stamenLayer.setName('Stamen Toner');
	stamenTerrainLayer = new OpenLayers.Layer.Stamen('terrain', {attribution: stamenAttribution});
	stamenTerrainLayer.setName('Stamen Terrain');
    OSMlayer = new OpenLayers.Layer.OSM();
	gmap = new OpenLayers.Layer.Google(
		"Google Streets", 
		{numZoomLevels: 20}
	);
	ghyb = new OpenLayers.Layer.Google(
		"Google Hybrid",
		{type: google.maps.MapTypeId.HYBRID, numZoomLevels: 20}
	);

	
	// define style maps
	
	lbStyle = new OpenLayers.Style({
		fillColor: '#33A02C', 
		strokeWidth: '.05', 
		strokeColor: 'black', 
		pointRadius: '8', 
		label:"${label}",
		fontColor: "#ffffff",
        fontOpacity: 0.8,
        fontSize: "12px" 
	}, {
		context: {
			label: function(feature) {
				// clustered features count or blank if feature is not a cluster
				return feature.cluster ? feature.cluster.length : "";  
      		}	
		}
	}); 

	var surplusStyleMap = new OpenLayers.StyleMap({fillColor: '#A6CEE3', strokeWidth: '.05', strokeColor: 'black'});
	lbStyleMap = new OpenLayers.StyleMap(lbStyle);
	var searchResultStyleMap = new OpenLayers.StyleMap({fillColor: '#1F78B4', strokeWidth: '.05', strokeColor: 'black'});

	// define vector layers
	polygonLayer = new OpenLayers.Layer.Vector("Drawn Search Area"); // search by polygon layer
	searchResultsLayer = new OpenLayers.Layer.Vector("Search Results", {styleMap: searchResultStyleMap}); 
	surplusLayer = new OpenLayers.Layer.Vector("Surplus Properties", {
		strategies: [new OpenLayers.Strategy.Fixed()],
		styleMap: surplusStyleMap,
		protocol: new OpenLayers.Protocol.HTTP({
			url: "/map/search/?searchType=sp",
			format: new OpenLayers.Format.GeoJSON()
		})
	});

	browserWarning.prototype.test = function(callback){
		if(this.isOldBrowser()){
			alert("here");
		}
	}

	lbLayer = new OpenLayers.Layer.Vector("Landbank Properties", {
		protocol: new OpenLayers.Protocol.HTTP({
			url: "/map/search/?searchType=lb",
			format: new OpenLayers.Format.GeoJSON()
		}),
		strategies: [
			new OpenLayers.Strategy.Fixed() //,
			//clusterStrategy
    	],
		styleMap: lbStyleMap
	});
	map.addLayer(lbLayer);

	map.addLayer(stamenLayer);	
	map.addLayer(OSMlayer);
	map.addLayer(gmap);
	map.addLayer(ghyb);
	map.addLayer(polygonLayer);
    map.addLayer(stamenTerrainLayer);

   //	map.addLayer(surplusLayer);
	map.addLayer(searchResultsLayer);

	//surplusLayer.setVisibility(false);

	map.setCenter(new OpenLayers.LonLat(lon, lat), zoom);

	// draw polygon to define search area   
	polyfeature = new OpenLayers.Control.DrawFeature(polygonLayer, OpenLayers.Handler.Polygon);
	map.addControl(polyfeature);
	

	selectControl = new OpenLayers.Control.SelectFeature([lbLayer, searchResultsLayer],
		{onSelect: onFeatureSelect, onUnselect: onFeatureUnselect});
	map.addControl(selectControl);
	selectControl.activate(); 

}


function getCSV(){
	var tmp = $("#myForm").serialize(); 
	document.location.href = "/map/search/?returnType=csv&" + tmp;
}

function getSearchResults(data)  { 
	searchResultsLayer.addFeatures(geojson_format.read(data));
}

function clearSearchResults(){
	searchResultsLayer.destroyFeatures();
	$('#myTable').empty();
	//clearDrawn();
}

;
function toggleSearchOptions(){
	if ( $('#searchToggle').is(':contains("Show more search options")') ){
		$('#moreSearchOptions').show();
		$('#searchToggle').html('Show fewer search options');
		return;
	}else{
		$('#moreSearchOptions').hide();
		$('#searchToggle').html('Show more search options');
	}
	
}

function toggleClustering(){
	//alert("in toggleClustering()");
	selectControl.deactivate();
	map.removeControl(selectControl);
	map.removeLayer(lbLayer);
	var strategies = [];
	console.log(document.getElementById("toggleClustersCheckbox").checked);
	if ( document.getElementById("toggleClustersCheckbox").checked ) {
		strategies.push(new OpenLayers.Strategy.Fixed());
		strategies.push(clusterStrategy);
	}else {
		strategies.push(new OpenLayers.Strategy.Fixed());
	}
	console.log(strategies);
	lbLayer = new OpenLayers.Layer.Vector("Landbank Properties", {
		protocol: new OpenLayers.Protocol.HTTP({
			url: "/map/search/?searchType=lb",
			format: new OpenLayers.Format.GeoJSON()
		}),
		strategies: strategies,
		styleMap: lbStyleMap
	});
	map.addLayer(lbLayer);
	selectControl = new OpenLayers.Control.SelectFeature([lbLayer, searchResultsLayer],
		{onSelect: onFeatureSelect, onUnselect: onFeatureUnselect});
	map.addControl(selectControl);
	selectControl.activate(); 

}

//jquery ajax form
$(function(){
	var options = {		
		beforeSerialize: function(){
			getSearchArea();
		},		
		dataType: 'html', // because it makes it a json javascript object if you chose json
		success: getSearchResults
	};

	var optionsTable = {
		beforeSerialize: function(){
			getSearchArea();
		},
		data: { returnType: 'html'},				
		dataType: 'html', // because it makes it a json javascript object if you chose json
		success: function(data) { 
		    $('#myTable')
				.empty()
				.append(data)
				.endlessPaginate(); 
		} 
	};


	$("#myForm").validate({
		rules: {
			maxsize: {
				number: true
			},
			minsize: {
				number: true
			}
		},
		submitHandler: function(form) {
			$(form).ajaxSubmit(optionsTable);
			$(form).ajaxSubmit(options);
			return false;
		},
		debug: true,
		success: "valid"
	});
});

$(function() {
	$( "#intro" ).dialog();


	$('#help-hints').click(function () {
		$("#intro").dialog('open');
        return false;
    });
	$('#searchToggle').click(function() { toggleSearchOptions(); });
	$('#downloadButton').click(function() { getCSV(); } );
	$('#toggleClustersCheckbox').change(function() { toggleClustering(); } );

 });


