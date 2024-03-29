new Module('ui/operations-counter.js', ['jsage/eventbus.js', 'jsage/baseui.js', 'jsage/mixin.js'], function () {

console.log('Operations counter - group_spy main screen\'s component')

groupspy.OperationsCounter = new jsage.Class('OperationsCounter', [jsage.BaseUIObject, jsage.GlobalMessagingObject], {
	
	template: "<div data-tag='main' style='padding:5px;'><div style='width:43px; height:11px; margin-top: -2px; display:inline-block;' data-tag='picture'></div><div style='display:inline; font-size: 16px; margin-top:2px; margin-left:10px;' data-tag='counter'></div></div>",
	
	init: function(div) {
		this.elements = this.process_template(this.template)
		this.elements.picture.style.background = "url(static/" + ASSETS["img/ajax-loader.gif"] + ")"
		this.elements.main.style.display = 'none'
		div.appendChild (this.elements['main'])
		this.subscribe(groupspy.messages.active_ajax_count_changed, this.operations_count_changed)
		this.elements.counter.innerHTML = "10"
	},
	
	free: function() {
		this.free_GlobalMessagingObject()
	},
	
	operations_count_changed: function(value) {
		this.elements.counter.innerHTML = value.toString()
		this.elements.main.style.display = value > 0 ? 'block' : 'none'
	}
	
})

})