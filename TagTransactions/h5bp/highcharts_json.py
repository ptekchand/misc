#!C:/Python27/Python.exe
# -*- coding: utf-8 -*-
# This Python file uses the following encoding: utf-8

# C:\Python27\python.exe highcharts_json.py

# Data exported to json using parse_hb.py
# Package that into json data suitable for drawing with highcharts_json

#------------------------------------------------------------------------------
import sys
import codecs
if sys.stdout.encoding != 'cp850':
	sys.stdout = codecs.getwriter('cp850')(sys.stdout, 'strict')
if sys.stderr.encoding != 'cp850':
	sys.stderr = codecs.getwriter('cp850')(sys.stderr, 'strict')
#------------------------------------------------------------------------------

from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse
import json
import os

import math #ceil

def get_default_highchart_dict():
	return {
        "chart": {
            "type": 'line' # 'column' (vertical), 'bar' (horizontal)
        },
        "title": {
            "text": 'Monthly Temperature for June 2014',
            "x": -20 #center
        },
        "subtitle": {
            "text": '"Source": WUnderground.com',
            "x": -20
        },
        "xAxis": {
            "categories": [] # range(1, 30)
        },
        "yAxis": {
            "title": {
                "text": 'Temperature (°C)'
            },
            "plotLines": [{
                "value": 0,
                "width": 1,
                "color": '#808080'
            }]
        },
        "tooltip": {
            "valueSuffix": '°C'
        },
        "legend": {
            "layout": 'vertical',
            "align": 'right',
            "verticalAlign": 'middle',
            "borderWidth": 0
        },
        "series": [{
            "name": 'Avg',
            "data": []
        }]
    }
