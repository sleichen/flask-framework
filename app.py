from flask import Flask, render_template, request, redirect
import requests
import pandas as pd
from bokeh.plotting import figure, show, output_notebook
from bokeh.embed import components 
from datetime import datetime as dt

app = Flask(__name__)

#initialize variables to some default values
app.vars = {}

@app.route('/')
@app.route('/index', methods = ['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('/index.html')
    else:
        app.vars['ticker'] = request.form['ticker']
        app.vars['features'] = request.form.getlist('features')
        return redirect('/graph')
    
@app.route('/graph')
def graph():
    ticker = app.vars['ticker']
    features  = app.vars['features']
    api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json' % ticker
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
    raw_data = session.get(api_url)
    data_df = pd.DataFrame(columns = raw_data.json()['column_names'], data  = raw_data.json()['data'])
    data_df.Date = data_df.Date.apply(lambda x: dt.strptime(x, '%Y-%m-%d'))

    plot = figure(title='Stock Price Data from Quandle for '+ ticker,
              x_axis_label='Date',
              x_axis_type='datetime',
              y_axis_label = 'Price')

    color_dic = {'Open':'green', 'Close': 'red', 'Adj. Open': 'green', 'Adj. Close': 'purple'}

    for feature in features:
        plot.line(data_df['Date'], data_df[feature], legend = ticker + ":" + feature,\
              line_width=1, line_color=color_dic[feature])    

    script, div = components(plot)

    return render_template('graph.html', script=script, div=div)
        
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=33507)
