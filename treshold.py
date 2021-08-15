import json
import requests
import pandas as pd
import smtplib, ssl
from email.message import EmailMessage
from requests import Request, Session
import sys
import os
import openpyxl


# USER SHOULD CONFIGURE THE VARIABLES BELOW
# ------------------------------------------------------------------------------------------------------------------------------------------

#VARIABLES TO COMPLETE/CHANGE BY THE USER
capital = 10000.00 # Initial amount of USD to invest
number_of_coins = 7 # Amount of coins to invest in (excluding stables)
treshold = 0.05 # Max percentage that a coin can slip (up or down) from the fixed weight in the portfolio
btc_pct = 0.3 # Percentage of BTC in the Portfolio
eth_pct = 0.5 # Percentage of ETH in the Portfolio
rest_pct = (1 - btc_pct - eth_pct) / (number_of_coins-2) # Percentage of the rest of coins in the Portfolio
sender_email = "" # email address of the account you will use to send the alert email. You will have to allow access to “less secure apps" in your google account https://myaccount.google.com/lesssecureapps (using a different account than your main account is recommended) 
password = "" # email password of the account you will use to send the alert email
receiver_email = [""] # email address or adressses you want to send the alert email to
coin_mkt_cap_key = '' # CoinMarketCap PRO API KEY. THERE IS A FREE TIER.
ignored_coins = ["USDT","USDC","DOGE","DAI","BUSD","WBTC"] # I ignore DOGE even though its not a stablecoin because it has way too much volatility
server = False #Is the script running in a server (True) or not (False)?. Variable used to know if it should send the email alerts or not.
# ------------------------------------------------------------------------------------------------------------------------------------------


#FIXED VARIABLES
portfolio_value = capital
return_portfolio = 0
treshold_reached = False

#CONNECT TO COIN MARKET CAP API AND DOWNLOAD TOP X number of COINS (defined in limit)
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

parameters = {
  'start':'1',
  'limit':'12', #number of coins to download (including stables)
  "convert":"usd"
}
headers = {
  'Accepts': 'application/json', 
  'X-CMC_PRO_API_KEY': coin_mkt_cap_key, 
}


session = Session()
session.headers.update(headers)

json = requests.get(url, params = parameters, headers = headers).json()

coins = json["data"]
symbols = []
cmc_ranks = []
prices = []

for x in coins:
	symbols.append(x["symbol"])
	cmc_ranks.append(x["cmc_rank"])
	prices.append(x["quote"]["USD"]["price"])



#CREATE DATAFRAME WITH REAL TIME DATA OBTAINED BY COINMARKETCAP API
df = pd.DataFrame(columns=["Rank", "Symbol", "Price"])

df["Rank"] = cmc_ranks
df["Symbol"] = symbols
df["Price"] = prices

df = df.set_index("Symbol")


#DROP IGNORED COINS
df = df.drop(ignored_coins, errors='ignore')

df = df.reset_index().set_index('Rank')

for coin in df["Symbol"]:
	df["USD Allocation"] = df["Symbol"].apply(lambda x: (capital * btc_pct) if x == "BTC" else ((capital * eth_pct) if x == "ETH" else (capital * rest_pct)))
	df["Coins Allocation"] = df["USD Allocation"] / df["Price"]


df = df[["Symbol","Price","Coins Allocation","USD Allocation"]]
	

#ONLY KEEP LAST x NUMBER OF COINS
df = df.iloc[0:number_of_coins]


# print("\n")
# print("REAL TIME DATA")
# print(df[["Symbol","Price"]])



#READ DATAFRAME FROM FILE IF EXISTS; CREATES A NEW ONE OTHERWISE
try:
	df_invested = pd.read_excel("treshold.xlsx")
except:
	df_invested = df



#UPDATES REAL TIME PRICES AND VALUATION
def invest():
	global df
	global df_invested
	df = df.reset_index().set_index('Symbol')
	df_invested = df_invested.reset_index().set_index('Symbol')
	for coin in df_invested["Coins Allocation"]:
		df_invested["Rank"] = df["Rank"]
	df = df.reset_index().set_index('Rank')
	df_invested = df_invested.reset_index().set_index('Rank')
	for coin in df_invested["Symbol"]:
		df_invested["Price"] = df["Price"]
		df_invested["USD Allocation"] = round(df_invested["Price"] * df_invested["Coins Allocation"],2)


invest()



new_portfolio_value = round(df_invested['USD Allocation'].sum(),2)



#UPDATES THE VALUE OF THE PORTFOLIO USING REAL TIME PRICES
def update_portfolio_value(dataframe):
	for coin in dataframe["Symbol"]:
		dataframe["% Portfolio"] = round(dataframe["USD Allocation"] / new_portfolio_value * 100,2)

update_portfolio_value(df_invested)

