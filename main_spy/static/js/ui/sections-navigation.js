new Module('ui/sections-navigation.js', ['jsage/mixin.js', 'jsage/eventbus.js'], function () {
	
$(document).ready(function () {

var tabs = {}
var elements = $("div.app-tab")
for (var i = 0, l = elements.length; i < l; i++) {
	var elem = elements[i]
	tabs[elem.getAttribute("data-navigate")] = elem
}

var cur_section = elements[0]
var cur_group = null
var cur_content = null
var cur_header = null
var turn_on_section = function(section) {
	$(cur_section).toggleClass("white")
	cur_section = section
	$(cur_section).toggleClass("white")
	var id = cur_section.getAttribute("data-navigate")
	
	if (cur_header)
		$(cur_header).toggle()
	cur_header = $("#" + id + "-header")[0]
	$(cur_header).toggle()
	
	if (cur_content)
		$(cur_content).toggle()
	cur_content = $("#central-" + id)
	$(cur_content).toggle()	
	jsage.global_bus.trigger(id + "_frame_activate", cur_group)
}

var turn_off_cur_central = function() {
	if (cur_header) {
		$(cur_header).toggle()
		cur_header = null
	}
	if (cur_content) {
		$(cur_content).toggle()
		cur_content = null
	}
}

$("div.app-tab").bind("click", function(event) {
	var navigate_to = event.target.getAttribute("data-navigate")
	if (navigate_to == "under-construction") {
		alert("This section is under construction")
		return
	}
	if (navigate_to.length > 0) {
		turn_on_section(tabs[navigate_to])
	} else {
		$("body").css("background", "#c1c1c1")
		$("#app-content").toggle()
		$("#groups-tiles").toggle()
		
		$("#app-stats").toggle()
		$("#group-tabs").toggle()
	}
})

jsage.global_bus.subscribe(groupspy.messages.group_entered, window, function(group) {
	if ($("#app-content").css("display") == "none") {
		$("body").css("background", "#fff")
		$("#app-stats").toggle()
		$("#group-tabs").toggle()
		$("#groups-tiles").toggle()
		$("#app-content").toggle()	
	}
	$("#chosen-group-label")[0].innerHTML = group.alias
	cur_group = group.gid
	turn_on_section(cur_section)
})

jsage.global_bus.subscribe(groupspy.messages.groups_clashed, window, function() {
	$("#app-content").toggle()	
	$("#groups-tiles").toggle()
	$("#central-group-comparison").toggle()
	$("body").css("background", "#fff")
	turn_off_cur_central()
})

$("#group-comparison-close").bind("click", function() {
	$("#app-content").toggle()	
	$("#groups-tiles").toggle()
	console.log("X")
	$("#central-group-comparison").css("display", "none")
	$("body").css("background", "#c1c1c1")	
})

})

})