## crypto dashboard ##
- Project Description
This project is a Cryptocurrency Dashboard built with Python and Tkinter. Using OOP style.

# Features
1. Real-time data using WebSocket
2. Candlestick chart using Matplotlib
3. Multiple crypto selection (BTC, ETH, SOL, DOGE, etc.)
4. Show / hide panels dynamically
5. Save user preferences (selected crypto, visible panels)

# Class Overview
1. CryptoDashboard
It's a main controller of the application that creates the UI layout,  
manages all panels ,handles user interactions and Updates all components when a crypto is selected  

2. CryptoTicker
- Shows real-time price updates
- Uses WebSocket to receive live data
- Allows user to select a cryptocurrency

3.OrderBookPanel
- Displays buy and sell orders
- Updates in real time from Binance

4. TradesPanel
- Shows latest trade history
- Keeps recent trades using a queue (deque)

5. CandlestickChart
- Displays candlestick price chart
- Uses Matplotlib embedded in Tkinter

6. PriceTable
- Displays price statistics (open, high, low, volume, etc.)

7. utils.py
- Saves and loads user preferences
- Stores data in dashboard_config.json

# Advanced feature 
- Real-time cryptocurrency data : The dashboard shows live prices using WebSocket connections.
- Multiple cryptocurrency support : Users can choose between BTC, ETH, SOL, DOGE, XRP, ADA, and MATIC.
- Live price ticker : Displays current price and price changes in real time.
- Order book display : Shows buy and sell orders for the selected cryptocurrency.
- Recent trades panel : Displays the latest trade history with timestamps.
- Candlestick price chart : Visualizes price movement using a candlestick chart.
- Price statistics table : Shows important price information such as open, high, low, and volume.
- Panel show / hide control : Users can show or hide panels using control buttons.
- Saved user preferences : The application remembers selected crypto and visible panels.
- Object-Oriented Design (OOP) : The code is structured into multiple classes for better organization.
- Tkinter GUI : Built with Python Tkinter for a desktop application interface.

# How to Run the Program
1. Install Required Libraries
2. make sure that all code was in the same folder
3. Run the file (main.py)
