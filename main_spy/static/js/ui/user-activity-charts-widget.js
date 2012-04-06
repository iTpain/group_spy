new Module('ui/user-activity-charts-widget.js', ['ui/charts-widget.js', 'ui/charts-creator.js', 'jsage/eventbus.js'], function() {

groupspy.UserActivityChartsWidget = new jsage.Class('UserActivityChartsWidget', [groupspy.ChartsWidget, jsage.GlobalMessagingObject], {
	
	init: function() {
		this.chart_creators = [this.create_social_stats_snapshots_chart, this.create_social_stats_finals_chart]
		this.subscribe(groupspy.messages.user_activity_frame_activate, this.on_activate)
		//this.init_ChartsWidget()
	},
	
	on_activate: function(group_id) {
		if (!this.built) {
			this.init_ChartsWidget()
			this.built = true
		}
		this.set_group(group_id)
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
				title: 'Историческая статистика активности пользователей', 
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
	}
	
	
})

$(document).ready(function () {
	var widget = groupspy.UserActivityChartsWidget.create()
})


})