new Module('ui/main_screen.js', ['ui/operations-counter.js'], function() {

console.log("Main screen - group spy")

var screens_info = {
	'screen-stat': {
		address: 'group'
	},
	'screen-post': {
		address: 'posts'
	},
	'screen-query': {
		address: 'queries'
	}		
}
var current_screen = 'screen-stat'
var group_shown = null

$("#screen-select").bind("change", function (e) {
	current_screen = e.target.value
	redrawFrame()
})

function find_group_by_id(gid) {
	for (var i = 0, l = groups_info.length; i < l; i++) {
		if (gid == groups_info[i].gid)
			return groups_info[i]
	}
	return null
}
	
function redrawFrame() {
	if (group_shown != null) {
		document.getElementById ("graphFrame").src = screens_info[current_screen].address + group_shown
		$("div.group_asking_to_click")[0].style.display = "none"
		if (curSelected != null) 
			$(curSelected)[0].style.color = ""
		$("#group_alias_" + group_shown)[0].style.color = "#ff6600"
		curSelected = $("#group_alias_" + group_shown)[0]	
		
		for (var e in screens_info) {
			var header = $('#' + e + '-header')[0]
			header.style.display = e == current_screen ? 'block' : 'none'
		}
	}
}

var opened_dialog = null
var dialog_funcs = {
	"group_info_updater": function (gid) {
		$("#group_id_hidden_input")[0].value = gid
		$("#group_agency_input")[0].value = $("#group_agency_span_" + gid)[0].innerHTML
		$("#group_brand_input")[0].value = $("#group_brand_span_" + gid)[0].innerHTML
		$("#group_updater_header")[0].innerHTML = find_group_by_id(gid).alias
	}
}
function show_dialog (dialog_id, params) {
	close_current_dialog()
	dialog_funcs[dialog_id].apply (window, params)
	opened_dialog = $("#" + dialog_id)
	opened_dialog.openDOMWindow({
		windowSourceID: '#' + dialog_id,
		height: 150
	})
}

function close_current_dialog() {
	if (opened_dialog != null) {
		opened_dialog.closeDOMWindow()
		opened_dialog = null
	}
}

function update_group_info() {
	var agency = $("#group_agency_input")[0].value
	var brand = $("#group_brand_input")[0].value
	var gid = $("#group_id_hidden_input")[0].value
	$.ajax({
		url: '/group' + gid + '/update_info/',
		type: 'post',
		data: 'agency=' + encodeURIComponent(agency) + "&brand=" + encodeURIComponent(brand),
		success: function (data) {
			$("#group_agency_span_" + gid)[0].innerHTML = agency
			$("#group_brand_span_" + gid)[0].innerHTML = brand;
			close_current_dialog()
		}
	})
}

var curSelected = null
window.showGroup = function (gid, obj) {
	group_shown = gid
	redrawFrame()
}

function addGroup () {
	gid = $("#added_group_id")[0].value
	if (gid.length == 0)
		return;
	$.ajax ({
		'url': '/group/add/' + gid,
		'error': function (err) { alert (err.errors) },
		'success': function (res) {
			if (res.errors.length > 0) {
				alert (res.errors)
			} else {
				res = res.response
				var div = $('<div class="group">' +
							'<div class="group_alias" id="group_alias_' + res.gid + '" onclick="showGroup(' + res.gid + ')">' + res.alias + '</div>' +
							'<div class="group_info"><span id="group_minor_info_' + res.gid + '" onclick="show_dialog(\'group_info_updater\', [' + res.gid + '])"><span id="group_agency_span_'+res.gid+'">��������� �� �������</span> - <span id="group_brand_span_'+res.gid+'">����� �� ������</span></span></div>' +
							'<div class="group_href"><a target="blank" class="group_href" href="http://vkontakte.ru/club' + res.gid + '">http://vkontakte.ru/club' + res.gid + '</a></div>' +
							'</div>')[0]
				$("#group-list-column")[0].appendChild (div);
				groups_info.push({gid: res.gid, alias: res.alias, agency: '', brand: ''})
			}
		},
	});
}

$("#methodology-help").bind("click", function (ev) {$.openDOMWindow({
	windowSourceID: "#methodology-helper",
	width: 640,
	height: 480
})})

// operations counter
console.log(groupspy)
var opCounter = new groupspy.OperationsCounter($("#operations-counter")[0])

})