
/****************************************************************
 *  clear object
 ****************************************************************/
 function f_clear(obj) {
	obj.value = "";
 }

 
/****************************************************************
 *  on Load
 ****************************************************************/
(function($) {
	$(document).ready(function() {
		var strErrMsg = $("#errMsg").val();
		if(strErrMsg) {
			alert(strErrMsg);
		}
	});
})($);




/****************************************************************
 *  number only
 ****************************************************************/
function f_numOnly(objId) {
	
	var regexp = /[^[0-9]/gi;

	if(regexp.test($('#' + objId).val())){
		alert('number only');
		$('#' + objId).val("");
		$('#' + objId).focus();
		return false;
	}
	return true;
}








/****************************************************************
 *  CSRF Token
 ****************************************************************/
function f_getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = $.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}


/****************************************************************
 *  CSRF Token
 ****************************************************************/
function f_csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}



/****************************************************************
 *  only English & number
 ****************************************************************/
function f_checkSpecial(objectId){  

	var chkObject = $("#" + objectId);
	var str = chkObject.val();
	
	// special character
	var regExp = /[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]/gi
	if(regExp.test(str)){
		var retStr = str.replace(regExp, "")
		chkObject.val(retStr);
		alert("You can't use a special letters.");
		chkObject.focus();
		return false;
	}

	// space
	var blank_pattern = /[\s]/g;
	if (blank_pattern.test(str) == true) {
		var retStr = str.replace(blank_pattern, "")
		chkObject.val(retStr);
		alert("No space please.");
		chkObject.focus();
		return false;
	}
	
	return true;
}
	



/****************************************************************
 *  check number only
 ****************************************************************/
function f_checkNumOnly(objId) {
	
	var regexp = /^[0-9]+$/;

	if(!regexp.test($('#' + objId).val())){
		alert('number only');
		$('#' + objId).val("");
		$('#' + objId).focus();
		return false;
	}
	return true;
}



/****************************************************************
 *  float only
 ****************************************************************/
function f_checkFloatOnly(objId) {
	
	var regexp = /^\d+(?:[.]\d+)?$/;
	if(!regexp.test($('#' + objId).val())){
		alert('float only');
		$('#' + objId).val("");
		$('#' + objId).focus();
		return false;
	}
	return true;
}




/****************************************************************
 *  list only for ED 
 *      ex)  1,2,3
 ****************************************************************/
function f_checkNumListOnly(objId) {
	
	var regexp = /^\d*(,\d+)*$/;
	if(!regexp.test($('#' + objId).val())){
		alert('Number list only');
		$('#' + objId).val("");
		$('#' + objId).focus();
		return false;
	}
	return true;
}


