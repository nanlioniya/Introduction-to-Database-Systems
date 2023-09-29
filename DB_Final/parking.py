import discord
import googlemaps
import CRUD
import time
from discord.ext import tasks
import numpy as np

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
google_maps = googlemaps.Client(key='AIzaSyDdGpmtx4cGNI7hxIre_y9E7lt5wY4cJks')

txt0='（輸入訊息請以"at"開頭，連鎖店地標需包含地區或店名等資訊。Ex: at好市多竹北）'
txt1='欲查詢車位，請輸入所在地址或附近地標'+txt0
txt2='查詢失敗\n請重新輸入'+txt0
txt3='查詢成功'
txt4='已設定「汽車」'
txt5='已設定「機車」'
p=['停車','車位','park','PARK','Park','空位','空格','開車','騎車','哪裡','where','Where','help','Help','?', '？']
c=['汽車','car','Car','CAR','開車']
s=['騎車','機車','摩托車','scooter','auto bike','autobike','Scooter','SCOOTER','Auto Bike','AUTO BIKE','AUTOBIKE','motorcycle','Motorcycle','MOTORCYCLE']


#use these functions to get geometry coordinate or adress
#the result will be -1 or empty string if some errors occur
def get_lat(adr):
    result=google_maps.geocode(adr)
    if len(result)>0:
        return result[0]['geometry']['location']['lat']
    else:
        return -1.0
    
def get_lng(adr):
    result=google_maps.geocode(adr)
    if len(result)>0:
        return result[0]['geometry']['location']['lng']
    else:
        return -1.0
    
def get_adr(lat,lng):
    tmp=str(lat)+', '+str(lng)
    result=google_maps.geocode(tmp)
    if len(result)>0:
        return result[0]['formatted_address']
    else:
        return ''

# get top five recommended parking lots
def get_recommended(destinations, info):
    
    origin = (lat, lng) # location of origin
    
    # get travel info(duration, distance...) from google maps api
    res = google_maps.distance_matrix(origin, destinations, mode='driving') 
 
    # pick up the duration of parking lots candidates
    durations = []
    for row in res['rows']:
        for ele in row['elements']:
            durations.append(ele['duration']['value'])

    # sort the parking lots by duration time
    recommend = list(zip(destinations, durations)) # pair up parking lots and their durations
    recommend = sorted(recommend, key=lambda x: x[1]) 

    # pick up the top5 least duration parking lots locations
    if(len(recommend)>5): recommend_addr = [i[0] for i in recommend[:5]]
    else: recommend_addr = [i[0] for i in recommend[:len(recommend)]]

    # turn the parking lots locations into parking lots' names
    recommend_sopts = []
    cnt=0
    for addr in recommend_addr:
        for parking in info:
            if parking[0]==addr:
                cnt+=1
                recommend_sopts.append(parking)
        if cnt>=5: break

    return recommend_sopts

def convert(a):
    b = [str(i) for i in a]
    return b

@client.event
async def on_ready():
    print('目前登入身份：', client.user)
    CRUD.setup()
    Update.start()
    global iscar
    iscar = False
    global ismot
    ismot = False
    global lat
    lat = -1
    global lng
    lng = -1


@tasks.loop(seconds = 300) # repeat after every 5 minutes
async def Update():
    CRUD.update()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    for str in p:
        if message.content.find(str)!=-1:
            await message.channel.send(txt1)
            break

    global lat
    global lng

    if message.content.startswith('at'):
        adr=message.content[2:]
        lat=get_lat(adr)
        lng=get_lng(adr)
        if lat<0 or lng<0:
            await message.channel.send(txt2)
        else:
            await message.channel.send(txt3)
    
    global iscar
    global ismot
    for str in c:
        if message.content.find(str)!=-1:
            iscar=True
            ismot=False
            await message.channel.send(txt4)
            break
    
    for str in s:
        if message.content.find(str)!=-1:
            iscar=False
            ismot=True
            await message.channel.send(txt5)
            break
    
    if (lat>0 and lng>0) and not ismot and not iscar:
        await message.channel.send('請輸入「汽車」或「機車」')

    if message.content.find('唱')!=-1:
        await message.channel.send('轟隆隆隆隆衝衝衝衝～')

    if (iscar or ismot) and (lat>0 and lng>0):
        Type = ""
        day = ""
        if iscar:
            Type = "CAR"
        else:
            Type = "MOT"
        if time.localtime().tm_wday >= 5:
            day = "HOLIDAY"
        else:
            day = "WEEKDAYS"
        ret = CRUD.query(lat, lng, Type, time.localtime().tm_hour, day) # ret: query 結果
        

        #getting parking recommendations
        tmp_ret = np.array(ret) # get column values from ret(table)
        x = tmp_ret[:, 4].tolist() # lat of parking lots
        y = tmp_ret[:, 5].tolist() # lng of parking lots
        cost = tmp_ret[:, 2].tolist()
        tmp_remain = tmp_ret[:, 3].tolist()
        remain = convert(tmp_remain)
        pos = list(zip(x,y)) # list of locations(lat, lng)
        names = tmp_ret[:, 0].tolist()
        info = list(zip(pos, names, cost, remain)) # pair up locations and parking lots' names
        recommendations = get_recommended(pos, info) # return top5 parling lots' names

        # show names to user
        await message.channel.send('已為您找出推薦的停車場(按距離遠近)：\n')
        for parking in recommendations:
            await message.channel.send('【 '+ parking[1] + ' 】\n'+'停車費： '+parking[2]+'\n剩餘車位：'+ parking[3]+'\n')
        # end of getting recommenfations


        print(ret)
        iscar = False
        ismot = False
        lat = -1
        lng = -1


client.run('MTA1MTExMjU0NjA2MjU3NzY3NA.GWLQkK.hCWzy2Xu__iwcuvWtWgtyagg1GDu4y1Ybjz0z4')