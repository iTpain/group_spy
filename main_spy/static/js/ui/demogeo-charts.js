new Module('ui/demogeo-charts.js', ['jsage/baseui.js'], function() {
$(document).ready(function () {
	
var time_now = Math.round(new Date().getTime() / 1000)
	
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
	for (var i = 0, l = arr.length; i < l; i++)
		sum += arr[i][1]
	for (i = 0; i < l; i++)
		arr[i][1] *= 100 / sum
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
	url: '/group' + GROUP_ID + '/latest_demogeo_snapshot/' + time_now + '/',
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
$(demogeoSwitcher).bind("change", function(e) {
	draw_demogeo_charts(e.target.get_selected())
})

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
			x: -3,
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