'''
Load assessment scores
  - from excel files

Peter Ryan May 2020
'''

import os
import pandas as pd
import numpy as np
import math
from scipy import stats

import statsmodels.api as sm
from statsmodels.stats import diagnostic as diag
from statsmodels.stats.outliers_influence import variance_inflation_factor


from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

from tabulate import tabulate




# Directory containing files
directory = 'H:\\Projects\\CoB\\FNP31 Results\\'
filename = 'FNP31_results_clean.xlsx'

df = pd.read_excel(directory + filename,
                   sheet_name='2019',
                   skipfooter=0)

print(tabulate(df, headers='keys'))
# check correlations
print(df.corr())
print('\n\n')


# describe the data sets
print(df.describe())
#df.hist(grid=False, color='cadetblue')

# check kurtosis ans skew
'''
print(stats.kurtosistest(df['Test']))
print(stats.kurtosistest(df['Assign']))
print(stats.kurtosistest(df['Exam']))

print(stats.skewtest(df['Test']))
print(stats.skewtest(df['Assign']))
print(stats.skewtest(df['Exam']))
'''



print(tabulate(df, headers='keys'))

pd.plotting.scatter_matrix(df, alpha=1, figsize=(30, 20))
import pylab
#pylab.show()

X = df.drop(['Exam', 'Term'], axis=1)
Y = df[['Exam']]

#split data set in training and testing
X_train, X_test, y_train, y_test = train_test_split(X, Y,
                                                    test_size=0.20,
                                                    random_state=1)

# create model
reg = LinearRegression()

# fit model
reg.fit(X, Y)

int = reg.intercept_[0]
coeff = reg.coef_[0]

print(int)
for c in zip(X.columns, coeff):
  print(" The coeff for {} is {}".format(c[0], c[1]))

# Get predictions
y_predict = reg.predict(X_test)

#define input
X2 = sm.add_constant(X)

# create OLS model
model = sm.OLS(Y, X2)

# fit data
est = model.fit()


# test for heteroscedasticity (want p values over 0.05)
_, pval, _, f_pval = diag.het_white(est.resid, est.model.exog, retres=False)
print(pval, f_pval)
print('_'*100)

_, pval, _, f_pval = diag.het_breuschpagan(est.resid, est.model.exog)
print(pval, f_pval)
print('_'*100)
# values greater than 0.05 there is no heterodasticity

# test for autocorrelation want p values over 0.05)
lag = min(10, (len(X)//5))
print("number of lags is {}".format(lag))
ibvalue, pval = diag.acorr_ljungbox(est.resid, lags=lag)
print(min(pval))
print('_'*100)

# check residuals are normal (visual, close to line)

sm.qqplot(est.resid, line='s')
pylab.show()

# check that mean of the residuals is zero
mean_resid = sum(est.resid)/len(est.resid)
print('mean residual= {}'.format(mean_resid))
print('_'*100)

# calculate root mean square error
model_rmse = math.sqrt(mean_squared_error(y_test, y_predict))

print('rmse= {}'.format(model_rmse))
print('_'*100)

# calculate r2
print('r2= {}'.format(r2_score(y_test, y_predict)))
print('_'*100)

print(est.conf_int())
print('_'*100)
print(est.pvalues)
print('_'*100)

print(est.summary())


df.Assign = df.Assign.fillna(df.Assign.mean())
df.Test = df.Test.fillna(df.Test.mean())


reg = LinearRegression()

reg.fit(df[['Test', 'Assign']], df.Exam)

print(reg.coef_)

print(reg.intercept_)

print(reg.predict([[7.5, 25], [12, 27], [12, 26], [12, 24]]))
