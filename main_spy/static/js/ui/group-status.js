new Module('ui/group-status.js', ['jsage/baseui.js'], function () {

$(document).ready(function() {
	date_now = Math.round (new Date().getTime() / 1000)
	back_for_month = date_now - 364 * 24 * 60 * 60
	
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
	
	function create_controls(chart_description) {
		if ('controls' in chart_description) {
			var controls = chart_description.controls
			if (controls.aggregate) {
				chart_description.controls.aggregate = jsage.OptionsList.create($("#" + chart_description.container)[0].parentNode, [{label: 'Сумму', data: 'sum'}, {label: 'Среднее', data: 'avg'}])
				//chart_description.aggregation_changed(v)
			}
		}	
	}
	
	// group users/activity diagrams
	function process_series_response(update, index, description, full_response) {
		description.data = description.data || []
		current_series = description.data[index] || []
		
		var cur_update_index = 0
		var cur_series_index = 0
		var update_len = update.length
		var series_len = current_series.length
		var points_to_add = []
		while (cur_update_index < update_len) {
			if (cur_series_index >= series_len) {
				for (var i = cur_update_index; i < update_len; i++)
					points_to_add.push (update[i])
				break
			}
			var date_update = update[cur_update_index][0]
			var date_series = current_series[cur_series_index][0]
			if (date_update > date_series) {
				cur_series_index++
			} else if (date_update < date_series) {
				points_to_add.push (update[cur_update_index])
				cur_update_index++
			} else {
				cur_series_index++
				cur_update_index++
			}
		}
		
		var total_data = current_series
		for (var i = 0, l = points_to_add.length; i < l; i++) {
			total_data.push(points_to_add[i])
		}
		
		total_data.sort(function (x,y) { x = x[0]; y = y[0]; if (x > y) return 1; else if (x < y) return -1; else return 0;  })
		description.data[index] = total_data
		//console.log(total_data.length)
	}
	
	function create_line_chart(chart_description) {
		var opts = chart_description.series_opts
		var series_objs = []
		
		for (var j = 0, ln = opts.length; j < ln; j++)
			series_objs.push({
				type: 'line',
				name: opts[j].label,
				color: opts[j].color,
				data: [],
				lineWidth: 1
			});
		var chart = new Highcharts.StockChart({
			chart: {
				renderTo: chart_description.container,
				width: 800,
				height: 500,
				zoomType: 'x',
				events: {
					selection: function(event) {
						if (event.xAxis) {
							//console.log('select')
							//refresh_func (chart_description, Math.round (event.xAxis[0].min / 1000), Math.round (event.xAxis[0].max / 1000))
						}
					}
				}
			},
			rangeSelector: {
				selected: 0
			},
			legend: {
				enabled: true,
				y: -420,
				align: 'left',
				floating: true
			},
			title: {
				text: chart_description.title,
				style: {
					"font-family": "Segoe UI",
					"color": "#0066ff",
					"font-size": "20px",
				},
				align: "left",
				x: 0,
				margin: 50
			},
			xAxis: {
				type: 'datetime',
				min: new Date().getTime() - 365 * 24 * 60 * 60 * 1000,
				max: new Date().getTime(),
				showLastLabel: true,
				maxPadding: 0.0,
				ordinal: false,
				events: {
					setExtremes: (function () {
						var prevMin = -1
						var prevMax = -1
						return function(event) {
							if (prevMin != event.min || prevMax != event.max) {
								chart_description.refresh (chart_description, Math.round (event.min / 1000), Math.round (event.max / 1000))
								prevMin = event.min
								prevMax = event.max
							}
						}
					}) ()
				}
			},
			yAxis: {
				title: {
					text: 'Count'
				},
				min: 0
			},
			plotOptions: {
				line: {marker: {
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
		});
		chart_description.chart = chart
		create_controls(chart_description)
	}
	
	function refresh_userstat_chart(chart_desc, t1, t2) {
		for (var i = 0, l = chart_desc.series_opts.length; i < l; i++) {
			var opts = chart_desc.series_opts[i]
			$.ajax ({
				url: '/series/group' + GROUP_ID + '/' + opts.stat_id + '/' + t1 + '/' + t2 + '/',
				success: (function(index) { 
					return function(data) { 
						process_series_response(data.response.series, index, chart_desc, data.response) 
						chart_desc.chart.series[index].setData(chart_desc.data[index])
					}}) (opts.index)
			});
		}
	}
	
	function refresh_socialstat_chart(chart_desc, t1, t2) {
		$.ajax ({
			url: '/series/all_social_stats/group' + GROUP_ID + '/' + t1 + '/' + t2 + '/',
			success: function(data) { 
				response = data.response
				for (var i = 0, l = chart_desc.series_opts.length; i < l; i++) {
					var opts = chart_desc.series_opts[i]
					process_series_response(response[opts.stat_id].series, opts.index, chart_desc, response)
					chart_desc.chart.series[opts.index].setData(chart_desc.data[opts.index])
				}
			}
		});	
	}
	
	series_opts_group_users_chart = [
		{ color: '#0000ff', label: "Всего участников", stat_id: "total_users", index: 0},
		{ color: '#ff6600', label: "Без аватара", stat_id: "faceless_users", index: 1},
		{ color: '#ff0000', label: "Забаненные", stat_id: "banned_users", index: 2},
		{ color: '#44aa44', label: "Активные", stat_id: "users_1", index: 3},
		{ color: '#22ff22', label: "Очень активные", stat_id: "users_3", index: 4}
	]
	
	series_opts_group_activity_chart = [
		{ color: '#00ff00', label: "Всего активных постов", stat_id: "active_posts_count", index: 0},
		{ color: '#ff0000', label: "Всего лайков для а.п.", stat_id: "active_posts_likes", index: 1 },
		{ color: '#ff6600', label: "Всего комментариев для а.п.", stat_id: "active_posts_comments", index: 2},
		{ color: '#0000ff', label: "Всего репостов для а.п.", stat_id: "active_posts_reposts", index: 3}
	]

	group_charts = [
		{ title: 'Общая статистика по участникам', series_opts: series_opts_group_users_chart, container: "group_users_chart", refresh: refresh_userstat_chart},
		{ title: 'Снимки активности участников', series_opts: series_opts_group_activity_chart, container: "group_activity_chart", refresh: refresh_socialstat_chart }
	]
	
	for (var i = 0, l = group_charts.length; i < l; i++) {
		create_line_chart(group_charts[i])
		group_charts[i].refresh(group_charts[i], back_for_month, date_now)
	}
	
	/* stratification charts */
	strata_charts = [
		{
			container: 'social_activity_hourly_stratified',
			title: 'Внутридневная результативность постов',
			strata_type: 'intraday_stratify',
			strata_labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
			key_func: function (key) { return parseInt(key) }, 
			controls: {aggregate: true},
		},
		{
			container: 'social_activity_daily_stratified',
			title: 'Внутринедельная результативность постов',
			strata_type: 'intraweek_stratify',
			strata_labels: [0, 1, 2, 3, 4, 5, 6],
			key_func: function (key) { return parseInt(key) }, 
			controls: {aggregate: true}
		},
		{
			container: 'social_activity_content_stratified',
			title: 'Результативность постов по типу приложений',
			strata_type: 'content_stratify',
			strata_labels: ['app', 'audio', 'doc', 'graffiti', 'link', 'no_attachment', 'note', 'page', 'photo', 'poll', 'posted_photo', 'video'],
			key_func: function (key) { return key }, 
			controls: {aggregate: true}
		}		
	]
	
	function redraw_strata_chart(params) {
		var total_data = {}
		var aggregation = params.controls.aggregate.get_selected()
		for (var e in params.data) {
			if (e == "active_posts_count")
				continue
			var series = params.data[e]
			var new_data = total_data[e] = []
			for (var i = 0, l = series.length; i < l; i++) {
				if (aggregation == "avg")
					new_data.push(params.data["active_posts_count"][i] > 0 ? series[i] / params.data["active_posts_count"][i] : 0)
				else
					new_data.push(series[i])					
			}
		}
		params.chart.series[0].setData(total_data["active_posts_likes"])
		params.chart.series[1].setData(total_data["active_posts_reposts"])
		params.chart.series[2].setData(total_data["active_posts_comments"])
	}
	
	for (var i = 0, l = strata_charts.length; i < l; i++) {
		var params = strata_charts[i]
		params.aggregation_changed = (function (params) {
			return function () {
				redraw_strata_chart(params)
			}
		}) (params)
		
		var schart = new Highcharts.Chart({
			chart: {
				renderTo: params.container,
				defaultSeriesType: 'column',
				width: 800,
				height: 500
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
				x: 0,
				margin: 50
			},
			xAxis: {
				categories: params.strata_labels
			},
			yAxis: {
				min: 0,
				title: {
					text: 'Count'
				}
			},
			plotOptions: {
				series: {
					stacking: 'normal'
				}
			}
		});
		schart.addSeries({name: "лайки"})
		schart.addSeries({name: "репосты"})
		schart.addSeries({name: "комментарии"})
		params.chart = schart
		create_controls(params)
	}
	
	function make_stratas_request(params, t1, t2) {
		if (!params.data) {
			params.data = {
				active_posts_likes: [],
				active_posts_comments: [],
				active_posts_reposts: [],
				active_posts_count: []
			}
		}
		$.ajax({
			url: '/group' + GROUP_ID + '/' + params.strata_type + '/' + t1 + '/' + t2 + '/',
			success: function (data) {
				data = data.response
				var list = []
				for (var e in data)
					list.push ([e, data[e]])
				list.sort (function (x, y) {
					x = params.key_func(x[0])
					y = params.key_func(y[0])
					if (x > y)
						return 1
					else if (x < y)
						return -1
					else
						return 0
				})
				for (var i = 0, l = list.length; i < l; i++) {
					var stats = list[i][1].stats
					for (var t in params.data) {
						params.data[t].push(stats[t])
					}
				}
				redraw_strata_chart(params)
			}
		});
	}
	
	for (i = 0, l = strata_charts.length; i < l; i++)
		make_stratas_request(strata_charts[i], date_now - 30 * 60 * 60 * 24, date_now)
	
	// social dynamics
	var series_opts_soc_dynamics_chart = [
		{ color: '#ff0000', label: "лайки", stat_id: "likes", index: 0 },
		{ color: '#ff6600', label: "комментарии", stat_id: "comments", index: 1},
		{ color: '#0000ff', label: "репосты", stat_id: "reposts", index: 2}
	]
	
	var prevT1 = 0
	var prevT2 = 0
	var prevContentTypes = ''
	function refresh_social_dynamics_chart(chart_desc, t1, t2) {
		if (!t1)
			t1 = prevT1
		if (!t2)
			t2 = prevT2
		prevT1 = t1
		prevT2 = t2
		make_social_dynamics_request(t1, t2, soc_dynamics_chart_desc)
	}
	
	function make_social_dynamics_request(t1, t2, description) {
		content_types = filters_group.get_selected().join(",")
		if (content_types.length == 0)
			content_types = 'all'
		$.ajax ({
			url: '/series/group' + GROUP_ID + '/social_dynamics_all/' + content_types + '/' + t1 + '/' + t2 + '/',
			success: function(data) { 
				if (content_types != prevContentTypes)
					description.data = null
				prevContentTypes = content_types
				var series_info = description.series_opts
				for (var i = 0, l = series_info.length; i < l; i++) {
					var series = data.response[series_info[i].stat_id].series
					if (series[series.length - 1][1] == 0)
						series.pop()
					process_series_response(series, series_info[i].index, description)
					var series_data = description.data[series_info[i].index]
					var filtered_data = make_sliding_average(series_data, series_data.length / 50)
					description.chart.series[series_info[i].index].setData(filtered_data)
				}
			}
		});	
	}
	
	var soc_dynamics_chart_desc = { title: 'Историческая статистика результативности постов', series_opts: series_opts_soc_dynamics_chart, container: "group_social_activity_dynamics", refresh: refresh_social_dynamics_chart }
	create_line_chart(soc_dynamics_chart_desc, refresh_social_dynamics_chart)
	var content_types = ['app', 'audio', 'doc', 'graffiti', 'link', 'no_attachment', 'note', 'page', 'photo', 'poll', 'posted_photo', 'video']
	var content_types_labels = ['Приложение', "Аудио", "Документ", "Граффити", "Ссылка", "Без вложений", "Заметка", "Страница", "Фото", "Опрос", "Фото(к)", "Видео"] 
	var content_filters = []
	for (var i = 0, l = content_types.length; i < l; i++) {
		content_filters.push({label: content_types_labels[i], data: content_types[i]});
	}
	var filters_group = jsage.CheckboxList.create($("#group_social_activity_dynamics")[0], content_filters)
	refresh_social_dynamics_chart(soc_dynamics_chart_desc, back_for_month, date_now)
	
	// demogeo snapshot
	function arrays_to_percents() {
		var l = arguments.length
		for (var i = 0; i < l; i++) {
			var arr = arguments[i]
			for (var j = 0, lj = arr.length; j < lj; j++)
				arr[j][1] *= 100
		}
	}
	
	function absolute_to_percents_in_array(arr) {
		var sum = 0
		for (var i = 0, l = arr.length; i < l; i++) {
			sum += arr[i][1]
		}
		for (i = 0; i < l; i++) {
			arr[i][1] *= 100 / sum
		}
	}
	
	function create_demo_stratas(data, params, filters) {
		function cannot_distinguish(p1, p2) {
			for (var e in p1) {
				var stratas = params[e]
				for (var i = 0, l = stratas.length; i < l; i++) {
					//console.log(stratas[i].indexOf(p1[e]), stratas[i].indexOf(p2[e]))
					var s1 = stratas[i].indexOf(p1[e]) + 1
					var s2 = stratas[i].indexOf(p2[e]) + 1
					if ((s1 * s2 == 0) && !(s1 == 0 && s2 == 0)) {
						return false
					}
				}
			}
			return true
		}		
		
		function create_name(props) {
			var order = ['sex', 'age', 'education']
			var name_pieces = []
			for (var p in params) {
				if (params[p].length == 0)
					continue
				var stratas = params[p]
				for (var i = 0, l = stratas.length; i < l; i++) {
					if (stratas[i].indexOf(props[p]) > -1) {
						name_pieces.push([p, props[p]])
						break
					}
				}
			}
			name_pieces.sort(function (n1, n2) {
				n1 = order.indexOf(n1[0])
				n2 = order.indexOf(n2[0])
				if (n1 > n2) return 1
				else if (n1 < n2) return -1
				else return 0
			})
			name_pieces = name_pieces.map(function(el) { return el[1] })
			return name_pieces.join(" ")
		}
		
		var groups = []
		outer: for (var e in data) {
			var pieces = e.split(":")
			var props = {
				age: pieces[0],
				sex: pieces[1],
				education: pieces[2]
			}
			if (filters != null) {
				for (var f in filters) {
					if (filters[f].indexOf(props[f]) < 0) {
						continue outer
					}
				}
			}
			var found_same = false
			for (var i = 0, l = groups.length; i < l; i++) {
				if (cannot_distinguish(groups[i][0], props)) {
					groups[i][1] += data[e]
					found_same = true
					break
				}
			}
			if (!found_same) {
				groups.push([props, data[e]])
			}
		}
		
		for (i = 0, l = groups.length; i < l; i++) {
			groups[i][0] = create_name(groups[i][0])
		}
		groups.sort(function(g1, g2) {
			g1 = g1[0]
			g2 = g2[0]
			if (g1 > g2) return 1
			else if (g1 < g2) return -1
			else return 0
		})
		
		return groups
	}
	
	var geo_chart_desc = {container: 'geo_snapshot_chart', width: 400, height: 400, title: 'Распределение участников по городам', size: 150}
	
	var ages_stratas = [['0-11'], ['12-15'], ['16-18'], ['19-21'], ['22-24'], ['25-27'], ['28-30'], ['31-35'], ['36-45'], ['46-120']]
	var demos = [
		[{age: [], education: [], sex: [['man'], ['woman']]}, null],
		[{age: [], education: [['higher'], ['other']], sex: []}, null],
		[{age: ages_stratas, education: [], sex: []}, null],
		[{age: ages_stratas, education: [], sex: []}, {sex: ['man']}],
		[{age: ages_stratas, education: [], sex: []}, {sex: ['woman']}]
	]
	
	var demo_descriptions = [
		{container: 'sex_snapshot_chart', width: 400, height: 400, title: 'Распределение по полу', size: 200},
		{container: 'education_snapshot_chart', width: 400, height: 400, title: 'Распределение по образованию', size: 200},
		{container: 'age_snapshot_chart', width: 400, height: 400, title: 'Распределение по возрасту', size: 200},
		{container: 'man_age_snapshot_chart', width: 400, height: 400, title: 'Распределение мужчин по возрасту', size: 200},
		{container: 'woman_age_snapshot_chart', width: 400, height: 400, title: 'Распределение женщин по возрасту', size: 200}
	]
	
	$.ajax({
		url: '/group' + GROUP_ID + '/demogeo_snapshot/' + date_now,
		success: function (data) {
			data = data.response			
			arrays_to_percents(data.whole_group.geo, data.active_users.geo)
			geo_chart_desc.initial_data = [data.whole_group.geo, data.active_users.geo]
			
			var demo_data = [data.whole_group.demo, data.active_users.demo]
			for (var i = 0, l = demo_descriptions.length; i < l; i++) {
				demo_descriptions[i].initial_data = demo_data
			}
			draw_demogeo_charts(0)
		}
	});
	
	function draw_demogeo_charts(data_index) {
		geo_chart_desc.data = geo_chart_desc.initial_data[data_index]
		if (geo_chart_desc.chart)
			geo_chart_desc.chart.destroy()
		create_pie_chart(geo_chart_desc)
		
		for (var i = 0, l = demo_descriptions.length; i < l; i++) {
			var series = create_demo_stratas(demo_descriptions[i].initial_data[data_index], demos[i][0], demos[i][1])
			demo_descriptions[i].data = series
			absolute_to_percents_in_array(series)
			if (demo_descriptions[i].chart)
				demo_descriptions[i].chart.destroy()
			create_pie_chart(demo_descriptions[i])
		}	
	}
	
	var demogeoSwitcher = jsage.OptionsList.create($("#demogeo_switcher")[0], [{label: 'всем участникам', data: 0}, {label: 'активной аудитории', data: 1}])
	
	function create_pie_chart(chart_desc) {
		var schart = new Highcharts.Chart({
			chart: {
				renderTo: chart_desc.container,
				defaultSeriesType: 'pie',
				width: chart_desc.width,
				height: chart_desc.height
			},
			title: {
				text: chart_desc.title,
				style: {
					"font-family": "Segoe UI",
					"color": "#0066ff",
					"font-size": "14px",
				},
				align: "left",
				x: 0,
				margin: 0
			},
			plotOptions: {
				pie: {
					size: chart_desc.size
				}
			},
			series: [{
				data: chart_desc.data
			}]
		});	
		chart_desc.chart = schart
	}
})
	
})
