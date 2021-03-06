import yfinance as yf
import datetime 
import pandas as pd
import datetime as dt
from datetime import date
import math
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
from tqdm.notebook import tqdm
from tensorflow import keras
from plotly import graph_objs as go
import cufflinks as cf
import pandas_datareader as pdr

# App title
st.markdown('''
# Stock Price App
Shown are the stock price data for query companies!

**Credits**
- App built by Van Hieu
- Built in `Python` using `streamlit`,`yfinance`, `cufflinks`, `pandas` and `datetime`
''')
st.write('---')

# Get ticker list
ticker_list = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/s-and-p-500-companies/master/data/constituents_symbols.txt')

# Loading Data
def load_data(ticker, start_date, end_date):
    # Get ticker data
    tickerData = yf.Ticker(ticker)
    #Get the historical prices for this ticker
    data = tickerData.history(period='1d', start=start_date, end=end_date)
    return data

def close_price_plot(data, symbol):
    data['Date'] = data.index
    st.set_option('deprecation.showPyplotGlobalUse', False)
    plt.fill_between(data.Date, data.Close, alpha=0.3)
    plt.plot(data.Date, data.Close, alpha=0.8)
    plt.xticks(rotation=90)
    plt.title(symbol, fontweight='bold')
    plt.xlabel('Date', fontweight='bold')
    plt.ylabel('Çlosing Price', fontweight='bold')
    return st.pyplot()

def open_price_plot(data1, symbol1):
    data1['Date'] = data1.index
    st.set_option('deprecation.showPyplotGlobalUse', False)
    plt.fill_between(data1.Date, data1.Open, alpha=0.3)
    plt.plot(data1.Date, data1.Open, alpha=0.8)
    plt.xticks(rotation=90)
    plt.title(symbol1, fontweight='bold')
    plt.xlabel('Date', fontweight='bold')
    plt.ylabel('Opening Price', fontweight='bold')
    return st.pyplot()
    
def low_price_plot(data2, symbol2):
    data2['Date'] = data2.index
    st.set_option('deprecation.showPyplotGlobalUse', False)
    plt.fill_between(data2.Date, data2.Low, alpha=0.3)
    plt.plot(data2.Date, data2.Low, alpha=0.8)
    plt.xticks(rotation=90)
    plt.title(symbol2, fontweight='bold')
    plt.xlabel('Date', fontweight='bold')
    plt.ylabel('Low Price', fontweight='bold')
    return st.pyplot()

def high_price_plot(data3, symbol3):
    data3['Date'] = data3.index
    st.set_option('deprecation.showPyplotGlobalUse', False)
    plt.fill_between(data3.Date, data3.High, alpha=0.3)
    plt.plot(data3.Date, data3.High, alpha=0.8)
    plt.xticks(rotation=90)
    plt.title(symbol3, fontweight='bold')
    plt.xlabel('Date', fontweight='bold')
    plt.ylabel('High Price', fontweight='bold')
    return st.pyplot()

#For Stock Financials
def stock_financials(tickerSymbol):
    df_ticker = yf.Ticker(tickerSymbol)
    sector = df_ticker.info['sector']
    prevClose = df_ticker.info['previousClose']
    marketCap = df_ticker.info['marketCap']
    twoHunDayAvg = df_ticker.info['twoHundredDayAverage']
    fiftyTwoWeekHigh = df_ticker.info['fiftyTwoWeekHigh']
    fiftyTwoWeekLow = df_ticker.info['fiftyTwoWeekLow']
    Name = df_ticker.info['longName']
    averageVolume = df_ticker.info['averageVolume']
    ftWeekChange = df_ticker.info['52WeekChange']
    website = df_ticker.info['website']

#Creating Training and Testing Data for other Models ----------------------
def create_train_test_data(df1):

    data = df1.sort_index(ascending=True, axis=0)
    new_data = pd.DataFrame(index=range(0, len(df1)), columns=['Date', 'High', 'Low', 'Open', 'Volume', 'Close'])

    for i in range(0, len(data)):
        new_data['Date'][i] = data['Date'][i]
        new_data['High'][i] = data['High'][i]
        new_data['Low'][i] = data['Low'][i]
        new_data['Open'][i] = data['Open'][i]
        new_data['Volume'][i] = data['Volume'][i]
        new_data['Close'][i] = data['Close'][i]

    #Removing the hour, minute and second
    new_data['Date'] = pd.to_datetime(new_data['Date']).dt.date

    train_data_len = math.ceil(len(new_data) * .8)

    train_data = new_data[:train_data_len]
    test_data = new_data[train_data_len:]

    return train_data, test_data

