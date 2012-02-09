new Module('utils/async-operations.js', ['lib/mixin.js', 'lib/eventbus.js'], function() {
	
groupspy.AjaxOperation = new jsage.Class('AjaxOperation', [jsage.GlobalMessagerObject], {	
	init: function (url, req_type, data, success, error, operation_details) {
		var that = this
		$.ajax({
			url: url,
			type: req_type,
			data: data,
			success: function(response) {
				var result = success(response)
				if (result)
					that.trigger(groupspy.messages.ajax_success, operation_details)
				else
					that.trigger(groupspy.messages.ajax_failure, operation_details)
			},
			error: function(response) {
				if (error)
					error(response)
				that.trigger(groupspy.messages.ajax_failure, operation_details)
			}
		})
	}	
})	

groupspy.AjaxOperationsManager = new jsage.Class('AjaxOperationsManager', [jsage.GlobalMessagingObject], {
	init: function () {
		this.operations_now = {}
		this.operations_count = 0
		this.id_counter = 0
		this.subscribe(groupspy.messages.ajax_success, this.oncomplete)
		this.subscribe(groupspy.messages.ajax_failure, this.oncomplete)
	},
	
	do_operation: function(url, req_type, data, success, error, details) {
		details = details || {}
		details.manager_id = this.id_counter++
		var operation = groupspy.AjaxOperation.create(url, req_type, data, success, error, details)
		this.operations_now[details.manager_id] = operation
		this.operations_count++
		this.trigger(groupspy.messages.active_ajax_count_changed, this.operations_count)
	},
	
	oncomplete: function(details) {
		this.operations_count--
		delete this.operations_now[details.manager_id]
		this.trigger(groupspy.messages.active_ajax_count_changed, this.operations_count)
	}
})
	
})
