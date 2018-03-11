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
        # self.init = True
        # self.load_data()
        self.init_screen()
        self.fetch_weather()

    def init_screen(self):
        self.screen = Screen('/dev/ttyAMA0')
        self.screen.connect()
        self.screen.handshake()
        self.screen.clear()
        self.screen.set_memory(MEM_SD)

    def run(self):
        while True:
            minute = time.strftime("%M") 
            if minute == '01' or minute == '31':
                self.fetch_weather()
            self.update_screen()
            time.sleep(60)

    def update_screen(self):
        self.screen.clear()
        self.show_timedate()
        self.show_weather()
        self.show_indoor_cond()
        self.twitter_DM()
        self.book_movie()
        self.screen.update()

    
    def show_timedate(self):
        clock_x = 40
        clock_y = 40
        temp_x = 0
        time_now = datetime.datetime.now()
        time_str = time_now.strftime('%H:%M')
        date_str = time_now.strftime('%Y-%m-%d')
        week_str = time_now.strftime('%A')
    
        self.screen.set_en_font_size(FONT_SIZE_48)
        for c in time_str:
            w_bmp = 'NUM{}.BMP'.format('S' if c == ':' else c)
            self.screen.bitmap(clock_x + temp_x, clock_y, w_bmp)
            temp_x += 70 if c == ':' else 100
        self.screen.text(clock_x + 350 + 140, clock_y + 10, date_str)
        self.screen.text(clock_x + 350 + 170, clock_y + 70, week_str)
        self.screen.line(0, clock_y + 160, 800, clock_y + 160)
        self.screen.line(0, clock_y + 161, 800, clock_y + 161)
        self.screen.line(240, 200, 240, 600)
    
    
    def fetch_weather(self):
        json_web = urllib2.urlopen('http://api.wunderground.com/api/467046bee5094888/conditions/q/zmw:00000.40.03571.json')
        json_str = json_web.read()
        self.wdict    = json.loads(json_str)  

    def show_weather(self):

        self.screen.text(20, 220,'Cambridge')  # Location
        
        
        temp = self.wdict['current_observation']['temp_c']
        temp = str(temp)
        humi = self.wdict['current_observation']['relative_humidity']
        cw_f = self.wdict['current_observation']['weather']
        cw   = cw_f.split()[1]
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
        self.screen.bitmap(260, 250, 'TEMP.BMP')
        self.screen.bitmap(260, 300, 'HUMI.BMP') 
        self.screen.text(300,240, rtemp)
        self.screen.text(300,290, rhumi)
    
    
    def twitter_DM(self):
        DM = api.direct_messages(count=1,full_text=True) 
        msg = DM[0].text
        wrap = textwrap.wrap(msg,26)
        self.screen.bitmap(420, 250, 'MSG.BMP')
        self.screen.set_en_font_size(FONT_SIZE_32)
        self.screen.text(500,250, wrap[0])
        if len(wrap) > 1:
            self.screen.text(500,290, wrap[1])

        '''
        TheDay = datetime.date(2018,06,22)
        Today  = datetime.date.today()
        cntdown = (TheDay - Today).days
        self.screen.bitmap(420, 250, 'MSG.BMP')
        self.screen.set_en_font_size(FONT_SIZE_32)
        self.screen.text(500,250, 'There are               days')
        self.screen.text(500,290, 'until going home!')
        self.screen.set_en_font_size(FONT_SIZE_64)
        self.screen.text(650,220, str(cntdown))
        '''
    
    def book_movie(self):
        self.screen.bitmap(250, 350, 'FILM.BMP')
        self.screen.bitmap(250, 450, 'BOOK.BMP')

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