#For LSTM Model ------------------------------
def create_train_test_LSTM(df, epoch, b_s, ticker_name):

    df_filtered = df.filter(['Close'])
    dataset = df_filtered.values

    #Training Data
    training_data_len = math.ceil(len(dataset) * .7)

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset)

    train_data = scaled_data[0: training_data_len, :]

    x_train_data, y_train_data = [], []

    for i in range(60, len(train_data)):
        x_train_data.append(train_data[i-60:i, 0])
        y_train_data.append(train_data[i, 0])

    x_train_data, y_train_data = np.array(x_train_data), np.array(y_train_data)

    x_train_data = np.reshape(x_train_data, (x_train_data.shape[0], x_train_data.shape[1], 1))

    #Testing Data
    test_data = scaled_data[training_data_len - 60:, :]

    x_test_data = []
    y_test_data = dataset[training_data_len:, :]

    for j in range(60, len(test_data)):
        x_test_data.append(test_data[j - 60:j, 0])

    x_test_data = np.array(x_test_data)

    x_test_data = np.reshape(x_test_data, (x_test_data.shape[0], x_test_data.shape[1], 1))


    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train_data.shape[1], 1)))
    model.add(LSTM(units=50, return_sequences=False))

    model.add(Dense(25))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')

    model.fit(x_train_data, y_train_data, batch_size=int(b_s), epochs=int(epoch))
    st.success("Your Model is Trained Succesfully!")
    st.markdown('')
    st.write("Predicted vs Actual Results for LSTM")
    st.write("Stock Prediction on Test Data for - ",ticker_name)

    predictions = model.predict(x_test_data)
    predictions = scaler.inverse_transform(predictions)

    train = df_filtered[:training_data_len]
    valid = df_filtered[training_data_len:]
    valid['Predictions'] = predictions

    new_valid = valid.reset_index()
    new_valid.drop('index', inplace=True, axis=1)
    st.dataframe(new_valid)
    st.markdown('')
    st.write("Plotting Actual vs Predicted ")

    st.set_option('deprecation.showPyplotGlobalUse', False)
    plt.figure(figsize=(14, 8))
    plt.title('Actual Close prices vs Predicted Using LSTM Model', fontsize=20)
    plt.plot(valid[['Close', 'Predictions']])
    plt.legend(['Actual', 'Predictions'], loc='upper left', prop={"size":20})
    st.pyplot()

#Finding Moving Average ---------------------------------------

def find_moving_avg(ma_button, df):
    days = ma_button

    data1 = df.sort_index(ascending=True, axis=0)
    new_data = pd.DataFrame(index=range(0, len(df)), columns=['Date', 'Close'])

    for i in range(0, len(data1)):
        new_data['Date'][i] = data1['Date'][i]
        new_data['Close'][i] = data1['Close'][i]

    new_data['SMA_'+str(days)] = new_data['Close'].rolling(min_periods=1, window=days).mean()

    #new_data.dropna(inplace=True)
    new_data.isna().sum()

    #st.write(new_data)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=new_data['Date'], y=new_data['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=new_data['Date'], y=new_data['SMA_'+str(days)], mode='lines', name='SMA_'+str(days)))
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01), height=550, width=800,
                      autosize=False, margin=dict(l=25, r=75, b=100, t=0))

    st.plotly_chart(fig)

#Finding Linear Regression ----------------------------

def Linear_Regression_model(train_data, test_data):

    x_train = train_data.drop(columns=['Date', 'Close'], axis=1)
    x_test = test_data.drop(columns=['Date', 'Close'], axis=1)
    y_train = train_data['Close']
    y_test = test_data['Close']

    #First Create the LinearRegression object and then fit it into the model
    from sklearn.linear_model import LinearRegression

    model = LinearRegression()
    model.fit(x_train, y_train)

    #Making the Predictions
    prediction = model.predict(x_test)

    return prediction

#Plotting the Predictions -------------------------
def prediction_plot(pred_data, test_data, models, ticker_name):

    test_data['Predicted'] = 0
    test_data['Predicted'] = pred_data

    #Resetting the index
    test_data.reset_index(inplace=True, drop=True)
    st.success("Your Model is Trained Succesfully!")
    st.markdown('')
    st.write("Predicted Price vs Actual Close Price Results for - " ,models)
    st.write("Stock Prediction on Test Data for - ", ticker_name)
    st.write(test_data[['Date', 'Close', 'Predicted']])
    st.write("Plotting Close Price vs Predicted Price for - ", models)

    #Plotting the Graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=test_data['Date'], y=test_data['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=test_data['Date'], y=test_data['Predicted'], mode='lines', name='Predicted'))
    fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01), height=550, width=800,
                      autosize=False, margin=dict(l=25, r=75, b=100, t=0))

    st.plotly_chart(fig)

def BollingerBands(tickerSymbol):
    st.header(f'{tickerSymbol} Stock Price')
    df_ticker = pdr.DataReader(tickerSymbol, 'yahoo', start_date, end_date)
    qf = cf.QuantFig(df_ticker, legend='top', name=tickerSymbol)
    qf.add_rsi(periods=20, color='java')
    qf.add_bollinger_bands(periods=20,boll_std=2,colors=['magenta','grey'],fill=True)
    qf.add_volume()
    fig = qf.iplot(asFigure=True, dimensions=(800, 600))
    st.plotly_chart(fig)

