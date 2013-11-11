var hasOldBrowser;
var browserWarning = function(options){
	this.options = Basic.extend({
			// browser version need to be greater than this values
			lowerVersionFor: {
				ie      : 8, 
				safari  : 4, 
				opera   : 9.5,
				firefox : 3, 
				chrome  : 3
			},
			oldByDefault: false,
			cookie: {
				enabled: false,
				name:    'browserWarning',
				value:   'allreadyWarned',
				expired: null
			}
	}, options);
};

browserWarning.prototype.test = function(callback){
	if(!Basic.isFunction(callback)){
		throw 'BrowserWarning.test : you need to pass a callback action';
	}

	if(this.isOldBrowser() && (!this.options.cookie.enabled || !this.hasBrowserWarningCookie())){
		//callback.call();
		hasOldBrowser = true;
		alert("here");
		
		if(this.options.cookie.enabled){
			this.setBrowserWarningCookie();
		}
	}
};

browserWarning.prototype.isOldBrowser = function(){
	browserDetect.init();

	var isOldBrowser = {
		value: null,
		testVersion: function(browserVersion, neededVersion, defaultValue){
			this.value = parseFloat(browserVersion) < neededVersion  ? true : (/^[0-9\.]*$/.test(browserVersion) ? false : defaultValue);
		}
	};


	
	switch (browserDetect.browser) {
	case 'Opera':
		isOldBrowser.testVersion(browserDetect.version, this.options.lowerVersionFor.opera, this.options.oldByDefault);
		break;
	case 'Firefox':
		isOldBrowser.testVersion(browserDetect.version, this.options.lowerVersionFor.firefox, this.options.oldByDefault);
		break;
	case 'Safari':
		isOldBrowser.testVersion(browserDetect.version, this.options.lowerVersionFor.safari, this.options.oldByDefault);
		break;
	case 'Explorer':
		isOldBrowser.testVersion(browserDetect.version, this.options.lowerVersionFor.ie, this.options.oldByDefault);
		break;
	case 'Chrome':
		isOldBrowser.testVersion(browserDetect.version, this.options.lowerVersionFor.chrome, this.options.oldByDefault);
		break;
	default: 
		isOldBrowser.value = this.options.oldByDefault;
		break;
	}
	
	return isOldBrowser.value;
};


browserWarning.prototype.hasBrowserWarningCookie = function(){
	var c_start = -1, c_end = -1, value = null, hasCookie = false;
	
	if (document.cookie.length > 0) {
		c_start = document.cookie.indexOf(this.options.cookie.name + "=");
		if (c_start != -1) {
			c_start = c_start + this.options.cookie.name.length + 1;
			c_end   = document.cookie.indexOf(";",c_start);
			if (c_end == -1) {
				c_end = document.cookie.length;
			}
			value = unescape(document.cookie.substring(c_start,c_end));
			hasCookie = value == this.options.cookie.value ? true : false;
		} 
	}
	return hasCookie;
};

browserWarning.prototype.setBrowserWarningCookie = function(){
	var exdate = new Date();
	exdate.setDate(exdate.getDate() + this.options.cookie.expired);
	document.cookie = this.options.cookie.name + "=" + escape( this.options.cookie.value) + ((this.options.cookie.expired === null) ? "" : ";expires=" + exdate.toGMTString());
};





/**
 * coded by Peter-Paul Koch
 * source : http://www.quirksmode.org/js/detect.html
 */
var browserDetect = {
	init: function () {
		this.browser = this.searchString(this.dataBrowser) || "An unknown browser";
		this.version = this.searchVersion(navigator.userAgent)
			|| this.searchVersion(navigator.appVersion)
			|| "an unknown version";
		this.OS = this.searchString(this.dataOS) || "an unknown OS";
	},
	searchString: function (data) {
		for (var i=0;i<data.length;i++)	{
			var dataString = data[i].string;
			var dataProp = data[i].prop;
			this.versionSearchString = data[i].versionSearch || data[i].identity;
			if (dataString) {
				if (dataString.indexOf(data[i].subString) != -1)
					return data[i].identity;
			}
			else if (dataProp)
				return data[i].identity;
		}
	},
	searchVersion: function (dataString) {
		var index = dataString.indexOf(this.versionSearchString);
		if (index == -1) return;
		return parseFloat(dataString.substring(index+this.versionSearchString.length+1));
	},
	dataBrowser: [
		{
			string: navigator.userAgent,
			subString: "Chrome",
			identity: "Chrome"
		},
		{ 	string: navigator.userAgent,
			subString: "OmniWeb",
			versionSearch: "OmniWeb/",
			identity: "OmniWeb"
		},
		{
			string: navigator.vendor,
			subString: "Apple",
			identity: "Safari",
			versionSearch: "Version"
		},
		{
			prop: window.opera,
			identity: "Opera"
		},
		{
			string: navigator.vendor,
			subString: "iCab",
			identity: "iCab"
		},
		{
			string: navigator.vendor,
			subString: "KDE",
			identity: "Konqueror"
		},
		{
			string: navigator.userAgent,
			subString: "Firefox",
			identity: "Firefox"
		},
		{
			string: navigator.vendor,
			subString: "Camino",
			identity: "Camino"
		},
		{		// for newer Netscapes (6+)
			string: navigator.userAgent,
			subString: "Netscape",
			identity: "Netscape"
		},
		{
			string: navigator.userAgent,
			subString: "MSIE",
			identity: "Explorer",
			versionSearch: "MSIE"
		},
		{
			string: navigator.userAgent,
			subString: "Gecko",
			identity: "Mozilla",
			versionSearch: "rv"
		},
		{ 		// for older Netscapes (4-)
			string: navigator.userAgent,
			subString: "Mozilla",
			identity: "Netscape",
			versionSearch: "Mozilla"
		}
	],
	dataOS : [
		{
			string: navigator.platform,
			subString: "Win",
			identity: "Windows"
		},
		{
			string: navigator.platform,
			subString: "Mac",
			identity: "Mac"
		},
		{
			   string: navigator.userAgent,
			   subString: "iPhone",
			   identity: "iPhone/iPod"
	    },
		{
			string: navigator.platform,
			subString: "Linux",
			identity: "Linux"
		}
	]

};




