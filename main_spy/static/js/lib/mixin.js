new Module('lib/mixin.js', [], function() {

console.log('Mixin.js - lightweight pseudoclasses implementation')

jsage.Class = function(name, methods, mixins) {
	this.init(name, methods, mixins)
}

jsage.Class.prototype = {
	
	init: function(name, mixins, methods) {
		this.name = name
		this.methods = methods || {}
		mixins = mixins || []
		this.create_prototype_object(mixins.slice(0, mixins.length))
	},
	
	create_prototype_object: function(mixins) {
		if ('init' in this.methods)
			this.methods['init_' + this.name] = this.methods.init	
		if ('free' in this.methods)
			this.methods['free_' + this.name] = this.methods.free
		var object = {}
		var all_methods = []
		var all_tables = mixins.map(function (m) { return {name: m.name, methods: m.proto_object} })
		all_tables.push(this)
		for (var i = 0, l = all_tables.length; i < l; i++) {
			var methods = all_tables[i].methods
			for (var m in methods) {
				if (m != 'init' && m != 'free') {
					if (m in object)
						console.log("warning -- overwriting property " + m + " for class " + this.name + " from mixin " + all_tables[i].name)
					object[m] = methods[m]
				}
			}
		}
		if ('init' in this.methods)
			object.init = this.methods.init
		if ('free' in this.methods)
			object.free = this.methods.free
		this.proto_object = object
	},
	
	create: function() {
		var object = {}
		object.__proto__ = this.proto_object
		if ('init' in this.proto_object)
			object.init.apply(object, arguments)
		return object
	} 
	
}

/*
 * 
 * Example usage
 * 
 * 
var A = new jsage.Class('A', [], {  
	init: function(x, y) {
		console.log(arguments)
		this.x = x
		this.y = y
		console.log('constructor A')
	},
	normalize: function() {
		var n = Math.sqrt(this.x * this.x + this.y * this.y)
		this.x /= n
		this.y /= n
	}
})

var B = new jsage.Class('B', [A], {
	init: function(x, y, c) {
		this.init_A(x, y)
		this.c = c
	},
	log: function() {
		this.normalize()
		console.log(this.x, this.y, this.c)
	}
})

var a = A.create(1, 1)
var b = B.create(10, 10, 'x')
b.log()

* 
* 
*/

})