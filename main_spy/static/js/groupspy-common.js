window.groupspy = {}

var messages_list = [
	'ajax_success',
	'ajax_failure',
	'active_ajax_count_changed',
	'group_frame_activate',
	'posts_frame_activate',
	'usertop_frame_activate',
	'sa_distribution_frame_activate',
	'group_added',
	'group_removed'
]

groupspy.messages = {}
for (var i = 0, l = messages_list.length; i < l; i++)
	groupspy.messages[messages_list[i]] = messages_list[i]

groupspy.counter = 0

