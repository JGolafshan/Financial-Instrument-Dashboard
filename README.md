# Stock Dashboard


This repository provides an interactive dashboard for analyzing financial assets. It includes:
 - Asset Overview – A comprehensive summary of various financial assets.
 - Black-Scholes Pricing Model – An interactive dashboard that visualizes option prices under different market conditions, allowing users to explore the impact of spot price, volatility, and other parameters on option valuation.

The dashboard is designed to be user-friendly and interactive, making financial analysis more accessible and insightful.

Additionally, this repository includes a comprehensive list of over 54,000 tickers, covering a wide range of financial instruments.

https://financial-instrument-dashboard.streamlit.app/

# TODO

- Query Review
- Enable custom stock database
- Database
- cookie user id
- Create a document database 
- Show all requests
- Improve doc string
- Improve comments
- Improve Performance
- Complete README

# Completed
- Finish instrument page 
  - monti carlo
  - BS Model
  - Overview

- Search Functionality:DONE
- Error page:DONE
- Query Page finalized:DONE
    
## 🚀 Features:

1. **Options Pricing Visualization**: 
   - Displays both Call and Put option prices using an interactive heatmap.
   - The heatmap dynamically updates as you adjust parameters like Spot Price, Volatility, and Time to Maturity.
   
2. **Interactive Dashboard**:
   - The dashboard allows real-time updates to the Black-Scholes model parameters.
   - Users can input different values for the Spot Price, Volatility, Strike Price, Time to Maturity, and Risk-Free Interest Rate to observe how these factors influence option prices.
   - Both Call and Put option prices are calculated and displayed for immediate comparison.
   
3. **Customizable Parameters**:
   - Set custom ranges for Spot Price and Volatility to generate a comprehensive view of option prices under different market conditions.

4. **View Other User Queries**:
   

## 🔧 Dependencies: 
- `yfinance`: To fetch current asset prices.
- `numpy`: For numerical operations.
- `matplotlib`: For heatmap visualization.


