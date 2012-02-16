new Module('ui/main-charts-frame/main-charts-frame.js', ['jsage/eventbus.js', 'ui/main-charts-frame/main-charts-widget.js', 
														 'ui/main-charts-frame/stats-snapshot-widget.js', 'ui/main-charts-frame/demogeo-snapshot-widget.js'], function () {
$(document).ready(function() {

groupspy.BaseChartsFrame = new jsage.Class('BaseChartsFrame', [jsage.GlobalMessagingObject], {
	
	init: function(widgets_classes) {
		this.widgets_classes = widgets_classes
		this.built = false
		this.subscribe(groupspy.messages.group_frame_activate, this.on_activate)

	},
	
	on_activate: function(group_id) {
		if (!this.built) {
			this.widgets = []
			for (var i = 0, l = this.widgets_classes.length; i < l; i++)
				this.widgets[i] = this.widgets_classes[i].create()
			this.built = true
		}
		for (var i = 0, l = this.widgets.length; i < l; i++) {
			this.widgets[i].set_group(group_id)
		}
	}
	
})

var frame = groupspy.BaseChartsFrame.create([groupspy.StatsSnapshotWidget, groupspy.MainChartsWidget, groupspy.DemogeoSnapshotWidget])
	
})
})
