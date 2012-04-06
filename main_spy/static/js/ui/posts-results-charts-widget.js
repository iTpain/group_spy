new Module('ui/posts-results-charts-widget.js', ['ui/charts-widget.js', 'ui/charts-creator.js', 'jsage/eventbus.js'], function() {

groupspy.PostsResultsChartsWidget = new jsage.Class('PostsResultsChartsWidget', [groupspy.ChartsWidget, jsage.GlobalMessagingObject], {
	
	init: function() {
		this.chart_creators = [this.create_strata_charts]
		this.subscribe(groupspy.messages.posts_results_frame_activate, this.on_activate)
		//this.init_ChartsWidget()
	},
	
	on_activate: function(group_id) {
		if (!this.built) {
			this.init_ChartsWidget()
			this.built = true
		}
		this.set_group(group_id)
	},
	
	create_strata_charts: function() {
		var strata_charts = [
			{
				container: 'social_activity_content_stratified',
				title: 'Результативность постов по типу приложений',
				strata_type: 'content_stratify',
				strata_labels: ['app', 'audio', 'doc', 'graffiti', 'link', 'no_attachment', 'note', 'page', 'photo', 'poll', 'posted_photo', 'video']
			}		
		]
		var charts = []
		for (var i = 0, l = strata_charts.length; i < l; i++) {
			var params = {
				width: 800,
				height: 500,
				title_x: -10,
				title_margin: 50
			}
			params.container = strata_charts[i].container
			params.title = strata_charts[i].title
			params.axis_x_categories = strata_charts[i].strata_labels
			var filters = [jsage.charts.DefaultTimeFilter.create(this.month_before, this.time_now)]
			charts.push(jsage.charts.DataChartPresentation.create(
				[
					{ label: "лайки", name: "лайки", id: "active_posts_likes", source: this.create_series('/group<GROUP_ID>/' + strata_charts[i].strata_type + '/', 'active_posts_likes', filters)},
					{ label: "комментарии", name: "комментарии", id: "active_posts_comments", source: this.create_series('/group<GROUP_ID>/' + strata_charts[i].strata_type + '/', 'active_posts_comments', filters) },
					{ label: "репосты", name: "репосты", id: "active_posts_reposts", source: this.create_series('/group<GROUP_ID>/' + strata_charts[i].strata_type + '/', 'active_posts_reposts', filters) }
				],
				[groupspy.AverageDataTransformer.create(false), groupspy.NormalizeDataTransformer.create(false)],
				params,
				create_column_chart
			))
		}
		return charts		
	}
	
	
})

$(document).ready(function () {
	var widget = groupspy.PostsResultsChartsWidget.create()
})


})