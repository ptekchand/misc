﻿#!/usr/bin/python
# -*- coding: utf-8 -*-
# C:\Python27\python.exe ah_scraper.py
# This Python file uses the following encoding: utf-8
#------------------------------------------------------------------------------
# Here's the plan.
# Parse page results from AH up to one week ago?
# Store results.
# Check if anything is within 31 minutes to work.
# Sort results
# Separately, keep polling the page for anything new.
# Mark the URLs that get warnings separately for manual inspection.
# Allow editing the data file to ignore the warning once inspected.
#------------------------------------------------------------------------------


import httplib
import time
from datetime import datetime
from datetime import timedelta
from lxml.html import fromstring
import lxml.html
from lxml.cssselect import CSSSelector
import json
import random
import os
import re

# C:\Python27\Lib\site-packages\
# cssselect-0.9.1-py2.7.egg
#import cssselect
# lxml-3.4.4-py2.7-win32.egg
#from lxml import cssselect

#	return codecs.charmap_encode(input,errors,encoding_map)
#		UnicodeEncodeError: 'charmap' codec can't encode character u'\xb4' in position 75: character maps to <undefined>
# http://stackoverflow.com/a/16120218
import sys
import codecs
if sys.stdout.encoding != 'cp850':
	sys.stdout = codecs.getwriter('cp850')(sys.stdout, 'strict')
if sys.stderr.encoding != 'cp850':
	sys.stderr = codecs.getwriter('cp850')(sys.stderr, 'strict')

#------------------------------------------------------------------------------
def ah_get_params(page_no, method = "POST"):
	url_params_prefix = ""
	url_params_suffix  = "&ListType=1&Search=&adtype_id=0&location_id=0&furnish_id=0&haspictures=false&country_id=1&rok=0&kvm=0&price=0" # "&X-Requested-With=XMLHttpRequest"

	referer_url_path = "/annonser" # Think of making this more generic.
	url_params_page = ""
	
	if page_no > 0:
		url_params_page = "Start={}".format(20*(page_no-1)+1)
	if page_no > 1:
		referer_url_path = "/annonser"
		#if method == "GET"
		#	referer_url_path = "/annonser/{}".format(page_no-2)
		
	url_params = url_params_prefix + url_params_page + url_params_suffix
	
	return referer_url_path, url_params
	
#------------------------------------------------------------------------------
def ah_get_headers(base_url, url_path, page_no, method = "POST"):
	referer_url_path, param_str = ah_get_params(page_no)
	header_referer = 'http://{}{}'.format(base_url, referer_url_path)
	if method == "GET":
		if page_no > 1:
			referer_url_path, referer_param_str = ah_get_params(page_no-1)
			header_referer = '{}?{}'.format(header_referer, referer_param_str)
	header_user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0'
	headers = {
		"Referer": header_referer,
		"User-Agent": header_user_agent
		#"Host:" base_url,
	}
	if method == "POST":
		headers["Content-type"] = "application/x-www-form-urlencoded"
	return headers

#------------------------------------------------------------------------------
# TODO: Merge in.
#def do_connect_response_with_socket_error_sleep(base_url, url_path, url_params, headers, max_errors = 2):

#------------------------------------------------------------------------------
def ah_search_apartments(listing_details_list, page_no = 1):
	base_url     = "www.ah.se"
	url_path     = "/annonser" # ? before params
	
	referer_url_path, url_params  = ah_get_params(page_no)

	headers = ah_get_headers(base_url, url_path, page_no)
	# Make Connection
	connection = httplib.HTTPConnection(base_url)
	connection.request("POST", url_path, url_params, headers)
	response = connection.getresponse()
	response_data = response.read()
	connection.close()
	
	# https://docs.python.org/2/library/httplib.html#httplib.responses
	if response.status != 200 and response.status != 302:
		print "ERROR: Unable to fetch from ({}) response.status({}: {})\n{}".format(base_url, response.status, response.reason, response)
		global g_stats
		g_stats["search_errors"] += 1
		return datetime.now() - g_max_time_delta
	
	print "INFO: Fetched from ({}) response.status({}: {})\n{}".format(base_url, response.status, response.reason, response)
	#print response_data
	# Parse the received page.
	return ah_parse_results_page(response_data, listing_details_list, page_no)