class GetHandler(BaseHTTPRequestHandler):
	
	def do_GET(self):
		parsed_path = urlparse.urlparse(self.path)
		message_parts = [
				'CLIENT VALUES:',
				'client_address=%s (%s)' % (self.client_address,
											self.address_string()),
				'command=%s' % self.command,
				'path=%s' % self.path,
				'real path=%s' % parsed_path.path,
				'query=%s' % parsed_path.query,
				'request_version=%s' % self.request_version,
				'',
				'SERVER VALUES:',
				'server_version=%s' % self.server_version,
				'sys_version=%s' % self.sys_version,
				'protocol_version=%s' % self.protocol_version,
				'',
				'HEADERS RECEIVED:',
				]
		for name, value in sorted(self.headers.items()):
			message_parts.append('%s=%s' % (name, value.rstrip()))
		message_parts.append('')
		message_str = '\r\n'.join(message_parts)
		
		response_obj = {
			"status": 0,
			"data": message_str
		}
		
		message = ""
		#print "DEBUG: parse_path: ({})".format(parsed_path.path)
		current_dir = os.path.realpath('.')
		#print "DEBUG: current_dir: {}".format(current_dir)
		local_sub_dir_file_path = None
		full_parsed_path = os.path.realpath("{}{}".format(current_dir, parsed_path.path))
		#print "DEBUG: full_parsed_path: {}".format(full_parsed_path)
		if os.path.exists(full_parsed_path) and full_parsed_path.find(current_dir)==0:
			local_sub_dir_file_path = full_parsed_path
			local_sub_dir_file_path = parsed_path.path[1:] # Or just drop the /
		
		service_routes = ["/chart/", "/month_keys", "/balance/"]
		is_service_route = False
		for sroute in service_routes:
			if parsed_path.path.find(sroute) == 0:
				is_service_route = True
		if is_service_route:
			parsed_data_by_month_with_label_sums = 'js/month_transactions.json'
			if os.path.exists(parsed_data_by_month_with_label_sums):
				with open(parsed_data_by_month_with_label_sums, 'r') as chart_json_file_handle:
					by_month_with_label_sums = json.load(chart_json_file_handle)
					
					if parsed_path.path.find("/chart/") == 0:
						self.get_chart(response_obj, by_month_with_label_sums, parsed_path)
					elif parsed_path.path.find("/month_keys") == 0:
						self.get_month_keys(response_obj, by_month_with_label_sums)
					elif parsed_path.path.find("/balance/") == 0:
						self.get_balances(response_obj, by_month_with_label_sums)
						
					message = json.dumps(response_obj);
					
		elif local_sub_dir_file_path is not None:
			if local_sub_dir_file_path == '':
				local_sub_dir_file_path = 'index.html'
			file_mode = 'rb'
			text_extensions = ['.html', '.json', '.js', '.css', '.txt']
			for te in text_extensions:
				if local_sub_dir_file_path.endswith(te):
					file_mode = 'r'
					break
			with open(local_sub_dir_file_path, file_mode) as local_sub_dir_file_handle:
				#response_obj['data'] = local_sub_dir_file_handle.read()
				#response_obj['status'] = 1
				message = local_sub_dir_file_handle.read()
		else:
			message = json.dumps(response_obj);
		
		self.send_response(200)
		self.end_headers()
		self.wfile.write(message)
		return
	
	def get_chart(self, response_obj, by_month_with_label_sums, parsed_path):
		data_found = False
		chart_json_res_path = ""; # "resources/intermediate/Gui/" # FIXME: Set to a path based on the project's resources path.
		chart_json_name = parsed_path.path[7:] # Requested chart: "201409" # TODO: Or a label name <- Try and send the last 12 months of aggregates for that label.
	
		month_key = chart_json_name
		if month_key in by_month_with_label_sums:
			data_found = True
			
			highchart_dict = get_default_highchart_dict()
			# create_chart_data(by_month_with_label_sums[month_key])
			highchart_dict['chart']['type'] = "column"
			highchart_dict['title']['text'] = "Label Aggregates"
			highchart_dict['subtitle']['text'] = "Month: {}".format(month_key)
			highchart_dict['tooltip']['valueSuffix'] = " SEK"
			#highchart_dict['yAxis']['title']['text'] = "Amount (SEK)"
			highchart_dict['yAxis'] = {}
			highchart_series_0 = highchart_dict['series'][0]
			highchart_series_0['name'] = 'label sums'
			highchart_series_0['data'] = []
			hichart_xAxis = highchart_dict['xAxis']
			show_overlay = True
			if show_overlay:
				highchart_series_0['type'] = "column"
			else:
				hichart_xAxis['categories'] = []


			lsums_data = by_month_with_label_sums[month_key]['lsums']
			skip_label_list = ['salary', 'rent', 'payback'] # Draw these as overlay pie (bubble) charts with scaled radius. And/or show a bubble for carry over amount (Sum of everything +/-) - "saving" or "balance"
			# FIXME: We need to generate JS here instead.
			# To better handle theme changes.
			# http://api.highcharts.com/highcharts#colors
			HighchartsOptionsColors = ['#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9', 
'#f15c80', '#e4d354', '#2b908f', '#f45b5b', '#91e8e1']
			colorIdx = 0
			for lname in lsums_data:
				if lname in skip_label_list:
					continue
				lsum = lsums_data[lname]
				rounded_value = -math.ceil(lsum*100)/100
				if show_overlay:
					data_row = {
						"name": lname,
						"y": rounded_value,
						#"drilldown": None, #null,
						"color": HighchartsOptionsColors[colorIdx] # JS: Highcharts.getOptions().colors[0]
					}
					highchart_series_0['data'].append( data_row )
					colorIdx += 1
					if colorIdx == len(HighchartsOptionsColors):
						colorIdx = 0
				else:
					hichart_xAxis['categories'].append(lname)
					highchart_series_0['data'].append( rounded_value )
				
			# TODO: Parse and receive actual spend from transactions? (Since labels are applied multiple times)
			# http://www.highcharts.com/demo/column-drilldown/dark-unica
			highchart_series_1 = highchart_dict['series'].append({
						"type": 'pie',
						"name": 'SpendSave',
						"data": [
							{'name':'SalWithoutRent', 'y': (lsums_data['salary']+lsums_data['rent'])},
							{'name':'Paybacks', 'y': lsums_data['payback']},
							{'name':'RentNeg', 'y': -lsums_data['rent']},
						],
						"center": [700, 150], # Find x coord using lowest y value?
						"size": 100,
						"showInLegend": False,
						"dataLabels": {
							"enabled": False
						},
						"tooltip": {
							"valueSuffix": " SEK",
							"followPointer": False,
							"snap": 0
						},
					})
			
			response_obj['data'] = highchart_dict
			response_obj['status'] = 1
			#print json.dumps(highchart_dict, indent=2)
		if data_found == False:
			# If you try to read the value as respon_obj.data:
			#AttributeError: 'dict' object has no attribute 'data'
			# Remember, this is Python. Not Javascript.
			response_obj['data'] = "{}\r\nUnable to find chart json data: {}".format(response_obj['data'], chart_json_file_path)
			#message = json.dumps(response_obj); # Done outside path processing if block
	
	def get_month_keys(self, response_obj, by_month_with_label_sums):
		#month_key_list = []
		#for month_key in by_month_with_label_sums:
		#	month_key_list.append(month_key)
		month_key_list = sorted(by_month_with_label_sums)
		response_obj['data'] = month_key_list
		response_obj['status'] = 1
	
	def get_balances(self, response_obj, by_month_with_label_sums):
		# TODO: Check why we don't see the line chart on the page.
		# Build a basic line chart with the balance values
		highchart_dict = get_default_highchart_dict()
		# create_chart_data(by_month_with_label_sums[month_key])
		highchart_dict['chart']['type'] = "line"
		highchart_dict['title']['text'] = "Balances"
		highchart_dict['subtitle']['text'] = ""# "Month: {}".format(month_key)
		highchart_dict['tooltip']['valueSuffix'] = " SEK"
		highchart_dict['yAxis']['title']['text'] = "Amount (SEK)"
		highchart_series_0 = highchart_dict['series'][0]
		highchart_series_0['name'] = 'Balances'
		highchart_series_0['data'] = []
		hichart_xAxis = highchart_dict['xAxis']
		hichart_xAxis['categories'] = []
		
		for month_key in sorted(by_month_with_label_sums):
			totals_data = by_month_with_label_sums[month_key]['totals']
			rounded_value = math.ceil(totals_data['balance']*100)/100
			highchart_series_0['data'].append(rounded_value)
			hichart_xAxis['categories'].append(month_key)
		
		#print json.dumps(highchart_dict, indent=2)
		response_obj['data'] = highchart_dict
		response_obj['status'] = 1


if __name__ == '__main__':
	from BaseHTTPServer import HTTPServer
	desired_host = ''
	desired_port = 8080
	server = HTTPServer((desired_host, desired_port), GetHandler)
	print 'Starting server, use <Ctrl-C> to stop.'
	desired_host_str = 'localhost' if desired_host == '' else desired_host		
	print "Point your browser to http://{}:{}/transact.html.".format(desired_host_str, desired_port)
	server.serve_forever()