# st.title("Stock Analysis")
menu = ["Stock Analysis", "Train Model"]
choices = st.sidebar.selectbox("Menu", menu)

if choices == "Stock Analysis":
    # Create subheader
    st.subheader("Extract Data")
    st.markdown('')
    st.markdown('**_Select_ _Stocks_ _to_ Train**')
    # Create startdate and enddate input
    tickerSymbol = st.selectbox('Stock ticker', ticker_list)
    tickerData = yf.Ticker(tickerSymbol)
    start_date = st.date_input("Start date", datetime.date(2015, 1, 1))
    end_date = st.date_input("End date", datetime.date(2021, 1, 31))
    # Trigger data
    data = load_data(tickerSymbol, start_date, end_date)
    st.markdown('')
    st.write('---')
    # Ticker information
    string_logo = '<img src=%s>' % tickerData.info['logo_url']
    st.markdown(string_logo, unsafe_allow_html=True)
    # Name company
    string_name = tickerData.info['longName']
    st.subheader('**%s**' % string_name)
    # Info. company
    string_summary = tickerData.info['longBusinessSummary']
    st.info(string_summary)
    st.write('---')
    st.subheader('**%s data**' % string_name)
    st.write(data)
    st.markdown('')
    st.write('---')
    # Data plots
    menu1 = ["Select your option","Closing Price Plot", "Opening Price Plot","Low Price Plot", "High Price Plot"]
    st.markdown('Select from the options below to Explore Stocks')
    options = st.selectbox("", menu1)
    if options == 'Closing Price Plot':
        submit_button = st.button("Extract Features")
        if submit_button:
            st.subheader('Stock Closing Price')
            close_price_plot(data, tickerSymbol)

    elif options == 'Opening Price Plot':
        submit_button = st.button("Extract Features")
        if submit_button:
            st.subheader('Stock Opening Price')
            open_price_plot(data, tickerSymbol)
    
    elif options == 'Low Price Plot':
        submit_button = st.button("Extract Features")
        if submit_button:
            st.subheader('Stock Low Price')
            low_price_plot(data, tickerSymbol)
    
    elif options == 'High Price Plot':
        submit_button = st.button("Extract Features")
        if submit_button:
            st.subheader('Stock High Price')
            high_price_plot(data, tickerSymbol)

elif choices == 'Train Model':
    # Create subheader
    st.subheader("Train Machine Learning Models for Stock Prediction")
    st.markdown('')
    st.markdown('**_Select_ _Stocks_ _to_ Train**')
    # Create startdate and enddate input
    tickerSymbol = st.selectbox('Stock ticker', ticker_list)
    tickerData = yf.Ticker(tickerSymbol)
    start_date = st.date_input("Start date", datetime.date(2015, 1, 1))
    end_date = st.date_input("End date", datetime.date(2021, 1, 31))
    # Trigger data
    data = load_data(tickerSymbol, start_date, end_date)
    data = data.reset_index()
    data['Date'] = pd.to_datetime(data['Date']).dt.date
    # Selected options
    options = ['Select your option', 'Moving Average', 'Linear Regression', 'Bollinger Bands', 'LSTM']
    st.markdown('')
    st.markdown('**_Select_ _Machine_ _Learning_ _Algorithms_ to Train**')
    models = st.selectbox("", options)
    submit1 = st.button('Train Model')
    
    if models == 'LSTM':
        st.markdown('')
        st.markdown('')
        st.markdown("**Select the _Number_ _of_ _epochs_ and _batch_ _size_ for _training_ form the following**")
        st.markdown('')
        epoch = st.slider("Epochs", 0, 300, step=1)
        b_s = st.slider("Batch Size", 32, 1024, step=1)
        if submit1:
            st.write('**Your _final_ _dataframe_ _for_ Training**')
            st.write(data[['Date','Close']])
            create_train_test_LSTM(data, epoch, b_s, tickerSymbol)

    elif models == 'Linear Regression':
        if submit1:
            st.write('**Your _final_ _dataframe_ _for_ Training**')
            st.write(data[['Date','Close']])
            train_data, test_data = create_train_test_data(data)
            pred_data = Linear_Regression_model(train_data, test_data)
            prediction_plot(pred_data, test_data, models, tickerSymbol)

    elif models == 'Bollinger Bands':
        if submit1:
           BollingerBands(tickerSymbol)

    elif models == 'Moving Average':
        ma_button = st.number_input("Select Number of Days Moving Average", 5, 200)
        st.write('Stock Data based on Moving Average')
        st.write('A Moving Average(MA) is a stock indicator that is commonly used in technical analysis')
        st.write(
            'The reason for calculating moving average of a stock is to help smooth out the price of data over '
            'a specified period of time by creating a constanly updated average price')
        st.write(
            'A Simple Moving Average (SMA) is a calculation that takes the arithmatic mean of a given set of '
            'prices over the specified number of days in the past, for example: over the previous 15, 30, 50, '
            '100, or 200 days.')
        if submit1:
                st.write('You entered the Moving Average for ', ma_button, 'days')
                find_moving_avg(ma_button, data)
