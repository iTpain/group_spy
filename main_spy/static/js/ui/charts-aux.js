new Module('ui/charts-aux.js', ['jsage/baseui.js'], function(){

groupspy.LabeledCheckbox = new jsage.Class('LabeledCheckbox', [jsage.BaseUIObject], {
	
	template: "<div style='display:inline; margin-left: 10px; margin-right:6px' data-tag='container'><div data-tag='label' style='display:inline; margin-right: 2px;'></div><input style='vertical-align:-2px' data-tag='box' type='checkbox'/></div>",
	
	init: function(label, checked, callback) {
		this.checked = checked || false
		this.callback = callback
		this.container = $()[0]
		this.elements = this.process_template(this.template)
		this.container = this.elements.container
		this.elements.label.innerHTML = label
		this.box = this.elements.box
		this.box.checked = this.checked
		$(this.box).bind('click', function(e) { callback() })
	}

})

groupspy.BaseDataTransformer = new jsage.Class('BaseDataTransformer', [], {
	
	set_chart: function(chart) {
		this.chart = chart
		this.chart_has_been_set()
	},
	
	params_changed: function(new_params) {
		this.set_params(new_params)
		this.chart.chart_data_fetched()
	},
	
	set_params: function(new_params) {
		this.params = new_params
	}
	
})

groupspy.CheckboxControlledTransformer = new jsage.Class('CheckboxControlledTransformer', [], {
	
	create_gui: function(label, checked) {
		var that = this
		this.gui = groupspy.LabeledCheckbox.create(label, checked, function(e) { that.onchange() })
	},
	
	onchange: function(e) {
		this.params_changed(this.gui.box.checked)
	},
	
	chart_has_been_set: function() {
		this.chart.get_container().appendChild(this.gui.container)
	}
	
})

groupspy.AverageDataTransformer = new jsage.Class('AverageDataTransformer', [groupspy.BaseDataTransformer, groupspy.CheckboxControlledTransformer], {
	
	init: function(checked) {
		this.create_gui('Среднее: ', checked)
		this.set_params(checked)
	},
	
	transform: function(data) {
		if (this.params)
			return data.map(function(d) { if (d[2] > 0) return [d[0], d[1] / d[2], d[2]]; else return [d[0], d[1], d[2]]})
		else
			return data
	}
	
})

groupspy.NormalizeDataTransformer = new jsage.Class('NormalizeDataTransformer', [groupspy.BaseDataTransformer, groupspy.CheckboxControlledTransformer], {
	
	init: function(checked) {
		this.create_gui('Нормализовать: ', checked)
		this.set_params(checked)
	},
	
	transform: function(data) {
		if (this.params) {
			var normalized = []
			var sum = 0
			for (var i = 0, l = data.length; i < l; i++)
				sum += data[i][1]
			for (i = 0; i < l; i++)
				normalized[i] = [data[i][0], data[i][1] / sum]
			return normalized
		} else {
			return data
		}
	}
	
})

groupspy.SlidingAverageDataTransformer = new jsage.Class('NormalizeDataTransformer', [groupspy.BaseDataTransformer, groupspy.CheckboxControlledTransformer], {

	init: function(checked, coef) {
		this.coef = coef || 0.02
		this.create_gui('Сгладить: ', checked)
		this.set_params(checked)
	},
	
	transform: function(data) {
		if (this.params) {
			var l = data.length
			var count = Math.round(l * this.coef)
			var min_t = data[0][0]
			var max_t = data[l - 1][0]
			var interval = (max_t - min_t) / (l - 1)
			var last_index_greater = 0
			var new_data = []
			for (var i = 0; i < l; i++) {
				var t = min_t + interval * i
				for (var j = last_index_greater; j < l; j++) {
					if (data[j][0] >= t)
						break
				}
				last_index_greater = j
				if (!(last_index_greater == 0 || last_index_greater >= l)) {
					var l1 = data[last_index_greater - 1][0]
					var l2 = data[last_index_greater][0]
					var value = data[last_index_greater - 1][1] * (t - l1) / (l2 - l1) + data[last_index_greater][1] * (l2 - t) / (l2 - l1)
					new_data.push([t, value])
				} else {
					new_data.push([t, data[last_index_greater][1]])
				}
			}
			return this.sliding_average(new_data, count)
		} else {
			return data
		}
	},
	
	sliding_average: function(data, count) {
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

})

groupspy.MultiChoiceFilter = new jsage.Class('MultiChoiceFilter', [jsage.BaseUIObject], {
	
	clean_required: true,
	
	init: function(options, labels) {
		var zipped = []
		for (var i = 0, l = options.length; i < l; i++)
			zipped[i] = {label: labels[i], data: options[i]}
		this.options = zipped
	},
	
	set_chart: function(chart) {
		var that = this
		this.chart = chart
		var div = $("<div style='margin-left:10px; margin-top:10px;'></div>")[0]
		this.gui = jsage.CheckboxList.create(div, this.options)
		chart.get_container().appendChild(div)
		$(this.gui).bind('change', function() { that.onchange() })
	},
	
	make_url_part: function() {
		var selected = this.gui.get_selected().join(",")
		return selected.length > 0 ? selected : 'all'
	},
	
	onchange: function() {
		this.chart.fetch_chart_data()
	}
	
})


})