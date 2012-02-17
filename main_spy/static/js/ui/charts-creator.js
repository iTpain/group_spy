new Module('ui/charts-creator.js', [], function() {
	
window.create_column_chart = function(series, params) {
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
			margin: params.title_margin,
			floating: params.title_floating || false
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

window.create_line_chart = function(series, params) {
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
				setExtremes: function(event) { on_range_select (Math.round (event.min / 1000), Math.round (event.max / 1000)) }
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
	
})