/*
 * extend method coming from jQuery lib
 */
var Basic = {
		isFunction: function( obj ) {
			return typeof obj === "function";
		},
		
		isArray: function( obj ) {
			return toString.call(obj) === "[object Array]";
		},
		
		isPlainObject: function( obj ) {
			// Must be an Object.
			// Because of IE, we also have to check the presence of the constructor property.
			// Make sure that DOM nodes and window objects don't pass through, as well
			if ( !obj || toString.call(obj) !== "[object Object]" || obj.nodeType || obj.setInterval ) {
				return false;
			}
			
			// Not own constructor property must be Object
			if ( obj.constructor
				&& !hasOwnProperty.call(obj, "constructor")
				&& !hasOwnProperty.call(obj.constructor.prototype, "isPrototypeOf") ) {
				return false;
			}
			
			// Own properties are enumerated firstly, so to speed up,
			// if last one is own, then all properties are own.
		
			var key;
			for ( key in obj ) {}
			
			return key === undefined || hasOwnProperty.call( obj, key );
		},
		
		isEmptyObject: function( obj ) {
			for ( var name in obj ) {
				return false;
			}
			return true;
		},
		
		extend: function() {
			// copy reference to target object
			var target = arguments[0] || {}, i = 1, length = arguments.length, deep = false, options, name, src, copy;

			// Handle a deep copy situation
			if ( typeof target === "boolean" ) {
				deep = target;
				target = arguments[1] || {};
				// skip the boolean and the target
				i = 2;
			}

			// Handle case when target is a string or something (possible in deep copy)
			if ( typeof target !== "object" && !Basic.isFunction(target) ) {
				target = {};
			}

			// extend Basic itself if only one argument is passed
			if ( length === i ) {
				target = this;
				--i;
			}

			for ( ; i < length; i++ ) {
				// Only deal with non-null/undefined values
				if ( (options = arguments[ i ]) != null ) {
					// Extend the base object
					for ( name in options ) {
						src = target[ name ];
						copy = options[ name ];

						// Prevent never-ending loop
						if ( target === copy ) {
							continue;
						}

						// Recurse if we're merging object literal values or arrays
						if ( deep && copy && ( Basic.isPlainObject(copy) || Basic.isArray(copy) ) ) {
							var clone = src && ( Basic.isPlainObject(src) || Basic.isArray(src) ) ? src
								: Basic.isArray(copy) ? [] : {};

							// Never move original objects, clone them
							target[ name ] = Basic.extend( deep, clone, copy );

						// Don't bring in undefined values
						} else if ( copy !== undefined ) {
							target[ name ] = copy;
						}
					}
				}
			}

			// Return the modified object
			return target;
		},
		
};




var badBrowser = new browserWarning();

window.onload = function(){
	badBrowser.test(function(){
		var warningContent = document.createElement('div');
		warningContent.innerHTML =   '<strong>Warning</strong><br />'
								   + 'Your browser is too old, some web functionalities are not available.<br />' 
								   + 'If you would like to have a full support of lastest internet technologies, please update or change your browser.<br />'
								   + '<a target="_blank" href="http://getfirefox.com" title="get FireFox"><img src="http://zazabe.ismerging.us/browser-warning/firefox.png" alt="get Firefox" style="margin: 5px;" /></a>'
								   + '<a target="_blank" href="http://www.opera.com/download/" title="get Opera"><img src="http://zazabe.ismerging.us/browser-warning/opera.png" alt="get Opera" style="margin: 5px;" /></a>'
								   + '<a target="_blank" href="http://www.apple.com/safari/" title="get Safari"><img src="http://zazabe.ismerging.us/browser-warning/safari.png" alt="get Safari" style="margin: 5px;" /></a>'
								   + '<a target="_blank" href="http://www.microsoft.com/windows/downloads/ie/getitnow.mspx" title="get Internet Exporer"><img src="http://zazabe.ismerging.us/browser-warning/ie.png" alt="get Internet Explorer" style="margin: 5px;" /></a>'
								   + '<button id="close" style="position: absolute; top: 10px; right: 10px;" type="button">Close</button>'; 
		warningContent.style.width        = '100%';
		warningContent.style.borderBottom = '1px solid #900'; 
		warningContent.style.background   = '#fff9d4'; 
		warningContent.style.fontSize     = '1.5em';
		warningContent.style.textAlign    = 'center';
		warningContent.style.position     = 'absolute';
		warningContent.style.top          = '0px';
		warningContent.style.zIndex       = '999';

		document.body.insertBefore(warningContent, document.body.firstChild); ;
		
		var button = document.getElementById('close');
		button.onclick = function(){
			warningContent.style.display = 'none';
			return false;
		}
	});
}
