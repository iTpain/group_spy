window.groupspy = {}

var messages_list = [
	'ajax_success',
	'ajax_failure',
	'active_ajax_count_changed'
]

groupspy.messages = {}
for (var i = 0, l = messages_list.length; i < l; i++)
	groupspy.messages[messages_list[i]] = messages_list[i]