#------------------------------------------------------------------------------
def ah_visit_listing(listing_detail, save_page = False):
	base_url     = "www.ah.se"
	trim_base_url = False
	if base_url.find('http://')>=0:
		base_url = listing_detail["url"].replace('http://', '')
		trim_base_url = True
	listing_url = listing_detail["url"]
	next_slash_pos = listing_url.find('/')
	if next_slash_pos < 0:
		print "WARN: url doesn't have a slash in the path as expected\n    : {}".format(listing_url)
	next_qmark_pos = listing_url.find('?')
	if next_qmark_pos < 0:
		next_qmark_pos = None
	url_path = listing_url[next_slash_pos:next_qmark_pos]
	url_params = ""
	if next_qmark_pos>=0:
		url_params = base_url[next_qmark_pos+1:]
	if trim_base_url:
		base_url = base_url[:next_slash_pos]
	
	referer_url_path, referer_params_str  = ah_get_params(listing_detail["page"])

	headers = ah_get_headers(base_url, referer_url_path, listing_detail["page"], "GET")
	#print "DEBUG: Will visit:\n    base_url:{}\n    url_path:{}\n    url_params: {}\n    headers: {}".format(base_url, url_path, url_params, headers)
	#quit()

	connection = httplib.HTTPConnection(base_url)
	connection.request("GET", url_path, url_params, headers)
	response = connection.getresponse()
	response_data = response.read()
	connection.close()
	
	if response.status != 200 and response.status != 302:
		print "ERROR: Unable to fetch from ({}) response.status({}: {})\n{}".format(base_url, response.status, response.reason, response)
		global g_stats
		g_stats["listing_errors"] += 1
		return
	
	print "INFO: Fetched from ({}) response.status({}: {})\n{}".format(base_url, response.status, response.reason, response)
	#print response_data
	# Parse the received page.
	if save_page:
		with open("Response_{}.txt".format(listing_detail["item_id"]), 'w') as resp_handle:
			resp_handle.write(response_data)
			quit()
	
	ah_parse_listing_page(response_data, listing_detail)


#------------------------------------------------------------------------------
# Get the first element from the results of a selector and warn if there are more than 1.
# TODO: Cleanup: add another wrapper that returns the stripped text of the first element.
def get_first_element(selector, sel_target_ele, warn_ele_type, warm_target_ele_id, warn_extra="", warn_on_zero=True):
	global g_stats
	# TODO: Just re-factor this function to accept this selector_str instead of the CSSSelector
	#selector = CSSSelector(selector_str) # Drop the warn_extra parameter.
	first_element = None
	selector_result = selector(sel_target_ele)
	num_results = len(selector_result)
	if num_results > 1:
		print u"WARN: {} has more than 1 {} for details ({})".format(warm_target_ele_id, warn_ele_type, len(selector_result))
		g_stats["parse_warn"] += 1
	if num_results != 0:
		first_element = selector_result[0]
	elif warn_on_zero:
		print u"WARN: {} has ZERO {} for details ({})".format(warm_target_ele_id, warn_ele_type, warn_extra)
		g_stats["parse_warn"] += 1
	return first_element

