new Module('ui/charts-core.js', ['jsage/baseui.js'], function() {

groupspy.DefaultTimeFilter = new jsage.Class('DefaultTimeFilter', [], {
	
	clean_required: false,
	
	init: function (t1, t2) {
		this.set_range(t1, t2)
	},
	
	on_chart_range_selected: function(t1, t2) {
		this.set_range(t1, t2)
	},
	
	set_range: function(t1, t2) {
		this.t1 = t1
		this.t2 = t2
	},
	
	make_url_part: function() {
		return Math.round(this.t1) + "/" + Math.round(this.t2)
	},
	
	set_chart: function() {}
	
})

groupspy.DataChartPresentation = new jsage.Class('DataChartPresentation', [], {
	
	init: function(series_description, data_transformers, data_filters, chart_options, chart_constructor, data_url) {
		this.chart_options = chart_options
		this.previous_filters_results = []
		this.prev_data_url = null
		this.ajax_token = 0
		var that = this
		chart_options.on_chart_range_select = function (t1, t2) { that.chart_range_selected(t1, t2) }
		this.chart = chart_constructor(series_description, chart_options)
		this.series_description = series_description
		var series_ids = {}
		for (i = 0, l = series_description.length; i < l; i++)
			series_ids[series_description[i].id] = true
		this.series = groupspy.DataSeriesGroup.create(series_ids, this, function (token) { that.chart_data_fetched(token) })
		
		this.data_transformers = data_transformers.slice()
		for (var i = 0, l = data_transformers.length; i < l; i++) {
			data_transformers[i].set_chart(this)
		}
		this.data_filters = data_filters.slice()
		for (i = 0, l = data_filters.length; i < l; i++) {
			data_filters[i].set_chart(this)
			this.previous_filters_results[i] = null
		}
		this.data_url = data_url
	},
	
	get_container: function() {
		return this.chart.container.parentNode
	},
	
	fetch_chart_data: function() {
		var path = []
		var clean_required = false
		for (var i = 0, l = this.data_filters.length; i < l; i++) {
			path[i] = this.data_filters[i].make_url_part()
			if (path[i] != this.previous_filters_results[i] && this.data_filters[i].clean_required)
				clean_required = true
			this.previous_filters_results[i] = path[i]
		}
		var filters_path = path.join("/") + "/"
		if (clean_required || this.data_url != this.previous_data_url) {
			this.series.clean()
			this.ajax_token++
		}
		this.previous_data_url = this.data_url
		if (this.series.update(this.data_url + filters_path, this.ajax_token)) {
			this.chart.showLoading()
		}
	},
	
	reset_axis_extremes: function() {
		if ('axis_x_min' in this.chart_options) {
			this.chart.xAxis[0].setExtremes(this.chart_options.axis_x_min, this.chart_options.axis_x_max)
		}
	},
	
	valid_token: function(token) {
		return this.ajax_token == token
	},
	
	chart_data_fetched: function(token) {
		if (token != this.ajax_token) {
			return
		}
		this.chart.hideLoading()
		this.transform_chart_data()
	},
	
	transform_chart_data: function() {
		for (var i = 0, l = this.series_description.length; i < l; i++) {
			var desc = this.series_description[i]
			var id = desc.id
			var data = this.series.get_data_by_id(id)
			for (var j = 0, lj = this.data_transformers.length; j < lj; j++)
				data = this.data_transformers[j].transform(data)
			this.chart.series[desc.index].setData(data)
		}		
	},
	
	chart_range_selected: function(t1, t2) {
		for (var i = 0, l = this.data_filters.length; i < l; i++) {
			if ('on_chart_range_selected' in this.data_filters[i])
				this.data_filters[i].on_chart_range_selected(t1, t2)
		}
		this.fetch_chart_data()
	}
	
})

groupspy.DataSeriesGroup = new jsage.Class('DataSeriesGroup', [], {
	
	last_url_requested: null,
	
	init: function(series_ids, parent, update_callback) {
		this.parent = parent
		this.update_callback = update_callback
		this.series = {}
		for (var id in series_ids)
			this.series[id] = groupspy.DataSeries.create()
	},
	
	get_data_by_id: function(id) {
		return this.series[id].get_data_copy()
	},
	
	update: function(url, token) {
		var that = this
		if (url != this.last_url_requested) {
			this.last_url_requested = url
			$.ajax({
				url: url,
				success: function(response) {
					if (!that.parent.valid_token(token))
						return
					for (var id in that.series) {
						var data = response.response[id].series
						that.series[id].receive_update(data)
					}
					that.update_callback(token)
				}
			})
			return true
		} else {
			return false
		}
	},
	
	clean: function(url) {
		for (var id in this.series)
			this.series[id].clean()
	}
	
})	

/*
 * the data must be an array of arrays. Each of subarrays is an observation of the form 
 * [data_label(for instance, timestamp or label), data_value(number), ... additional params can follow]
 */	
groupspy.DataSeries = new jsage.Class('DataSeries', [], {
	
	init: function() {
		this.data = []
	},
	
	clean: function() {
		this.data = []
	},
	
	get_data_copy: function() {
		return this.data.slice()
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
	}
		
})	

})
