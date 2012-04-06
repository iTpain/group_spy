new Module('ui/group-posts.js', ['jsage/mvc.js', 'jsage/baseui.js', 'jsage/eventbus.js', 'ui/main-screen.js'], function() {
	
$(document).ready(function () {

// parent window classes
var ajax_operations_manager = window.ajaxOperationsManager

// view classes
var TextCategoryCell = new jsage.Class('TextCategoryCell', [jsage.BaseView, jsage.BaseUIObject], {	
	template: "<div class='text-category-box tag' data-tag='container'><div data-tag='name'></div><div data-tag='edit'><input type='text' data-tag='input'><span class='tag-edit-ok' data-tag='ok'>OK</span><span class='tag-edit-del' data-tag='del'>X</span></div>",
	
	init: function() { 
		this.elements = this.process_template(this.template)
		this.root = this.elements.container
		this.elements.edit.style.display = 'none'
		var that = this
		this.dblclick = function(e) { that.on_double_click() }
		this.okclick = function(e) { that.on_ok_click() }
		this.delclick = function(e) { that.on_del_click() }
		$(this.elements.container).bind('dblclick', this.dblclick)
		$(this.elements.ok).bind('click', this.okclick)
		$(this.elements.del).bind('click', this.delclick)
		this.make_draggable()
		this.init_BaseView() 
	},
	
	make_draggable: function() {
		var that = this
		$(this.root).draggable({
			helper: function(event) {
				var data = that.data_providers['default'].present()
				var div = $("<div class='text-category-box tag'>" + data.alias + "</div>")[0]
				div.data_id = data.id
				return div
			}
		})
	},
	
	on_data_update: function(provider) {
		var presentation = provider.present()
		this.elements.name.innerHTML = this.elements.input.value = presentation.alias
	},
	
	on_ok_click: function(e) {
		var data = this.data_providers['default'].present()
		this.elements.edit.style.display = 'none'
		this.elements.name.style.display = 'block'	
		adjust_height()	
		if (data.alias != this.elements.input.value)
			update_text_category_command(data.id, this.elements.input.value)
	},
	
	on_del_click: function(e) {
		var data = this.data_providers['default'].present()
		if (confirm("Вы уверены?"))
			delete_text_category_command(data.id)
	},
	
	on_double_click: function(e) {
		var data = this.data_providers['default'].present()
		this.elements.edit.style.display = 'block'
		this.elements.name.style.display = 'none'
		adjust_height()
	},
	
	free: function() { 
		$(this.elements.container).unbind('dblclick', this.dblclick)
		$(this.elements.ok).unbind('click', this.okclick)
		$(this.elements.del).unbind('click', this.delclick)
		this.free_BaseView() 
	}
		
})

var PostCell = new jsage.Class('PostCell', [jsage.BaseView, jsage.BaseUIObject], {	
	template: "<div class='post-cell' data-tag='container'><div data-tag='date' class='post-cell-date'></div><div class='post-text' data-tag='text'></div><div class='post-cell-tags' data-tag='tags_list'></div></div>",
	
	init: function() { 
		this.elements = this.process_template(this.template)
		this.root = this.elements.container
		this.tags_list = this.elements.tags_list
		var that = this
		this.tag_click = function(e) { that.on_tag_click(e) }
		this.make_droppable()
		this.init_BaseView() 
	},
	
	make_droppable: function() {
		var that = this
		$(this.root).droppable({
			accept: '.text-category-box',
			drop: function(e) {
				var post_id = that.data_providers["default"].id
				add_category_to_post_command(post_id, e.toElement.data_id)
			}
		})
	},
	
	on_tag_click: function(e) {
		var post_id = this.data_providers['default'].id
		var category_id = e.target.data_category_id
		remove_category_from_post_command(post_id, category_id)
	},
	
	on_data_update: function(provider) {
		var presentation = provider.present(2)
		this.elements.text.innerHTML = presentation.text
		this.elements.date.innerHTML = presentation.date
		while (this.tags_list.firstChild) {
			this.tags_list.removeChild(this.tags_list.firstChild)
		}
		$(this.tags_list.childNodes).unbind('dblclick', this.tag_click)
		var categories = presentation.relations
		for (i = 0, l = categories.length; i < l; i++) {
			var category = categories[i].text_category[0]
			var tag = $("<div class='post-tag'>" + category.alias + "</div>")[0]
			tag.data_category_id = category.id
			this.tags_list.appendChild(tag)
		}
		
		$(this.tags_list.childNodes).bind('dblclick', this.tag_click)
	},
	
	free: function() { 
		this.free_BaseView() 
	}
		
})

// data model
var text_category_set = jsage.EntitySet.create('text_category', {
	relations: {entity_set: 'post_category_relation', pipe: 'text_category', propagate_delete: true}
})

var post_category_relation_set = jsage.EntitySet.create('post_category_relation', {
	post: {entity_set: 'post', pipe: 'relations'},
	text_category: {entity_set: 'text_category', pipe: 'relations'}
})

var post_set = jsage.EntitySet.create('post', {
	relations: {entity_set: 'post_category_relation', pipe: 'post'}
})

var text_category_collection = jsage.ArrayCollection.create(text_category_set)
var post_collection = jsage.ArrayCollection.create(post_set)
var filtered_post_collection = jsage.ArrayCollection.create(post_set)

// commands
function error_response_decorator(func) {
	return function(response) {
		if (response.errors.length > 0)
			return response.errors
		else
			return func(response)
	}
}

function add_text_category_command() {	
	var alias = $("#text-category-input")[0].value
	ajax_operations_manager.do_operation(
		'group' + GROUP_ID + '/category/add/', 'post', {alias: alias},
		error_response_decorator(function(response) {
			text_category_collection.add(text_category_set.create_entity(response.response.id, {alias: alias}))
			adjust_height()
			return true
		}),
		function (err) { },
		{ toString: function () { return 'Add-text-category ' + alias} }
	)
}

function update_text_category_command(id, new_alias) {
	ajax_operations_manager.do_operation(
		'text_category' + id + '/update/', 'post', {alias: new_alias},
		error_response_decorator(function(response) {
			text_category_set.get_by_id(id).set('alias', new_alias, 2)
			adjust_height()
			return true
		}),
		function (err) { },
		{ toString: function () { return 'Update-text-category ' + id} }
	)
}

function delete_text_category_command(id) {
	ajax_operations_manager.do_operation(
		'text_category' + id + '/delete/', 'get', null,
		error_response_decorator(function(response) {
			text_category_set.remove_by_ids(id)
			adjust_height()
			return true
		}),
		function (err) { },
		{ toString: function () { return 'Delete-text-category ' + id} }
	)		
}

function add_category_to_post_command(post_id, category_id) {
	var post = post_set.get_by_id(post_id)
	var category = text_category_set.get_by_id(category_id)
	var post_relations = post.get('relations')
	var category_relations = category.get('relations')
	for (var e in post_relations)
		if (e in category_relations)
			return
	ajax_operations_manager.do_operation(
		'text_category' + category_id + '/assoc/' + post_id + '/', 'get', null,
		error_response_decorator(function(response) {
			var new_link = post_category_relation_set.create_entity(ps_rel_counter++)
			new_link.set('post', post_id, 0)
			new_link.set('text_category', category_id)	
			return true	
		}),
		function (err) { },
		{ toString: function () { return 'Add-category-to-post ' + post_id + ' ' + category_id} }
	)
}

function remove_category_from_post_command(post_id, category_id) {
	var post = post_set.get_by_id(post_id)
	var category = text_category_set.get_by_id(category_id)
	var post_relations = post.get('relations')
	var category_relations = category.get('relations')
	var index = -1
	for (var e in post_relations)
		if (e in category_relations)
			index = e
	if (index != -1) {
		ajax_operations_manager.do_operation(
			'text_category' + category_id + '/deassoc/' + post_id + '/', 'get', null,
			error_response_decorator(function(response) {
				post_category_relation_set.remove_by_ids(index)	
				return true
			}),
			function (err) { },
			{ toString: function () { return 'Remove-category-from-post ' + post_id + ' ' + category_id} }
		)
	}	
}

function change_posts_filter_command(new_filter_on) {
	if (filter_on != new_filter_on) {
		filter_on = new_filter_on
		if (filter_on) {
			post_list.unbind_provider('default', post_collection)
			post_list.bind_provider('default', filtered_post_collection)
		} else {
			post_list.unbind_provider('default', filtered_post_collection)
			post_list.bind_provider('default', post_collection)			
		}
	}
}

var filter_on = false
var ps_rel_counter = 0
function get_posts_fetcher(filter, collection) {
	var posts_loaded = 0
	var no_more_posts = false
	var posts_loading = false
	var last_group_id = 0
	
	return function () {
		if (last_group_id != GROUP_ID) {
			posts_loaded = 0
			no_more_posts = false
			last_group_id = GROUP_ID
			posts_loading = false
		}
		var token = GROUP_AJAX_TOKEN
		if (!no_more_posts && !posts_loading) {
			posts_loading = true
			$.ajax({
				url: 'group' + GROUP_ID + '/posts/' + posts_loaded + '/100/' + filter + '/',
				success: function(response) {
					if (token != GROUP_AJAX_TOKEN)
						return
					var data = response.response
					var added = []
					var filtered_added = []
					for (var i = 0, l = data.length; i < l; i++) {
						var d = data[i]				
						var entity = post_set.create_entity(d.id, {text: d.text.replace(/(<([^>]+)>)/ig, " "), date: d.date})
						var relations = []
						for (var j = 0, lj = d.categories.length; j < lj; j++) {
							var rel = post_category_relation_set.create_entity(ps_rel_counter++)
							rel.set("text_category", d.categories[j], 0)
							rel.set("post", d.id, 0)
							relations.push(rel.id)
						}
						entity.set("relations", relations)
						added.push(entity)
					}
					collection.add(added)
					posts_loaded += data.length
					if (data.length < 100)
						no_more_posts = true
					posts_loading = false
				},
				error: function() {
					posts_loading = true
				}
			})
		}
	}
}
var all_posts_loader = get_posts_fetcher("all", post_collection)
var group_posts_loader = get_posts_fetcher("group", filtered_post_collection)

// view builder
var text_category_list = jsage.BaseList.create($("#tag-set")[0], TextCategoryCell, $("<div>Список категорий пуст</div>")[0])
text_category_list.bind_provider('default', text_category_collection)

var post_list = jsage.BaseList.create($("#posts-list")[0], PostCell, $("<div>Список постов пуст</div>")[0])
post_list.bind_provider('default', post_collection)
$("#posts-list").scroll(function(e) {
	if ($(e.target)[0].scrollHeight - $(e.target).height() - $(e.target).scrollTop() < $(e.target).height()) {
		if (filter_on)
			group_posts_loader()
		else
			all_posts_loader()
	}
})

// external functions
window.add_text_category = function() {
	add_text_category_command()
}

$("#filter-box input").bind("change", function(e) {
	change_posts_filter_command(e.target.checked)
})

// resizing
function adjust_height () {
	var h = $(window).height()
	var tags_h = $("#tag-set").height()
	$("#posts-list").css({'height': Math.max(0, h - tags_h - 232) + "px"})
}
$(window).resize(adjust_height)
adjust_height()

// fucking widget itself
var GROUP_ID = 0
var GROUP_AJAX_TOKEN = 0
groupspy.PostsFrame = new jsage.Class('PostsFrame', [jsage.GlobalMessagingObject], {
	
	init: function() {
		this.subscribe(groupspy.messages.posts_frame_activate, this.on_activate)
	},
	
	on_activate: function(gid) {
		GROUP_ID = gid
		var token = ++GROUP_AJAX_TOKEN
		post_collection.remove_all()
		filtered_post_collection.remove_all()
		text_category_collection.remove_all()
		post_set.hard_clear()
		post_category_relation_set.hard_clear()
		text_category_set.hard_clear()		
		$.ajax({
			url: 'group' + GROUP_ID + '/category/get_all/',
			success: function(response) {
				if (token != GROUP_AJAX_TOKEN)
					return
				data = response.response
				var elements = []
				for (var i = 0, l = data.length; i < l; i++) {
					var tag = text_category_set.create_entity(data[i].id, {alias: data[i].alias})
					elements.push(tag)
				}
				text_category_collection.add(elements)
				adjust_height()
				all_posts_loader()
				group_posts_loader()
			}	
		})
	}
	
})

var widget = groupspy.PostsFrame.create()

	
})		
})
