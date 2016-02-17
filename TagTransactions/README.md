# TagTransactions
Experiment to take the xlsx statement exported form HB and group transactions by labels.
Then draw graphs using [highcharts](https://github.com/highcharts/highcharts/) with the data exported to JSON for an overview.

Usage:
1. Export/download transactions from HB.
2. Parse downloaded excel file and process to JSON.
   `python parse_hb.py`
   Requires [OpenPyXL](http://openpyxl.readthedocs.org/en/2.3.3/)
   `pip install openpyxl` assuming you have [pip](https://pip.pypa.io/en/latest/installing/) installed.
3. Update JS data file. The script above asks if you wish for it to do so.
4. Run the viewer application/server.
   `python highcharts_json.py`
5. View in a browser window.
   Visit: localhost:8080/transact.html

Requirements:
[Python](http://www.python.org/) 2.7.x
[OpenPyXL](http://openpyxl.readthedocs.org/en/2.3.3/)
[Highcharts](http://www.highcharts.com/)-[4.2.1](http://code.highcharts.com/zips/Highcharts-4.2.1.zip)+ extracted to `h5bp/js/vendor/highcharts-4.2.1/` ([GitHub project](https://github.com/highcharts/highcharts/))
[html5 boiler plate](https://html5boilerplate.com/)-[5.2.0](https://github.com/h5bp/html5-boilerplate/releases/download/5.2.0/html5-boilerplate_v5.2.0.zip)+ extracted to `h5bp/`

# This was the plan:
Use an htlm5 based graphing library to create an interface over transaction statements, just to get a personal overview.
Features:
Label/categorize
Compare/navigate monthly/weekly
Scrub timelines

Possible graphic library: hicharts

Transactions table
each row is associated with a list of labels

But we want it indexed by label as well.

Essentially for totals.

Automatic labeling pass. Do I need to get the data from Toshl to "train" it?
