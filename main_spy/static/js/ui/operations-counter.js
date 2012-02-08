new Module('ui/operations-counter.js', ['lib/eventbus.js', 'lib/baseui.js', 'lib/mixin.js'], function () {

console.log('Operations counter - group_spy main screen\'s component')

groupspy.OperationsCounter = function(div) {
	this.init(div)
	jsage.eventbus_augmentation(this)
}

groupspy.OperationsCounter.prototype = {
	
	template: "<div data-tag='main'><div style='width:32px; height:32px; margin-top: -2px;' data-tag='picture'></div></div>",
	
	init: function(div) {
		this.elements = this.process_template(this.template)
		this.elements.picture.style.background = "url('" + PATH_TO_JAVASCRIPTS + "ui/ajax-loader.gif')"
		div.appendChild (this.elements['main'])
	},
	
	operations_count_changed: function() {
		
	}

}
jsage.extend(groupspy.OperationsCounter, jsage.BaseUIObject)
})