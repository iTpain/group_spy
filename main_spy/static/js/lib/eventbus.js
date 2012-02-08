new Module('lib/eventbus.js', [], function () {

console.log("EventBus - pub/sub messaging system")

jsage.EventBus = function () {
	this.init()
}

jsage.EventBus.prototype = {
	
	event_types: null,
	
	init: function() {
		this.event_types = {}
	},
	
	subscribe: function(msg_type, obj) {
		if (!(msg_types in this.event_types)) {
			this.event_types[msg_type] = []
		}
		if (this.event_types[msg_type].indexOf(obj) < 0)
			this.event_types[msg_type].push(obj)
	},
	
	unsubscribe: function(msg_type, obj) {
		if (!(msg_type in this.event_types))
			return
		var subscribers = this.event_types[msg_types]
		var pos = subscribers.indexOf(obj)
		if (pos > -1) 
			subscribers.splice(pos, 1)
	},
	
	trigger: function(msg_type, msg) {
		console.log(msg_type)
		if (msg_type in this.event_types) {
			var subscribers = this.event_types[msg_types]
			for (var i = 0, l = subscribers.length; i < l; i++)
				subscribers[i](msg)
		}
	}

}

window.make_event_augmentation_factory = function (bus) { 
	return function augment_with_messaging(obj) {
		var p = obj.__proto__
		p.subscribe = function(msg_type) {
			bus.subscribe(msg_type, this)
		}
		p.unsubscribe = function(msg_type) {
			bus.unsubscribe(msg_type, this)
		}
		p.trigger = function(msg_type, msg) {
			bus.trigger(msg_type, msg)
		}
	}
}

window.jsage.eventbus_augmentation = make_event_augmentation_factory(new jsage.EventBus())
})
