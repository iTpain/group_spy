new Module('ui/main-charts-frame/main-charts-widget.js', ['ui/charts-widget.js', 'ui/charts-creator.js'], function() {

groupspy.MainChartsWidget = new jsage.Class('MainChartsWidget', [groupspy.ChartsWidget], {
	
	init: function() {
		this.chart_creators = [this.create_user_stats_chart]
		this.init_ChartsWidget()
	},
	
	create_user_stats_chart: function() {
		var filters = [jsage.charts.DefaultTimeFilter.create(this.three_months_before, this.time_now, true)]
		return jsage.charts.DataChartPresentation.create([
				{ color: '#0000ff', label: "Всего участников", id: "total_users", source: this.create_series('/group<GROUP_ID>/all_user_stats_snapshots/', 'total_users', filters)},
				{ color: '#ff6600', label: "Без аватара", id: "faceless_users", source: this.create_series('/group<GROUP_ID>/all_user_stats_snapshots/', 'faceless_users', filters) },
				{ color: '#ff0000', label: "Забаненные", id: "banned_users", source: this.create_series('/group<GROUP_ID>/all_user_stats_snapshots/', 'banned_users', filters) },
				{ color: '#44aa44', label: "Активные", id: "users_1", source: this.create_series('/group<GROUP_ID>/all_user_stats_snapshots/', 'users_1', filters) },
				{ color: '#22ff22', label: "Очень активные", id: "users_3", source: this.create_series('/group<GROUP_ID>/all_user_stats_snapshots/', 'users_3', filters) }
			],
			[groupspy.NormalizeDataTransformer.create(false), groupspy.SlidingAverageDataTransformer.create(false, 0.05)], 
			{ 
				title: 'Общая статистика по участникам', 
				container: "group_users_chart",
				width: 800,
				height: 500,
				title_x: -10,
				title_margin: 50,
				legend_y: -420,
				range_selected: 0,
				axis_x_min: this.three_months_before * 1000,
				axis_x_max: this.time_now * 1000
			},
			create_line_chart, jsage.charts.date_transformer
		)		
	}
	
})

})