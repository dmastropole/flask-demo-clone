#from __future__ import print_function # In python 2.7
#import sys

import datetime
import dateutil.relativedelta
import numpy as np
import scipy as sp
import bokeh.plotting as bp
from bokeh import embed
import pandas as pd

import requests
import simplejson as json

from flask import Flask, render_template, request, redirect
app_stock = Flask(__name__)

@app_stock.route('/', methods=['GET','POST'])
def main():
  if request.method == 'GET':
    return render_template('wiki_code.html')
  else:
    return redirect('/trends')

@app_stock.route('/trends', methods=['GET', 'POST'])
def trends():
  
  #create url for api
  wiki_code = request.form['wiki_code']
  url = 'https://www.quandl.com/api/v3/datasets/WIKI/'
  url = url + wiki_code + '.json?'
  
  #set start and end date
  end_date = datetime.date.today()
  start_date = end_date - dateutil.relativedelta.relativedelta(months=1)

  #convert dates to strings
  start_date = start_date.strftime('%Y/%m/%d')
  end_date = end_date.strftime('%Y/%m/%d')
  
  #set parameters for url
  params = {'column_index':4,'start_date':start_date,'end_date':end_date,'api_key':'SFx6jqyfXv_dK7zyzniy'}
  
  #request data
  #print(url,file=sys.stderr) #debugging purposes
  r = requests.get(url=url, params=params)
  dataset = json.loads(r.content)
  data_dict = dataset['dataset']
  data = data_dict['data']
  
  #organize data into pandas dataframe
  data = np.array(data)
  X = data[:,0]
  Y = data[:,1]
  x = X.astype('datetime64')
  y = Y.astype('float')

  df = pd.DataFrame({'Prices':y},index=x)
  df.sort_index()
  
  #print bokeh plot
  ttl = "Last Month's Closing Price for "  + wiki_code
  p = bp.figure(title=ttl, x_axis_label='Date', y_axis_label='Price', x_axis_type='datetime')
  p.line(df.index, df['Prices'], color='#2222aa', line_width=3)
  
  #embed bokeh plot
  script, div = embed.components(p)
  
  return render_template('timeseries.html', script=script, div=div, ttl=ttl)

if __name__ == '__main__':
  app_stock.run(host='0.0.0.0', port=5000)
