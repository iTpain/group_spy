new Module('ui/main-screen.js', ['jsage/eventbus.js', 'ui/operations-counter.js', 'utils/async-operations.js', 'ui/group-comparison.js', 'ui/groups.js'], function() {

console.log("Main screen - group spy")

$(document).ready(function () {
	
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

})

})