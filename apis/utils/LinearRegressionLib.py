from sklearn.linear_model import LinearRegression
from statsmodels.tsa.deterministic import CalendarFourier, DeterministicProcess
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from .yFinanaceData import getTickerData
from ..models import Tickers, LinearRegressionModel

def train_model(SYMBOL="RELIANCE.NS"):
    # from .yFinanaceData import getTickerData
    SYMBOL = SYMBOL.upper()
    ticker, name = getTickerData(SYMBOL)
    ticker['Time'] = np.arange(len(ticker.index))
    ticker['Date'] = ticker.index
    ticker = ticker.set_index("Date").to_period('D')
    ticker = ticker.loc['6/1/2020':]
    ticker = ticker[["Close"]]
    df = ticker.copy()
    df['Time'] = np.arange(len(ticker.index))

    from sklearn.linear_model import LinearRegression

    # Training data
    X = df.loc[:, ['Time']]  # features
    y = df.loc[:, 'Close']  # target

    # Train the model
    model = LinearRegression()
    model.fit(X, y)

    # Store the fitted values as a time series with the same time index as
    # the training data
    y_pred = pd.Series(model.predict(X), index=X.index)

    df['Lag_1'] = df['Close'].shift(1)

    from sklearn.linear_model import LinearRegression

    X = df.loc[:, ['Lag_1']]
    X.dropna(inplace=True)  # drop missing values in the feature set
    y = df.loc[:, 'Close']  # create the target
    y, X = y.align(X, join='inner')  # drop corresponding values in target

    model = LinearRegression()
    model.fit(X, y)

    y_pred = pd.Series(model.predict(X), index=X.index)

    from statsmodels.tsa.deterministic import DeterministicProcess

    dp = DeterministicProcess(
        index=ticker.index,  # dates from the training data
        constant=True,       # dummy feature for the bias (y_intercept)
        order=1,             # the time dummy (trend)
        drop=True,           # drop terms if necessary to avoid collinearity
    )
    # `in_sample` creates features for the dates given in the `index` argument
    X = dp.in_sample()

    from sklearn.linear_model import LinearRegression

    y = ticker["Close"]  # the target

    # The intercept is the same as the `const` feature from
    # Deterministic Process. LinearRegression behaves badly with duplicated
    # features, so we need to be sure to exclude it here.
    model = LinearRegression(fit_intercept=False)
    model.fit(X, y)

    y_pred = pd.Series(model.predict(X), index=X.index)

    X = dp.out_of_sample(steps=30)

    y_fore = pd.Series(model.predict(X), index=X.index)

    trend_forecast = pd.concat([y_pred, y_fore])
    trend_forecast = [round(float_value, 2) for float_value in trend_forecast]

    from statsmodels.tsa.deterministic import CalendarFourier, DeterministicProcess

    fourier = CalendarFourier(freq="A", order=10)  # 10 sin/cos pairs for "A"nnual seasonality

    dp = DeterministicProcess(
        index=ticker.index,
        constant=True,               # dummy feature for bias (y-intercept)
        order=1,                     # trend (order 1 means linear)
        seasonal=True,               # weekly seasonality (indicators)
        additional_terms=[fourier],  # annual seasonality (fourier)
        drop=True,                   # drop terms to avoid collinearity
    )

    X = dp.in_sample()  # create features for dates in tunnel.index

    y = ticker["Close"]
    model = LinearRegression(fit_intercept=False)
    _ = model.fit(X, y)

    y_pred = pd.Series(model.predict(X), index=y.index)
    X_fore = dp.out_of_sample(steps=90)
    y_fore = pd.Series(model.predict(X_fore), index=X_fore.index)

    seasonal_forecast = pd.concat([y_pred, y_fore])
    seasonal_forecast = [round(float_value, 2) for float_value in seasonal_forecast]
    dates = [str(date) for date in y.index]
    # Get the Ticker object
    try:
        ticker = Tickers.objects.get(ticker=SYMBOL)
    except Tickers.DoesNotExist:
        ticker = Tickers.objects.create(ticker=SYMBOL, name=name)
        ticker.save()

    # Check if the Ticker exists
    if LinearRegressionModel.objects.filter(ticker=ticker).exists() is False:
    # If the Ticker does not exist, create a new LinearRegressionModel
        LinearRegressionModel.objects.create(ticker=ticker, trend_forecast=trend_forecast, seasonal_forecast=seasonal_forecast, dates=dates).save()
    else:
    # If the Ticker exists, update the associated LinearRegressionModel
        try:
            linear_regression_data = LinearRegressionModel.objects.get(ticker=ticker)
            linear_regression_data.trend_forecast = trend_forecast
            linear_regression_data.seasonal_forecast = seasonal_forecast
            linear_regression_data.dates = dates
            linear_regression_data.save()
        except LinearRegressionModel.DoesNotExist:
            LinearRegressionModel.objects.create(ticker=ticker, trend_forecast=trend_forecast, seasonal_forecast=seasonal_forecast, dates=dates).save()
