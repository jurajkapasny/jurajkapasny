
# coding: utf-8

# In[24]:

import smtplib
from email.mime.text import MIMEText
import requests
import pandas as pd

from pandas import DataFrame
from StringIO import StringIO
me = "info@jamieniederer.com"
you = "toma.lukas@gmail.com"
USERNAME = "wp12368441-349353"
PASSWORD = "HHgs152.2"
SERVER = 'wp028.webpack.hosteurope.de'
PORT = 587


# In[22]:

#read from google doc
r = requests.get('https://docs.google.com/spreadsheets/d/1Lytul8W-hYwhyWoD2Z4_ZqpkV2iNg0aNoNS27waHr2c/export?format=csv&id')
data = r.content

df = pd.read_csv(StringIO(data))


# In[25]:

#create message
msg = MIMEText("test text to send")
msg['Subject'] = "FREE VIAGRA"
msg['From'] = me
msg['To'] = you

# Send the message via our own SMTP server, but don't include the
# envelope header.
s = smtplib.SMTP(SERVER, PORT)
s.ehlo()
s.starttls()
s.ehlo()
s.login(USERNAME, PASSWORD)
s.sendmail(me, [you], msg.as_string())
s.quit()


# In[ ]:

df_ready_to_send = df.ix[df.to_send == "OK"]

