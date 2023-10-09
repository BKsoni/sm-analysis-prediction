import yfinance as yf
from dateutil.relativedelta import relativedelta
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
import pandas as pd
from .yFinanaceData import getTickerData
from ..models import Tickers, LSTMModel

TIME_STEP = 100
EPOCHS = 10
FIELD = 'Close'

def replace_nan_with_nearest(arr):
    for i in range(len(arr)):
        if np.isnan(arr[i][0]):
            left_index = i - 1
            right_index = i + 1

            while left_index >= 0 and np.isnan(arr[left_index][0]):
                left_index -= 1
            while right_index < len(arr) and np.isnan(arr[right_index][0]):
                right_index += 1

            if left_index >= 0 and right_index < len(arr):
                arr[i][0] = (arr[left_index][0] + arr[right_index][0]) / 2
            elif left_index >= 0:
                arr[i][0] = arr[left_index][0]
            elif right_index < len(arr):
                arr[i][0] = arr[right_index][0]

def create_dataset(dataset,time_step=1):
    dataX,dataY = [],[]
    for i in range(len(dataset)-time_step-1):
        a = dataset[i:(i+time_step),0]
        dataX.append(a)
        dataY.append(dataset[i+time_step,0])
    return np.array(dataX),np.array(dataY)

def train_lstm_model(SYMBOL="RELIANCE.NS"):
    print("INSIDEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
    # from .yFinanaceData import getTickerData
    SYMBOL = SYMBOL.upper()
    ticker, name = getTickerData(SYMBOL)
    ticker.dropna(axis=0,inplace=True)
    ticker['MA5'] = ticker['Close'].rolling(5).mean()
    ticker['MA20'] = ticker['Close'].rolling(20).mean()
    df=ticker.reset_index()[FIELD]

    scaler=MinMaxScaler(feature_range=(0,1))
    df=scaler.fit_transform(np.array(df).reshape(-1,1))

    training_size=int(len(df)*0.70)
    train_data, test_data = df[0:training_size,:], df[training_size:len(df),:1]

    X_train,Y_train = create_dataset(train_data, TIME_STEP)
    X_test,Y_test = create_dataset(test_data, TIME_STEP)
    X_train = X_train.reshape(X_train.shape[0],X_train.shape[1],1)
    X_test = X_test.reshape(X_test.shape[0],X_test.shape[1],1)
    model=Sequential()
    model.add(LSTM(50,return_sequences=True,input_shape=(TIME_STEP,1)))
    model.add(LSTM(50,return_sequences=True))
    model.add(LSTM(50,return_sequences=True))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error',optimizer='adam')

    print("LSTM Model Created!")
    print(model.summary())

    model.fit(X_train,Y_train, validation_data=(X_test,Y_test), epochs=EPOCHS, batch_size=64, verbose=1)

    train_predict=model.predict(X_train)
    test_predict=model.predict(X_test)

    train_predict=scaler.inverse_transform(train_predict)
    test_predict=scaler.inverse_transform(test_predict)

    newY_test = Y_test.reshape(-1, 1)
    newY_test = scaler.inverse_transform(newY_test)
    x_input=test_data[len(test_data)-TIME_STEP:].reshape(1,-1)
    temp_input=list(x_input)
    temp_input=temp_input[0].tolist()

    lst_output=[]
    n_step=TIME_STEP
    i=0
    while(i<30):
        if(len(temp_input)>100):
            x_input=np.array(temp_input[1:])
            x_input=x_input.reshape(1,-1)
            x_input=x_input.reshape((1,n_step,1))
            yh=model.predict(x_input,verbose=0)
            temp_input.extend(yh[0].tolist())
            temp_input=temp_input[1:]
            lst_output.extend(yh.tolist())
            i=i+1
        else:
            x_input=x_input.reshape((1,n_step,1))
            yh=model.predict(x_input,verbose=0)
            temp_input.extend(yh[0].tolist())
            lst_output.extend(yh.tolist())
            i=i+1

    print("LSTM Model Predicted!")
    df2=df.tolist()

    # Extending Predicted output
    df2.extend(lst_output)
    df2=scaler.inverse_transform(df2).tolist()
    replace_nan_with_nearest(df2)
    all_prices = [item[0] for item in df2 if not np.isnan(item[0])]
    print(all_prices)
    # Extending new dates
    current_date = ticker.index[-1]

    all_dates = ticker.index.tolist()

    for i in range(30):
        current_date = current_date + relativedelta(days=1)
        all_dates.append(current_date.strftime("%Y-%m-%d"))

    converted_dates = []
    for date in all_dates:
        if isinstance(date, pd.Timestamp):
            converted_date = date.strftime('%Y-%m-%d')
        else:
            converted_date = date

        converted_dates.append(converted_date)

    all_dates = converted_dates

    # Get the Ticker object
    try:
        ticker = Tickers.objects.get(ticker=SYMBOL)
    except Tickers.DoesNotExist:
        ticker = Tickers.objects.create(ticker=SYMBOL, name=name)
        ticker.save()

    # Check if the Ticker exists
    if LSTMModel.objects.filter(ticker=ticker).exists() is False:
    # If the Ticker does not exist, create a new LinearRegressionModel
        LSTMModel.objects.create(ticker=ticker, prices=all_prices, dates=all_dates).save()
    else:
    # If the Ticker exists, update the associated LinearRegressionModel
        try:
            lstm_data = LSTMModel.objects.get(ticker=ticker)
            lstm_data.prices = all_prices
            lstm_data.dates = all_dates
            lstm_data.save()
        except LSTMModel.DoesNotExist:
            LSTMModel.objects.create(ticker=ticker, prices=all_prices, dates=all_dates).save()
