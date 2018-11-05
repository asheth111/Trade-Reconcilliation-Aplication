from flask import Flask
import urllib
import json, csv
from flask_table import Table, Col

app = Flask(__name__)

class UnmatchTable(Table):
	trade_date = Col('Trade Date')
	exchange = Col('Exchange')
	symbol = Col('Symbol')
	buy_sell = Col('Buy/Sell')
	price = Col('Price')
	quantity = Col('Quantity')
	our_count = Col('Our Count')
	exchg_count = Col('Exchange Count')

# Get some objects
class Item(object):
	def __init__(self, trade_date, exchange, symbol, buy_sell, price, quantity, our_count, exchg_count):
		#, symbol, buy_sell, price, quantity, our_count,exchg_count):
		self.trade_date = trade_date
		self.exchange = exchange 
		self.symbol = symbol
		self.buy_sell = buy_sell
		self.price = price
		self.quantity = quantity
		self.our_count = our_count
		self.exchg_count = exchg_count

@app.route("/")
def hello():
	#Parse JSON URL and loads the data into json_data
	json_url = 'https://pastebin.com/raw/WzweeTST'
	json_response = urllib.urlopen(json_url).read()
	json_data = json.loads(json_response)
	'''
	Initialize symbol_dataset which will keep track of both JSON and CSV symbols
	In symbol_dataset key will be stock ticker and value will be list of list
	'''
	symbol_dataset = {}
	for row in json_data['data']:
		symbol_dataset[row['symbol']] = [[row['trade_date'], row['buy_sell'],  row['price'], row['quantity'], 1, 0]]

	#Parse CSV data and loads the data into reader
	csv_url = 'https://pastebin.com/raw/rkP1Jsnk'
	csv_response = urllib.urlopen(csv_url).read().decode()
	reader = csv.reader(csv_response.split('\n'), delimiter=',') 
	'''
	Iterate throgh all CSV data and checks if the Symbol is already there in Symbol or not.
	If Symbol is already available method will insert 1 to 5
	'''
	for row in reader:
		#Discard Header
		if row[8] == 'Symbol':
			continue
		#Checks if stock ticker is there in the data or not
		if row[8] in symbol_dataset:
			current_data = symbol_dataset[row[8]][0]
			#checks value mismatch, If there is no mismatch updates 5th position to 1
			if row[3] == current_data[0] and row[9][0] == current_data[1] and row[11] == current_data[2] and row[10] == current_data[3]:
				symbol_dataset[row[8]][0][5] = 1
			else:
				symbol_dataset[row[8]].append([row[3],row[9][0],row[10],row[11],0,1])
		else:
			symbol_dataset[row[8]] = [row[3],row[9][0],row[10],row[11],0,1]

	unmatch_data = []
	
	for k,v in sorted(symbol_dataset.items()):
		#There is unmatched data if value at 4th position is not equal to value at 5th position
		if v[0][4] != v[0][5]:
			if(len(v)) == 1:
				unmatch_data.append(Item(v[0][0],'TONKOTSU', k, v[0][1],v[0][2],v[0][3], v[0][4],v[0][5]))
			else:
				for i in range(2):
					unmatch_data.append(Item(v[i][0],'TONKOTSU', k, v[i][1],v[i][2],v[i][3], v[i][4],v[i][5])) 
		

	# Populate the table
	table = UnmatchTable(unmatch_data)

	with open('index.html','w') as file:
		file.write('<html><body>' + table.__html__() +'</body></html>')
	
	return '<html><body>' + table.__html__() +'</body></html>'
	
	
if __name__ == "__main__":
    app.run()

	