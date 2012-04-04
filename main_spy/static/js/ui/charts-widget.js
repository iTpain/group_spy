new Module('ui/charts-widget.js', ['jsage/baseui.js', 'jsage/charts/charts-core.js', 'jsage/charts/charts-aux.js', 'ui/charts-creator.js'], function() {

groupspy.ChartsWidget = new jsage.Class('ChartsWidget', [], {
	
	init: function() {
		var date_now = new Date()
		date_now.setSeconds(0)
		date_now.setMinutes(0)
		date_now.setHours(0)
		date_now.setMilliseconds(0)
		this.time_now = Math.round(date_now.getTime() / 1000)
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
	
	create_charts: function() {
		for (var i = 0, l = this.chart_creators.length; i < l; i++)
			this.accept_charts(this.chart_creators[i].apply(this))		
		this.url_templates = []
		for (var i = 0, l = this.series.length; i < l; i++)
			this.url_templates[i] = this.series[i].data_url
	},
	
	accept_charts: function(charts) {
		if (!(charts instanceof Array))
			charts = [charts]
		for (var i = 0, l = charts.length; i < l; i++) {
			this.charts.push(charts[i])
			var flash_id = "flash_saver_" + (groupspy.counter++)
			var loader = $("<div class='emphasize' style='width:100px; height:30px; margin-left:7px;'><div style='width:100px; height:30px;' id=" + flash_id + "></div></div>")[0]
			var flash_params = {
				menu: "false",
				scale: "noscale",
				allowFullscreen: "true",
				allowScriptAccess: "always",
				bgcolor: "#FFFFFF",
				wmode: "transparent"
			}
			$("#" + charts[i].chart_options.container)[0].appendChild(loader)
			groupspy[flash_id] = (function (chart) {
				return function() {
					return chart.get_excel_xml()
				}
			})(charts[i])
			swfobject.embedSWF("static/" + ASSETS["swf/JSHelper_Saver.swf"], flash_id, "100%", "100%", "10.0.0", "expressInstall.swf", {defaultName:"report.xml", jsCallback: "groupspy." + flash_id, text: "Загрузить XML", width: 100, height: 30}, flash_params, {id: flash_id});
		}
	}
	
	
})

})