return_portfolio = round(((new_portfolio_value / capital)-1) * 100,2)
amount_return = round(new_portfolio_value - capital,2)


#DELETES AND SAVES DATAFRAME TO FILE
try:
	os.remove("treshold.xlsx")
except:
	pass
try:	
	df_invested = df_invested.drop(columns="index")
except:
	pass
writer = pd.ExcelWriter('treshold.xlsx')
df_invested.to_excel(writer)
writer.save()


#PRINTS WITH INFO
print("\n")
print("INVESTED PORTFOLIO")
print(df_invested)
print("\n")
print("Initial Investment: $ " + str(f"{capital:,}"))
print("Porfolio Value:     $ " + str(f"{new_portfolio_value:,}"))
print("Difference in USD:  $ " + str(f"{amount_return:,}"))
print("Portolio Return:      " + str(return_portfolio) + " %")
print("\n")



#CHECKS IF THE TOP X COINS REMAINS THE SAME AS THE INVESTED PORTFOLIO. SENDS EMAIL IF NOT.
def check_coin_list():
	global treshold_reached
	list_coins = []
	list_invested_coins = []
	sell_coin = df_invested["Symbol"].iloc[-1]
	buy_coin = df["Symbol"].iloc[-1]
	
	subject= "New Coin in Portfolio"
	msg = EmailMessage()
	msg.set_content(f"""There is a new coin in the top {number_of_coins}. \n \n SELL {sell_coin} \n BUY {buy_coin}  \n \n Modify Excel Spreadsheet with {buy_coin}. \n Remember to change all columns including the correct index matching ranking of Coin Market Cap""") #email body
	msg["Subject"] = subject
	msg["From"] = 'Portfolio Rebalance Alert <{sender_email}>'
	msg["To"] = receiver_email
	for coin,new_coin in zip(df["Symbol"],df_invested["Symbol"]):
		list_coins.append(coin)
		list_invested_coins.append(new_coin)
	if set(list_coins) == set(list_invested_coins):
		pass
	else:
		if server == True:
			context = ssl.create_default_context()
			with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
		    		smtp.starttls(context=context)
		    		smtp.login(sender_email, password)
		    		smtp.send_message(msg)
			treshold_reached = True

			print("********************* THERE IS A NEW COIN IN THE TOP " + str(number_of_coins)+ " **********************")
			print("*************************** BUY " + buy_coin + " ***************************")
			print("*************************** SELL " + sell_coin + " ***************************")
			print("******* MODIFY EXCEL SPREADSHEET WITH NEW COIN AND NUMBER OF COINS **********")
			sys.exit("\n")
		else:
			print("********************* THERE IS A NEW COIN IN THE TOP " + str(number_of_coins)+ " **********************")
			print("*************************** BUY " + buy_coin + " ***************************")
			print("*************************** SELL " + sell_coin + "***************************")
			print("******* MODIFY EXCEL SPREADSHEET WITH NEW COIN AND NUMBER OF COINS **********")
			sys.exit("\n")

check_coin_list()


#CHECKS IF SOME OF THE COINS WE ARE INVESTED IN REACHED THE THRESHOLD FOR REBALANCE
def check_treshold():
	global treshold_reached
	for coin,pct in zip(df_invested["Symbol"],df_invested["% Portfolio"]):
		if coin == "BTC" and pct > (btc_pct * (1 + treshold)*100):
			print("***************** THE PORTFOLIO SHOULD BE REBALANCED *****************")
			print("********* MODIFY EXCEL SPREADSHEET WITH NEW COIN ALLOCATIONS *********")
			treshold_reached = True
			break
		elif coin == "BTC" and pct < (btc_pct * (1 - treshold)*100):
			print("***************** THE PORTFOLIO SHOULD BE REBALANCED *****************")
			print("********* MODIFY EXCEL SPREADSHEET WITH NEW COIN ALLOCATIONS *********")
			treshold_reached = True
			break
		elif coin == "ETH" and pct > (eth_pct * (1 + treshold)*100):
			print("***************** THE PORTFOLIO SHOULD BE REBALANCED *****************")
			print("********* MODIFY EXCEL SPREADSHEET WITH NEW COIN ALLOCATIONS *********")
			treshold_reached = True
			break
		elif coin == "ETH" and pct < (eth_pct * (1 - treshold)*100):
			print("***************** THE PORTFOLIO SHOULD BE REBALANCED *****************")
			print("********* MODIFY EXCEL SPREADSHEET WITH NEW COIN ALLOCATIONS *********")
			treshold_reached = True
			break
		elif coin != "BTC" and coin != "ETH" and pct > (rest_pct * (1 + treshold)*100):
			print("***************** THE PORTFOLIO SHOULD BE REBALANCED *****************")
			print("********* MODIFY EXCEL SPREADSHEET WITH NEW COIN ALLOCATIONS *********")
			treshold_reached = True
			break
		elif coin != "BTC" and coin != "ETH" and pct < (rest_pct * (1 - treshold)*100):
			print("***************** THE PORTFOLIO SHOULD BE REBALANCED *****************")
			print("********* MODIFY EXCEL SPREADSHEET WITH NEW COIN ALLOCATIONS *********")
			treshold_reached = True
			break
		else:
			pass
	print("\n")	

