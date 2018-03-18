#coding=utf-8
import datetime
import json
import urllib2
import threading
import Adafruit_DHT
import time
from Waveshare_Epaper_UART import *

time.sleep(30)

class DisplayAll(threading.Thread):
    def __init__(self):  
        threading.Thread.__init__(self)
        self.wdict = None
        self.filmlines = None
        self.booklines = None
        # self.init = True
        # self.load_data()
        self.init_screen()
        self.fetch_weather()
        self.fetch_quotes()

    def init_screen(self):
        self.screen = Screen('/dev/ttyAMA0')
        self.screen.connect()
        self.screen.handshake()
        self.screen.clear()
        self.screen.set_memory(MEM_SD)

    def run(self):
        while True:
            minute = time.strftime("%M") 
            hour = time.strftime("%H")
            if minute == '01' or '31': # update weather every 30m
                self.fetch_weather()
            if hour == '06' or '18': # update quote every 12h
                self.fetch_quotes()
            self.update_screen()
            time.sleep(60)

    def update_screen(self):
        self.screen.clear()
        self.show_timedate()
        self.show_weather()
        self.show_indoor_cond()
        self.show_cntdown()
        self.book_movie()
        self.screen.update()

    
    def show_timedate(self):
        clock_x = 5
        clock_y = 40
        temp_x = 0
        time_now = datetime.datetime.now()
        time_str = time_now.strftime('%H:%M')
        date_str = time_now.strftime('%d/%m/%Y')
        week_str = time_now.strftime('%a')
    
        self.screen.set_en_font_size(FONT_SIZE_48)
        for c in time_str:
            # n_bmp = 'NUM{}.BMP'.format('S' if c == ':' else c)
            n_bmp = 'N{}.BMP'.format('UMS' if c == ':' else c)
            self.screen.bitmap(clock_x + temp_x, clock_y, n_bmp)
            temp_x += 60 if c == ':' else 91
        self.screen.text(clock_x + 450 , clock_y + 90, date_str)
        self.screen.text(clock_x + 450 + 250, clock_y + 90, week_str)
        self.screen.line(0, clock_y + 160, 800, clock_y + 160)
        self.screen.line(0, clock_y + 161, 800, clock_y + 161)
        self.screen.line(230, 200, 230, 600)
        self.screen.line(230, 360, 800, 360)

        TheDay = datetime.date(2018,04,11)
        Today  = datetime.date.today()
        cntdown = (TheDay - Today).days
        self.screen.set_en_font_size(FONT_SIZE_64)
        self.screen.text(clock_x + 450 + 10, clock_y, str(cntdown))
        self.screen.set_en_font_size(FONT_SIZE_32)
        self.screen.text(clock_x + 450 + 10 + 68, clock_y+25, 'days till in-class test')
        self.screen.set_en_font_size(FONT_SIZE_48)
    
    
    def fetch_weather(self):
        json_web = urllib2.urlopen('http://api.wunderground.com/api/467046bee5094888/conditions/q/zmw:00000.40.03571.json')
        json_str = json_web.read()
        self.wdict    = json.loads(json_str)  

    def fetch_quotes(self):
        statuses = api.user_timeline(id='MovieQuotesPage',count=15)
        for s in statuses:
            if len(s.text) <= 80:
                tweet = s.text
        self.filmlines = textwrap.wrap(tweet,39)

        bookstatuses = api.user_timeline(id='HereBestBooks',count=15)
        for s in bookstatuses:
            if len(s.text) <= 80:
                booktweet = s.text
        self.booklines = textwrap.wrap(booktweet,39)



    def show_weather(self):

        self.screen.text(15, 220,'Cambridge')  # Location
        temp = self.wdict['current_observation']['temp_c']
        temp = str(temp)
        humi = self.wdict['current_observation']['relative_humidity']
        cw_f = self.wdict['current_observation']['weather']
        cw_f  = cw_f.split()
        if len(cw_f) > 1:
            cw = cw_f[1]
        else:
            cw = cw_f[0]
        self.screen.text(40, 460, cw)
        self.screen.text(1, 530, temp + '℃')
        self.screen.text(140, 530, humi)
    
        w_bmp = 'WDYZQ.BMP'
        if cw_f == 'Clear':
            w_bmp = 'WQING.BMP'
        elif cw_f == 'Cloudy' or cw_f == 'Overcast':
            w_bmp = 'WYIN.BMP'
        elif 'Partly' in cw_f or 'Mostly' in cw_f:
            w_bmp = 'WDYZQ.BMP'
        elif 'Rain' in cw_f:
            w_bmp = 'WYU.BMP'
        elif 'Drizzle' in cw_f:
            w_bmp = 'WXYU.BMP'
        elif 'Snow' in cw_f:
            w_bmp = 'WXUE.BMP'
        elif 'Hail' in cw_f:
            w_bmp = 'WBBAO.BMP'
        elif 'Fog' in cw_f or 'Haze' in cw_f:
            w_bmp = 'WWU.BMP'
        
        self.screen.bitmap(20, 280, w_bmp)
    
    
    def show_indoor_cond(self):
        h, t = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
        rtemp = str(int(t)) + '℃'
        rhumi = str(int(h)) + ' %'
        self.screen.bitmap(250, 250, 'TEMP.BMP')
        self.screen.bitmap(250, 300, 'HUMI.BMP') 
        self.screen.text(290,240, rtemp)
        self.screen.text(290,290, rhumi)
    
    
    def show_cntdown(self):
        DM = api.direct_messages(count=1,full_text=True) 
        msg = DM[0].text
        wrap = textwrap.wrap(msg,26)
        self.screen.bitmap(410, 250, 'MSG.BMP')
        self.screen.set_en_font_size(FONT_SIZE_32)
        self.screen.text(490,250, wrap[0])
        if len(wrap) > 1:
            self.screen.text(490,290, wrap[1])

    
    def book_movie(self):
        self.screen.bitmap(240, 395, 'FILM.BMP')
        self.screen.bitmap(240, 505, 'BOOK.BMP')

        self.screen.text(320,390, self.filmlines[0])
        if len(self.filmlines) > 1:
            self.screen.text(320,430, self.filmlines[1])
        self.screen.text(320,500, self.booklines[0])
        if len(self.booklines) > 1:
            self.screen.text(320,540, self.booklines[1])


import textwrap
import tweepy

consumer_key        = "EnwX69MWlC7btxqIN8vwrxkEG"
consumer_secret     = "izGyD5qCSdg3lPsDuURpN57Y7VbqW1xWqP0813Vg1HgH2yXBzC"
access_token        = "972286632677330949-bQuQgj8pxbM6g2XvAli1gxFjbhLcFKi"
access_token_secret = "Ts8jsVYZmCs4LoMQwfxHZMbU1ctbKGWB3PF0vxHkTtbPO"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

Epaper = DisplayAll()
Epaper.start()
