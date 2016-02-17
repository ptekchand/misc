#!C:/Python27/Python.exe
# -*- coding: utf-8 -*-
# This Python file uses the following encoding: utf-8

# C:\Python27\python.exe parse_hb.py

# Data from HB. Use openpyxl to open.

#------------------------------------------------------------------------------
import sys
import codecs
if sys.stdout.encoding != 'cp850':
	sys.stdout = codecs.getwriter('cp850')(sys.stdout, 'strict')
if sys.stderr.encoding != 'cp850':
	sys.stderr = codecs.getwriter('cp850')(sys.stderr, 'strict')
#------------------------------------------------------------------------------

import json
from json import JSONEncoder
import os
import datetime

from openpyxl import load_workbook

# Can be generated using the LabelMatcher list below.
all_labels = [
	"rent",
	"groceries", # ICA, Hemköp, Coop, Willys, LIDL
	"food", # lunch/dinner out. snack (flapjack etc charges < ~30? Pressbyran)
	"training", # klatter
	"transportation", # -790
	"travel",
	"hotel",
	"alcohol",
	"beer",
	"entertainment",
	"personal", # Decathlon, Clas Ohlson, IKEA
	"phone",
	"salary", # "lön"
	"payback", # numbers (airbnb)
	"no_label"
]
#zero_label_sums = dict( zip(all_labels, [0.0]*len(all_labels)) ) # Copy this
zero_label_sums = { key: 0.0 for key in all_labels }

class LabelMatcher(object):
	def __init__(self, name, keywords, amount):
		#super(LabelMatcher, self).__init__()
		#object.__init__(self)
		#print u"LabelMatcher.__init__({})".format(name)
		self.name = name
		self.keywords = keywords # or change to regexes?
		self.amount = amount
		self.stop_processing = False # Feature: Process no further for this record if this Label matches.
	
	# Perform some automatic matching based on keywords and later use a UI to confirm/correct mistakes.
	def has_match(self, t_record):
		# Specific amount matcher
		if self.amount is not None:
			if self.amount == t_record.amount:
				return True

		# Description text matcher
		if t_record.text is not None:
			for keyword in self.keywords:
				#print u"k({}) in t({})?".format(keyword, t_record.text)
				if keyword.lower() in t_record.text.lower():
					return True
		
		# Some global rules?
		#if t_record.amount > 0.0:
		#	also append "salary", "airbnb", or "payback"
		
		return False

class WholeWordLabelMatcher(LabelMatcher):
	def __init__(self, name, keywords, amount):
		LabelMatcher.__init__(self, name, keywords, amount)
		#super(WholeWordLabelMatcher, self).__init__(name, keywords, amount)
		#print "WholeWordLabelMatcher.__init__"

	def has_match(self, t_record):
		# Description text matcher
		if t_record.text is not None:
			for keyword in self.keywords:
				#print u"k({}) in t({})?".format(keyword, t_record.text)
				if keyword.lower() == t_record.text.lower():
					return True
		#return super.has_match(t_record)
		return False

class MinAmountLabelMatcher(LabelMatcher):
	def __init__(self, name, keywords, amount):
		LabelMatcher.__init__(self, name, keywords, amount)
		#super(MinAmountLabelMatcher, self).__init__(name, keywords, amount)
		#print "MinAmountLabelMatcher.__init__"
		
	def has_match(self, t_record):
		# Positive amount matcher
		if self.amount is not None:
			if t_record.amount > self.amount:
				return True
		#return super.has_match(t_record)
		return False

class ExistingLabelMatcher(LabelMatcher):
	def __init__(self, name, keywords, amount):
		LabelMatcher.__init__(self, name, keywords, amount)
		
	def has_match(self, t_record):
		matched_all = True
		# Check this matchers keywords against the records existing labels. You want to add this after other matchers.
		if self.keywords is not None:
			for label_keyword in self.keywords:
				if label_keyword not in t_record.labels:
					matched_all = False
					break
		# TODO: Create an AndLabelMatcher which takes a list of label matcher types and returns has match if all in the list pass?
		# This is the equivalent of MinAmountLabelMatcher's has_match
		if self.amount is not None:
			if t_record.amount < self.amount:
				matched_all = False
		#return super.has_match(t_record)
		return matched_all

