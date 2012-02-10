new Module('ui/group-status.js', ['jsage/baseui.js', 'ui/charts-core.js'], function () {
$(document).ready(function() {

/*
var content_types = ['app', 'audio', 'doc', 'graffiti', 'link', 'no_attachment', 'note', 'page', 'photo', 'poll', 'posted_photo', 'video']
var content_types_labels = ['Приложение', "Аудио", "Документ", "Граффити", "Ссылка", "Без вложений", "Заметка", "Страница", "Фото", "Опрос", "Фото(к)", "Видео"] 

function make_sliding_average(data, count) {
	count = Math.round(count)
	if (count < 2)
		return data
	var cur_arr = []
	var output = []
	for (var i = 0, l = data.length; i < l; i++) {
		cur_arr.push(data[i])
		if (cur_arr.length <= count) {
			output.push(data[i])
		} else {
			cur_arr.shift()
			var sum = 0
			for (var j = 0; j < count; j++) 
				sum += cur_arr[j][1]
			output.push([data[i][0], sum / count])
		}
	}
	return output
}
*/

var time_now = Math.round(new Date().getTime() / 1000)
var month_before = time_now - 31 * 24 * 3600
var year_before = time_now - 364 * 24 * 3600

function create_column_chart(series, params) {
	var chart = new Highcharts.Chart({
		chart: {
			renderTo: params.container,
			defaultSeriesType: 'column',
			width: params.width,
			height: params.height
		},
		tooltip: {
			formatter: function() {
				return '<b>'+ this.x +'</b><br/>'+
					this.series.name +': '+ this.y +'<br/>'+
					'Total: '+ this.point.stackTotal;
			}
		},
		title: {
			text: params.title,
			style: {
				"font-family": "Segoe UI",
				"color": "#0066ff",
				"font-size": "20px",
			},
			align: "left",
			x: params.title_x,
			margin: params.title_margin
		},
		xAxis: { categories: params.axis_x_categories },
		yAxis: { min: 0 },
		plotOptions: {
			series: { stacking: 'normal' }
		}
	})
	for (var i = 0, l = series.length; i < l; i++) {
		chart.addSeries(series[i])
		series[i].index = i
	}
	return chart
}

function create_line_chart(series, params) {
	var series_objs = []		
	for (var j = 0, ln = series.length; j < ln; j++) {
		var s = series[j]
		series_objs.push({ type: 'line', name: s.label, color: s.color, data: [], lineWidth: 1 })
		s.index = j
	}
	var on_range_select = params.on_chart_range_select
	var chart = new Highcharts.StockChart({
		chart: {
			renderTo: params.container,
			width: params.width,
			height: params.height,
			zoomType: 'x',
		},
		rangeSelector: {
			selected: params.range_selected
		},
		legend: {
			enabled: true,
			y: params.legend_y,
			align: 'left',
			floating: true
		},
		title: {
			text: params.title,
			style: { "font-family": "Segoe UI", "color": "#0066ff", "font-size": "20px" },
			align: "left",
			x: params.title_x,
			margin: params.title_margin
		},
		xAxis: {
			type: 'datetime',
			min: params.axis_x_min,
			max: params.axis_x_max,
			showLastLabel: true,
			maxPadding: 0.0,
			ordinal: false,
			events: {
				setExtremes: function(event) { console.log(event); on_range_select (Math.round (event.min / 1000), Math.round (event.max / 1000)) }
			}
		},
		yAxis: { min: 0 },
		plotOptions: {
			line: {
				marker: {
					enabled: false,
					states: {
						hover: {
							enabled: true,
							radius: 5
						}
					}
				},
				shadow: false
			}
		},
		series: series_objs
	})
	return chart
}

var user_stats_snapshots_chart = groupspy.DataChartPresentation.create(
	[
		{ color: '#0000ff', label: "Всего участников", id: "total_users" },
		{ color: '#ff6600', label: "Без аватара", id: "faceless_users" },
		{ color: '#ff0000', label: "Забаненные", id: "banned_users" },
		{ color: '#44aa44', label: "Активные", id: "users_1" },
		{ color: '#22ff22', label: "Очень активные", id: "users_3" }
	],
	[], 
	[groupspy.DefaultTimeFilter.create(month_before, time_now)],
	{ 
		title: 'Общая статистика по участникам', 
		container: "group_users_chart",
		width: 800,
		height: 500,
		title_x: 0,
		title_margin: 50,
		legend_y: -420,
		range_selected: 0,
		axis_x_min: month_before * 1000,
		axis_x_max: time_now * 1000
	},
	create_line_chart,
	'/group' + GROUP_ID +'/all_user_stats_snapshots/'
)

var social_stats_snapshots_chart = groupspy.DataChartPresentation.create(
	[
		{ color: '#00ff00', label: "Всего активных постов", id: "active_posts_count" },
		{ color: '#ff0000', label: "Всего лайков для а.п.", id: "active_posts_likes" },
		{ color: '#ff6600', label: "Всего комментариев для а.п.", id: "active_posts_comments" },
		{ color: '#0000ff', label: "Всего репостов для а.п.", id: "active_posts_reposts" }
	],
	[],
	[groupspy.DefaultTimeFilter.create(month_before, time_now)],
	{
		title: 'Снимки активности участников', 
		container: "group_activity_chart",
		width: 800,
		height: 500,
		title_x: 0,
		title_margin: 50,
		legend_y: -420,
		range_selected: 0,
		axis_x_min: month_before * 1000,
		axis_x_max: time_now * 1000		
	},
	create_line_chart,
	'/group' + GROUP_ID +'/all_social_stats_snapshots/'
)

var social_stats_finals_chart = groupspy.DataChartPresentation.create(
	[
		{ color: '#ff0000', label: "лайки", id: "likes" },
		{ color: '#ff6600', label: "комментарии", id: "comments" },
		{ color: '#0000ff', label: "репосты", id: "reposts" }
	],
	[],
	[groupspy.DefaultTimeFilter.create(year_before, time_now), { make_url_part: function() { return 'all' } }],
	{
		title: 'Историческая статистика результативности постов', 
		container: "group_social_activity_dynamics",
		width: 800,
		height: 500,
		title_x: 0,
		title_margin: 50,
		legend_y: -420,
		range_selected: 0,
		axis_x_min: year_before * 1000,
		axis_x_max: time_now * 1000		
	},
	create_line_chart,
	'/group' + GROUP_ID +'/all_social_stats_finals/'
)

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
for (var i = 0, l = strata_charts.length; i < l; i++) {
	var params = {
		width: 800,
		height: 500,
		title_x: 0,
		title_margin: 50
	}
	params.container = strata_charts[i].container
	params.title = strata_charts[i].title
	params.axis_x_categories = strata_charts[i].strata_labels
	var chart = groupspy.DataChartPresentation.create(
		[
			{ label: "лайки", name: "лайки", id: "active_posts_likes" },
			{ label: "комментарии", name: "комментарии", id: "active_posts_comments" },
			{ label: "репосты", name: "репосты", id: "active_posts_reposts" }
		],
		[],
		[groupspy.DefaultTimeFilter.create(month_before, time_now)],
		params,
		create_column_chart,
		'/group' + GROUP_ID +'/' + strata_charts[i].strata_type + '/'
	)
}
	
})
})
