new Module('ui/group-posts.js', ['jsage/mvc.js', 'jsage/baseui.js'], function() {
	
$(document).ready(function () {

// view classes
var TextCategoryCell = new jsage.Class('TextCategoryCell', [jsage.BaseView, jsage.BaseUIObject], {	
	template: "<div class='text-category-box' data-tag='container'><div data-tag='name'></div><div data-tag='edit'><input type='text' data-tag='input'><span data-tag='ok'>OK</span><span data-tag='del'>X</span></div>",
	
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
				var div = $("<div class='text-category-box'>" + data.alias + "</div>")[0]
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
		update_text_category_command(data.id, this.elements.input.value)
	},
	
	on_del_click: function(e) {
		var data = this.data_providers['default'].present()
		delete_text_category_command(data.id)
	},
	
	on_double_click: function(e) {
		var data = this.data_providers['default'].present()
		this.elements.edit.style.display = 'block'
		this.elements.name.style.display = 'none'
	},
	
	free: function() { 
		$(this.elements.container).unbind('dblclick', this.dblclick)
		$(this.elements.ok).unbind('click', this.okclick)
		$(this.elements.del).unbind('click', this.delclick)
		this.free_BaseView() 
	}
		
})

var PostCell = new jsage.Class('PostCell', [jsage.BaseView, jsage.BaseUIObject], {	
	template: "<div data-tag='container'><div data-tag='text'></div><div data-tag='tags_list'></div></div>",
	
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
		while (this.tags_list.firstChild) {
			this.tags_list.removeChild(this.tags_list.firstChild)
		}
		$(this.tags_list.childNodes).unbind('dblclick', this.tag_click)
		var categories = presentation.relations
		for (i = 0, l = categories.length; i < l; i++) {
			var category = categories[i].text_category[0]
			var tag = $("<div>" + category.alias + "</div>")[0]
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

// commands
function add_text_category_command() {	
	var alias = $("#text-category-input")[0].value
	$.ajax({
		url: 'group' + GROUP_ID + '/category/add/',
		data: {alias: alias},
		type: 'post',
		success: function(response) {
			text_category_collection.add(text_category_set.create_entity(response.response.id, {alias: alias}))
		}
	})
}

function update_text_category_command(id, new_alias) {
	$.ajax({
		url: 'text_category' + id + '/update/',
		type: 'post',
		data: {alias: new_alias},
		success: function(response) {
			text_category_set.get_by_id(id).set('alias', new_alias, 2)
		}
	})
}

function delete_text_category_command(id) {
	$.ajax({
		url: 'text_category' + id + '/delete/',
		success: function(response) {
			text_category_set.remove_by_ids(id)
		}
	})		
}

function add_category_to_post_command(post_id, category_id) {
	var post = post_set.get_by_id(post_id)
	var category = text_category_set.get_by_id(category_id)
	var post_relations = post.get('relations')
	var category_relations = category.get('relations')
	for (var e in post_relations)
		if (e in category_relations)
			return
	$.ajax({
		url: 'text_category' + category_id + '/assoc/' + post_id + '/',
		success: function(response) {
			var new_link = post_category_relation_set.create_entity(ps_rel_counter++)
			new_link.set('post', post_id, 0)
			new_link.set('text_category', category_id)		
		}
	})
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
		$.ajax({
			url: 'text_category' + category_id + '/deassoc/' + post_id + '/',
			success: function(response) {
				post_category_relation_set.remove_by_ids(index)	
			}
		})
	}	
}

var posts_loaded = 0
var no_more_posts = false
var posts_loading = false
var ps_rel_counter = 0
function get_more_posts() {
	if (!no_more_posts && !posts_loading) {
		posts_loading = true
		$.ajax({
			url: 'group' + GROUP_ID + '/posts/' + posts_loaded + '/10/',
			success: function(response) {
				var data = response.response
				var added = []
				for (var i = 0, l = data.length; i < l; i++) {
					var d = data[i]				
					var entity = post_set.create_entity(d.id, {text: d.text})
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
				post_collection.add(added)
				posts_loaded += data.length
				if (data.length < 10)
					no_more_posts = true
				posts_loading = false
			},
			error: function() {
				posts_loading = true
			}
		})
	}
}

// view builder
var text_category_list = jsage.BaseList.create($("#tag-set")[0], TextCategoryCell, $("<div>Список категорий пуст</div>")[0])
text_category_list.bind_provider('default', text_category_collection)

var post_list = jsage.BaseList.create($("#posts-list")[0], PostCell, $("<div>Список постов пуст</div>")[0])
post_list.bind_provider('default', post_collection)
$("#posts-list").scroll(function(e) {
	if ($(e.target)[0].scrollHeight - $(e.target).height() - $(e.target).scrollTop() < $(e.target).height())
		get_more_posts()
})

// initial data load
$.ajax({
	url: 'group' + GROUP_ID + '/category/get_all/',
	success: function(response) {
		data = response.response
		var elements = []
		for (var i = 0, l = data.length; i < l; i++) {
			var tag = text_category_set.create_entity(data[i].id, {alias: data[i].alias})
			elements.push(tag)
		}
		text_category_collection.add(elements)
		get_more_posts()
	}	
})

// external functions
window.add_text_category = function() {
	add_text_category_command()
}

	
})		
})
