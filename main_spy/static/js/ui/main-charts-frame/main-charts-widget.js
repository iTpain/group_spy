new Module('ui/main-charts-frame/main-charts-widget.js', ['jsage/baseui.js', 'jsage/charts/charts-core.js', 'jsage/charts/charts-aux.js', 'ui/charts-creator.js'], function() {

groupspy.MainChartsWidget = new jsage.Class('MainChartsWidget', [], {
	
	init: function() {
		this.time_now = Math.round(new Date().getTime() / 1000)
		this.month_before = this.time_now - 31 * 24 * 3600
		this.three_months_before = this.time_now - 93 * 24 * 3600
		this.year_before = this.time_now - 364 * 24 * 3600
		this.charts = []
		this.series = []
		this.create_charts()
	},
	
	set_group: function(gid) {
		for (var i = 0, l = this.series.length; i < l; i++) {
			this.series[i].data_url = this.url_templates[i].replace('<GROUP_ID>', gid.toString())
			this.series[i].filters[0].reset()
			this.series[i].fetch_data()			
		}
		for (i = 0, l = this.charts.length; i < l; i++)
			this.charts[i].reset_axis_extremes()
	},
	
	create_series: function(url, data_key, filters) {
		var series = jsage.charts.DataSeries.create(url, data_key, filters)
		this.series.push(series)
		return series
	},
	
	create_user_stats_chart: function() {
		var filters = [jsage.charts.DefaultTimeFilter.create(this.month_before, this.time_now)]
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
				axis_x_min: this.month_before * 1000,
				axis_x_max: this.time_now * 1000
			},
			create_line_chart
		)		
	},
	
	create_social_stats_snapshots_chart: function() {
		var filters = [jsage.charts.DefaultTimeFilter.create(this.month_before, this.time_now)]
		return jsage.charts.DataChartPresentation.create([
				{ color: '#00ff00', label: "Всего активных постов", id: "active_posts_count", source: this.create_series('/group<GROUP_ID>/all_social_stats_snapshots/', 'active_posts_count', filters) },
				{ color: '#ff0000', label: "Всего лайков для а.п.", id: "active_posts_likes", source: this.create_series('/group<GROUP_ID>/all_social_stats_snapshots/', 'active_posts_likes', filters) },
				{ color: '#ff6600', label: "Всего комментариев для а.п.", id: "active_posts_comments", source: this.create_series('/group<GROUP_ID>/all_social_stats_snapshots/', 'active_posts_comments', filters) },
				{ color: '#0000ff', label: "Всего репостов для а.п.", id: "active_posts_reposts", source: this.create_series('/group<GROUP_ID>/all_social_stats_snapshots/', 'active_posts_reposts', filters) }
			],
			[groupspy.NormalizeDataTransformer.create(false), groupspy.SlidingAverageDataTransformer.create(true, 0.035)],
			{
				title: 'Снимки активности участников', 
				container: "group_activity_chart",
				width: 800,
				height: 500,
				title_x: -10,
				title_margin: 50,
				legend_y: -420,
				range_selected: 0,
				axis_x_min: this.month_before * 1000,
				axis_x_max: this.time_now * 1000		
			},
			create_line_chart
		)		
	},
	
	create_social_stats_finals_chart: function() {
		var content_types = ['app', 'audio', 'doc', 'graffiti', 'link', 'no_attachment', 'note', 'page', 'photo', 'poll', 'posted_photo', 'video']
		var content_types_labels = ['Приложение', "Аудио", "Документ", "Граффити", "Ссылка", "Без вложений", "Заметка", "Страница", "Фото", "Опрос", "Фото(к)", "Видео"] 
		var filters = [jsage.charts.DefaultTimeFilter.create(this.year_before, this.time_now), groupspy.MultiChoiceFilter.create(content_types, content_types_labels)]
		var chart = jsage.charts.DataChartPresentation.create([
				{ color: '#ff0000', label: "лайки", id: "likes", source: this.create_series('/group<GROUP_ID>/all_social_stats_finals/', 'likes', filters) },
				{ color: '#ff6600', label: "комментарии", id: "comments", source: this.create_series('/group<GROUP_ID>/all_social_stats_finals/', 'comments', filters) },
				{ color: '#0000ff', label: "репосты", id: "reposts", source: this.create_series('/group<GROUP_ID>/all_social_stats_finals/', 'reposts', filters) }
			],
			[groupspy.AverageDataTransformer.create(false), groupspy.NormalizeDataTransformer.create(false), groupspy.SlidingAverageDataTransformer.create(true, 0.02)],
			{
				title: 'Историческая статистика результативности постов', 
				container: "group_social_activity_dynamics",
				width: 800,
				height: 500,
				title_x: -10,
				title_margin: 50,
				legend_y: -420,
				range_selected: 0,
				axis_x_min: this.year_before * 1000,
				axis_x_max: this.time_now * 1000		
			},
			create_line_chart
		)	
		filters[1].set_chart(chart)
		return chart	
	},
	
	create_strata_charts: function() {
		var strata_charts = [
			{
				container: 'social_activity_hourly_stratified',
				title: 'Внутридневная результативность постов',
				strata_type: 'intraday_stratify',
				strata_labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
			},
			{
				container: 'social_activity_daily_stratified',
				title: 'Внутринедельная результативность постов',
				strata_type: 'intraweek_stratify',
				strata_labels: [0, 1, 2, 3, 4, 5, 6]
			},
			{
				container: 'social_activity_content_stratified',
				title: 'Результативность постов по типу приложений',
				strata_type: 'content_stratify',
				strata_labels: ['app', 'audio', 'doc', 'graffiti', 'link', 'no_attachment', 'note', 'page', 'photo', 'poll', 'posted_photo', 'video']
			}		
		]
		var charts = []
		for (var i = 0, l = strata_charts.length; i < l; i++) {
			var params = {
				width: 800,
				height: 500,
				title_x: -10,
				title_margin: 50
			}
			params.container = strata_charts[i].container
			params.title = strata_charts[i].title
			params.axis_x_categories = strata_charts[i].strata_labels
			var filters = [jsage.charts.DefaultTimeFilter.create(this.month_before, this.time_now)]
			charts.push(jsage.charts.DataChartPresentation.create(
				[
					{ label: "лайки", name: "лайки", id: "active_posts_likes", source: this.create_series('/group<GROUP_ID>/' + strata_charts[i].strata_type + '/', 'active_posts_likes', filters)},
					{ label: "комментарии", name: "комментарии", id: "active_posts_comments", source: this.create_series('/group<GROUP_ID>/' + strata_charts[i].strata_type + '/', 'active_posts_comments', filters) },
					{ label: "репосты", name: "репосты", id: "active_posts_reposts", source: this.create_series('/group<GROUP_ID>/' + strata_charts[i].strata_type + '/', 'active_posts_reposts', filters) }
				],
				[groupspy.AverageDataTransformer.create(false), groupspy.NormalizeDataTransformer.create(false)],
				params,
				create_column_chart
			))
		}
		return charts		
	},
	
	accept_charts: function(charts) {
		if (!(charts instanceof Array))
			charts = [charts]
		for (var i = 0, l = charts.length; i < l; i++)
			this.charts.push(charts[i])
	},
	
	create_charts: function() {
		this.accept_charts(this.create_user_stats_chart())
		this.accept_charts(this.create_social_stats_snapshots_chart())
		this.accept_charts(this.create_social_stats_finals_chart())
		this.accept_charts(this.create_strata_charts())	
		
		this.url_templates = []
		for (var i = 0, l = this.series.length; i < l; i++)
			this.url_templates[i] = this.series[i].data_url
	}
	
	
})

})