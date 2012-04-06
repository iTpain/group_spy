new Module('ui/groups.js', ['ui/sections-navigation.js', 'jsage/layouts/living-tiles.js', 'jsage/charts/sparkline.js', 'jsage/mvc.js', 'jsage/baseui.js'], function () {
$(document).ready(function () {

/*
 * view classes 
 */

var GroupEditor = new jsage.Class('GroupEditor', [jsage.BaseView], {
	
	init: function() {
		this.init_BaseView()
		var that = this
		$("#app-update-group").bind('click', function() { that.on_update_click() })
		$("#app-delete-group").bind('click', function() { that.on_delete_click() })
	},
	
	on_update_click: function() {
		var data = this.data_providers["default"].present()
		update_group_command(data.gid, $("#group_agency_input")[0].value, $("#group_brand_input")[0].value, this.data_providers["default"])
		$.closeDOMWindow({
			windowSourceID: '#group_info_updater'
		})
	},
	
	on_delete_click: function() {
		var data = this.data_providers["default"].present()
		delete_group_command(data.gid, this.data_providers["default"])
		this.unbind_provider("default")
		$.closeDOMWindow({
			windowSourceID: '#group_info_updater'
		})
	},
	
	on_data_update: function(provider) {
		if (provider == null)
			return
		var data = provider.present()
		$("#group_updater_header")[0].innerHTML = data.alias
		$("#group_agency_input")[0].value = data.agency
		$("#group_brand_input")[0].value = data.brand		
	}
	
})
var group_editor = GroupEditor.create()

// for select box
var GroupBoxCell = new jsage.Class('GroupBoxCell', [jsage.BaseUIObject, jsage.BaseView, jsage.GlobalMessagerObject], {
	
	template: "<div data-tag='container'></div>",
	
	init: function() {
		this.elements = this.process_template(this.template)
		this.root = this.elements.container
		this.init_BaseView() 
		var that = this	
		this.click_handler = function() { that.on_click() }	
		$(this.root).bind('click', this.click_handler)
	},
	
	on_data_update: function(provider) {
		this.elements.container.innerHTML = provider.present().alias
	},
	
	on_click: function() {
		$("#groups-box").toggle()
		this.trigger(groupspy.messages.group_entered, this.data_providers["default"].present())
	},
	
	free: function() {
		$(this.root).unbind('click', this.click_handler)
		this.free_BaseView()
	}
	
})

var dragging_id = null
var GroupCell = new jsage.Class('GroupCell', [jsage.BaseUIObject, jsage.BaseView, jsage.GlobalMessagerObject], {
	
	template: "<div class='group-tile' data-tag='container'><div class='inner-group-tile'>" +
			  	"<div class='group-tile-header' data-tag='alias'></div><div class='group-tile-attr' data-tag='brand'></div><div class='group-tile-attr' data-tag='agency'></div>" +
			  	"<div data-tag='sparklines'>" +
			  	"<div style='margin-top:10px' data-tag='empty'>Нет данных для этой группы</div>" +
			  	"<div data-tag='full' style='display:none' class='group-tile-sparkline'>" +
			  	"<table><tr><td>" +
			  	"<div>участники</div><table><tr><td><div data-tag='total_users_series'></div></td><td><div data-tag='total_users_series_v'></div><div data-tag='total_users_series_d'></div></td></tr></table>" +
			  	"</td><td class='group-tile-sparklines-second-column'>" +
			  	"<div>забаненные</div><table><tr><td><div data-tag='banned_users_series'></div></td><td><div data-tag='banned_users_series_v'></div><div data-tag='banned_users_series_d'></div></td></tr></table>" +
			  	"</td><tr><td>" +
			  	"<div>активные</div><table><tr><td><div data-tag='active_users_series'></div></td><td><div data-tag='active_users_series_v'></div><div data-tag='active_users_series_d'></div></td></tr></table>" +
			  	"</td><td class='group-tile-sparklines-second-column'>" + 
			  	"<div>соц. действия</div><table><tr><td><div data-tag='sa_series'></div></td><td><div data-tag='sa_series_v'></div><div data-tag='sa_series_d'></div></td></tr></table>" +
			  	"</td></tr></table>" +
			  	"</div></div></div>",
			  	
	sparklines: [["Участники", "total_users_series", 1], ["Забаненные", "banned_users_series", -1], ["Активные", "active_users_series", 1], ["Соц. действия", "sa_series", 1]],
	
	init: function() {
		this.elements = this.process_template(this.template)
		this.root = this.elements.container
		this.init_BaseView() 
		var that = this
		this.dblclick_handler = function() { that.on_dblclick() }
		this.click_handler = function() { that.on_click() }
		$(this.root).bind('dblclick', this.dblclick_handler)
		$(this.root).bind('click', this.click_handler)
		this.make_draggable(this.root)
		this.make_droppable(this.root)
		this.create_sparklines()
	},
	
	create_sparklines: function() {
		this.created_sparklines = {}
		for (var i = 0, l = this.sparklines.length; i < l; i++) {
			var desc = this.sparklines[i]
			this.created_sparklines[desc[1]] = jsage.charts.Sparkline.create(this.elements[desc[1]], 110, 30, 0.3)
			this.created_sparklines[desc[1]].reverse_direction = desc[2]
		}
	},
	
	make_draggable: function(elements) {
		var that = this
		$(elements).draggable({
			containment: "body",
			helper: function(event) {
				var target = event.currentTarget
				var data = that.data_providers["default"].present()
				var div = $("<div class='lightblue boldy'>" + data.alias + "</div>")[0]
				dragging_id = data
				return div
			}
		})
	},
	
	make_droppable: function(elements) {
		var that = this
		$(elements).droppable({
			drop: function(e) {
				var g1 = that.data_providers["default"].present()
				that.trigger(groupspy.messages.groups_clashed, {g1: g1, g2: dragging_id})
			}
		})
	},
	
	on_data_update: function(provider) {
		var data = provider.present()
		this.elements.alias.innerHTML = data.alias
		this.elements.brand.innerHTML = data.brand
		$(this.elements.brand).css("display", data.brand.length > 0 ? "inline-block" : "none")
		this.elements.agency.innerHTML = data.agency
		$(this.elements.agency).css("display", data.agency.length > 0 ? "inline-block" : "none")
		this.gid = data.gid
		var sparkline_data_here = "sparklines" in data
		$(this.elements.empty).css("display", sparkline_data_here ? "none" : "block")
		$(this.elements.full).css("display", !sparkline_data_here ? "none" : "block")
		if (sparkline_data_here) {
			var sparklines = data["sparklines"]
			for (var e in sparklines)
				this.refresh_sparkline(e, sparklines[e], this.created_sparklines[e])
		}
	},
	
	refresh_sparkline: function(key, data, sparkline) {
		if (("first" in data) && ("last" in data)) {
			var percentage = (data.last[1] - data.first[1]) / data.first[1]
			sparkline.set_graph_color(percentage * sparkline.reverse_direction >= 0 ? "#008800" : "#ff0000")
			sparkline.set_series(data.series)
			this.elements[key + "_v"].innerHTML = (percentage < 0 ? "" : "+") + (percentage * 100).toPrecision(3) +"%"
		}
	},
	
	on_dblclick: function() {
		group_editor.bind_provider("default", this.data_providers["default"])
		$.openDOMWindow({
			windowSourceID: '#group_info_updater',
			height: 150
		})
	},
	
	on_click: function() {
		this.trigger(groupspy.messages.group_entered, this.data_providers["default"].present())
	},
	
	free: function() {
		$(this.root).unbind('dblclick', this.dblclick_handler)
		$(this.root).unbind('click', this.click_handler)
		this.free_BaseView()
	}
	
})

/*
 * structure
 */

var id_counter = 0
var group_set = jsage.EntitySet.create('group')
var group_collection = jsage.ArrayCollection.create(group_set)

/*
 * gui
 */

var group_tiles = jsage.BaseList.create($("#groups-tiles")[0], GroupCell)
jsage.layouts.LivingTiles.create($("#groups-tiles")[0], true, 0.15, 30, 30, ["lightblue"])
var group_select = jsage.BaseList.create($("#groups-box")[0], GroupBoxCell)
$("#chosen-group-label").bind("click", function() {
	$("#groups-box").toggle()
})

group_tiles.bind_provider("default", group_collection)
group_select.bind_provider("default", group_collection)


/*
 * commands
 */
var add_group_command = function() {
	gid = $("#add-group-id")[0].value
	if (gid.length == 0)
		return;
	ajax_operations_manager.do_operation(
		'/group' + gid + '/add/', 'get', null,
		function (res) {
			if (res.errors.length > 0) {
				return res.errors
			} else {
				res = res.response
				var new_group = group_set.create_entity(id_counter++, {gid: res.gid, alias: res.alias, agency: '', brand: ''})
				group_collection.add(new_group)
				return true
			}
		},
		function (err) { },
		{ toString: function () { return 'Add-group ' + gid} }
	)
}

var update_group_command = function(gid, agency, brand, group) {
	ajax_operations_manager.do_operation(
		'/group' + gid + '/update_info/', 'post', {agency: encodeURIComponent(agency), brand: encodeURIComponent(brand)},
		function (data) {
			group.mset({agency: agency, brand: brand})
			return true
		}
	)	
}

var delete_group_command = function(gid, entity) {
	if (confirm('Вы уверены, что хотите удалить группу?'))
		ajax_operations_manager.do_operation(
			'/group' + gid + '/delete/', 'get', null,
			function (res) {
				if (res.errors.length > 0) {
					return res.errors
				} else {
					group_set.remove_by_ids(entity.id, 1)
					return true
				}
			},
			function (err) { },
			{ toString: function () { return 'Delete-group ' + gid} }
		)	
}

/*
 * initialization
 */
var date_now = new Date()
date_now.setSeconds(0)
date_now.setMinutes(0)
date_now.setHours(0)
date_now.setMilliseconds(0)
var time_now = Math.round(date_now.getTime() / 1000)
var month_ago = time_now - 31 * 24 * 3600

var make_series_dict = function(series) {
	var sparkline_series = []
	for (var i = 0, l = series.length; i < l; i++)
		sparkline_series[i] = series[i][1]
	var dict = {series: sparkline_series}
	if (series.length >= 2) {
		dict.last = series[series.length - 1]
		dict.first = series[0]
	}
	return dict
}

$.ajax({
	url: '/groups/get/',
	success: function(response) {
		var groups = response.response
		for (var i = 0, l = groups.length; i < l; i++) {
			var g = groups[i]
			var new_group = group_set.create_entity(id_counter++, {gid: g.gid, alias: g.alias, brand: decodeURIComponent(g.brand), agency: decodeURIComponent(g.agency)})
			group_collection.add(new_group)
			// download data for sparklines
			var on_success = (function(entity) {
				return function (response) {
					var r = response.response
					var users_1 = r.users_1.series
					var users_3 = r.users_3.series
					var active_users_series = []
					for (var i = 0, l = users_1.length; i < l; i++)
						active_users_series[i] = [users_1[i][0], users_1[i][1] + users_1[i][1]]
					var dict = {
						total_users_series: make_series_dict(r.total_users.series),
						banned_users_series: make_series_dict(r.banned_users.series),
						active_users_series: make_series_dict(active_users_series)
					}
					var sparklines = entity.get("sparklines") || {}
					for (var e in dict)
						sparklines[e] = dict[e]
					entity.set("sparklines", sparklines)
				}
			})(new_group)
			$.ajax({
				url: 'group' + g.gid + '/all_user_stats_snapshots/' + month_ago + '/' + time_now + '/',
				success: on_success
			})
			var on_success_sa = (function(entity) {
				return function (response) {
					var r = response.response
					var s1 = r.active_posts_likes.series
					var s2 = r.active_posts_reposts.series
					var s3 = r.active_posts_comments.series
					var sa_series = []
					for (var i = 0, l = s1.length; i < l; i++)
						sa_series[i] = [s1[i][0], s1[i][1] + s2[i][1] + s3[i][1]]
					var sparklines = entity.get("sparklines") || {}
					sparklines.sa_series = make_series_dict(sa_series)
					entity.set("sparklines", sparklines)
				}
			})(new_group)
			$.ajax({
				url: 'group' + g.gid + '/all_social_stats_snapshots/' + month_ago + '/' + time_now + '/',
				success: on_success_sa				
			})
		}
	}
})

$("#add-group-div").bind("click", function () {
	add_group_command()
})
	
})	
})
