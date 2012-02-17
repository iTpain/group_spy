new Module('ui/group-comparison.js', ['jsage/mixin.js', 'jsage/eventbus.js', 'ui/charts-aux.js', 'ui/charts-core.js'], function() {

var DemogeoTableWidget = new jsage.Class('DemogeoTableWidget', [], {
	
	set_groups: function(g1, g2) {
		
	}
	
})

var DemogeoChartWidget = new jsage.Class('DemogeoChartWidget', [], {
	
	set_groups: function(g1, g2) {
		
	}
		
})

var DynamicsChartWidget = new jsage.Class('DynamicsChartWidget', [], {
	
	init: function() {
		this.time_now = Math.round(new Date().getTime() / 1000)
		this.year_before = this.time_now - 364 * 24 * 3600
	},
	
	build: function() {
		this.built = true
		this.chart = groupspy.DataChartPresentation.create([
				{ color: '#0000ff', label: "Всего участников", id: "total_users" },
				{ color: '#ff6600', label: "Без аватара", id: "faceless_users" },
				{ color: '#ff0000', label: "Забаненные", id: "banned_users" },
				{ color: '#44aa44', label: "Активные", id: "users_1" },
				{ color: '#22ff22', label: "Очень активные", id: "users_3" }
			],
			[groupspy.NormalizeDataTransformer.create(false), groupspy.SlidingAverageDataTransformer.create(false, 0.05)], 
			[groupspy.DefaultTimeFilter.create(this.month_before, this.time_now)],
			{ 
				title: '', 
				title_floating: true,
				container: "gc-dynamics-chart-container",
				width: 800,
				height: 500,
				legend_y: -420,
				range_selected: 0,
				axis_x_min: this.year_before * 1000,
				axis_x_max: this.time_now * 1000
			},
			create_line_chart,
			'/group<GROUP_1_ID>/all_user_stats_snapshots/')
		this.url_templates = ['/group<GROUP_1_ID>/all_user_stats_snapshots/']
	},
	
	set_groups: function(g1, g2) {
		if (!this.built)
			this.build()
		for (var i = 0, l = this.url_templates.length; i < l; i++) {
			this.chart.data_url = this.url_templates[i].replace('<GROUP_1_ID>', g1).replace('<GROUP_2_ID>', g2)
		}
		console.log(this.chart.data_url)
		this.chart.reset_axis_extremes()
		this.chart.fetch_chart_data()
	}
		
})

var ComparisonWidget = new jsage.Class('ComparisonWidget', [], {
	
	init: function(window_id) {
		this.window_id = window_id
		this.widgets = [DynamicsChartWidget.create('id-of-dynamics'), DemogeoChartWidget.create('id-of-demogeo-chart'),DemogeoTableWidget.create('id-of-demogeo-table')]
	},
	
	open: function(gid1, gid2) {
		$.openDOMWindow({
			windowSourceID: this.window_id,
			width: 1024,
			height: 600
		})
		$("#gc-alias-1")[0].innerHTML = find_group_by_id(gid1).alias
		$("#gc-alias-2")[0].innerHTML = find_group_by_id(gid2).alias
		
		for (var i = 0, l = this.widgets.length; i < l; i++)
			this.widgets[i].set_groups(gid1, gid2)
	}
	
})

groupspy.GroupComparisonBase = new jsage.Class('GroupComparisonBase', [jsage.GlobalMessagingObject], {
	
	init: function() {
		this.subscribe(groupspy.messages.group_added, this.on_group_added)
		this.discover_group_divs()
		this.comparison_widget = ComparisonWidget.create('#group-comparison')
	},
	
	discover_group_divs: function() {
		var divs = $("div.group_header")
		this.make_draggable(divs)
		this.make_droppable(divs)
	},
	
	make_draggable: function(elements) {
		$(elements).draggable({
			containment: "#groups-list",
			helper: function(event) {
				var target = event.currentTarget
				var div = $("<div class='group_header emphasize'>" + target.childNodes[0].innerHTML + "</div>")[0]
				div.group_id = target.getAttribute("data-group-id")
				return div
			}
		})
	},
	
	make_droppable: function(elements) {
		var that = this
		$(elements).droppable({
			accept: 'div.group_header',
			drop: function(e) {
				var id1 = e.target.getAttribute("data-group-id")
				var id2 = e.toElement.group_id
				that.comparison_widget.open(id1, id2)
			}
		})
	},
	
	on_group_added: function(el) {
		this.make_draggable(el.childNodes[0])
		this.make_droppable(el.childNodes[0])
	}
	
	
})
	
	
})
