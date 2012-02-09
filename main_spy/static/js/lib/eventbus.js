new Module('lib/eventbus.js', ['lib/mixin.js'], function () {

console.log("EventBus - pub/sub messaging system")

jsage.EventBus = function () {
	this.init()
}

jsage.EventBus.prototype = {
	
	event_types: null,
	
	init: function() {
		this.event_types = {}
	},
	
	find: function(arr, obj, response) {
		for (var i = 0, l = arr.length; i < l; i++) {
			var elem = arr[i]
			if (elem[0] == obj && elem[1] == response)
				return i
		}
		return -1
	},
	
	subscribe: function(msg_type, obj, response) {
		if (!(msg_type in this.event_types)) {
			this.event_types[msg_type] = []
		}
		if (this.find(this.event_types[msg_type], obj, response) < 0)
			this.event_types[msg_type].push([obj, response])
	},
	
	unsubscribe: function(msg_type, obj, response) {
		if (!(msg_type in this.event_types))
			return
		var subscribers = this.event_types[msg_type]
		var pos = this.find(subscribers, obj, response)
		if (pos > -1) 
			subscribers.splice(pos, 1)
	},
	
	fully_unsubscribe: function(obj) {
		for (var e in this.event_types) {
			var subscribers = this.event_types[e]
			for (var i = 0, l = subscribers.length; i < l; i++) {
				if (subscribers[i][0] == obj) {
					subscribers[i] = subscribers[l - 1]
					subscribers.pop()
					i--
					l--
				}
			}
		}
	},
	
	trigger: function(msg_type, msg) {
		if (msg_type in this.event_types) {
			var subscribers = this.event_types[msg_type]
			for (var i = 0, l = subscribers.length; i < l; i++) {
				var obj = subscribers[i][0]
				var func = subscribers[i][1]
				func.apply(obj, [msg])
			}
		}
	}

}

jsage.MessagingObject = new jsage.Class("MessagingObject", [], {
		
	init: function(bus) {
		this.bus = bus
	},
	
	free: function() {
		this.bus.fully_unsubscribe(this)
	},
	
	subscribe: function(msg_type, response) {
		this.bus.subscribe(msg_type, this, response)
	},
	
	unsubscribe: function(msg_type, response) {
		this.bus.unsubscribe(msg_type, this, response)
	},
	
	trigger: function(msg_type, msg) {
		this.bus.trigger(msg_type, msg)
	}
	
})

var global_bus = new jsage.EventBus()
jsage.GlobalMessagingObject = new jsage.Class("GlobalMessagingObject", [jsage.MessagingObject], {
	bus: global_bus,
	
	free: function() {
		this.free_MessagingObject()
	}
})

jsage.GlobalMessagerObject = new jsage.Class("GlobalMessagerObject", [], {
	trigger: function(msg_type, msg) {
		global_bus.trigger(msg_type, msg)
	}
})

})
