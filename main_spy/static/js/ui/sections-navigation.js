new Module('ui/sections-navigation.js', ['jsage/mixin.js', 'jsage/eventbus.js'], function () {
	
$(document).ready(function () {
jsage.global_bus.subscribe(groupspy.messages.groups_received, window, function(group_set) {

/* binding group sections events */
var tabs = {}
var elements = $("div.app-tab")
for (var i = 0, l = elements.length; i < l; i++) {
	var elem = elements[i]
	tabs[elem.getAttribute("data-navigate")] = elem
}

var set_window_hash = function(hash) {
	if (window.location.hash != hash)
		ignore_next_hash_change = true
	window.location.hash = hash
}
var ignore_next_hash_change = false
$(window).bind('hashchange', function(event) {
	if (ignore_next_hash_change) {
		ignore_next_hash_change = false
	} else {
		goto_by_hash()
	}
})

var goto_by_hash = function() {
	var hash = window.location.hash
	for (var e in states) {
		var response = states[e].hash_acceptable(hash)
		if (response) {
			change_state_to(states[e], response)
			break
		}
	}
}

var find_by_gid = function(gid) {
	return group_set.filter(function(e) { return e.get("gid") == gid })[0]	
}
var states = {
	
	tiles: {
		
		on_enter: function() {
			$("#groups-tiles").css("display", "block")
			$("#app-stats").css("display", "block")
			$("body").css("background", "#c1c1c1")
			set_window_hash("")
		},
		
		on_exit: function() {
			$("#groups-tiles").css("display", "none")
			$("#app-stats").css("display", "none")
		},
		
		hash_acceptable: function(h) {
			return (h == "" || h == "#") ? [] : false
		}
	},
	
	group: {
		
		cur_group: null,
		cur_section: elements[0],
		cur_content: null,
		sections_cache: {},
		
		on_enter: function(group, section) {
			section = section || this.cur_section
			this.cur_group = group || this.cur_group
			var id = section.getAttribute("data-navigate")
			
			$("#group-tabs").css("display", "block")
			$("#app-content").css("display", "block")
			$("#chosen-group-label").html(this.cur_group.alias)
			$("body").css("background", "#fff")

			$(this.cur_section).toggleClass("white")
			$(this.cur_content).css("display", "none")
			this.cur_section = section
			this.cur_content = $("#central-" + id)
			$(this.cur_section).toggleClass("white")
			$(this.cur_content).css("display", "block")
			
			jsage.global_bus.trigger(id + "_frame_activate", this.cur_group.gid)
			set_window_hash("#" + this.cur_group.gid + "-" + id)	
		},
		
		on_exit: function() {
			$("#group-tabs").css("display", "none")
			$("#app-content").css("display", "none")
			$(this.cur_content).css("display", "none")		
		},
		
		hash_acceptable: function(h) {
			var re = /#(\d+)-([a-z_]+)/
			var result = re.exec(h)
			if (result)
				return [find_by_gid(result[1]).present(), tabs[result[2]]]
			else
				return false
		}
		
	},
	
	group_comparison: {

		on_enter: function(g1, g2) {
			$("#app-content").css("display", "block")
			$("#app-stats").css("display", "block")
			$("#central-group-comparison").css("display", "block")
			$("body").css("background", "#fff")	
			set_window_hash("#compare" + g1.gid + "," + g2.gid)		
		},
		
		on_exit: function() {
			$("#app-content").css("display", "none")
			$("#app-stats").css("display", "none")
			$("#central-group-comparison").css("display", "none")			
		},
		
		hash_acceptable: function(h) {
			var re = /#compare(\d+),(\d+)/
			var result = re.exec(h)
			if (result)
				return [find_by_gid(result[1]).present(), find_by_gid(result[2]).present()]		
			else
				return false	
		}
		
	}
	
}
var cur_state = states.tiles

/*
 * bind state transition events' triggering for controls
 */
$("div.app-tab").bind("click", function(event) {
	var navigate_to = event.target.getAttribute("data-navigate")
	if (navigate_to.length > 0) {
		jsage.global_bus.trigger(groupspy.messages.group_entered, {group: null, section: tabs[navigate_to]})
	} else {
		jsage.global_bus.trigger(groupspy.messages.main_screen_entered)
	}
})

$("#group-comparison-close").bind("click", function() {
	jsage.global_bus.trigger(groupspy.messages.main_screen_entered)
})

/*
 * bind listeners for transition events
 */
var change_state_to = function(state, args) {
	cur_state.on_exit()
	cur_state = state
	cur_state.on_enter.apply(cur_state, args)
}

jsage.global_bus.subscribe(groupspy.messages.group_entered, window, function(event) {
	change_state_to(states.group, [event.group, event.section])
})

jsage.global_bus.subscribe(groupspy.messages.main_screen_entered, window, function (event) {
	change_state_to(states.tiles)
})

jsage.global_bus.subscribe(groupspy.messages.groups_clashed, window, function(event) {
	change_state_to(states.group_comparison, [event.g1, event.g2])
})

goto_by_hash()

})})

})