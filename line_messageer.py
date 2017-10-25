import datetime

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from coverage.files import os
from matplotlib import style
from matplotlib.finance import candlestick_ohlc

from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage

from flask import Flask, request, json
from pymongo import MongoClient
from chart import Chart

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client['stock']
collectStock = db['stock']
otc_list = db['otc_list']
twse_list = db['twse_list']


@app.route('/')
def index():
    return "<p>Hello World!</p>"


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.route('/callback', methods=['POST'])
def callback():
    json_line = request.get_json()
    json_line = json.dumps(json_line)
    decoded = json.loads(json_line)

    message = decoded['events'][0]['message']['text']
    stockNo = message[1:5]

    type = decoded['events'][0]['source']['type']
    source = decoded['events'][0]['source']

    line_bot_api = LineBotApi('')

    if message[:1] == 'K':
        Chart(stockNo)
        image_message = ImageSendMessage(
            original_content_url='https://48622930.ngrok.io/static/{0}.png'.format(stockNo),
            preview_image_url='https://48622930.ngrok.io/static/{0}.png'.format(stockNo)
        )
        if type == 'group':
            line_bot_api.push_message(source['groupId'], image_message)
        else:
            line_bot_api.push_message(source['userId'], image_message)

    elif message[:1] == 'I':
        str = ''

        result = twse_list.find_one({'stock_id': stockNo})

        if result is not None:
            str = '{0}\n{1}\n{2}\n{3}'.format('上市', result['stock_name'], result['stock_id'], result['stock_category'])
        else:
            result = otc_list.find_one({'stock_id': stockNo})
            str = '{0}\n{1}\n{2}\n{3}'.format('上櫃', result['stock_name'], result['stock_id'], result['stock_category'])

        if type == 'group':
            line_bot_api.push_message(source['groupId'], TextSendMessage(text=str))
        else:
            line_bot_api.push_message(source['userId'], TextSendMessage(text=str))

    return ''


if __name__ == '__main__':
    app.run(debug=True)
