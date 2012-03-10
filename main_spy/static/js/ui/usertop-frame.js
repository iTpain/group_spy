new Module('ui/usertop-frame.js', ['jsage/eventbus.js', 'ui/main-screen.js', 'jsage/mixin.js'], function() {
$(document).ready(function () {
	
groupspy.UsertopFrame = new jsage.Class('UsertopFrame', [jsage.GlobalMessagingObject], {
	
	init: function() {
		this.subscribe(groupspy.messages.usertop_frame_activate, this.on_activate)
		this.create_table()
		this.ajax_token = 0
	},
	
	create_table: function() {
		$('#usertop-table').html('<table cellpadding="0" cellspacing="0" border="0" class="display" id="usertop-table-content"></table>');
		$('#usertop-table-content').dataTable({
			"iDisplayLength": 25,
			"aaData": [],
			"aoColumns": [
				{ "sTitle": "id", "sType": "html"},
				{ "sTitle": "Имя" },
				{ "sTitle": "Фамилия" },
				{ "sTitle": "Лайки", "sClass": "center" },
				{ "sTitle": "Комментарии", "sClass": "center" },
				{ "sTitle": "Всего действий", "sClass": "center" }
			],
			"oLanguage": {
				"sEmptyTable": "Нет данных",
				"oPaginate": {
					"sNext": "след.",
					"sPrevious": "пред.",
					"sFirst": "начало",
					"sLast": "конец"
				},
				"sLengthMenu": 'показать <select>'+
			        '<option value="25">25</option>'+
			        '<option value="50">50</option>'+
			        '<option value="100">100</option>'+
			        '<option value="-1">все</option>'+
			        '</select>',
			    "sSearch": "поиск",
			    "sInfo": "показаны записи (_START_ - _END_) из _TOTAL_",
			    "sInfoEmpty": ""
			}
		})   
		this.table = $('#usertop-table-content').dataTable()
	},
	
	on_activate: function(group_id) {
		this.ajax_token = group_id
		var token = group_id
		var that = this
		$.ajax({
			url: "group" + group_id + "/users_top/",
			success: function(data) {
				if (that.ajax_token != token)
					return
				that.table.fnClearTable()
				var table_data = []
				var data = data.response
				for (var p in data) {
					var row = data[p]
					table_data.push(["<a href='http://vk.com/id" + row.user__snid + "' target='_blank'/>" + row.user__snid + "</a>", row.user__first_name, row.user__last_name, row.likes, row.comments, row.likes + row.comments])
				}
				that.table.fnAddData(table_data)
				that.table.fnSort([[5, 'desc'], [2, 'asc'], [1, 'asc']])
			}
		})
	}
	
})

var frame = groupspy.UsertopFrame.create()
	
})	
})