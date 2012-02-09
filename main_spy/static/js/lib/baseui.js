new Module('lib/baseui.js', ['lib/mixin.js'], function() {

console.log('BaseUI - basic UI components and utilities')

jsage.BaseUIObject = new jsage.Class('BaseUIObject', [], {
	
	process_template: function(template) {
		var DOM = $(template)[0]
		var elements = {}
		this.extract_elements(DOM, elements)
		return elements
	},
	
	extract_elements: function(dom, elements) {
		var attr_value = dom.getAttribute("data-tag")
		if (attr_value != null)
			elements[attr_value] = dom
		var children = dom.childNodes
		for (var i = 0, l = children.length; i < l; i++)
			this.extract_elements(children[i], elements)
	}

})

// error is {error: error_obj, operation_details: details_obj}
jsage.ErrorPanel = new jsage.Class('ErrorPanel', [jsage.BaseUIObject, jsage.GlobalMessagingObject], {
	
	template: '<div data-tag="container" style="position:fixed; right: 0px; bottom:50px"></div>',
	cell_template: '<div style="width: 400px; padding: 5px; background:#FF7D63; font-size:10px; font-family:courier"></div>',
	
	errors: [],
	cells: {},
	err_id: 0,
	last_time: 0,
	timeout: -1,
	
	init: function(max_errors, time_limit, error_messages, template, cell_template) {
		this.max_errors = max_errors
		this.time_limit = time_limit
		this.template = template || this.template
		this.cell_template = cell_template || this.cell_template
		this.elements = this.process_template(this.template)
		for (var i = 0, l = error_messages.length; i < l; i++) {
			this.subscribe(error_messages[i], this.onerror)
		}
		this.last_time = new Date().getTime()
	},
	
	onerror: function(err) {
		this.errors.push([this.err_id++, true])
		this.add_cell(err, this.err_id - 1)
		this.rebuild()
		var that = this
		var mark = this.err_id - 1
		setTimeout(function () {
			that.mark_error(mark)
			that.rebuild()
		}, this.time_limit)
	},
	
	add_cell: function (err, id) {
		var div = $(this.cell_template)[0]
		div.innerHTML = err.details.toString() + ": " + err.error.toString() 
		$(this.elements.container).prepend(div)
		this.cells[id] = div
	},
	
	mark_error: function(err_id) {
		for (var i = 0, l = this.errors.length; i < l; i++) {
			if (this.errors[i][0] == err_id) {
				this.errors[i][1] = false
			}
		}
	},
	
	rebuild: function() {
		var errors_to_remove = []
		while (this.errors.length > this.max_errors) {
			var err_desc = this.errors.shift()
			errors_to_remove.push(err_desc)
		}
		for (var i = 0, l = this.errors.length; i < l; i++) {
			err_desc = this.errors[i]
			if (!err_desc[1]) {
				this.errors[i] = this.errors[l - 1]
				this.errors.pop()
				i--
				l--
				errors_to_remove.push(err_desc)
			}
		}
		for (i = 0, l = errors_to_remove.length; i < l; i++) {
			err_desc = errors_to_remove[i]
			this.elements.container.removeChild(this.cells[err_desc[0]])
			delete this.cells[err_desc[0]]			
		}
	}
		
})

})