new Module('ui/groups.js', ['jsage/layouts/living-tiles.js', 'jsage/mvc.js', 'jsage/baseui.js'], function () {
$(document).ready(function () {

/*
 * view classes 
 */

var GroupEditor = new jsage.Class('GroupEditor', [jsage.BaseView], {
	
	init: function() {
		this.init_BaseView()
		var that = this
		$("#app-update-group").bind('click', function() { that.on_update_click() })
		$("#app-delete-group").bind('click', function() { that.on_delete_click() })
	},
	
	on_update_click: function() {
		var data = this.data_providers["default"].present()
		update_group_command(data.gid, $("#group_agency_input")[0].value, $("#group_brand_input")[0].value, this.data_providers["default"])
		$.closeDOMWindow({
			windowSourceID: '#group_info_updater'
		})
	},
	
	on_delete_click: function() {
		var data = this.data_providers["default"].present()
		delete_group_command(data.gid, this.data_providers["default"])
		this.unbind_provider("default")
		$.closeDOMWindow({
			windowSourceID: '#group_info_updater'
		})
	},
	
	on_data_update: function(provider) {
		if (provider == null)
			return
		var data = provider.present()
		$("#group_updater_header")[0].innerHTML = data.alias
		$("#group_agency_input")[0].value = data.agency
		$("#group_brand_input")[0].value = data.brand		
	}
	
})
var group_editor = GroupEditor.create()

var dragging_id = null
var GroupCell = new jsage.Class('GroupCell', [jsage.BaseUIObject, jsage.BaseView, jsage.GlobalMessagerObject], {
	
	template: "<div class='group-tile' data-tag='container'><div class='inner-group-tile'><div data-tag='alias'></div><div data-tag='brand'></div><div data-tag='agency'></div></div></div>",
	
	init: function() {
		this.elements = this.process_template(this.template)
		this.root = this.elements.container
		this.init_BaseView() 
		var that = this
		this.dblclick_handler = function() { that.on_dblclick() }
		$(this.root).bind('dblclick', this.dblclick_handler)
		this.make_draggable(this.root)
		this.make_droppable(this.root)
	},
	
	make_draggable: function(elements) {
		var that = this
		$(elements).draggable({
			containment: "body",
			helper: function(event) {
				var target = event.currentTarget
				var data = that.data_providers["default"].present()
				var div = $("<div class='blue'>" + data.alias + "</div>")[0]
				dragging_id = data
				return div
			}
		})
	},
	
	make_droppable: function(elements) {
		var that = this
		$(elements).droppable({
			drop: function(e) {
				var g1 = that.data_providers["default"].present()
				that.trigger(groupspy.messages.groups_clashed, {g1: g1, g2: dragging_id})
			}
		})
	},
	
	on_data_update: function(provider) {
		var data = provider.present()
		this.elements.alias.innerHTML = data.alias
		this.elements.brand.innerHTML = (data.brand.length > 0 ? data.brand : "бренд не указан")
		this.elements.agency.innerHTML = (data.agency.length > 0 ? data.agency : "агентство не указано")
		this.gid = data.gid
	},
	
	on_dblclick: function() {
		group_editor.bind_provider("default", this.data_providers["default"])
		$.openDOMWindow({
			windowSourceID: '#group_info_updater',
			height: 150
		})

	},
	
	free: function() {
		$(this.root).unbind('dblclick', this.dblclick_handler)
		this.free_BaseView()
	}
	
})

/*
 * structure
 */

var group_set = jsage.EntitySet.create('group')
var group_collection = jsage.ArrayCollection.create(group_set)
var group_tiles = jsage.BaseList.create($("#groups-tiles")[0], GroupCell)
jsage.layouts.LivingTiles.create($("#groups-tiles")[0], true, 0.15, 30, 30, ["blue"])
group_tiles.bind_provider("default", group_collection)
var id_counter = 0

/*
 * commands
 */
var add_group_command = function() {
	gid = $("#add-group-id")[0].value
	if (gid.length == 0)
		return;
	ajax_operations_manager.do_operation(
		'/group' + gid + '/add/', 'get', null,
		function (res) {
			if (res.errors.length > 0) {
				return res.errors
			} else {
				res = res.response
				var new_group = group_set.create_entity(id_counter++, {gid: res.gid, alias: res.alias, agency: '', brand: ''})
				group_collection.add(new_group)
				return true
			}
		},
		function (err) { },
		{ toString: function () { return 'Add-group ' + gid} }
	)
}

var update_group_command = function(gid, agency, brand, group) {
	ajax_operations_manager.do_operation(
		'/group' + gid + '/update_info/', 'post', {agency: encodeURIComponent(agency), brand: encodeURIComponent(brand)},
		function (data) {
			group.mset({agency: agency, brand: brand})
			return true
		}
	)	
}

var delete_group_command = function(gid, entity) {
	if (confirm('Вы уверены, что хотите удалить группу?'))
		ajax_operations_manager.do_operation(
			'/group' + gid + '/delete/', 'get', null,
			function (res) {
				if (res.errors.length > 0) {
					return res.errors
				} else {
					group_set.remove_by_ids(entity.id, 1)
					return true
				}
			},
			function (err) { },
			{ toString: function () { return 'Delete-group ' + gid} }
		)	
}

/*
 * initialization
 */

$.ajax({
	url: '/groups/get/',
	success: function(response) {
		var groups = response.response
		for (var i = 0, l = groups.length; i < l; i++) {
			var g = groups[i]
			var new_group = group_set.create_entity(id_counter++, {gid: g.gid, alias: g.alias, brand: g.brand, agency: g.agency})
			group_collection.add(new_group)
		}
	}
})

$("#add-group-div").bind("click", function () {
	add_group_command()
})
	
})	
})
