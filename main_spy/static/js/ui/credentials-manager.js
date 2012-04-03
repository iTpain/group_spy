new Module('ui/credentials-manager.js', ['ui/main-screen.js'], function() {
	
$(document).ready(function () {

var ajax_operations_manager = window.ajaxOperationsManager

var CredentialsCell = new jsage.Class('CredentialsCell', [jsage.BaseView, jsage.BaseUIObject], {	
	template: "<div style='line-height:normal' data-tag='container'><div data-tag='api_id'></div><div data-tag='users' style='margin-left:10px; font-size:10px;'></div></div>",
	
	init: function() { 
		this.elements = this.process_template(this.template)
		this.root = this.elements.container
		this.listeners = []
		this.init_BaseView() 
	},
	
	on_data_update: function(provider) {
		var presentation = provider.present()
		var api_id = presentation.api_id
		var users = presentation.users
		this.elements.api_id.innerHTML = api_id
		this.elements.users.innerHTML = ''
		this.unbind_users()
		for (i = 0, l = users.length; i < l; i++) {
			var div = $("<div class='pointer''>" + users[i].viewer_id + "</div>")[0]
			var handler = this.create_handler(api_id, users[i].viewer_id)
			$(div).bind('dblclick', handler)
			$(div).css('color', users[i].valid ? 'green' : 'red')
			this.listeners[i] = [div, handler]
			this.elements.users.appendChild(div)
		}
	},
	
	create_handler: function(api_id, user_id) {
		return function() {
			remove_credentials_command(api_id, user_id)
		}
	},
	
	unbind_users: function() {
		for (var i = 0, l = this.listeners.length; i < l; i++)
			$(this.listeners[i][0]).unbind('dblclick', this.listeners[i][1])		
		this.listeners = []
	},
	
	free: function() { 
		this.unbind_users()
		this.free_BaseView() 
	}
		
})
var credentials_list = jsage.BaseList.create($("#system-credentials-list")[0], CredentialsCell, $("<div>Список аккаунтов пуст</div>")[0])
var credentials_set = jsage.EntitySet.create('credentials')
var credentials_collection = jsage.ArrayCollection.create(credentials_set)
credentials_list.bind_provider("default", credentials_collection)
var credentials_counter = 0

$.ajax({
	url: 'credentials/get/',
	success: function(response) {
		var credentials = response.response;
		var dict = {}
		for (var i = 0, l = credentials.length; i < l; i++) {
			var api_id = credentials[i].api_id
			if (!(api_id in dict)) {
				dict[api_id] = []
			}
			dict[api_id].push(credentials[i])
		}
		for (var p in dict) {
			var credentials = credentials_set.create_entity(credentials_counter++, {api_id: p, users: dict[p]})
			credentials_collection.add(credentials)
		}
		check_recommended_accounts_quantity()
		
	}
})

function remove_credentials_command(api_id, viewer_id) {
	ajax_operations_manager.do_operation(
		'/credentials/delete/' + api_id + '/' + viewer_id + '/', 'get', null,
		function (response) {
			var elem = credentials_set.filter(function(el) { return el.get("api_id") == api_id })[0]
			var elem_users = elem.get("users")
			for (var i = 0, l = elem_users.length; i < l; i++) {
				if (elem_users[i].viewer_id == viewer_id) {
					elem_users.splice(i, 1)
					break
				}
			}
			if (elem_users.length == 0)
				credentials_set.remove_elements([elem])
			else
				elem.set("users", elem_users)		
			check_recommended_accounts_quantity()
			return true
		}
	)
}

function add_credentials_command(api_id, viewer_id, sid, secret) {
	ajax_operations_manager.do_operation(
		'/credentials/add/' + api_id + '/' + viewer_id + '/' + sid + '/' + secret + '/', 'get', null,
		function (response) {
			if (response.errors.length > 0) {
				return response['errors']
			} else {
				var elems = credentials_set.filter(function(el) { return el.get("api_id") == api_id })
				if (elems.length == 0) {
					var credentials = credentials_set.create_entity(credentials_counter++, {api_id: api_id, users: [{viewer_id: viewer_id, valid: true}]})
					credentials_collection.add(credentials)					
				} else {
					var credentials = elems[0]
					var users = credentials.get("users")
					for (var i = 0, l = users.length; i < l; i++) {
						if (users[i].viewer_id == viewer_id)
							return true
					}
					users.push({viewer_id: viewer_id, valid: true})
					credentials.set("users", users)
				}
				return true
			}
		}, null, 'Adding credentials ' + api_id + ' ' + viewer_id
	)	
}

function check_recommended_accounts_quantity() {
	var all_credentials = credentials_set.filter()
	var count = 0
	for (var i = 0, l = all_credentials.length; i < l; i++) {
		for (var j = 0, lj = all_credentials[i].get("users").length; j < lj; j++) 
			if (all_credentials[i].get("users")[j].valid)
				count++
	}
	var recommended = Number($("#rec-credentials-count")[0].innerHTML)
	$("#credentials-count").css("color", recommended > count ? "red" : "green")
	$("#credentials-count")[0].innerHTML = String(count)
}

$("#credentials-add-button").bind("click", function() {
	var input = $("#credentials-input")[0]
	var value = input.value
	pieces = value.split("/")
	if (pieces.length >= 4) {
		add_credentials_command(pieces[0].trim(), pieces[1].trim(), pieces[2].trim(), pieces[3].trim())
		
	}
})

})
})