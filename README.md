# rebalanced-crypto-portfolio

This is a script to invest in the Top "x" number of cryptos by market cap, and keep the portfolio balanced by a determined threshold.

For explanation visit:  
https://www.reddit.com/r/CryptoCurrency/comments/ozlvfy/python_script_to_rebalance_portfolio_and_invest/

What it basically does is given a certain amount of capital, how many coins you want to invest in, the percentage of each coin you want to allocate in the portfolio and the threshold you decide to use for rebalancing; it constructs the portfolio.  

It will download real time data from CoinMarketCap, remove the stable coins from the list and allocate the capital according to your settings.

![Screen Shot 2021-08-08 at 19 04 26](https://user-images.githubusercontent.com/28694518/128783477-7f6ab24f-119d-4e6f-bffb-d1d76bde96a1.png)

Also It will generate an excel file (treshold.xlsx) in the same folder where the script is at with your portfolio holdings and real time prices and values. When rebalancing you can edit the excel accordingly (the coins allocation column) so next time the script runs it picks up your new rebalanced portfolio allocations.  

![Screen Shot 2021-08-08 at 19 05 35](https://user-images.githubusercontent.com/28694518/128783499-a831b428-79cf-46ff-a86a-8642070a09ae.png)

When rebalancing a portfolio you have two options. Rebalancing by frequency or by threshold. I chose the latter. It means that if you for instance ,choose to allocate 30% of the portfolio to BTC, a threshold of 10 % would be reached when the weight in the portfolio reaches 27 or 33% (30% +/- 0.1 * 30).
If rebalancing is needed it will tell you the amount of coins for each crypto you have to buy or sell to keep the portfolio balanced.  

![Screen Shot 2021-08-08 at 19 19 35](https://user-images.githubusercontent.com/28694518/128783519-934efabe-efbc-46a2-918b-af0b0e8e4a9e.png) 

If you keep it running in a server it will automatically alert you by email when you have to rebalance the portfolio because a threshold has been reached for one or more coins. It will also alert you if any new coin has entered the top "x" in your list so you get rid of the old one for the new one.  

![Screen Shot 2021-08-08 at 19 29 17](https://user-images.githubusercontent.com/28694518/128783540-6576d54e-3552-4cbf-85d9-de5ec02e13c6.jpg)

  
    
      
#
#
#

AUTHOR: Diego Madrigali   
TWITTER: @dmadrigali   
GITHUB: burdo3417  

