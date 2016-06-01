
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
dtype_dict = {'bathrooms':float, 
              'waterfront':int, 
              'sqft_above':int, 
              'sqft_living15':float,
              'grade':int,
              'yr_renovated':int,
              'price':float, 
              'bedrooms':float, 
              'zipcode':str, 
              'long':float, 'sqft_lot15':float, 'sqft_living':float, 'floors':str, 
              'condition':int, 'lat':float, 'date':str, 'sqft_basement':int, 'yr_built':int,
              'id':str, 'sqft_lot':int, 'view':int}


# In[2]:

def polynomial_dframe(feature, degree):
    # assume that degree >= 1
    # initialize the DFrame:
    poly_dframe = pd.DataFrame()
    # and set poly_sframe['power_1'] equal to the passed feature
    poly_dframe["power_1"] = feature
    # first check if degree > 1
    if degree > 1:
        # then loop over the remaining degrees:
        for power in range(2, degree+1):
            # first we'll give the column a name:
            name = 'power_' + str(power)
            # assign poly_sframe[name] to be feature^power
            poly_dframe[name] = feature ** power
    return poly_dframe


# In[5]:

sales = pd.read_csv('kc_house_data.csv', dtype=dtype_dict)
sales = sales.sort_values(['sqft_living','price'])


# In[6]:

poly1_data = polynomial_dframe(sales['sqft_living'], 1)
poly1_data['price'] = sales['price']


# In[10]:

from sklearn import linear_model
# Create linear regression object
regr1 = linear_model.LinearRegression()
model1 = regr1.fit(poly1_data.power_1.values.reshape(len(poly1_data.index), 1), 
                   poly1_data.price.values.reshape(len(poly1_data.index), 1))


# In[13]:

import matplotlib.pyplot as plt
plt.plot(poly1_data['power_1'],
         poly1_data['price'],
         '.',
         poly1_data['power_1'],
         (regr1.predict(poly1_data
                      .power_1
                      .values
                      .reshape(len(poly1_data
                                   .index),
                               1))
          .transpose())[0],'-')
plt.show()


# In[15]:

part1 = pd.read_csv("wk3_kc_house_set_1_data.csv", dtype=dtype_dict)
part2 = pd.read_csv("wk3_kc_house_set_2_data.csv", dtype=dtype_dict)
part3 = pd.read_csv("wk3_kc_house_set_3_data.csv", dtype=dtype_dict)
part4 = pd.read_csv("wk3_kc_house_set_4_data.csv", dtype=dtype_dict)


# In[21]:

poly1_data = polynomial_dframe(part1['sqft_living'], 15)
poly2_data = polynomial_dframe(part2['sqft_living'], 15)
poly3_data = polynomial_dframe(part3['sqft_living'], 15)
poly4_data = polynomial_dframe(part4['sqft_living'], 15)
poly1_data['price'] = part1['price']
poly2_data['price'] = part2['price']
poly3_data['price'] = part3['price']
poly4_data['price'] = part4['price']


# In[26]:

regr1 = linear_model.LinearRegression()
model1 = regr1.fit(poly1_data.drop("price", axis=1).as_matrix(), 
                   poly1_data.price.values.reshape(len(poly1_data.index), 1))
regr2 = linear_model.LinearRegression()
model2 = regr2.fit(poly2_data.drop("price", axis=1).as_matrix(), 
                   poly2_data.price.values.reshape(len(poly2_data.index), 1))
regr3 = linear_model.LinearRegression()
model3 = regr3.fit(poly3_data.drop("price", axis=1).as_matrix(), 
                   poly3_data.price.values.reshape(len(poly3_data.index), 1))
regr4 = linear_model.LinearRegression()
model4 = regr1.fit(poly4_data.drop("price", axis=1).as_matrix(), 
                   poly4_data.price.values.reshape(len(poly4_data.index), 1))


# In[27]:

train = pd.read_csv("wk3_kc_house_train_data.csv", dtype=dtype_dict)
test = pd.read_csv("wk3_kc_house_test_data.csv", dtype=dtype_dict)
validation = pd.read_csv("wk3_kc_house_valid_data.csv", dtype=dtype_dict)


# In[30]:

best = 0
best_rss = float("Inf")
for i in range(1, 16):
    poly1_data = polynomial_dframe(train["sqft_living"], i)
    poly1_data["price"] = train["price"]
    regr1 = linear_model.LinearRegression()
    model1 = regr1.fit(poly1_data.drop("price", axis=1).as_matrix(), 
                       poly1_data.price.values.reshape(len(poly1_data.index), 1))
    
    poly1_data_val = polynomial_dframe(validation["sqft_living"], i)
    poly1_data_val["price"] = validation["price"]
    pred_test = regr1.predict(poly1_data_val.drop("price", axis=1).as_matrix()).transpose()[0]
    rss = np.mean((pred_test - poly1_data_val.price.values) ** 2)
    print("Residual sum of squares: %.2f , order polynomial: %s"
      % (rss, i))
    if rss < best_rss:
        best_rss = rss
        best = i
print "Best rss for order: %s" %best
poly1_data = polynomial_dframe(train["sqft_living"], best)
poly1_data["price"] = train["price"]
regr1 = linear_model.LinearRegression()
model1 = regr1.fit(poly1_data.drop("price", axis=1).as_matrix(), 
                   poly1_data.price.values.reshape(len(poly1_data.index), 1))

poly1_data_test = polynomial_dframe(test["sqft_living"], best)
poly1_data_test["price"] = test["price"]
pred_test = regr1.predict(poly1_data_test.drop("price", axis=1).as_matrix()).transpose()[0]
rss = np.mean((pred_test - poly1_data_test.price.values) ** 2)
print "RSS on test: %s" %rss


# In[ ]:



