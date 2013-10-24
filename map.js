var lon = -9590863.695045754313469;
var lat = 4835547.198063937388361;
var zoom = 12;
var map, OSMlayer, gmap, gypb, statemLayer, stamenTerrainLayer, drawControls, polyfeature, polygonLayer, searchResultsLayer, searchResults, surplusLayer;
var selectControl, selectedFeature, selectedFill, selectedLayer;
var searchArea = new Array();

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
	var surplusStyleMap = new OpenLayers.StyleMap({fillColor: '#A6CEE3', strokeWidth: '.05', strokeColor: 'black'});
	var lbStyleMap = new OpenLayers.StyleMap({fillColor: '#33A02C', strokeWidth: '.05', strokeColor: 'black'});
	var searchResultStyleMap = new OpenLayers.StyleMap({fillColor: '#1F78B4', strokeWidth: '.05', strokeColor: 'black'});

	var strat = new OpenLayers.Strategy.Cluster({distance:20, threshold:2});

	// define vector layers
	polygonLayer = new OpenLayers.Layer.Vector("Drawn Search Area"); // search by polygon layer
	searchResultsLayer = new OpenLayers.Layer.Vector("Search Results", {styleMap: searchResultStyleMap}); 
	surplusLayer = new OpenLayers.Layer.Vector("Surplus Properties", {
		//projection: "EPSG:4326",
		strategies: [new OpenLayers.Strategy.Fixed()],
		styleMap: surplusStyleMap,
		protocol: new OpenLayers.Protocol.HTTP({
			url: "/map/search/?searchType=sp",
			format: new OpenLayers.Format.GeoJSON()
		})
	});


	lbLayer = new OpenLayers.Layer.Vector("Landbank Properties", {
		//projection: "EPSG:4326",
		strategies: [new OpenLayers.Strategy.Fixed()],
		styleMap: lbStyleMap,
		protocol: new OpenLayers.Protocol.HTTP({
			url: "/map/search/?searchType=lb",
			format: new OpenLayers.Format.GeoJSON()
		})
	});


	map.addLayer(stamenLayer);	
	map.addLayer(OSMlayer);
	map.addLayer(gmap);
	map.addLayer(ghyb);
	map.addLayer(polygonLayer);
    map.addLayer(stamenTerrainLayer);
	map.addLayer(lbLayer);
   	//map.addLayer(surplusLayer);
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


