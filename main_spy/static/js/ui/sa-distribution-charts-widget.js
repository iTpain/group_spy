new Module('ui/sa-distribution-charts-widget.js', ['ui/charts-widget.js', 'ui/charts-creator.js', 'jsage/eventbus.js'], function() {

groupspy.SADistributionChartsWidget = new jsage.Class('SADistributionChartsWidget', [groupspy.ChartsWidget, jsage.GlobalMessagingObject], {
	
	init: function() {
		this.chart_creators = [this.create_strata_charts, this.create_distribution_charts]
		this.subscribe(groupspy.messages.sa_distribution_frame_activate, this.on_activate)
		//this.init_ChartsWidget()
	},
	
	on_activate: function(group_id) {
		if (!this.built) {
			this.init_ChartsWidget()
			this.built = true
		}
		this.set_group(group_id)
	},
	
	create_distribution_charts: function() {
		var strata_charts = [
			{
				container: 'sa-intraday-distribution',
				title: 'Внутридневное распределение соц. действий',
				key: 'hours',
				strata_labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
			},
			{
				container: 'sa-intraweek-distribution',
				title: 'Внутринедельное распределение соц. действий',
				key: 'days',
				strata_labels: [0, 1, 2, 3, 4, 5, 6]
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
					{ label: "лайки", name: "лайки", id: "likes", source: this.create_series('/group<GROUP_ID>/social_actions_distribution/likes/', strata_charts[i].key, filters)},
					{ label: "комментарии", name: "комментарии", id: "comments", source: this.create_series('/group<GROUP_ID>/social_actions_distribution/comments/', strata_charts[i].key, filters) }
				],
				[groupspy.NormalizeDataTransformer.create(true)],
				params,
				create_column_chart
			))
		}
		return charts		
	},
	
	create_strata_charts: function() {
		var strata_charts = [
			{
				container: 'sa-intraday-result',
				title: 'Внутридневная результативность постов',
				strata_type: 'intraday_stratify',
				strata_labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
			},
			{
				container: 'sa-intraweek-result',
				title: 'Внутринедельная результативность постов',
				strata_type: 'intraweek_stratify',
				strata_labels: [0, 1, 2, 3, 4, 5, 6]
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
	var widget = groupspy.SADistributionChartsWidget.create()
})


})