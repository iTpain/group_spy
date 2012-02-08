new Module('lib/baseui.js', [], function() {

console.log('BaseUI - ui helpers toolbox')

jsage.BaseUIObject = function() {}

jsage.BaseUIObject.prototype = {
	
	process_template: function(template) {
		var DOM = $(template)[0]
		var elements = {}
		this.extract_elements(DOM, elements)
		return elements
	},
	
	extract_elements: function(dom, elements) {
		var attr_value = dom.getAttribute("data-tag")
		if (attr_value != null)
			elements[attr_value] = dom
		var children = dom.childNodes
		for (var i = 0, l = children.length; i < l; i++)
			this.extract_elements(children[i], elements)
	}

}

})