check_treshold()


#REBALANCE IF THRESHOLD HAS BEEN REACHED. SEND EMAIL 
def rebalance():
	global df_invested
	global treshold_reached
	global portfolio_value
	new_df_invested = df_invested
	coins_difference = []
	coin_buy_sell = {}
	
	#CALCULATE BUY AND SELL FOR REBALANCING EACH COIN
	for coin, usd, price in zip(new_df_invested["Symbol"],new_df_invested["USD Allocation"],new_df_invested["Price"]):
		if (str(coin) == "BTC"):
			coin_buy_sell[str(coin)] = round(((usd - new_portfolio_value * btc_pct) * -1) / price,5)
			coins_difference.append(coin_buy_sell)

			if coin_buy_sell.get(coin) >= 0:
				print("BUY  " + str(coin) + " : " + "+" + str(coin_buy_sell.get(str(coin))))
			else:
				print("SELL " + str(coin) + " : " + str(coin_buy_sell.get(str(coin))))

		elif (str(coin) == "ETH"):
			coin_buy_sell[str(coin)] = round(((usd - new_portfolio_value * eth_pct) * -1) / price,5)
			coins_difference.append(coin_buy_sell)

			if coin_buy_sell.get(coin) >= 0:
				print("BUY  " + str(coin) + " : " + "+" + str(coin_buy_sell.get(str(coin))))
			else:
				print("SELL " + str(coin) + " : " + str(coin_buy_sell.get(str(coin))))
		
		else :
			coin_buy_sell[str(coin)] = round(((usd - new_portfolio_value * rest_pct) * -1) / price,5)
			coins_difference.append(coin_buy_sell)

			if coin_buy_sell.get(coin) >= 0:
				print("BUY  " + str(coin) + " : " + "+" + str(coin_buy_sell.get(str(coin))))
			else:
				print("SELL " + str(coin) + " : " + str(coin_buy_sell.get(str(coin))))
	coins_difference = coins_difference[number_of_coins-1]

	#NEW ALLOCATIONS PORTFOLIO
	for coin, usd, price in zip(new_df_invested["Symbol"],new_df_invested["USD Allocation"],new_df_invested["Price"]):
		new_df_invested["USD Allocation"] = new_df_invested["Symbol"].apply(lambda x: (new_portfolio_value * btc_pct) if x == "BTC" else ((new_portfolio_value * eth_pct) if x == "ETH" else (new_portfolio_value * rest_pct)))
		new_df_invested["Coins Allocation"] = new_df_invested["USD Allocation"] / df["Price"]
		
	
	# SEND EMAIL IF RUNNING IN SERVER 
	subject= "Portfolio Rebalance Alert"
	msg = EmailMessage()
	msg.set_content(f"""Rebalance Portfolio. Threshold reached. \n \n {df_invested} \n \n Initial Investment:  $ {f"{capital:,}"} \n Portfolio Value:      $ {f"{new_portfolio_value:,}"} \n Difference in USD: $ {f"{amount_return:,}"} \n Portfolio Return:    {return_portfolio} % \n \n Coin Rebalance: \n {coins_difference} \n""") #email body
	msg["Subject"] = subject
	msg["From"] = 'Portfolio Rebalance Alert <{sender_email}>'
	msg["To"] = receiver_email

	
	if server == True:
		context = ssl.create_default_context()
		with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
			smtp.starttls(context=context)
			smtp.login(sender_email, password)
			smtp.send_message(msg)
			print("\n" + 'Email Alert Sent' + "\n")
	else:
		pass						
	
	#UPDATE INVESTED PORTFOLIO WITH REBALANCED ALLOCATION AND SAVE TO FILE
	update_portfolio_value(new_df_invested)
	treshold_reached = False
	df_invested = df_invested[0:0] 
	df_invested = new_df_invested
	update_portfolio_value(df_invested)

	try:
		os.remove("treshold.xlsx")
	except:
		pass
	try:	
		df_invested = df_invested.drop(columns="index")
	except:
		pass
	
	writer = pd.ExcelWriter('treshold.xlsx')
	df_invested.to_excel(writer)
	writer.save()

	print("\n")
	print("***************** THE PORTFOLIO SHOULD BE REBALANCED *****************")
	print("********* MODIFY EXCEL SPREADSHEET WITH NEW COIN ALLOCATIONS *********")
	print("\n")
	print("REBALANCED PORTFOLIO")
	print(df_invested)
	print("\n")
	

if treshold_reached:
	rebalance()
	









