new Module('ui/main-charts-frame/stats-snapshot-widget.js', ['jsage/mixin.js'], function() {

var snapshot_decoration = {
	"banned_users": {
		title: "Забаненные участники",
		addition: function (data) {return " <span class='snapshot-cell-additional-info'>(" + ((100 * data.banned_users.latest / data.total_users.latest).toPrecision(2)) + "%)</span>"},
		reverse_color_delta: true
	},
	"faceless_users": {
		title: "Участники без аватара",
		addition: function (data) {return " <span class='snapshot-cell-additional-info'>(" + ((100 * data.faceless_users.latest / data.total_users.latest).toPrecision(2)) + "%)</span>"},
		reverse_color_delta: true
	},
	"total_users": {
		title: "Всего участников",
		reverse_color_delta: false
	},
	"active_posts_likes": {
		title: "Лайки (всего по а.п.)",
		addition: function (data) {return " <span class='snapshot-cell-additional-info'>(" + (Math.round(data.active_posts_likes.latest / data.active_posts_count.latest)) + " в ср.)</span>"},
		reverse_color_delta: false
	},
	"active_posts_reposts": {
		title: "Репосты (всего по а.п.)",
		addition: function (data) {return " <span class='snapshot-cell-additional-info'>(" + (Math.round(data.active_posts_reposts.latest / data.active_posts_count.latest)) + " в ср.)</span>"},
		reverse_color_delta: false
	},
	"active_posts_comments": {
		title: "Комментарии (всего по а.п.)",
		addition: function (data) {return " <span class='snapshot-cell-additional-info'>(" + (Math.round(data.active_posts_comments.latest / data.active_posts_count.latest)) + " в ср.)</span>"},
		reverse_color_delta: false
	},	
	"active_posts_count": {
		title: "Активные посты",
		reverse_color_delta: false
	},
	"users_1": {
		title: "Активные пользователи",
		addition: function (data) {return " <span class='snapshot-cell-additional-info'>(" + (Math.round(100 * data.users_1.latest / (data.total_users.latest - data.banned_users.latest))) + "%)</span>"},
		reverse_color_delta: false
	},	
	"users_3": {
		title: "Ядро аудитории",
		addition: function (data) {return " <span class='snapshot-cell-additional-info'>(" + (Math.round(100 * data.users_3.latest / (data.total_users.latest - data.banned_users.latest))) + "%)</span>"},
		reverse_color_delta: false
	}				
}

groupspy.StatsSnapshotWidget = new jsage.Class('StatSnapshotWidget', [], {
	
	init: function() {
		this.ajax_token = 0
	},
	
	set_group: function(gid) {
		var div = $("#group_stats_snapshot")[0]
		div.innerHTML = ''
		var token = ++this.ajax_token
		var that = this
		$.ajax ({		
			url: '/group' + gid + '/snapshot/',
			success: function(data) {
				if (token != that.ajax_token)
					return
				data = data.response
				var order = ["total_users", "faceless_users", "banned_users", "BREAK", "active_posts_likes", "active_posts_reposts", "active_posts_comments", "active_posts_count", "users_1", "users_3"]
				current_div = $("<div style='clear:both'></div>")[0]
				div.appendChild (current_div)
				for (var i = 0, l = order.length; i < l; i++) {
					var key = order[i]
					if (key == "BREAK") {
						current_div = $("<div style='clear:both'></div>")[0]
						div.appendChild (current_div)
					} else {
						cell = $("<div class='snapshot-cell'></div>")[0]
						var dec = snapshot_decoration[key] 
						
						var c1 = dec.reverse_color_delta ? "#ff0000": "#55aa55"
						var c2 = dec.reverse_color_delta ? "#55aa55" : "#ff0000" 
						if (data[key].week_ago != "undefined") {
							var color = data[key].latest >= data[key].week_ago ? c1 : c2
						} else if (data[key].day_ago != "undefined") {
							color = data[key].latest >= data[key].day_ago ? c1 : c2
						} else {
							color = '#000000'
						}
						
						var title = ''
						function create_title_part(label, now, prev) {
							if (prev == "undefined") {
								percentage = "no data"
							} else {
								var p = 100 * (now - prev) / prev
								if (p > 0)
									var percentage = "+" + p.toPrecision(4) + "%"
								else 
									percentage = p.toPrecision(4) + "%"
							}
							return label + ": " + percentage + "  "
						}
						title += create_title_part("День назад", data[key].latest, data[key].day_ago)
						title += create_title_part("Неделю назад", data[key].latest, data[key].week_ago)
						title += create_title_part("Месяц назад", data[key].latest, data[key].month_ago)
						
						cell.innerHTML = dec.title + ": <span title='" + title + "' class='snapshot-cell-value' style='color:" + color + "'>" + data[key].latest + "</span>"
						if (dec.addition) {
							cell.innerHTML += dec.addition(data)
						}
						current_div.appendChild(cell)
					}			
				}
			}
		})
	}
})
	
})
