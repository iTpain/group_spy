new Module('ui/main-screen.js', ['jsage/eventbus.js', 'ui/operations-counter.js', 'utils/async-operations.js', 'ui/group-comparison.js'], function() {

console.log("Main screen - group spy")

$(document).ready(function () {
var screens_info = {
	'screen-stat': {
		address: 'group'
	},
	'screen-post': {
		address: 'posts'
	},
	'screen-group-comparison': {
		address: 'group-comparison'
	},
	'screen-usertop': {
		address: 'usertop'
	},
	'screen-sa_distribution': {
		address: 'sa_distribution'
	}		
}
var current_screen = 'screen-stat'
var group_shown = null
var current_screen_shown = null

$("#screen-select").bind("change", function (e) {
	open_central_frame(e.target.value)
})

window.open_central_frame = function(id) {
	current_screen = id
	redrawFrame()
}

window.find_group_by_id = function(gid) {
	for (var i = 0, l = groups_info.length; i < l; i++) {
		if (gid == groups_info[i].gid)
			return groups_info[i]
	}
	return null
}
	
function redrawFrame() {
	if (group_shown != null || current_screen == "screen-group-comparison") {
		if (current_screen_shown != null)
			current_screen_shown.style.display = 'none'

		current_screen_shown = document.getElementById('central-' + screens_info[current_screen].address)
		current_screen_shown.style.display = 'block'
		jsage.global_bus.trigger(groupspy.messages[screens_info[current_screen].address + '_frame_activate'], group_shown)
		
		$("div.group_asking_to_click")[0].style.display = "none"
		if (curSelected != null) 
			$(curSelected)[0].style.color = ""
		if (group_shown != null) {
			$("#group_alias_" + group_shown)[0].style.color = "#ff6600"
			curSelected = $("#group_alias_" + group_shown)[0]	
		}
		
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
window.show_dialog = function (dialog_id, params) {
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

window.update_group_info = function() {
	var agency = $("#group_agency_input")[0].value
	var brand = $("#group_brand_input")[0].value
	var gid = $("#group_id_hidden_input")[0].value
	ajaxOperationsManager.do_operation(
		'/group' + gid + '/update_info/', 'post', {agency: encodeURIComponent(agency), brand: encodeURIComponent(brand)},
		function (data) {
			$("#group_agency_span_" + gid)[0].innerHTML = agency
			$("#group_brand_span_" + gid)[0].innerHTML = brand;
			close_current_dialog()
			return true
		}
	)
}

var curSelected = null
window.showGroup = function (gid, obj) {
	group_shown = gid
	if (current_screen == "screen-group-comparison")
		current_screen = "screen-stat"
	redrawFrame()
}

window.addGroup = function () {
	gid = $("#added_group_id")[0].value
	if (gid.length == 0)
		return;
	ajaxOperationsManager.do_operation(
		'/group' + gid + '/add/', 'get', null,
		function (res) {
			if (res.errors.length > 0) {
				return res.errors
			} else {
				res = res.response
				var div = $('<div class="group" id="group_div_' + res.gid + '">' +
							'<div data-group-id="' + res.gid + '" class="group_header"><span class="group_alias" id="group_alias_' + res.gid + '" onclick="showGroup(' + res.gid + ')">' + res.alias + '</span><span onclick="deleteGroup(' + res.gid + ')" class="group_delete" style="display:none">x</span></div>' +
							'<div class="group_info"><span id="group_minor_info_' + res.gid + '" onclick="show_dialog(\'group_info_updater\', [' + res.gid + '])"><span id="group_agency_span_'+res.gid+'">агентство не указано</span> - <span id="group_brand_span_'+res.gid+'">бренд не указан</span></span></div>' +
							'<div class="group_href"><a target="blank" class="group_href" href="http://vkontakte.ru/club' + res.gid + '">http://vkontakte.ru/club' + res.gid + '</a></div>' +
							'</div>')[0]
				$("#groups-list")[0].appendChild (div);
				groups_mouse_interaction_bindage()
				groups_info.push({gid: res.gid, alias: res.alias, agency: '', brand: ''})
				jsage.global_bus.trigger(groupspy.messages.group_added, div)
				return true
			}
		},
		function (err) { },
		{ toString: function () { return 'Add-group ' + gid} }
	)
}

window.deleteGroup = function (gid) {
	if (confirm('Вы уверены, что хотите удалить группу?'))
		ajaxOperationsManager.do_operation(
			'/group' + gid + '/delete/', 'get', null,
			function (res) {
				if (res.errors.length > 0) {
					return res.errors
				} else {
					$("#groups-list")[0].removeChild($("#group_div_" + gid)[0])
					return true
				}
			},
			function (err) { },
			{ toString: function () { return 'Add-group ' + gid} }
		)	
}

function groups_mouse_interaction_bindage () {
	$("div.group_header").bind("mouseover", function(e) {
		e.currentTarget.childNodes[1].style.display = 'inline'
	})
	$("div.group_header").bind("mouseout", function(e) {
		e.currentTarget.childNodes[1].style.display = 'none'
	})
}
groups_mouse_interaction_bindage()

$("#methodology-help").bind("click", function (ev) {$.openDOMWindow({
	windowSourceID: "#methodology-helper",
	width: 640,
	height: 480
})})
$("#posts-help").bind("click", function (ev) {$.openDOMWindow({
	windowSourceID: "#posts-helper",
	width: 640,
	height: 480
})})

function adjust_height() {
	var h = $(window).height()
	$(".metro-scroll").height(h - 116)
	$("#stats-column").height(h - 116)
}
$(window).resize(adjust_height)
adjust_height()

// manager objects
window.ajaxOperationsManager = groupspy.AjaxOperationsManager.create()

// operations counter
var opCounter1 = groupspy.OperationsCounter.create($("#operations-counter")[0])

// errors panel
var errorsPanel = jsage.ErrorPanel.create(10, 5000, [groupspy.messages.ajax_failure])
$("body")[0].appendChild(errorsPanel.elements.container)

// group comparison
var group_comparison = groupspy.GroupComparisonBase.create()


})
})