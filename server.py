from flask import Flask, request, jsonify, session, redirect, url_for
from datetime import timedelta, datetime
import pymysql
import smtplib
import hashlib
from email.mime.text import MIMEText
from werkzeug.utils import secure_filename
import traceback
import googleplace
import filefunction
import os


app = Flask(__name__)
app.secret_key = 'HZt,}`v{&pwv&,qvtSV8Z9NE!z,p=e?('


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)  # 세션 타임관리


@app.route('/')
def index():
    return 'hello its ARea Server'


# 로그인 요청
@app.route('/login', methods=['POST'])
def login():
    data = {}
    if 'user_id' in session:
        data['result'] = 'already login'
        return jsonify(data)
    conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area', charset='utf8')
    curs = conn.cursor()
    u_id = request.form['id']
    u_pwd = request.form['pwd']
    sql = "SELECT * FROM user WHERE userId='" + u_id + "' AND userPassword='" + u_pwd + "'"
    curs.execute(sql)
    rows = curs.fetchall()
    data['result'] = 'success' if (len(rows) >= 1) else 'fail'
    if data['result'] == 'success':
        session['user_id'] = u_id
        row = rows[0]
        data['userId'] = row[0]
        data['userName'] = row[2]
        data['userRight'] = row[4]
        data['userEmail'] = row[5]
        data['userImage'] = row[7]
        print(row[7])
    curs.close()
    conn.close()
    return jsonify(data)


# 로그아웃 요청
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    data = {'result': 'success'}
    return jsonify(data)


# 회원가입 요청
@app.route('/register_user', methods=['POST'])
def register_user():
    u_id = request.form['id']
    u_pwd = request.form['pwd']
    u_name = request.form['name']
    u_email = request.form['email']
    key = generate_email_key(u_email)
    conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area', charset='utf8')
    curs = conn.cursor()
    sql = "INSERT INTO user(userId, userPassword, userName, userEmail, certified_key) VALUES('" + u_id + "', '" + u_pwd + "', '" + u_name + "', '" + u_email + "', '" + key + "')"
    curs.execute(sql)
    try:
        send_email(u_id, u_name, u_email, key)
    except Exception:
        return jsonify({'result': 'email fail'})
    conn.commit()
    curs.close()
    conn.close()
    return jsonify({'result': 'success'})


# 아이디 중복 확인
@app.route('/check_dup_id', methods=['POST'])
def check_dup_id():
    u_id = request.form['id']
    conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area', charset='utf8')
    curs = conn.cursor()
    sql = "SELECT * FROM user WHERE userId='" + u_id + "'"
    curs.execute(sql)
    rows = curs.fetchall()
    data = {'result': 'dup' if (len(rows) >= 1) else 'avail'}
    curs.close()
    conn.close()
    return jsonify(data)


# 닉네임 중복 확인
@app.route('/check_dup_name', methods=['POST'])
def check_dup_name():
    u_name = request.form['name']
    conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area', charset='utf8')
    curs = conn.cursor()
    sql = "SELECT * FROM user WHERE userName='" + u_name + "'"
    curs.execute(sql)
    rows = curs.fetchall()
    data = {'result': 'dup' if (len(rows) >= 1) else 'avail'}
    curs.close()
    conn.close()
    return jsonify(data)


# 이메일 키 생성기
def generate_email_key(email):
    m = hashlib.sha512()
    salt = datetime.now().strftime('%m/%d/%Y, %H:%M:%S')
    m.update(('%s%s' % (salt, email)).encode('utf-8'))
    return m.hexdigest()


# 이메일 보내기
def send_email(u_id, u_name, email_to, key):
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login('ddodd34@gmail.com', 'mhpvluuaimjjsskb')
        text = '아이디 : ' + u_id + ', 닉네임 : ' + u_name + ' 계정을 생성하셨다면 아래 링크를 눌러주세요.'
        text += '\nhttp://118.220.3.71:13565/certified_email?key=' + key
        msg = MIMEText(text)
        msg['Subject'] = '[본인인증] ARea 계정 이메일 인증을 해주세요.'
        s.sendmail('ddodd34@gmail.com', email_to, msg.as_string())
        s.quit()
    except Exception:
        raise Exception


