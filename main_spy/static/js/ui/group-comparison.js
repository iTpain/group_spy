new Module('ui/group-comparison.js', ['jsage/mixin.js', 'jsage/eventbus.js', 'jsage/event-dispatcher.js', 'jsage/charts/charts-aux.js', 'jsage/charts/charts-core.js'], function() {

var ages_stratas = [['0-11'], ['12-15'], ['16-18'], ['19-21'], ['22-24'], ['25-27'], ['28-30'], ['31-35'], ['36-45'], ['46-120']]

var DemogeoTableWidget = new jsage.Class('DemogeoTableWidget', [], {
	
	init: function(loader, div) {
		this.loader = loader
		this.div = $(div)[0]
		loader.add_listener('load', this, this.on_load)
	},
	
	on_load: function(data) {
		this.div.innerHTML = ''
		var table = $("<table style='text-align:center'></table>")[0]
		table.appendChild($("<tr><td style='width:10%'></td><td style='color:red'>" + find_group_by_id(this.g1).alias + "</td><td style='color:blue'>" + find_group_by_id(this.g2).alias + "</td></tr>")[0])
		for (var i = 0, l = ages_stratas.length; i < l; i++) {
			var value1 = ((this.find(data[0], ages_stratas[i]) || 0)).toPrecision(3) + "%"
			var value2 = ((this.find(data[1], ages_stratas[i]) || 0)).toPrecision(3) + "%"
			table.appendChild($("<tr><td>" + ages_stratas[i] + "</td><td>" + value1 + "</td><td>" + value2 + "</td></tr>")[0])
		}
		this.div.appendChild(table)
	},
	
	find: function(data, id) {
		for (var i = 0, l = data.length; i < l; i++) {
			if (data[i][0] == id)
				return data[i][1]
		}
		return 0
	},
	
	set_groups: function(g1, g2) {
		this.g1 = g1
		this.g2 = g2
		this.loader.load(g1, g2)
	}
	
})

var DemogeoChartWidget = new jsage.Class('DemogeoChartWidget', [], {
	
	init: function(loader, div) {
		this.loader = loader
		this.div = $(div)[0]
		loader.add_listener('load', this, this.on_load)
	},
	
	on_load: function() {
		
	},
	
	set_groups: function(g1, g2) {
		this.loader.load(g1, g2)
	}
		
})

var DemogeoLoader = new jsage.Class('DemogeoLoader', [jsage.EventDispatcher], {
	
	init: function() {
		this.init_EventDispatcher()
	},
	
	load: function(g1, g2) {
		var schema = {age: ages_stratas, education: [], sex: []}

		var time_now = Math.round(new Date().getTime() / 1000)
		var that = this
		if (g1 == this.prevg1 && g2 == this.prevg2)
			return
		this.prevg1 = g1
		this.prevg2 = g2
		$.ajax({
			url: '/group' + g1 + '/latest_demogeo_snapshot/' + time_now + '/',
			success: function(response) {
				var data1 = response.response.whole_group.demo
				$.ajax({
					url: '/group' + g2 + '/latest_demogeo_snapshot/' + time_now + '/',
					success: function(response) {
						var data2 = response.response.whole_group.demo
						that.dispatch_event('load', [absolute_to_percents_in_array(create_demo_stratas(data1, schema)), absolute_to_percents_in_array(create_demo_stratas(data2, schema))])
					}
				})
			}
		})
	}
	
})

var RadioChoiceWidget = new jsage.Class('RadioChoiceWidget', [jsage.EventDispatcher], {
	
	init: function(div, options, name) {
		var form = $("<form></form>")[0]
		div.appendChild(form)
		var elements = []
		for (var i = 0, l = options.length; i < l; i++) {
			var input = $("<div><input type='radio' name='" + name + "'>" + options[i].label + "</div>")[0]
			if (i == 0)
				input.childNodes[0].checked = true
			form.appendChild(input)
			input.data_id = options[i].data
			elements.push(input)
		}
		var that = this
		this.init_EventDispatcher()
		$(elements).bind('change', function(e) {
			that.dispatch_event('change', e.currentTarget.data_id)
		})
	}
	
})

var DynamicsChartWidget = new jsage.Class('DynamicsChartWidget', [], {
	
	init: function() {
		this.time_now = Math.round(new Date().getTime() / 1000)
		this.year_before = this.time_now - 364 * 24 * 3600
		this.series = []
		var radio_choice = RadioChoiceWidget.create($("#gc-dynamics-chart-filter")[0], [
			{label: 'Всего участников', data: 0},
			{label: 'Участники без аватара', data: 1},
			{label: 'Забаненные участники', data: 2},
			{label: 'Активные участники', data: 3},
			{label: 'Ядро аудитории', data: 4},
			{label: 'Снимок - активные посты', data: 5},
			{label: 'Снимок - лайки', data: 6},
			{label: 'Снимок - комментарии', data: 7},
			{label: 'Снимок - репосты', data: 8},
			{label: 'Финал - лайки', data: 9},
			{label: 'Финал - комментарии', data: 10},
			{label: 'Финал - репосты', data: 11}
		], 'group-comparison-dynamics-type')
		radio_choice.add_listener('change', this, this.on_filter_changed)
	},
	
	on_filter_changed: function(index) {
		var highchart = this.chart.chart
		for (var i = 0, l = this.chart.series_description.length; i < l; i++) {
			var sindex = this.chart.series_description[i].index
			if (sindex != index && sindex != index + l / 2) {
				highchart.series[sindex].hide()
			} else {
				highchart.series[sindex].show()
				highchart.options.navigator.baseSeries = sindex
			}
		}
		highchart.redraw()
	},
	
	build: function() {
		var time_filter = jsage.charts.DefaultTimeFilter.create(this.year_before, this.time_now)
		var filters = [time_filter]
		var finals_filters = [time_filter, { invalidating: function() {return true}, make_url_part: function() { return 'all'} }]
		this.url_templates = []
		this.built = true
		var series = []
		for (var i = 1; i < 3; i++) {
			var color = i == 1 ? "#ff0000" : "#0000ff"
			series = series.concat([
				{ color: color, inilabel: "Всего участников", id: "total_users", source: this.create_series('/group<GROUP_'+i+'_ID>/all_user_stats_snapshots/', 'total_users', filters) },
				{ color: color, inilabel: "Без аватара", id: "faceless_users", source: this.create_series('/group<GROUP_'+i+'_ID>/all_user_stats_snapshots/', 'faceless_users', filters) },
				{ color: color, inilabel: "Забаненные", id: "banned_users", source: this.create_series('/group<GROUP_'+i+'_ID>/all_user_stats_snapshots/', 'banned_users', filters) },
				{ color: color, inilabel: "Активные", id: "users_1", source: this.create_series('/group<GROUP_'+i+'_ID>/all_user_stats_snapshots/', 'users_1', filters) },
				{ color: color, inilabel: "Очень активные", id: "users_3", source: this.create_series('/group<GROUP_'+i+'_ID>/all_user_stats_snapshots/', 'users_3', filters) },
				{ color: color, inilabel: "Снимок - активные посты", id: "active_posts_count", source: this.create_series('/group<GROUP_'+i+'_ID>/all_social_stats_snapshots/', 'active_posts_count', filters) },
				{ color: color, inilabel: "Снимок - лайки", id: "active_posts_likes", source: this.create_series('/group<GROUP_'+i+'_ID>/all_social_stats_snapshots/', 'active_posts_likes', filters) },
				{ color: color, inilabel: "Снимок - комментарии", id: "active_posts_comments", source: this.create_series('/group<GROUP_'+i+'_ID>/all_social_stats_snapshots/', 'active_posts_comments', filters) },
				{ color: color, inilabel: "Снимок - репосты", id: "active_posts_reposts", source: this.create_series('/group<GROUP_'+i+'_ID>/all_social_stats_snapshots/', 'active_posts_reposts', filters) },
				{ color: color, inilabel: "Финал - лайки", id: "likes", source: this.create_series('/group<GROUP_'+i+'_ID>/all_social_stats_finals/', 'likes', finals_filters) },
				{ color: color, inilabel: "Финал - комментарии", id: "comments", source: this.create_series('/group<GROUP_'+i+'_ID>/all_social_stats_finals/', 'comments', finals_filters) },
				{ color: color, inilabel: "Финал - репосты", id: "reposts", source: this.create_series('/group<GROUP_'+i+'_ID>/all_social_stats_finals/', 'reposts', finals_filters) }
			])
		}
		this.chart = jsage.charts.DataChartPresentation.create(
			series,
			[groupspy.NormalizeDataTransformer.create(false), groupspy.SlidingAverageDataTransformer.create(true, 0.015)], 
			{ 
				title: '', 
				title_floating: true,
				container: "gc-dynamics-chart-container",
				width: 800,
				height: 500,
				legend_y: -420,
				legend_disabled: true,
				range_selected: 0,
				axis_x_min: this.year_before * 1000,
				axis_x_max: this.time_now * 1000
			},
			create_line_chart)
		this.on_filter_changed(0)
	},
	
	create_series: function(url, data_key, filters) {
		var series = jsage.charts.DataSeries.create(url, data_key, filters)
		this.url_templates.push(url)
		this.series.push(series)
		return series
	},
	
	set_groups: function(g1, g2) {
		if (!this.built)
			this.build()
		var alias1 = find_group_by_id(g1).alias
		var alias2 = find_group_by_id(g2).alias
		for (var i = 0, l = this.series.length; i < l; i++) {
			this.series[i].data_url = this.url_templates[i].replace('<GROUP_1_ID>', g1).replace('<GROUP_2_ID>', g2)
		}
		var highchart = this.chart.chart
		for (i = 0, l = this.chart.series_description.length; i < l; i++) {
			var series_desc = this.chart.series_description[i]
			highchart.series[series_desc.index].name = (i < l / 2 ? alias1 : alias2) + " " + series_desc.inilabel
		}
		//highchart.redraw()
		this.chart.fetch_chart_data()
		//this.chart.reset_axis_extremes()
	}
		
})

var ComparisonWidget = new jsage.Class('ComparisonWidget', [], {
	
	init: function(window_id) {
		this.window_id = window_id
		var demogeo_loader = DemogeoLoader.create()
		this.widgets = [DynamicsChartWidget.create('#gc-dynamics-chart-container'), DemogeoChartWidget.create(demogeo_loader, '#gc-demogeo-chart'),DemogeoTableWidget.create(demogeo_loader, '#gc-demogeo-table')]
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
