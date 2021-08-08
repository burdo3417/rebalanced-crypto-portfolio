# rebalanced-crypto-portfolio

This is a script to invest in the Top "x" number of cryptos by market cap, and keep the portfolio balanced by a determined threshold.

For explanation visit:  
https://www.reddit.com/r/CryptoCurrency/comments/ozlvfy/python_script_to_rebalance_portfolio_and_invest/

What it basically does is given a certain amount of capital, how many coins you want to invest in, the percentage of each coin you want to allocate in the portfolio and the threshold you decide to use for rebalancing; it constructs the portfolio.  

It will download real time data from CoinMarketCap, remove the stable coins from the list and allocate the capital according to your settings.    

Also It will generate an excel file (treshold.xlsx) in the same folder where the script is at with your portfolio holdings and real time prices and values. When rebalancing you can edit the excel accordingly (the coins allocation column) so next time the script runs it picks up your new rebalanced portfolio allocations.  

When rebalancing a portfolio you have two options. Rebalancing by frequency or by threshold. I chose the latter. It means that if you for instance ,choose to allocate 30% of the portfolio to BTC, a threshold of 10 % would be reached when the weight in the portfolio reaches 27 or 33% (30% +/- 0.1 * 30).
If rebalancing is needed it will tell you the amount of coins for each crypto you have to buy or sell to keep the portfolio balanced.  

If you keep it running in a server it will automatically alert you by email when you have to rebalance the portfolio because a threshold has been reached for one or more coins. It will also alert you if any new coin has entered the top "x" in your list so you get rid of the old one for the new one.  

  
    
      
#
#
#

AUTHOR: Diego Madrigali   
TWITTER: @dmadrigali   
GITHUB: burdo3417  

