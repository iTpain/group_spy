function ScriptLoader() {
	
}

ScriptLoader.prototype = {

	scripts_loaded: {},
	scripts_loading: {},
	
	modules_loaded: {},
	modules_loading: {},
	modules: {},
	
	loadDependencies: function(list, module) {
		this.modules[module.module_name] = module
		
		var all_loaded = true
		for (var i = 0, l = list.length; i < l; i++) {
			if (!(list[i] in this.modules_loaded)) {
				var dict = {}
				for (var j = 0, lj = list.length; j < lj; j++)
					dict[list[j]] = true
				this.modules_loading[module.module_name] = dict
				this.check_for_cycle_loading()
				all_loaded = false
				break
			}
		}
		
		if (all_loaded) {
			this.modules_loaded[module.module_name] = true
			module.execute()
			this.try_to_complete_modules()
			return
		}
		
		for (var i = 0; i < l; i++) 
			if (!(list[i] in this.scripts_loaded))
				this.load(list[i])
	},
	
	load: function(script_name) {
		if (!(script_name in this.scripts_loading)) {
			var script = document.createElement("script")
			script.src = window.PATH_TO_JAVASCRIPTS + script_name
			document.getElementsByTagName('head')[0].appendChild(script)
			script.onload = this.create_callback(this, script_name, script)
			this.scripts_loading[script_name] = true
		}
	},
	
	create_callback: function(that, script_name, script_obj) {
		return function() {
			script_obj.onload = null
			that.scripts_loaded[script_name] = true
			delete that.scripts_loading[script_name]
			that.try_to_complete_modules()
		}
	},
	
	try_to_complete_modules: function() {
		var trying = true
		while (trying) {
			trying = false
			outer: for (var e in this.modules_loading) {
				var deps = this.modules_loading[e]
				for (var d in deps) {
					if (!(d in this.modules_loaded)) {
						continue outer
					}
				}
				trying = true
				this.modules_loaded[e] = true
				delete this.modules_loading[e]
				this.modules[e].execute()
			}
		}
	},
	
	check_for_cycle_loading: function() {
		var graph = {}
		for (var e in this.modules_loading) {
			graph[e] = {}
			var loading = this.modules_loading[e]
			for (var p in loading) {
				graph[e][p] = true
			}
		}
		// tarjan's strongly connected components' search algorithm
		function tarjan_visit(v) {
			stack.push(v)
			dfsnum[v] = lowest[v] = counter++
			for (var w in graph[v]) {
				if (!(w in traversed_tree)) {
					traversed_tree[w] = true
					tarjan_visit(w)
					lowest[v] = Math.min(lowest[v], lowest[w])
				} else {
					lowest[v] = Math.min(lowest[v], dfsnum[w])
				}
			}
			
			if (lowest[v] == dfsnum[v]) {
				var component = []
				while (true) {
					var last_on_stack = stack[stack.length - 1]
					component.push(last_on_stack)
					stack.pop()
					delete graph[last_on_stack]
					for (var s in graph)
						delete graph[s][last_on_stack]
					if (last_on_stack == v)
						break
				}
				components.push(component)
				//console.log(component)
			}
		}
		
		var service_vertex = {}
		for (var e in graph)
			service_vertex[e] = true
		graph['i_am_service_vertex_cant_coincide_with_module_name'] = service_vertex
		var counter = 0
		var stack = []
		var dfsnum = {}
		var lowest = {}
		var traversed_tree = {'i_am_service_vertex_cant_coincide_with_module_name': true}
		var components = []
		tarjan_visit('i_am_service_vertex_cant_coincide_with_module_name')
		
		if (components.length != counter)
			throw ("ScriptLoader error -- cycle loading detected")
	}
	
}

window.jsage = {}
window.jsage.loader = new ScriptLoader()

function Module(module_name, to_load, func) {
	this.init(module_name, to_load, func)
}

Module.prototype = {
	
	init: function(module_name, to_load, func) {
		this.module_name = module_name
		this.executable = func
		jsage.loader.loadDependencies(to_load, this)
	},
		
	execute: function() {
		console.log("module " + this.module_name + " loaded")
		this.executable()
	}
	
}