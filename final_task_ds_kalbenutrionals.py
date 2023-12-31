# -*- coding: utf-8 -*-
"""Final_Task_DS_KalbeNutrionals.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14z5EPdo8bbHMkU6eyl0mulVZ7ojG7GXo
"""

from logging import warning
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings ('ignore')

from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, silhouette_score
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from pandas.plotting import autocorrelation_plot

df_customer = pd.read_csv(r'/content/drive/MyDrive/Machine Learning/CSV/Final Project PBI internship Kalbe Nutrionals DS/customer.csv', delimiter=';')
df_product = pd.read_csv(r'/content/drive/MyDrive/Machine Learning/CSV/Final Project PBI internship Kalbe Nutrionals DS/product.csv', delimiter=';')
df_store = pd.read_csv(r'/content/drive/MyDrive/Machine Learning/CSV/Final Project PBI internship Kalbe Nutrionals DS/store.csv', delimiter=';')
df_transaction = pd.read_csv(r'/content/drive/MyDrive/Machine Learning/CSV/Final Project PBI internship Kalbe Nutrionals DS/transaction.csv', delimiter=';')

df_customer.shape, df_product.shape, df_store.shape, df_transaction.shape

df_customer.head()

df_product.head()

df_store.head()

df_transaction.head()

df_customer['Income'] = df_customer['Income'].replace('[,]', '.',regex=True).astype('float')
df_store['Latitude'] = df_store['Latitude'].replace('[,]', '.',regex=True).astype('float')
df_store['Longitude'] = df_store['Longitude'].replace('[,]', '.',regex=True).astype('float')
df_transaction['Date'] = pd.to_datetime(df_transaction['Date'])

df_merge = pd.merge(df_transaction, df_customer, on=['CustomerID'])
df_merge = pd.merge(df_merge, df_product.drop(columns=['Price']), on=['ProductID'])
df_merge = pd.merge(df_merge, df_store, on=['StoreID'])

df_merge.head()

df_regresi = df_merge.groupby(['Date']).agg({
    'Qty' : 'sum'
}).reset_index()

df_regresi

decomposed = seasonal_decompose(df_regresi.set_index('Date'))
plt.figure(figsize=(8, 8))
plt.subplot(311)
decomposed.trend.plot(ax=plt.gca())
plt.title('Trend')
plt.subplot(312)
decomposed.seasonal.plot(ax=plt.gca())
plt.title('Seasonality')
plt.subplot(313)
decomposed.resid.plot(ax=plt.gca())
plt.title('Residuals')
plt.tight_layout()

cut_off = round(df_regresi.shape[0] * 0.9)
df_train = df_regresi[:cut_off]
df_test = df_regresi[cut_off:].reset_index(drop=True)
df_train.shape, df_test.shape

df_train

df_test

plt.figure(figsize=(20,5))
sns.lineplot(data=df_train, x=df_train['Date'], y=df_train['Qty'])
sns.lineplot(data=df_test, x=df_test['Date'], y=df_test['Qty'])

autocorrelation_plot(df_regresi['Qty'])

def rmse(y_actual, y_pred):
  print(f'RMSE Value {mean_squared_error(y_actual, y_pred)*0.5}')
def eval(y_actual, y_pred):
  rmse(y_actual, y_pred)
  print(f'MAX value {mean_absolute_error(y_actual, y_pred)}')

df_train = df_train.set_index('Date')
df_test = df_test.set_index('Date')

y = df_train['Qty']
ARIMAmodel = ARIMA(y, order = (2, 1, 1), seasonal_order=(2, 1, 1, 12))
ARIMAmodel = ARIMAmodel.fit()

y_pred = ARIMAmodel.get_forecast(len(df_test))

y_pred_df = y_pred.conf_int()
y_pred_df['predictions'] = ARIMAmodel.predict(start = y_pred_df.index[0], end = y_pred_df.index[-1])
y_pred_df.index = df_test.index
y_pred_out = y_pred_df['predictions']
eval(df_test['Qty'], y_pred_out)

"""Model Prediksi Quantity"""

plt.figure(figsize=(20,5))
plt.plot(df_train['Qty'])
plt.plot(df_test['Qty'], color = 'red')
plt.plot(y_pred_out, color = 'black', label = 'ARIMA Predictions')
plt.legend()

"""Segmentasi Pelanggan"""

df_merge.head()

df_cluster = df_merge.groupby(['CustomerID']).agg({
    'TransactionID' : 'count',
    'Qty' : 'sum',
    'TotalAmount' : 'sum'
}).reset_index()

df_cluster

data_cluster = df_cluster.drop(columns=['CustomerID'])
data_cluster_normalize = preprocessing.normalize(data_cluster)

data_cluster_normalize

K = range(2, 8)
fits = []
score = []

for k in K:
  model = KMeans(n_clusters = k, random_state = 0, n_init='auto').fit(data_cluster_normalize)
  fits.append(model)
  score.append(silhouette_score(data_cluster_normalize, model.labels_, metric = 'euclidean'))

sns.lineplot(x = K, y = score)

df_cluster['cluster_label'] = fits[1].labels_

df_cluster.groupby(['cluster_label']).agg({
    'CustomerID' : 'count',
    'TransactionID' : 'mean',
    'Qty' : 'mean',
    'TotalAmount' : 'mean'
})