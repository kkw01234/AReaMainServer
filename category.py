# -*- coding: utf-8 -*-
from flask import Flask, jsonify, send_from_directory
from datetime import datetime
import pymysql
from traceback import print_exc
from werkzeug.utils import secure_filename
import json

# ------------파일 저장하는 주소 --------------
UPLOAD_FOLDER = 'D:/upload_file/'
MY_IMAGE = UPLOAD_FOLDER + 'my_image/'
REVIEW_IMAGE = UPLOAD_FOLDER + 'review_image/'
WORD_CLOUD = UPLOAD_FOLDER + 'word_cloud/'
UPLOAD_PATH = UPLOAD_FOLDER + 'path/'

# ------------------가능한 확장자----------------------
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp'])


# --------------------파일형식------------
def allowed_file(filename):
    a = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    return a


# ---------------카테고리 분류
def category_upload(cate):
    print(cate)
    if cate == 'upload_my_image':
        return UploadFile().upload_my_image
    elif cate == 'upload_review_image':
        return UploadFile().upload_review_image
    elif cate == 'upload_path':
        return UploadFile().upload_path
    else:
        return None


def category_download(cate):
    if cate == 'download_my_image':
        return DownloadFile().download_my_image
    elif cate == 'download_recommend_image':
        return DownloadFile().download_recommend_image
    elif cate == 'load_wordcloud':
        return DownloadFile().load_wordcloud
    elif cate == 'download_review_image':
        return DownloadFile().download_review_image
    elif cate == 'path_image':
        return DownloadFile().path_image
    else:
        return None


class UploadFile:

    def upload_my_image(self, u_id, request):
        try:
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(MY_IMAGE + secure_filename(file.filename))
            else:
                return jsonify({"result": "Not allow file"})
            conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area',
                                   charset='utf8')
            curs = conn.cursor()
            sql = "UPDATE user SET userImage = '" + secure_filename(file.filename) + "' WHERE userID= '" + u_id + "'"
            curs.execute(sql)
            conn.commit()
            return jsonify({"result": "success"})
        except:
            print_exc()
            return jsonify({"result": "fail"})

    def upload_review_image(self, u_id, request):
        review_image = request.files['file']
        if review_image and allowed_file(review_image.filename):
            address = datetime.today().strftime('%Y%m%d%H%M%S') + '_' + u_id + '_' + secure_filename(
                review_image.filename)
            review_image.save(REVIEW_IMAGE + address)
        else:
            return jsonify({"result": "Not allow file"})
        try:
            rest_google_id = request.form['google_id']
            review_content = request.form['review_content']
            review_rate = request.form['review_rate']
            date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area',
                                   charset='utf8')
            curs = conn.cursor()
            sql = "INSERT INTO review(reviewUserId, reviewgoogleid, reviewdate, reviewContent, reviewRate, reviewImage) VALUES('" + u_id + "', '" + rest_google_id + "', '" + date + "', '" + review_content + "', " + review_rate + ", '" + address + "')"
            curs.execute(sql)
            conn.commit()
            sql = "UPDATE restaurant SET restImage='" + address + "' WHERE restgoogleid='" + rest_google_id + "'"
            curs.execute(sql)
            conn.commit()
            sql = "SELECT reviewId FROM review WHERE reviewUserId='" + u_id + "' AND reviewgoogleid='" + rest_google_id + "' AND reviewdate='" + date + "'"
            curs.execute(sql)
            rows = curs.fetchall()
            print(rows)
            if len(rows) > 0:
                row = rows[0]
                return jsonify({"result": "success",
                                "review_id": row[0]})
            else:
                return jsonify({"result": "not found in DB"})

        except:
            import os
            os.remove(REVIEW_IMAGE, secure_filename(review_image.filename))
            jsonify({"result": "SQL fail"})


    def upload_path(self, u_id, request):
        title = request.form['title']
        path_image = request.files['file']
        path_places = request.form['path_places']
        path_content = request.form['content']

        if path_image and allowed_file(path_image.filename):
            address = datetime.today().strftime('%Y%m%d%H%M%S') + '_' + u_id + '_' + secure_filename(
                path_image.filename)
            path_image.save(UPLOAD_PATH + address)
        conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area', charset='utf8')
        curs = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        sql = "INSERT INTO recommendationpath(title, content, writerName, image, date) VALUES('" + title + "', '" + path_content + "', '" + u_id + "', '" + address + "', '" + today + "')"
        curs.execute(sql)
        conn.commit()
        sql = "SELECT id FROM recommendationpath WHERE title='"+title +"' and writerName='"+u_id+"' and date='"+today+"'"
        curs.execute(sql)
        rows = curs.fetchall()
        if len(rows) > 0:
            path_id = rows[0][0]
        places = json.loads(path_places)
        print(places)
        for i, place in zip(range(0, len(places)), places):
            print(place)
            sql = "INSERT INTO recommendationroute VALUES('" + str(path_id) + "', '" + place['id'] + "',  '" + place['name'] + "', '" + str(place['latitude']) + "', '" +str(place['longitude']) + "', '"+str(i+1)+"')"
            print(sql)
            curs.execute(sql)
            conn.commit()

        return jsonify({"result": "success"})


class DownloadFile:

    def download_my_image(self, u_id, google_id=None):
        conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area', charset='utf8')
        curs = conn.cursor()
        sql = "SELECT userImage FROM user WHERE userID='" + u_id + "'"
        curs.execute(sql)
        rows = curs.fetchall()
        if len(rows) >= 1:
            row = rows[0]
            filename = row[0]
        return send_from_directory(directory=MY_IMAGE, filename=filename)

    def download_review_image(self, filename, google_id=None):
        return send_from_directory(directory=REVIEW_IMAGE, filename=filename)

    def load_wordcloud(self, u_id, google_id):
        filename = google_id + ".png"
        print(filename)
        return send_from_directory(directory=WORD_CLOUD, filename=filename)

    def path_image(self, u_id, google_id):
        path_id = google_id
        conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area', charset='utf8')
        curs = conn.cursor()
        sql = "SELECT image FROM recommendationpath WHERE id='" + path_id + "'"
        curs.execute(sql)
        rows = curs.fetchall()
        if len(rows) >= 1:
            row = rows[0]
            filename = row[0]
        else:
            return jsonify({"result": "ERROR"})
        return send_from_directory(directory=UPLOAD_PATH, filename=filename)