#------------------------------------------------------------------------------
def ah_parse_listing_page(response_data, listing_detail):
	global g_stats
	#g_stats["parse_warn"] += 1
	listing_detail["gps"] = None
	listing_detail["ad_expired"] = False
	listing_detail["street"] = None
	listing_detail["furnished"] = False
	listing_detail["duration"] = 0 # 0 = unknown, 1 = kort, 2 = tillsvidare, 3 = längre period
	listing_detail["category"] = "" #"lägenhet" # class=".subject-param .category"
	listing_detail["area"] = "" #"Stockholms stad - Katarina, Sofia"

	page_element = fromstring(response_data)
	sel_geo_inputs    = CSSSelector('.grid_9 > #adinformation > input') #CSSSelector('.tab_mapview')
	# <img id="hitta-map-broker" src="http://external.api.hitta.se/image/v2/0/15/59.296779:18.007213?width=727&amp;height=317&amp;markers=%7B%22pn%22%3A%5B59.296779%5D%2C%22pe%22%3A%5B18.007213%5D%2C%22marker%22%3A%22http%3A%2F%2Fwww.ah.se%2Fimg%2Fbostad%2Fmap_pin.png%22%2C%22mox%22%3A6%2C%22moy%22%3A-21%7D&amp;logo={}">
	geo_inputs = sel_geo_inputs(page_element)
	if geo_inputs is not None:
		gps_coord_str = ""
		if len(geo_inputs) != 2:
			print u"WARN:  item_id({}) did not have the correct number '#adinformation > input' ({})? No GPS coords parsed.".format(listing_detail['item_id'], len(geo_inputs))
			print "WARN:  item_id({}) - Unknown page format returned. Saving for inspection.".format(listing_detail['item_id'])
			with open(g_unknown_response, 'w') as ur_handle:
				ur_handle.write(response_data)
			g_stats["parse_warn"] += 1
			quit()
		else: 
			gps_a = geo_inputs[0].get('value').strip()
			gps_b = geo_inputs[1].get('value').strip()
			if "longitude" in geo_inputs[0].get('name').strip(): # #Ad_geodata_longitude / #Ad_geodata_latitude 
				gps_coord_str = "{},{}".format(gps_b, gps_a)
			else:
				gps_coord_str = "{},{}".format(gps_a, gps_b)
		listing_detail["gps"] = gps_coord_str
		#print "DEBUG: item_id({}) gps_coord({})".format(listing_detail['item_id'], gps_coord_str)
	else:
		print u"WARN:  item_id({}) did not have the selected '.map-wrapper > img'? No GPS coords parsed.".format(listing_detail['item_id'])
		#g_stats["parse_warn"] += 1
		sel_no_ad_title    = CSSSelector('#no_ad_title')
		no_ad_ele = get_first_element(sel_no_ad_title, page_element, 'h2', listing_detail['item_id'], 'no_ad_title')
		if no_ad_ele is not None:
			print u"INFO:  item_id({}) - This ad has possibly been REMOVED.".format(listing_detail['item_id'])
			listing_detail["ad_expired"] = True
		"""
		else:
			print "WARN:  item_id({}) - Unknown page format returned. Saving for inspection.".format(listing_detail['item_id'])
			with open(g_unknown_response, 'w') as ur_handle:
				ur_handle.write(response_data)
			g_stats["parse_warn"] += 1
			quit()
		"""
	sel_street_address = CSSSelector('.grid_28 > .graytext')
	street_div        = get_first_element(sel_street_address, page_element, 'div', listing_detail['item_id'], '.grid_28 > .graytext')
	if street_div is not None:
		listing_detail["street"] = (street_div.text).strip()
		
	
	numeric_cre = re.compile('[0-9,. ]+')
	# <ul style="padding-top: 10px;" id="description_details">
	sel_description = CSSSelector('#description_details > li')
	description_li_list = sel_description(page_element)
	if len(description_li_list) <= 0:
		print u"ERROR: Listing ({}) Does not have any #description_details lis!".format(listing_detail['item_id'])
		g_stats["listing_errors"] += 1
	else:
		sel_property = CSSSelector('.property')
		sel_value = CSSSelector('.value')
		for description_li in description_li_list:
			'''<li class="alt"><span class="property">Annonsnr:</span><span class="value">22473</span></li>'''
			property_text = sel_property(description_li)[0].text.strip()
			#print u"DEBUG: property_text: {}".format(property_text)
			
			value_text = ""
			if property_text == u"Hyra:" or property_text == u"Hyra högs.:" or property_text == u"Hyra lågs.:": # WARN: It uses text-transform: capitalize on these
				value_text    = description_li.cssselect('.value > strong')[0].text.strip()
			elif property_text == u"Visningar:":
				'''<span class="value"><img src="/images/icon_statistics.png" alt="" style="display: inline-block; padding-right: 10px; line-height: 14px;">32</span>'''
				#print u"DEBUG: value_text: {}".format(lxml.html.tostring(sel_value(description_li)[0]))
				value_text    = description_li.cssselect('.value > img')[0].tail.strip()
			else:
				value_text    = sel_value(description_li)[0].text
				if value_text is None:
					print u"WARN: property_text: {} has the value_text None".format(property_text)
					value_text = ""
				else:
					value_text = value_text.strip()
			#print u"DEBUG: value_text: {}".format(value_text)
			
			if property_text == u"Annonsnr:":
				#22378
				if value_text != listing_detail['item_id']:
					print u"INFO: Eh? {} has ({}):({})".format(listing_detail['item_id'], property_text, value_text)
			elif property_text == u"Område:":
				#Gröndal / Stockholm / Sverige
				listing_detail["area"] = value_text
			elif property_text == u"Hyra:" or property_text == u"Hyra högs.:":
				# "9100 kr/Månad" OR "3000 kr/Vecka"
				# Strip away the stuff other than numbers, commas and decimals
				check_rent = numeric_cre.match(value_text).group().strip().replace(' ', '')
				if "Vecka" in value_text or "vecka" in value_text:
					check_rent = check_rent*4
				listing_detail['rent'] = listing_detail['rent'].replace(u'\xa0', '')
				listing_rent_num_known = numeric_cre.match(listing_detail['rent']).group().strip()
				if listing_detail['rent'] == "":
					listing_detail['rent'] = check_rent
				elif check_rent != listing_rent_num_known:
					print u"INFO: Eh? {} has ({}):({}) was ({})".format(listing_detail['item_id'], property_text, value_text, listing_detail['rent'])
					if check_rent > listing_rent_num_known:
						listing_detail['rent'] = check_rent
			elif property_text == u"Hyra lågs.:":
				pass
			elif property_text == u"Rok:":
				# 3
				check_rooms = numeric_cre.match(value_text).group().strip()
				if listing_detail['rooms'] == "":
					listing_detail['rooms'] = check_rooms
				elif check_rooms != numeric_cre.match(listing_detail['rooms']).group().strip():
					print u"INFO: Eh? {} has ({}):({}) was ({})".format(listing_detail['item_id'], property_text, value_text, listing_detail['rooms'])
			elif property_text == u"Kvm:":
				#70 m²
				check_size = numeric_cre.match(value_text).group().strip()
				if listing_detail['size'] == "":
					listing_detail['size'] = check_size
				elif check_size != numeric_cre.match(listing_detail['size']).group().strip():
					print u"INFO: Eh? {} has ({}):({}) was ({})".format(listing_detail['item_id'], property_text, value_text, listing_detail['size'])
			elif property_text == u"Läge:":
				#Ganska Centralt
				pass
			elif property_text == u"Möblering:":
				if value_text == u"Möblerad":
					listing_detail["furnished"] = True
				else:
					print u"DEBUG: {} has ({}):({}).".format(listing_detail['item_id'], property_text, value_text)
					listing_detail["furnished"] = False
			elif property_text == u"Inlagd:":
				#Idag (08:46) # OR: 01 juni 2015
				if value_text != listing_detail['datetime']:
					print u"INFO: Eh? {} has ({}):({}) was ({})".format(listing_detail['item_id'], property_text, value_text, listing_detail['datetime'])
			elif property_text == u"Inflyttning:":
				#16 juli 2015
				pass
			elif property_text == u"Utflyttning:":
				#Tills vidare. # OR: 01 december 2015
				listing_detail["duration"] = value_text
			elif property_text == u"Visningar:":
				# Views of the ad
				pass
			else:
				print u"WARN: {} has an unknown description_detail ({}):({})".format(listing_detail['item_id'], property_text, value_text)
				g_stats["parse_warn"] += 1
			
	'''<h2 style="margin-right: 48px;">Rum</h2>'''
	sel_category = CSSSelector('#adinformation > h2')
	cat_h2        = get_first_element(sel_category, page_element, 'h2', listing_detail['item_id'], '#adinformation > h2')
	if cat_h2 is not None:
		listing_detail["category"] = (cat_h2.text).strip()	
		
	listing_detail["visited"] = True
	print "DEBUG: {}".format(json.dumps(listing_detail, indent=2))

#------------------------------------------------------------------------------	
def find_listing(item_id, listing_details_list):
	for a_listing_detail in listing_details_list:
		if a_listing_detail["item_id"] == item_id:
			return a_listing_detail
	return None
	
#------------------------------------------------------------------------------
def ah_parse_results_page(response_data, listing_details_list, page_no):
	global g_stats

	#from lxml.etree import fromstring
	#page_element = fromstring(response_data)
	page_element = fromstring(response_data)
	sel_item_row    = CSSSelector('.grid_28.list_row')
	sel_heading_a   = CSSSelector('.list_address') #'.grid_15 > a'
	sel_sprite_div  = CSSSelector('.grid_4 > div > a > div')
	sel_details_div = CSSSelector('.grid_15 > strong')
	#sel_size_span   = CSSSelector('.size')
	#sel_rooms_span   CSSSelector('.rooms')
	sel_time        = CSSSelector('.grid_15 > i')
	sel_rent_span = CSSSelector('.grid_4 > span')
	sel_category = CSSSelector('.grid_3')
	for div_item_row in sel_item_row(page_element):
	
		listing_heading = ""
		listing_url = ""
		listing_heading_ele_res = sel_heading_a(div_item_row)
		if len(listing_heading_ele_res) > 1:
			print "WARN: {} has more than 1 a for media-heading ({})".format(div_item_row_id, len(listing_heading_ele_res))
			g_stats["parse_warn"] += 1
		if len(listing_heading_ele_res) != 0:
			listing_heading_ele = listing_heading_ele_res[0]
			listing_heading = (listing_heading_ele.text).strip() # Note: This is likely to be unicode
			listing_url = listing_heading_ele.get('href')
			#print u"DEBUG: div_item_row({}) has listing_heading: {},\nlisting_url: {}".format(div_item_row_id, listing_heading, listing_url)
		
		div_item_row_id = listing_url.replace('/annons/', '')
		#print "DEBUG: div_item_row_id: {}".format(div_item_row_id)
	
		listing_image_url = "no image"
		bgimage_div = sel_sprite_div(div_item_row)
		if len(bgimage_div) > 1:
			print "WARN: {} has more than 1 a for sprite_list_placeholder ({})".format(div_item_row_id, len(bgimage_div))
			g_stats["parse_warn"] += 1
		if len(bgimage_div) != 0:
			#print "DEBUG: {} has {} a for sprite_list_placeholder.".format(div_item_row_id, len(bgimage_div))
			#print "DEBUG: {} has {} a for sprite_list_placeholder:\n{}".format(div_item_row_id, len(bgimage_div), lxml.html.tostring(div_item_row))
			bgimage_div = bgimage_div[0]
			#print "DEBUG: bgimage_div: {}".format(lxml.html.tostring(bgimage_div))
			listing_image_url = bgimage_div.get('style')
			img_url_pre_start = 'background-image: url('
			img_url_pre_start_pos = listing_image_url.find(img_url_pre_start)
			if img_url_pre_start_pos >=0:
				img_url_end_pos = listing_image_url.find( ')', len(img_url_pre_start) )
				if img_url_end_pos > 0:
					listing_image_url = listing_image_url[len(img_url_pre_start): img_url_end_pos]
				else:
					print "WARN: No image URL end parenthesis for ({})\nin: {}".format(div_item_row_id, listing_image_url)
					g_stats["parse_warn"] += 1
			else:
				print "WARN: No image URL for ({})\nin: {}".format(div_item_row_id, listing_image_url)
				g_stats["parse_warn"] += 1
			#print "DEBUG: div_item_row({}) has image_url: {}".format(div_item_row_id, listing_image_url)
		
		
		listing_details_rooms        = ""
		listing_details_monthly_rent = ""
		listing_details_size         = "0"
		details_divs = sel_details_div(div_item_row)
		if len(details_divs) > 1:
			print "WARN: {} has more than 1 div for details ({})".format(div_item_row_id, len(details_divs))
			g_stats["parse_warn"] += 1
		if len(details_divs) != 0:
			listing_details_ele = details_divs[0]
			details_text_list = (listing_details_ele.text).strip().split(',')
			
			listing_details_size         = details_text_list[0].strip()
			listing_details_rooms        = details_text_list[1].strip()

		rent_span = get_first_element(sel_rent_span, div_item_row, 'span', div_item_row_id, 'rent') # WARN: This may be a weekly rent too!
		listing_details_monthly_rent = rent_span.text.strip() if rent_span is not None else ""
		#listing_details_monthly_rent = listing_details_monthly_rent.replace(' ', '').replace('&nbsp;', '').replace('&#160;', '').replace('\u00a0', '') # 'rent'
		#listing_details_monthly_rent = listing_details_monthly_rent.decode("utf-8").replace('\u00a0', '')
		listing_details_monthly_rent = listing_details_monthly_rent.replace(u'\xa0', '')

		category_div = get_first_element(sel_category, div_item_row, 'div', div_item_row_id, 'category')
		listing_detail_category = category_div.text.strip() if category_div is not None else ""
		
		listing_posted_datetime = ""
		time_res = sel_time(div_item_row)
		if len(time_res) > 1:
			print "WARN: {} has more than 1 time for details ({})".format(div_item_row_id, len(time_res))
			g_stats["parse_warn"] += 1
		if len(time_res) != 0:
			listing_time_ele = time_res[0]
			listing_posted_datetime = listing_time_ele.text.strip().replace('Inlagd: ', '')
		
		listing_detail = {
			"item_id" : div_item_row_id,
			"image"   : listing_image_url,
			"heading" : listing_heading,
			"url"     : listing_url,
			"rooms"   : listing_details_rooms,
			"rent"    : listing_details_monthly_rent,
			"size"    : listing_details_size,
			"datetime": listing_posted_datetime,
			"page"    : page_no,
			"category": listing_detail_category,
			"visited" : False
		}
		existing_detail = find_listing(listing_detail["item_id"], listing_details_list)
		if existing_detail is None:
			listing_details_list.append(listing_detail)
		else:
			diff_string = ""
			#print u"DEBUG:"
			#import pprint
			#pprint.pprint( listing_detail )
			# ValueError: too many values to unpack; without iteritems.
			# Because it iterates over the keys. Any key more than 2 characters long would break 'key,value in ...'
			# Alternately, use "key in listing_detail" with "value = listing_detail[key]"
			for key,value in listing_detail.iteritems():
				if value != existing_detail[key]:
					diff_string = u"{} {}:[\"{}\"->\"{}\"]".format(diff_string, key, value, existing_detail[key])
			if diff_string == "":
				diff_string = "No differences."
			else:
				diff_string = u"Diff: {}".format(diff_string)
			print u"WARN: {} already known. {}".format(listing_detail["item_id"], diff_string);
			g_stats["parse_warn"] += 1
			
		print u"DEBUG: div_item_row({}) has listing_heading: {},\nlisting_url: {}\ndetails: {}, {}, {}\nPosted: {}".format(div_item_row_id, listing_heading, listing_url,
			listing_details_rooms, listing_details_monthly_rent, listing_details_size,
			listing_posted_datetime
		)
		#print u"DEBUG: {}".format( json.dumps(listing_detail, indent=2) )
		
		g_stats["num_results"] += 1
	# Return the date time of the last listing on this page
	last_listing_datetime = datetime.now() - g_max_time_delta
	if len(listing_details_list) > 0:
		last_listing_datetime = datetime.strptime( listing_details_list[-1]["datetime"], '%Y-%m-%d' )
		
	# Store updated information for lookups/checks later.
	store_on_each_page = True
	if store_on_each_page:
		global g_json_datafile
		with open(g_json_datafile, 'w') as json_file_handle:
			json.dump(listing_details_list, json_file_handle, indent=2)

	return last_listing_datetime

#------------------------------------------------------------------------------
def get_travel_time(depLong, depLat, destLong, destLat):
	resparams = "&from=SthlmCentral&to=Destination&fromX="+depLong +"&fromY="+depLat+"&toX="+destLong+"&toY="+destLat+"&coordSys=WGS84&apiVersion=2.1"
	url="/samtrafiken/resrobot/Search.json?key=your_resrobot_key" + resparams;
	
	connection = httplib.HTTPSConnection("api.trafiklab.se")
	connection.request("GET", url)
	response = connection.getresponse()
	data2 = response.read()
	connection.close()
	
	result2 = json.loads(data2)
	format = '%Y-%m-%d %H:%M'
	#time = str(result2["timetableresult"]["ttitem"][0]["segment"][0]["arrival"]["datetime"])
	try:
	    segmentList = result2["timetableresult"]["ttitem"]#[0]  #["segment"]
	except:
	    return timedelta(hours=3)
	time_arr = []
	
	#print result2.items()
	try:
		for i,segment in enumerate(segmentList): 
			depart = segment["segment"][0]["departure"]["datetime"]
			arrival = segment["segment"][-1]["arrival"]["datetime"]
			depart_time = datetime.strptime(depart, format)
			arrival_time = datetime.strptime(arrival, format)
			time_arr.append(["dept",depart_time,"arr",arrival_time])
			#if i > 5:
			#	break
	except:
		return timedelta(hours=4)
	#print time_arr
	travel_time = timedelta(hours=2)
	for t in time_arr:
		if t[3]-t[1] < travel_time:
			travel_time = t[3]-t[1]
	return travel_time

