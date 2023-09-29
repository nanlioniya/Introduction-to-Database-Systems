import json
import re
import psycopg2
import requests

def setup():
    conn = psycopg2.connect(
        host="hsinchuparking.cvsceubgnyae.us-east-1.rds.amazonaws.com",
        port="5432",
        dbname="postgres",
        user="HsinchuParking",
        password="UAYRKdtYFqQCde9S"
    )

    request_url = "https://hispark.hccg.gov.tw/OpenData/GetParkInfo"
    resp = requests.get(request_url)
    resp_text = resp.text
    file_name = 'GetParkInfo.json'
    f = open(file_name, 'w', newline='')
    f.write(resp_text)
    f.close()

    with open('GetParkInfo.json') as f:
        data = json.load(f)

    cur = conn.cursor()

    for i in range(len(data)):
        if "24H" in data[i]["BUSINESSHOURS"]:
            data[i]["BUSINESSHOURS_start"] = 0
            data[i]["BUSINESSHOURS_end"] = 24
        else:
            pattern = re.compile(r'[0-9]*:')
            sentence = data[i]["BUSINESSHOURS"]
            mylist = re.findall(pattern, sentence)
            data[i]["BUSINESSHOURS_start"] = int(mylist[0][:-1])
            data[i]["BUSINESSHOURS_end"] = int(mylist[1][:-1])

    cur.execute(f'''
        DELETE FROM parking_info;
        DELETE FROM parking_location;
    ''')
    tmp1 = 'INSERT INTO parking_location VALUES'
    tmp2 = 'INSERT INTO parking_info VALUES'
    for i in data:
        tmp1 += f" ('{i['PARKNO']}', '{i['PARKINGNAME']}', '{i['ADDRESS']}', '{i['X_COORDINATE']}', '{i['Y_COORDINATE']}'),"
        tmp2 += f" ('{i['PARKNO']}', '{i['BUSINESSHOURS_start']}', '{i['BUSINESSHOURS_end']}', '{i['WEEKDAYS']}', '{i['HOLIDAY']}', '{i['FREESPACE']}', '{i['TOTALSPACE']}', '{i['FREESPACEMOT']}', '{i['TOTALSPACEMOT']}'),"
    cur.execute(tmp1[:-1])
    cur.execute(tmp2[:-1])
    conn.commit()
    print("Setup Finish")
    conn.close()

def update():
    conn = psycopg2.connect(
        host="hsinchuparking.cvsceubgnyae.us-east-1.rds.amazonaws.com",
        port="5432",
        dbname="postgres",
        user="HsinchuParking",
        password="UAYRKdtYFqQCde9S"
    )

    request_url = "https://hispark.hccg.gov.tw/OpenData/GetParkInfo"
    resp = requests.get(request_url)
    resp_text = resp.text
    file_name = 'GetParkInfo.json'
    f = open(file_name, 'w', newline='')
    f.write(resp_text)
    f.close()

    with open('GetParkInfo.json') as f:
        data = json.load(f)

    cur = conn.cursor()

    for i in range(len(data)):
        if "24H" in data[i]["BUSINESSHOURS"]:
            data[i]["BUSINESSHOURS_start"] = 0
            data[i]["BUSINESSHOURS_end"] = 24
        else:
            pattern = re.compile(r'[0-9]*:')
            sentence = data[i]["BUSINESSHOURS"]
            mylist = re.findall(pattern, sentence)
            data[i]["BUSINESSHOURS_start"] = int(mylist[0][:-1])
            data[i]["BUSINESSHOURS_end"] = int(mylist[1][:-1])

    cur.execute(f'''
        DELETE FROM parking_info;
    ''')
    tmp2 = 'INSERT INTO parking_info VALUES'
    for i in data:
        tmp2 += f" ('{i['PARKNO']}', '{i['BUSINESSHOURS_start']}', '{i['BUSINESSHOURS_end']}', '{i['WEEKDAYS']}', '{i['HOLIDAY']}', '{i['FREESPACE']}', '{i['TOTALSPACE']}', '{i['FREESPACEMOT']}', '{i['TOTALSPACEMOT']}'),"
    cur.execute(tmp2[:-1])
    conn.commit()
    print("Update Finish")
    conn.close()

def query(x, y, Type, hr, day):
    conn = psycopg2.connect(
        host="hsinchuparking.cvsceubgnyae.us-east-1.rds.amazonaws.com",
        port="5432",
        dbname="postgres",
        user="HsinchuParking",
        password="UAYRKdtYFqQCde9S"
    )
    cur = conn.cursor()
    cur.execute(f"""
        WITH tmp1(PARKNO, {day}, FREESPACE{Type}) as
            (SELECT PARKNO, {day}, FREESPACE{Type}
            FROM parking_info
            WHERE FREESPACE{Type} > 0 and BUSINESSHOURS_start <= {hr} and {hr} <= BUSINESSHOURS_end)
        SELECT PARKINGNAME, ADDRESS, {day}, FREESPACE{Type}, X, Y
        FROM tmp1 natural join parking_location
        ORDER BY (x - {x})*(x - {x}) + (y - {y})*(y - {y})
        LIMIT 10
    """)
    conn.commit()
    ret = cur.fetchall()
    conn.close()
    return ret