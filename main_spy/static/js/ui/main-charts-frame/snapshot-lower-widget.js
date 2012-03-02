new Module('ui/main-charts-frame/snapshot-lower-widget.js', ['jsage/mixin.js'], function() {
	
$(document).ready(function() {

groupspy.SnapshotLowerWidget = new jsage.Class("SnapshotLowerWidget", [], {
	
	init: function() {
		var that = this;
		$(".gcp-datepicker").datepicker({maxDate: "+0D", onSelect: function() { that.refresh() }, changeMonth: true, changeYear: true})
		$(".gcp-datepicker").datepicker($.datepicker.regional["ru"])
			
		var oldDate = new Date()
		oldDate.setFullYear(2009)
		$("#gcp-time-end").datepicker("setDate", new Date())
		$("#gcp-time-start").datepicker("setDate", oldDate)		
	},
	
	set_group: function(gid) {
		this.group_id = gid
		this.refresh()
	},
	
	refresh: function() {
		if (this.group_id == null)
			return;
		var time_start = $("#gcp-time-start").datepicker("getDate")
		var time_end = $("#gcp-time-end").datepicker("getDate")
		$.ajax({
			url: "/group" + this.group_id + "/cumulative_post_stats/" + Math.round(time_start.getTime() / 1000) + "/" + Math.round(time_end.getTime() / 1000) + "/",
			success: function(response) {
				var data = response.response
				$("#gcp-posts-count")[0].innerHTML = data.posts_count
				var social_actions_count = data.social_actions_count
				$("#gcp-sa-count")[0].innerHTML = social_actions_count
				var params = [["posts_count", "#gcp-per-post-capita"], ["group_users_count", "#gcp-per-user-capita"], ["days_count", "#gcp-per-day-capita"]]
				for (var i = 0, l = params.length; i < l; i++) {
					var value = social_actions_count / data[params[i][0]]
					var rounded_value = value
					var current_mul = 1
					while (rounded_value < 1) {
						rounded_value *= 10
						current_mul *= 10
					}
					rounded_value = Math.round(rounded_value)
					var elem = $(params[i][1])[0]
					var html = ''
					if (value >= 0.0001) {
						var epic_value = Math.round(value * 100) / 100
						if (epic_value == 0) 
							epic_value = Math.round(value * 10000) / 10000
						html += String(epic_value)
					} else {
						html += String(rounded_value) + " на " + String(current_mul)
					}
					elem.innerHTML = html
				}
			}
		})		
	}
	
})

})
})