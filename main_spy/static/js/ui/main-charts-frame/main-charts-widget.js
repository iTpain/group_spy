new Module('ui/main-charts-frame/main-charts-widget.js', ['ui/charts-widget.js', 'ui/charts-creator.js'], function() {

groupspy.MainChartsWidget = new jsage.Class('MainChartsWidget', [groupspy.ChartsWidget], {
	
	init: function() {
		this.chart_creators = [this.create_user_stats_chart, this.create_social_stats_snapshots_chart, this.create_social_stats_finals_chart, this.create_strata_charts]
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
	},
	
	create_social_stats_snapshots_chart: function() {
		var filters = [jsage.charts.DefaultTimeFilter.create(this.three_months_before, this.time_now, true)]
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
				axis_x_min: this.three_months_before * 1000,
				axis_x_max: this.time_now * 1000		
			},
			create_line_chart, jsage.charts.date_transformer
		)		
	},
	
	create_social_stats_finals_chart: function() {
		var content_types = ['app', 'audio', 'doc', 'graffiti', 'link', 'no_attachment', 'note', 'page', 'photo', 'poll', 'posted_photo', 'video']
		var content_types_labels = ['Приложение', "Аудио", "Документ", "Граффити", "Ссылка", "Без вложений", "Заметка", "Страница", "Фото", "Опрос", "Фото(к)", "Видео"] 
		var filters = [jsage.charts.DefaultTimeFilter.create(this.year_before, this.time_now, true), groupspy.MultiChoiceFilter.create(content_types, content_types_labels)]
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
			create_line_chart, jsage.charts.date_transformer
		)	
		filters[1].set_chart(chart)
		return chart	
	},
	
	create_strata_charts: function() {
		var strata_charts = [
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
	}
	
	
})

})