label_matcher_list = [
	LabelMatcher("rent", [u"Rent"], None),
	LabelMatcher("groceries", ["ICA ","Hemkop","Hemk@p","Coop","Willys","LIDL ","OOB ", "Tasadash Livs", "er buco", "lundbergs kond", "lindquist kond", "pathivara food", "billa ", "kista grossen"], None),
	LabelMatcher("food", ["Restaura", "ristorante", "Noodle Mama", "mae thai", "thai wok", "thai food", "thaifood", "thai take", "asian & thai", "pho & bun", "shanti", "soft corner", "Indian Garden", "aso konditori", "Lima deli", "freds food", "G@tgatan stori", "oliver twist", "zocalo", "a la crepe", "Texas ", "Burger", "primo ciao", "pizzeria", "vapiano", "F@rno", "forno ", "sushi", "Kebab", "grill", "grekiska", "nero k.2", "boqueria", "bistro", "subway", "burger king", "max ", "mcdonald", "derhallarna", "vegetarisk", "melanders", "cafe", "Espresso House", "pressbyr", "7-eleven", "la venezia", "kondito", "frozen yog", "honey honey", "machhapuchre f", "mediterra n gr"], None), # lunch/dinner out. snack (flapjack etc charges < ~40? Pressbyran, 7-Eleven)
	WholeWordLabelMatcher("food", ["eat", "bamboo garden", "creme", "usine 3638", "konoba cesaric", "rest the bull", "medelhavsdeli", "fisher men s", "ruefa reisen", "kina dumplings", "samrat of indi", "chili & soy", "nybrogatan 38", "mormors dumpli", "liins asian t", "reggev hummus", "dell attore", "denniso hb", "mickibella ab", "theodora", "da givaroli"], None), # , "restaurang chi"
	LabelMatcher("training", ["klatter","kl#tter","eriksdal", "resole denanto"], None),
	LabelMatcher("transportation", ["SL ","Flygbuss","cykelstaden", "taxi", "ticket.se","resecentrum"], -790.00), # Will miss -2400 for summer card, UL
	LabelMatcher("travel", ["wiener linien", "croatia tix", "ticket.se", "tourist", "arlanda ", "billa "], None),
	LabelMatcher("hotel", ["hotel", "booking", "kungsberget", "airbnb"], None),
	LabelMatcher("alcohol", ["kvarnen", "tunnan", "systembolaget", "imperiet", "pub/event", "hilton slussen"], None),
	LabelMatcher("beer", ["beer"], None),
	LabelMatcher("entertainment", ["SF Bio", "kungsberget", "discgolf", "www.sf.se", "Stockholm Glob"], None),
	LabelMatcher("personal", ["steam", "decathlon", "xxl sport", "intersport", "stadium", "din sko", "adidas", "dressman", "H M ", "webhallen", "clas ohlson", "IKEA", "fredells", "WIRSTR@MS", "amazon", "aliexp", "cykelstaden", "panduro", "duty free", "heinemann duty" "game so", "karolinska", "apotek", "klarna ab"], None), # Decathlon, Clas Ohlson, IKEA
	LabelMatcher("phone", ["lyca"], None),
	ExistingLabelMatcher("dinner_out", ["food"], 200.00),
	WholeWordLabelMatcher("salary", ["lon", u"lön"], None), # "lön" (L\u00d6N)
	MinAmountLabelMatcher("payback", [], 0.0), # numbers (airbnb) or positive values.
]

label_matcher_list[-2].stop_processing = True # Make the 'salary' and 'payback' checks multually exclusive
		

duration_start = 0
duration_end = 0
sums_by_label = []
# Open
# Loop
#	Match multiple rules
#	Add matched rules to list
# Store aggregate

def str_or_unicode_to_float(input):
	return float(input.replace(',', '.').replace(' ', '')) if (type(input) is str or type(input) is unicode) else input

class TransactionRecord():
	def __init__(self, tdate, text, amount, balance, labels):
		self.tdate  = tdate
		#self.tdate = tdate.date().isoformat() if type(tdate) is datetime.date else tdate,
		#self.tdate = tdate.date().isoformat() if type(tdate) is datetime.datetime else self.tdate,
		#print u"Types: tdate: {}, text: {}, amount: {}, balance: {}, labels: {}".format(type(tdate), type(text), type(amount), type(balance), type(labels))
		self.text   = u"{}".format(text)
		# Convert to float. Strip spaces, replace localized number format comma111
		self.amount = str_or_unicode_to_float(amount)
		self.balance = str_or_unicode_to_float(balance)
		if self.balance is None:
			self.balance = 0.0
		self.labels = labels
		#print u"TransactionRecord({}, {}, {}: {})".format(self.tdate, self.amount, self.balance, self.text)

# Or create an encorder to pass to json.dumps (http://stackoverflow.com/a/3768975)
class TRJSONEncoder(JSONEncoder):
    def default(self, o):
        #return json.dumps(self.__dict__)
			if type(o) is datetime.datetime:
				return o.date().isoformat()
			
			tdate_str = o.tdate
			if type(o.tdate) is datetime.date or type(o.tdate) is datetime.datetime:
				tdate_str = o.tdate.date().isoformat()
			repr_dict = {
				"tdate" : tdate_str,
				"text"  : o.text,
				"amount": o.amount,
				"balance":o.balance,
				"labels": o.labels
			}
			return repr_dict

# Supply a custom object_hook to the JSONDecoder class
# JSONDecoder(object_hook = TR_from_json).decode('{"text":"ICA SUPERMARKE","amount":-33.95,"labels":["groceries"],"tdate":"2014-08-22"}')
def TR_from_json(json_object):
	if 'text' in json_object:
		return TransactionRecord(
			json_object['tdate'],
			json_object['text'],
			json_object['amount'],
			json_object['balance'],
			json_object['labels']
		)