#------------------------------------------------------------------------------
# main()
g_stats = {
	"num_results": 0,
	"parse_warn": 0,
	"search_errors": 0,
	"listing_errors": 0
}

# TODO: Change this to something closer to the commute
centerLat = "59.3302967"; # Stockholm Central Station
centerLong = "18.0582976"; # Stockholm Central Station
mdpLat = "59.314337"
mdpLon = "18.073551"
aCentralLat = "59.312768"
aCentralLon = "18.0735245"

listing_details_list = []
g_unknown_response = "ResponseBodyUnknown.txt"
g_json_datafile = "ResponseJSON.js"


g_max_time_delta = timedelta(days=60);

fetch_disabled_for_testing = False

last_listing_datetime = datetime.now()
# Load retrieved information for continuing between broken launches.
if os.path.exists(g_json_datafile):
	with open(g_json_datafile, 'r') as json_file_handle:
		listing_details_list = json.load(json_file_handle)
		if len(listing_details_list) > 0:
			last_listing_datetime = datetime.strptime( listing_details_list[-1]["datetime"], '%Y-%m-%d' )

page_no = 1 # Add Continue from page functionality?
while datetime.now() - last_listing_datetime < g_max_time_delta and page_no < 15 and not fetch_disabled_for_testing and False:
	sleep_sec = random.uniform(1, 3)
	print "INFO: Sleeping ({}) before loading results page ({})".format(sleep_sec, page_no)
	time.sleep(sleep_sec)
	last_listing_datetime = ah_search_apartments(listing_details_list, page_no)
	page_no += 1
