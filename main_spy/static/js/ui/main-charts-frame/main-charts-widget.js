new Module('ui/main-charts-frame/main-charts-widget.js', ['jsage/baseui.js', 'ui/charts-core.js', 'ui/charts-aux.js', 'ui/charts-creator.js'], function() {

groupspy.MainChartsWidget = new jsage.Class('MainChartsWidget', [], {
	
	init: function() {
		this.time_now = Math.round(new Date().getTime() / 1000)
		this.month_before = this.time_now - 31 * 24 * 3600
		this.three_months_before = this.time_now - 93 * 24 * 3600
		this.year_before = this.time_now - 364 * 24 * 3600
		this.charts = []
		this.create_charts()
	},
	
	set_group: function(gid) {
		for (var i = 0, l = this.charts.length; i < l; i++) {
			this.charts[i].data_url = this.url_templates[i].replace('<GROUP_ID>', gid.toString())
			this.charts[i].reset_axis_extremes()
			this.charts[i].fetch_chart_data()
		}
	},
	
	create_user_stats_chart: function() {
		return groupspy.DataChartPresentation.create([
				{ color: '#0000ff', label: "Всего участников", id: "total_users" },
				{ color: '#ff6600', label: "Без аватара", id: "faceless_users" },
				{ color: '#ff0000', label: "Забаненные", id: "banned_users" },
				{ color: '#44aa44', label: "Активные", id: "users_1" },
				{ color: '#22ff22', label: "Очень активные", id: "users_3" }
			],
			[groupspy.NormalizeDataTransformer.create(false), groupspy.SlidingAverageDataTransformer.create(false, 0.05)], 
			[groupspy.DefaultTimeFilter.create(this.month_before, this.time_now)],
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
			create_line_chart,
			'/group<GROUP_ID>/all_user_stats_snapshots/'
		)		
	},
	
	create_social_stats_snapshots_chart: function() {
		return groupspy.DataChartPresentation.create([
				{ color: '#00ff00', label: "Всего активных постов", id: "active_posts_count" },
				{ color: '#ff0000', label: "Всего лайков для а.п.", id: "active_posts_likes" },
				{ color: '#ff6600', label: "Всего комментариев для а.п.", id: "active_posts_comments" },
				{ color: '#0000ff', label: "Всего репостов для а.п.", id: "active_posts_reposts" }
			],
			[groupspy.NormalizeDataTransformer.create(false), groupspy.SlidingAverageDataTransformer.create(true, 0.035)],
			[groupspy.DefaultTimeFilter.create(this.month_before, this.time_now)],
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
			create_line_chart,
			'/group<GROUP_ID>/all_social_stats_snapshots/'
		)		
	},
	
	create_social_stats_finals_chart: function() {
		var content_types = ['app', 'audio', 'doc', 'graffiti', 'link', 'no_attachment', 'note', 'page', 'photo', 'poll', 'posted_photo', 'video']
		var content_types_labels = ['Приложение', "Аудио", "Документ", "Граффити", "Ссылка", "Без вложений", "Заметка", "Страница", "Фото", "Опрос", "Фото(к)", "Видео"] 
		return groupspy.DataChartPresentation.create([
				{ color: '#ff0000', label: "лайки", id: "likes" },
				{ color: '#ff6600', label: "комментарии", id: "comments" },
				{ color: '#0000ff', label: "репосты", id: "reposts" }
			],
			[groupspy.AverageDataTransformer.create(false), groupspy.NormalizeDataTransformer.create(false), groupspy.SlidingAverageDataTransformer.create(true, 0.02)],
			[groupspy.DefaultTimeFilter.create(this.year_before, this.time_now), groupspy.MultiChoiceFilter.create(content_types, content_types_labels)],
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
			create_line_chart,
			'/group<GROUP_ID>/all_social_stats_finals/'
		)		
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
			charts.push(groupspy.DataChartPresentation.create(
				[
					{ label: "лайки", name: "лайки", id: "active_posts_likes" },
					{ label: "комментарии", name: "комментарии", id: "active_posts_comments" },
					{ label: "репосты", name: "репосты", id: "active_posts_reposts" }
				],
				[groupspy.AverageDataTransformer.create(false), groupspy.NormalizeDataTransformer.create(false)],
				[groupspy.DefaultTimeFilter.create(this.month_before, this.time_now)],
				params,
				create_column_chart,
				'/group<GROUP_ID>/' + strata_charts[i].strata_type + '/'
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
		for (var i = 0, l = this.charts.length; i < l; i++)
			this.url_templates[i] = this.charts[i].data_url
	}
	
	
})

})