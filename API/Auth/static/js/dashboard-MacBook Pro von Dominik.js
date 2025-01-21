const dateOptions = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute:'2-digit'};
var datefrom = new Date();
datefrom.setDate(datefrom.getDate() - 1);
var dateto = new Date();

// Chart Variablen
var temperature_data = { labels: null, values: null };
var airpressure_data = { labels: null, values: null };
var airhumidity_data = { labels: null, values: null };
var light_data = { labels: null, values: null };

$(document).ready(function () {

	// Datetimepicker generieren
	
	let dateTimePickerFrom = new SimplePicker(".dateTimePickerFrom", {
	    zIndex: 1030
	});

	dateTimePickerFrom.reset(datefrom);
	$(".dateTimePickerInputFrom").val(datefrom.toLocaleString('de-DE', dateOptions));

	$(".dateTimePickerInputFrom").focus(function( ) {
	  	dateTimePickerFrom.open();
	});

	dateTimePickerFrom.on('submit', function(date, readableDate){
	  	$(".dateTimePickerInputFrom").val(date.toLocaleString('de-DE', dateOptions));
	  	datefrom = date;
	  	loadAllChartData();
	});

	let dateTimePickerTo = new SimplePicker(".dateTimePickerTo", {
	    zIndex: 1030
	});

	dateTimePickerTo.reset(dateto);
	$(".dateTimePickerInputTo").val(dateto.toLocaleString('de-DE', dateOptions));

	$(".dateTimePickerInputTo").focus(function( ) {
	  	dateTimePickerTo.open();
	});

	dateTimePickerTo.on('submit', function(date, readableDate){
	  	$(".dateTimePickerInputTo").val(date.toLocaleString('de-DE', dateOptions));
	  	dateto = date;
	  	loadAllChartData();
	});

	// Tabellen generieren
	$('#data_table').bootstrapTable();


	// Charts generieren	
	Chart.plugins.register({
    	afterDraw: function(chart) {
    		if ($.isEmptyObject(chart.data.datasets[0].data)) {
	      		var ctx = chart.chart.ctx;
	      		var width = chart.chart.width;
	      		var height = chart.chart.height
	      		chart.clear();

	      		ctx.save();
	      		ctx.textAlign = 'center';
	      		ctx.textBaseline = 'middle';
	      		ctx.font = "30px normal 'Helvetica Nueue'";
	      		ctx.fillText('Keine Daten', width / 2, height / 2);
	      		ctx.restore();
	    	}
	  	}
	});

	loadAllChartData();

    $(window).resize(function() {
	    createChart("temperature_chart", temperature_data);
	    createChart("airpressure_chart", airpressure_data);
	    createChart("airhumidity_chart", airhumidity_data);  
	    createChart("light_chart", light_data);
	});
});

function loadAllChartData() {
	loadChartData("/temperaturedata","temperature_chart", temperature_data);
	loadChartData("/airpressuredata","airpressure_chart", airpressure_data);
	loadChartData("/airhumiditydata","airhumidity_chart", airhumidity_data);
	loadChartData("/light","light_chart", light_data);
}

function loadChartData(url, elementId, data) {
	$.getJSON(url, { 
			from: datefrom.toISOString(), 
			to: dateto.toISOString() 
		},
		function(responseData) {
			if ($.isEmptyObject(responseData.data)) {
				data.values = null;
				data.labels = null;
			} else {
				data.values = responseData.data[0].map(function(v) {
			  		return parseFloat(v, 10);
				});

				data.labels = responseData.data[1];
			}
		

		createChart(elementId, data);
	});
}

function createChart(elementId, data) {
	if(window["chart_" + elementId] && window["chart_" + elementId] !== null) {
        window["chart_" + elementId].destroy();
    }

    var ctx = document.getElementById(elementId).getContext("2d");

	window["chart_" + elementId] = new Chart(ctx, {
        type: 'line',
        data: {
          	labels: data.labels,
          	datasets: [{
            	data: data.values,
            	lineTension: 0,
            	backgroundColor: 'transparent',
            	borderColor: '#01d1b2'
          	}]
        },
        options: {
        	animation: {
            	duration: 0
        	},
        	elements: {
                point:{
                    radius: 1
                }
            },
          	scales: {
            	yAxes: [{
              		ticks: {
                		beginAtZero: false
              		}
            	}],
            	xAxes: {
			        type: 'linear'
			    }
          	},
          	legend: {
            	display: false,
          	}
        }
    });
}