print "#------------------------------------------------------------------------------------------------"
print "INFO: The last datetime read from a listing was: {}".format(last_listing_datetime)
print "#------------------------------------------------------------------------------------------------"

# Test parsing with local data
full_src_path = "ResponseBodyP2.txt"
if fetch_disabled_for_testing and False:
	with open(full_src_path, 'r') as src_file_handle:
		test_response_data = src_file_handle.read()
		#print test_response_data
		last_listing_datetime = ah_parse_results_page(test_response_data, listing_details_list, 1)


# Store retrieved information for lookups/checks later.
with open(g_json_datafile, 'w') as json_file_handle:
	json.dump(listing_details_list, json_file_handle, indent=2)


c_index = 0
start_index = 0
for listing_detail in listing_details_list:
	if not listing_detail["visited"] and c_index >= start_index:
		sleep_sec = random.uniform(1, 3)
		print "INFO: Sleeping ({}) before loading listing page ({})".format(sleep_sec, listing_detail["item_id"])
		time.sleep(sleep_sec)
		ah_visit_listing(listing_detail)
	c_index += 1

# Store updated information for lookups/checks later.
with open(g_json_datafile, 'w') as json_file_handle:
	json.dump(listing_details_list, json_file_handle, indent=2)

# Test only.
#ah_visit_listing(listing_details_list[-1], True)
# Test parsing with local data
if fetch_disabled_for_testing:
	listing_detail = listing_details_list[-1]
	full_src_path = "Response_{}.txt".format(listing_detail["item_id"]) # Response_22473.txt
	with open(full_src_path, 'r') as src_file_handle:
		test_response_data = src_file_handle.read()
		ah_parse_listing_page(test_response_data, listing_detail)


# TODO: Loop over results
#	get_travel_time(centerLong,centerLat,longitude,latitude)
print """
	INFO: Stats:
		num_results   : {}
		parse_warn    : {}
		search_errors : {}
		listing_errors: {}
	""".format(g_stats["num_results"],
			g_stats["parse_warn"],
			g_stats["search_errors"],
			g_stats["listing_errors"]
	)
#print result