import requests
import traceback
import pymysql
import json
from bs4 import BeautifulSoup
import json

# ------------------하이퍼 파라미터---------------------------
key = 'AIzaSyDGUj-frLFa_pp5Jer5IKWUfRv1tQ-mrJI'  # 구글 API KEY

# --------------------지오 코딩------------------------------
def get_r_info(keyword):
    global key
    try:
        headers = {'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'}
        base_url = "https://maps.googleapis.com/maps/api/place/details/json?"
        url = base_url + 'place_id=' + keyword + '&key=' + key
        print(url)
        resp = requests.get(url, headers=headers)
        return resp.json()


    except Exception:
        traceback.print_exc()
        return resp.json()




#장소를 추가해주는 메소드
def insert_place(rest_google_id):

    data = get_r_info(rest_google_id)
    if data.get('status') == 'INVALID_REQUEST':
        return
    result = data.get('result')
    print(result)

    rest_name = result.get('name')
    rest_address = result.get('formatted_address')
    rest_lat = str(result.get('geometry').get('location').get('lat'))
    rest_lng = str(result.get('geometry').get('location').get('lng'))
    print(type(rest_lat))
    rest_text = ''
    rest_time = ''
    try:
        rest_time = result.get('opening_hours').get('weekday_text')[0]
    except:
        pass
    rest_phone = result.get('formatted_phone_number')
    conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area', charset='utf8')
    curs = conn.cursor()
    try:
        sql = "INSERT INTO restaurant(restgoogleid,restName,restAddress,restLat,restLng,restText,restTime,restPhone) VALUES('"+rest_google_id+"','"+rest_name+"','"+rest_address+"',"+rest_lat+","+rest_lng+",'"+rest_text+"','"+rest_time+"','"+rest_phone+"')"
        print(sql)

        curs.execute(sql)
        conn.commit()
    except:
        traceback.print_exc()

    curs.close()
    conn.close()
    return rest_name, rest_address, rest_text, rest_time, rest_phone

