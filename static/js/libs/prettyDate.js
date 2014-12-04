/*
 * JavaScript Pretty Date
 * Copyright (c) 2008 John Resig (jquery.com)
 * Licensed under the MIT license.
 */

// Takes an ISO time and returns a string representing how
// long ago the date represents.
function prettyDate(time){
	var date = new Date((time || "").replace(/-/g,"/").replace(/[T]/g," ")),
		diff = (((new Date()).getTime() - date.getTime()) / 1000),
		day_diff = Math.floor(diff / 86400);
			
	if ( isNaN(day_diff) || day_diff < 0 || day_diff >= 31 )
		return;
			
	return day_diff == 0 && (
			diff < 60 && app_page.general_messages['just-now'] ||
			diff < 120 && app_page.general_messages['minute-ago'] ||
			diff < 3600 && Math.floor( diff / 60 ) + " " + app_page.general_messages['minutes-ago'] ||
			diff < 7200 && app_page.general_messages["hour-ago"] ||
			diff < 86400 && Math.floor( diff / 3600 ) + " " + app_page.general_messages['hours-ago']) ||
		day_diff == 1 && app_page.general_messages['yesterday'] ||
		day_diff < 7 && day_diff + " " + app_page.general_messages['days-ago'] ||
		day_diff < 31 && Math.ceil( day_diff / 7 ) + " " + app_page.general_messages["weeks-ago"];
}

// If jQuery is included in the page, adds a jQuery plugin to handle it as well
if ( typeof jQuery != "undefined" )
	jQuery.fn.prettyDate = function(){
		return this.each(function(){
			var date = prettyDate(this.title);
			if ( date )
				jQuery(this).text( date );
		});
	};