transaction_record_list = []
workbook_path = "transactionlist.xlsx" # TODO: Use command line options.
json_file_path = "transactionlist.json"

def load_from_xlsx(workbook_path, transaction_record_list):
	wb_tlist = load_workbook(workbook_path, read_only=True)
	# Excel headers:
	# Columns: A = "Reskontradatum", C = "Transaktionsdatum", E = "Text" (may be empty), G = "Belopp", I = "Saldo"
	ldate, tdate, text, amount, balance = 0, 2, 4, 6, 8
	# First data row: 7. Last row 724 with salary. Stuff below it includes Thailand charges (749 to 742) - oldest = 2014-08-07
	# Could get older data from the Toshl export
	first_data_row = 7
	last_data_row  = 724
	r = 0
	ws_tlist = wb_tlist.active
	for row in ws_tlist.rows:
		r += 1
		if r < first_data_row:
			continue
		elif r > last_data_row:
			break

		#print u"DEBUG: {}".format( row[tdate].value )
		#print u"({})".format( float(row[balance].value.replace(',', '.').replace(' ', '')) )
		t_record = TransactionRecord(row[tdate].value, row[text].value, row[amount].value, row[balance].value, [])
		for label_matcher in label_matcher_list:
			if label_matcher.has_match( t_record ):
				t_record.labels.append( label_matcher.name )
				if label_matcher.stop_processing:
					break
				# TODO: Aggregate label total. hicharts_json.py is doing this.
				# label_matcher.total += t_record.amount
		
		transaction_record_list.append( t_record )
		#print u"append TR({}, {}, {}: {})".format(t_record.tdate, t_record.amount, t_record.balance, t_record.text)

def export_to_json(json_file_path, transaction_record_list):
	with open(json_file_path, 'w') as json_file_handle:
		json.dump(transaction_record_list, json_file_handle, indent=2, cls=TRJSONEncoder)

def import_from_json(json_file_path):
	with open(json_file_path, 'r') as json_file_handle:
		#transaction_record_list = json.load(json_file_handle, cls=TRJSONDecoder)
		transaction_record_list = json.load(json_file_handle, object_hook=TR_from_json)
		#print u"Records loaded: {}".format( len(transaction_record_list) )
		return transaction_record_list

parse_from_excel_mode = True # otherwise from previously parsed JSON
if parse_from_excel_mode:
	load_from_xlsx(workbook_path, transaction_record_list)
	export_to_json(json_file_path, transaction_record_list)
	#quit()
else:
	transaction_record_list = import_from_json(json_file_path)

print u"Records loaded: {}".format( len(transaction_record_list) )

# Another piece of data to write is the aggregate label totals
by_month_with_label_sums = {} # They keys would be "YYYYMM"
def group_labels_by_month(transaction_record_list, by_month_with_label_sums):
	for t_record in transaction_record_list:
		if type(t_record.tdate) is not unicode:
			if type(t_record.tdate) is datetime.datetime:
				t_record.tdate = t_record.tdate.date().isoformat()
			else:
				print u"WARN: tdate:{} is not unicode as expected. Is: {}. Row's text:{}".format(t_record.tdate, type(t_record.tdate), t_record.text)
				break
		month_key = u"{}{}".format(t_record.tdate[:4], t_record.tdate[5:7])
		if month_key not in by_month_with_label_sums:
			by_month_with_label_sums[month_key] = {
				"tlist":[],
				"lsums":dict(zero_label_sums),
				"totals":{"spent":0, "recvd":0, "balance":0}
			}
			# TODO: Add information about investments too (ESPP, ITP) and add/process that in highcharts_json.py (Separate chart?)
		
		by_month_with_label_sums[month_key]["tlist"].append(t_record)
		for label in t_record.labels:
			if label == "":
				label = "no_label"
			by_month_with_label_sums[month_key]["lsums"][label] += t_record.amount
		
		if t_record.amount > 0:
			by_month_with_label_sums[month_key]["totals"]["recvd"] += t_record.amount
		else:	
			by_month_with_label_sums[month_key]["totals"]["spent"] += t_record.amount
		# Set the balance as the first transaction processed
		# last transaction of the month since the excel is in reverse chronological order.
		if by_month_with_label_sums[month_key]["totals"]["balance"] == 0:
			by_month_with_label_sums[month_key]["totals"]["balance"] = t_record.balance
		
	#by_month_with_label_sums[month_key]["totals"]["recvd"] = -math.ceil(by_month_with_label_sums[month_key]["totals"]["recvd"]*100)/100
	#by_month_with_label_sums[month_key]["totals"]["spent"] = -math.ceil(by_month_with_label_sums[month_key]["totals"]["spent"]*100)/100


group_labels_by_month(transaction_record_list, by_month_with_label_sums)
export_to_json("month_transactions.json", by_month_with_label_sums)
		
# Create graph of data in html interface. See highcharts_json.py

