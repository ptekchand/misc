// TODO: Display the following on a chart:
// Timeline of the days of the month. A bar chart above each day for total expense.
// Label: Month/Year

// Separate chart:
// List of labels and a bar chart for their total.
// "Circle chart" for each label where the radius is the total for it.
// Maybe also a pie chart?
$(function () {
	function fetchMonthKeyAndChart(month_key) {
		//assert( YYYYMM matches (month_key) )
		$.ajax('/chart/'+month_key)
			.done(function(responseData) {
				//console.log("Received: ", responseData.slice( 0, 100 ))
				var responseJSON = JSON.parse(responseData);
				if(responseJSON['status'] == 1)
					var highchart_ajax_data = responseJSON['data'];
					// TODO: Change the x position of the pie chart based on the lowest y value in series[0] and closest to center of the graph.
					//highchart_ajax_data.series[1].center[0]
					$('#highchart-container1').highcharts(highchart_ajax_data);
			});
	}
	
	/* Fetch some default chart data using an ajax request */
	fetchMonthKeyAndChart('201410');
	
	// Get the list of months we have data for an make links for them.
	function fetchMonthKeysForChart() {
		$.ajax('/month_keys')
		.done(function(responseData) {
			//console.log("Received: ", responseData.slice( 0, 100 ))
			var responseJSON = JSON.parse(responseData);
			if(responseJSON['status'] == 1)
				var month_keys_data = responseJSON['data'];
				month_keys_html = "Month keys: ";
				// TODO: Sort this list?
				for(var month_key of month_keys_data) { // for ... of ECMAScript 2015 (ES6) standard
					month_keys_html += '<a href="#" class="month_key_fetch">'+month_key+'</a> '
				}
				$('#month-keys').html(month_keys_html);
				
				$('.month_key_fetch').on('click', function() {
					//console.log("on click: "+ $(this).html());
					var fetch_month_key = $(this).html();
					fetchMonthKeyAndChart(fetch_month_key);
				});
		});
	}
	fetchMonthKeysForChart();
	
	function fetchBalancesGraph(){
		$.ajax('/balance/')
			.done(function(responseData) {
				//console.log("Received: ", responseData.slice( 0, 100 ))
				var responseJSON = JSON.parse(responseData);
				if(responseJSON['status'] == 1)
					var highchart_ajax_data = responseJSON['data'];
					// TODO: Change the x position of the pie chart based on the lowest y value in series[0] and closest to center of the graph.
					//highchart_ajax_data.series[1].center[0]
					$('#highchart-container2').highcharts(highchart_ajax_data);
			});
	}
	fetchBalancesGraph();
	
	
	var test_data = {
        "chart": {
            "type": 'column'
        },
        "subtitle": {
          "text": "Month: 201410",
          "x": -20
        },
        "xAxis": {
          "type": "category"
          /*"categories": [
            "training",
            "transportation",
            "alcohol",
            "entertainment",
            "food",
            "travel",
            "hotel",
            "no_label",
            "phone",
            "beer",
            "personal",
            "groceries"
          ]*/
        },
        "title": {
          "text": "Label Aggregates",
          "x": -20
        },
        "series": [
          {
			"type": "column",
            "name": "label sums",
			/* try changing to a single xAxis with the labels here. http://www.highcharts.com/demo/column-drilldown/dark-unica */
            /*"data": [ 0.0, 790.0, 205.1, 0.0, 1153.0, 0.0, 0.0, 0.0, 0.0, 0.0, 312.0, 1784.53 ],*/
			/* Try using the combined?shared tooltip?*/
            "data": [
              { "name":"training", "y":0.0, "drilldown": null, color: Highcharts.getOptions().colors[0] },
              { "name":"transportation", "y":790.0, "drilldown": null, color: Highcharts.getOptions().colors[1] },
              { "name":"alcohol", "y":205.1, "drilldown": null, color: Highcharts.getOptions().colors[2] },
              { "name":"entertainment", "y":0.0, "drilldown": null, color: Highcharts.getOptions().colors[3] },
              { "name":"food", "y":1153.0, "drilldown": null, color: Highcharts.getOptions().colors[4] },
              { "name":"travel", "y":0.0, "drilldown": null, color: Highcharts.getOptions().colors[5] },
              { "name":"hotel", "y":0.0, "drilldown": null, color: Highcharts.getOptions().colors[6] },
              { "name":"no_label", "y":0.0, "drilldown": null, color: Highcharts.getOptions().colors[7] },
              { "name":"phone", "y":0.0, "drilldown": null, color: Highcharts.getOptions().colors[8] },
              { "name":"beer", "y":0.0, "drilldown": null, color: Highcharts.getOptions().colors[9] },
              { "name":"personal", "y":312.0, "drilldown": null, color: Highcharts.getOptions().colors[10] },
              { "name":"groceries", "y":1784.53, "drilldown": null, color: Highcharts.getOptions().colors[11] },
            ],
            "tooltip": {
              "valueSuffix": " SEK",
			  "followPointer": false,
			  "snap":0
            }/*,
 			"zIndex":10*/
          },
          {
            "type": "pie",
            "name": "SpendSave",
            "center": [ 700, 50 ],
            "dataLabels": {
              "enabled": false
            },
            "data": [
              {
                "y": 2805.0,
                "name": "SalWithoutRent"
              },
              {
                "y": 13500.0,
                "name": "Paybacks"
              },
              {
                "y": 16400.0,
                "name": "RentNeg"
              }
            ],
            "tooltip": {
              "valueSuffix": " SEK",
			  "followPointer": false,
			  "snap": 0
            },
            "showInLegend": false,
            "size": 100/*,
			"zIndex":20*/
          }
        ],
        "legend": {
          "enabled": false,
          "verticalAlign": "middle",
          "align": "right",
          "layout": "vertical",
          "borderWidth": 0
        },
        "plotOptions": {
            "column": {
                "stickyTracking": false
            },
            "pie": {
                "stickyTracking": false
            }
        }		
	};
	test_data_b = {
		  "subtitle": {
			"text": "",
			"x": -20
		  },
		  "xAxis": {
			"categories": [
			  "201410",
			  "201411",
			  "201412",
			  "201409",
			  "201408",
			  "201511",
			  "201508",
			  "201509",
			  "201510",
			  "201502",
			  "201503",
			  "201501",
			  "201506",
			  "201507",
			  "201504",
			  "201505"
			]
		  },
		  "title": {
			"text": "Balances",
			"x": -20
		  },
		  "series": [
			{
			  "data": [
				0.0,
				83775.47,
				91886.96,
				0.0,
				0.0,
				234248.4,
				168228.76,
				184880.46,
				234748.62,
				109604.49,
				119493.35,
				87795.53,
				135115.18,
				145813.72,
				112429.17,
				125191.33
			  ],
			  "name": "Balances"
			}
		  ],
		  "yAxis": {
			"plotLines": [
			  {
				"color": "#808080",
				"width": 1,
				"value": 0
			  }
			],
			"title": {
			  "text": "Amount (SEK)"
			}
		  },
		  "chart": {
			"type": "line"
		  },
		  "tooltip": {
			"valueSuffix": " SEK"
		  },
		  "legend": {
			"verticalAlign": "middle",
			"align": "right",
			"layout": "vertical",
			"borderWidth": 0
		  }
		};
	//$('#highchart-container-test').highcharts(test_data_b);

});