# -*- coding: utf-8 -*-
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

line_bot_api = LineBotApi('db2W0M6n+YN84WscM6W9vVtUmji+oAVXKNs3BCFs1cfOoX0ng4m3jtFmol7Z8C2Xmm3aY62JuYPtbDCzvPG23qit2P8RNFjrAKiAhCkhPj5FxPOrY9BA14WTb8swpL9I3LT4V4K3JQZhyWRaPkPIcwdB04t89/1O/w1cDnyilFU=')
# Channel access token (long-lived)
handler = WebhookHandler('91fec83ea2c09ab57ef0dd80e6be823e')
# Channel secret 

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def getNews():
    """
    建立一個抓最新消息的function
    """
    import requests
    import re
    from bs4 import BeautifulSoup

    url = 'https://www.ettoday.net/news/focus/3C%E5%AE%B6%E9%9B%BB/'
    r = requests.get(url)
    reponse = r.text

    url_list = re.findall(r'<h3><a href="/news/[\d]*/[\d]*.htm" .*>.*</a>',reponse)

    soup = BeautifulSoup(url_list[0])
    url = 'https://fashion.ettoday.net/' + soup.find('a')['href']
    title = soup.text


    tmp = title + ': ' +url
    return tmp

from bs4 import BeautifulSoup
import requests
def movie(num):
    num = int(num)
    target_url = 'http://www.atmovies.com.tw/movie/next/0/'
    print('Start parsing movie ...')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = []
    for index, data in enumerate(soup.select('ul.filmListAll a')):
        if index == num:
            break
        title = data.text.replace('\t', '').replace('\r', '')
        link = "http://www.atmovies.com.tw" + data['href']
        if len(title) == 0:
            num += 1
            continue
        content += [[title, link]]
    return content

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 傳送文字
    if event.message.text.startswith('電影-'):
        _, num = event.message.text.split('-')
        print(num)
        movie_info = movie(num)
        print(movie_info)
        columns_info = []
        for m in movie_info:
            colum = CarouselColumn(
                    thumbnail_image_url='https://example.com/item1.jpg',
                    title=m[0],
                    text=m[0],
                    actions=[
                        URITemplateAction(
                            label='前往觀看',
                            uri=m[1]
                        )
                    ]
                )
            columns_info += [colum]
        print(columns_info)        
        message = TemplateSendMessage(
            alt_text='新聞文章',
            template=CarouselTemplate(columns= columns_info)
        )
    else:
        message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)

    
if __name__ == '__main__':
    app.run(debug=True)