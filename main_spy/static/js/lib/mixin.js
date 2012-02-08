new Module('lib/mixin.js', [], function() {

console.log('Mixin.js - prototype toolset')

jsage.mixin = function (dst, src) {
	for (var e in src) {
		console.log(e)
		if (e in dst)
			throw ("Error while adding mixin " + src + " to " + dst + " -- coinciding property: " + e)
		dst[e] = src[e]
	}
}

jsage.extend = function (dst, src) {
	dst.prototype.__proto__ = src.prototype
}

})