# 이메일 인증 확인하기
@app.route('/certified_email', methods=['GET'])
def certified_email():
    key = request.args.get('key')
    conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area', charset='utf8')
    curs = conn.cursor()
    sql = "SELECT * FROM user WHERE certified_key='" + key + "'"
    curs.execute(sql)
    rows = curs.fetchall()
    if len(rows) >= 1:
        result = '인증이 완료되었습니다.'
        sql = "UPDATE user SET userRight=2 WHERE certified_key='" + key + "'"
        curs.execute(sql)
        conn.commit()
    else:
        result = '잘못된 접근입니다'
    curs.close()
    conn.close()
    return result


# 후기 등록
@app.route('/write_review', methods=['POST'])
def write_review():
    u_name = request.form['name']
    rest_id = request.form['']
    review_content = request.form['']
    review_point = request.form['']
    conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area', charset='utf8')
    curs = conn.cursor()
    sql = "INSERT INTO review(reviewUserName, reviewRestId, reviewText, reviewPoint) VALUES('" + u_name + "', '" + \
          rest_id + "', '" + review_content + "', " + review_point + ")"
    try:
        curs.execute(sql)
    except:
        return jsonify({'result': 'fail'})
    curs.close()
    conn.close()
    return jsonify({'result': 'success'})

#사진 업로드
@app.route('/write_image', methods=['POST'])
def write_image():
    u_id = session['user_id']
    user_image = request.form['user_image']
    conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area', charset='utf8')
    curs = conn.cursor()
    print(u_id)
    sql = "UPDATE user SET userImage = '"+user_image+"'  WHERE userID='"+u_id+"'"
    try:
        curs.execute(sql)
        conn.commit()
    except Exception:
        return jsonify({'result': 'fail'})
    curs.close()
    conn.close()

    return jsonify({'result': 'success'})

#사진_다운로드
@app.route('/read_image', methods=['POST'])
def read_image():
    u_id = session['user_id']
    conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area', charset='utf8')
    curs = conn.cursor()
    sql = "SELECT userImage FROM user WHERE userID='"+u_id+"'"
    try:
        curs.execute(sql)
        rows = curs.fetchall()
        if len(rows) > 0:
            row = rows[0]
            return jsonify({'user_image': row[0]})
        else:
            return jsonify({"user_image": "fail"})
    except Exception:
        return jsonify({"userImage": "fail"})
        raise Exception


UPLOAD_FOLDER ='D:/'
#파일 업로드
@app.route('/upload_file', methods=['GET','POST'])
def upload_file():
    try:
        file = request.files['file']
        print(file)
        if file and filefunction.allowed_file(file.filename):

            file.save(secure_filename(file.filename))
            return jsonify({"result" : "success"})
        else:
            return jsonify({"result": "false"})
    except Exception:
        raise Exception

#장소 찾기 (구글 place_id 존재할 때)
@app.route('/find_place', methods=['POST'])
def find_place():
    rest_google_id = request.form['google_id']
    conn = pymysql.connect(host='118.220.3.71', user='root', password='rjsdnrkkw4809!!', db='area', charset='utf8')
    curs = conn.cursor()
    sql = "SELECT *  FROM restaurant WHERE restgoogleid='"+rest_google_id +"'"
    try:
        curs.execute(sql)
        rows = curs.fetchall()
        print(rows)
        print(len(rows))
        if len(rows) > 0:
            row = rows[0]
            json = {
                'result': 'true',
                'rest_name': row[2],
                'rest_address': row[3],
                'rest_text': row[6],
                'rest_time': row[7],
                'rest_phone': row[8]
            }
            curs.close()
            conn.close()
            return jsonify(json)
        else:
            rest_name, rest_address, rest_text, rest_time, rest_phone = googleplace.insert_place(rest_google_id)

            return jsonify({
                'result': 'true',
                'rest_name': rest_name,
                'rest_address': rest_address,
                'rest_text': rest_text,
                'rest_time': rest_time,
                'rest_phone': rest_phone
            })
    except:
        traceback.print_exc()
        return jsonify({"result": "fail"})





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=13565)
    #googleplace.insert_place('ChIJT1UMZ7lbezURsHyAjbAF-gE')

