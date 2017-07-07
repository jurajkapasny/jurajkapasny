
# coding: utf-8

# In[1]:

import glob
import pandas as pd
import numpy as np


# In[2]:

#data_path = "/Users/jurajkapasny/Data/sk_text_for_api"


# In[4]:

def load_data(path):
    allFiles = glob.glob(path + "/*.csv")
    print "Number of files to process: %d" %len(allFiles)
    df = pd.DataFrame()
    list_ = []
    i = 0
    for file_ in allFiles:
        if (file_.find("articles") != -1) & (file_.find("temo") == -1):
            i = i + 1
            if i%50 == 0:
                print "Processing file %d" %i
            temp = pd.read_csv(file_,sep = "|",index_col=None, header=0, parse_dates=True, low_memory=False)
            list_.append(temp)
    df = pd.concat(list_)
    return df

# In[5]:

# df.count()


# In[ ]:



