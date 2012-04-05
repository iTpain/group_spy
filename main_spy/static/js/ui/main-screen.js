new Module('ui/main-screen.js', ['jsage/eventbus.js', 'ui/operations-counter.js', 'utils/async-operations.js', 'ui/group-comparison.js', 'ui/groups.js'], function() {

console.log("Main screen - group spy")

// operations counter
var opCounter1 = groupspy.OperationsCounter.create($("#operations-counter")[0])

// errors panel
var errorsPanel = jsage.ErrorPanel.create(10, 5000, [groupspy.messages.ajax_failure])
$("body")[0].appendChild(errorsPanel.elements.container)

// group comparison
var group_comparison = groupspy.GroupComparisonBase.create()

// help
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

// screen size adjustment
var adjust_elements = function () {
	var w = $(window).width()
	var h = $(window).height()
	$("#control_div").css("height", Math.max(640, h) + "px")	
	$("#groups-tiles").css("width", (w - 250) + "px")
}
$(window).resize(function () {
	adjust_elements()
})	
adjust_elements()
return

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

})