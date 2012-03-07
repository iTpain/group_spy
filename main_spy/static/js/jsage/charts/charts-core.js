new Module('jsage/charts/charts-core.js', ['jsage/baseui.js'], function() {

jsage.charts = {}
var ev_list = ['series_update', 'series_load_start']
jsage.charts.events = {	}
for (var i = 0 , l = ev_list.length; i < l; i++)
	jsage.charts.events[ev_list[i]] = ev_list[i]
	
jsage.charts.DefaultTimeFilter = new jsage.Class('DefaultTimeFilter', [], {
	
	invalidating: function() { return false },
	
	init: function (t1, t2) {
		this.initial_t2 = t2
		this.initial_t1 = t1
		this.set_range(t1, t2)
	},
	
	on_chart_range_selected: function(t1, t2) {
		this.set_range(t1, t2)
	},
	
	set_range: function(t1, t2) {
		if (isNaN(t1) || isNaN (t2))
			return
		this.t1 = t1
		this.t2 = Math.min(t2, this.initial_t2)
	},
	
	make_url_part: function() {
		return Math.round(this.t1) + "/" + Math.round(this.t2)
	},
	
	set_chart: function() {},
	
	reset: function() {
		this.t1 = this.initial_t1
		this.t2 = this.initial_t2
	}
	
})

jsage.charts.DataLoader = new jsage.Class('DataLoader', [], {
	
	init: function() {
		this.urls_loading = {}
	},
	
	load: function(object, url, token) {
		if (url in this.urls_loading) {
			this.urls_loading[url].push([object, token])
		} else {
			this.urls_loading[url] = [[object, token]]
			var that = this
			$.ajax({
				url: url,
				success: function(response) {
					var data = response.response
					var callbacks = that.urls_loading[url]
					for (var i = 0, l = callbacks.length; i < l; i++) {
						var callback_details = callbacks[i]
						callback_details[0].on_data_fetched(data, token)
					}
					delete that.urls_loading[url]
				}
			})
		}
	}
	
})
jsage.charts.data_loader = jsage.charts.DataLoader.create()

/*
 * the data must be an array of arrays. Each of subarrays is an observation of the form 
 * [data_label(for instance, timestamp or label), data_value(number), ... additional params can follow]
 */	
jsage.charts.DataSeries = new jsage.Class('DataSeries', [jsage.EventDispatcher], {
	
	init: function(data_url, data_key, filters) {
		this.data_key = data_key
		this.ajax_token = 0
		this.loading_with_last_token = 0
		this.prev_data_url = null
		this.prev_filters_results = []		
		this.data = []
		this.data_url = data_url
		this.filters = filters
		for (var i = 0, l = filters.length; i < l; i++)
			this.prev_filters_results[i] = null
		this.init_EventDispatcher()
	},
	
	clean: function() {
		this.data = []
	},
	
	get_data_copy: function() {
		return this.data.slice()
	},
	
	is_loading: function() {
		return this.loading_with_last_token > 0
	},
	
	receive_update: function(update) {
		var current_series = this.data		
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
		for (var i = 0, l = points_to_add.length; i < l; i++)
			total_data.push(points_to_add[i])
		
		total_data.sort(function (x,y) { x = x[0]; y = y[0]; if (x > y) return 1; else if (x < y) return -1; else return 0;  })
		this.data = total_data
	},
	
	fetch_data: function() {
		var filters_results = this.filters.map(function(f) { return f.make_url_part() })
		if (this.prev_data_url != this.data_url) {
			var cleaning_needed = true
		} else {
			for (var i = 0, l = filters_results.length; i < l; i++) {
				if (filters_results[i] != this.prev_filters_results[i] && this.filters[i].invalidating(filters_results[i], this.prev_filters_results[i])) {
					cleaning_needed = true
					break
				}
			}
		}
		if (cleaning_needed) {
			this.clean()
			this.ajax_token++
			this.loading_with_last_token = 1
		} else {
			this.loading_with_last_token++
		}
		this.prev_filters_results = filters_results
		this.prev_data_url = this.data_url
		var filters_url = filters_results.join("/")
		var effective_url = this.data_url + (filters_url.length > 0 ? filters_url + "/" : "")
		this.dispatch_event(jsage.charts.events.load_start, this)
		jsage.charts.data_loader.load(this, effective_url, this.ajax_token)
	},
	
	on_data_fetched: function(data, token) {
		if (token == this.ajax_token) {
			this.loading_with_last_token--
			if (this.data_key instanceof Function)
				this.receive_update(this.data_key(data))
			else
				this.receive_update(data[this.data_key].series)
			this.dispatch_event(jsage.charts.events.series_update, this)
		}
	}
		
})

jsage.charts.DataChartPresentation = new jsage.Class('DataChartPresentation', [], {
	
	init: function(series_description, data_transformers, chart_options, chart_constructor) {
		this.chart_options = chart_options
		var that = this
		chart_options.on_chart_range_select = function (t1, t2) { that.chart_range_selected(t1, t2) }
		this.chart = chart_constructor(series_description, chart_options)
		this.series_description = series_description
		for (i = 0, l = series_description.length; i < l; i++) {
			series_description[i].source.add_listener(jsage.charts.events.series_update, this, this.on_source_update)
			series_description[i].source.add_listener(jsage.charts.events.load_start, this, this.on_series_load_start)
		}
		this.data_transformers = data_transformers.slice()
		for (var i = 0, l = data_transformers.length; i < l; i++) {
			data_transformers[i].set_chart(this)
		}
	},
	
	get_container: function() {
		return this.chart.container.parentNode
	},
	
	fetch_chart_data: function() {
		for (var i = 0, l = this.series_description.length; i < l; i++) {
			this.series_description[i].source.fetch_data()
		}
	},
	
	reset_axis_extremes: function() {
		if ('axis_x_min' in this.chart_options) {
			this.chart.xAxis[0].setExtremes(this.chart_options.axis_x_min, this.chart_options.axis_x_max)
		}
	},
	
	on_series_load_start: function() {
		this.chart.showLoading()
	},
	
	on_source_update: function(source) {
		var description = this.find_by_source(source)
		this.transform_series_data(description)
		for (var i = 0, l = this.series_description.length; i < l; i++) {
			if (this.series_description[i].source.is_loading())
				return
		}
		this.chart.hideLoading()
	},
	
	transform_chart_data: function() {
		for (var i = 0, l = this.series_description.length; i < l; i++) {
			this.transform_series_data(this.series_description[i])
		}
	},
	
	transform_series_data: function(description) {
		var data = description.source.get_data_copy()
		for (var i = 0, l = this.data_transformers.length; i < l; i++)
			data = this.data_transformers[i].transform(data)
		this.chart.series[description.index].setData(data)	
	},
	
	find_by_source: function(src) {
		for (var i = 0, l = this.series_description.length; i < l; i++) {
			if (this.series_description[i].source == src)
				return this.series_description[i]
		}
		return null
	},
	
	chart_range_selected: function(t1, t2) {
		if (this.prevT1 == t1 && this.prevT2 == t2)
			return
		this.prevT1 = t1
		this.prevT2 = t2
		for (var i = 0, l = this.series_description.length; i < l; i++) {
			var series_source = this.series_description[i].source
			var series_filters = series_source.filters
			for (var j = 0, lj = series_filters.length; j < lj; j++) {
				if ('on_chart_range_selected' in series_filters[j])
					series_filters[j].on_chart_range_selected(t1, t2)
			}
		}
		this.fetch_chart_data()
	},
	
	get_excel_xml: function() {
		var xls = []
		xls.push('<?xml version="1.0"?><ss:Workbook xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"><ss:Worksheet ss:Name="Sheet1"><ss:Table>')
		var data = []
		for (var i = 0, l = this.series_description.length; i < l; i++) {
			xls.push('<ss:Column ss:Width="80"/>')
			data.push(this.series_description[i].source.get_data_copy().reverse())
		}
		xls.push('<ss:Row>')
		xls.push('<ss:Cell><ss:Data ss:Type="String">date</ss:Data></ss:Cell>')
		for (i = 0; i < l; i++) {
			xls.push('<ss:Cell><ss:Data ss:Type="String">' + this.series_description[i].id + '</ss:Data></ss:Cell>')
		}
		xls.push('</ss:Row>')
		for (i = 0, l = data[0].length; i < l; i++) {
			xls.push('<ss:Row>')
			var date = new Date(data[0][i][0])
			var day = date.getDate()
			var month = date.getMonth() + 1
			var year = date.getFullYear()
			var hours = date.getHours()
			var minutes = date.getMinutes()
			var date_str = day + "." + month + "." + year + " " + hours + ":" + minutes
			xls.push('<ss:Cell><ss:Data ss:Type="String">' + date_str + '</ss:Data></ss:Cell>')
			for (var j = 0, lj = this.series_description.length; j < lj; j++) {
				xls.push('<ss:Cell><ss:Data ss:Type="String">' + data[j][i][1] + '</ss:Data></ss:Cell>')
			}
			xls.push('</ss:Row>')
		}
		xls.push('</ss:Table></ss:Worksheet></ss:Workbook>')
		return xls.join("")
	}
	
})

})
