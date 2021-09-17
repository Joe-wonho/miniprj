from pymongo import MongoClient
from bson.objectid import ObjectId
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import json
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'
client = MongoClient('localhost', 27017)
# client = MongoClient('mongodb://test:test@3.34.177.185', 27017)
db = client.dbsparta

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})

        print(user_info)

        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # 회원가입
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    nickname_receive = request.form['nickname_give']
    age_receive = request.form['age_give']
    region_receive = request.form['region_give']
    gender_receive = request.form['gender_give']
    doc = {
        "username": username_receive,
        "password": password_hash,
        "nickname": nickname_receive,
        "age": age_receive,
        "region": region_receive,
        "gender": gender_receive,
        "profile_pic": "",
        "profile_pic_real": "profile_pics/profile_placeholder.png",
        "about":"소개를 작성해보세요!"
    }
    db.users.insert_one(doc)
    print(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # ID 중복확인
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/genre', methods=['GET'])
def view_movie():
    genre = request.args.get('givegenre')
    # count를 기준으로 내림차순 하고 위에서 부터 4줄 가져오기!
    top_4_movie = list(db.movie_info.find({},{'_id': False}).sort("count",-1))
    movie_list = list(db.movie_info.find({'genre': genre}, {'_id': False}))
    return jsonify({'movieList': movie_list,'topList':top_4_movie})


@app.route('/detail/<title>')
def detail(title):

    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"username": payload["id"]})

    title_info = db.movie_info.find_one({"title": title}, {"_id": False})

    return render_template("detail.html", list=title_info, user_info=user_info)


@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"username": payload["id"]})

    today = datetime.now()
    current_time = today.strftime('%Y-%m-%d-%H-%M-%S')
    contents_receive = request.form['contents_give']
    title_receive = request.form['title_give']

    before_count = db.movie_info.find_one({'title':title_receive})['count']
    after_count = before_count+1
    db.movie_info.update_one({'title':title_receive},{'$set':{'count':after_count}})

    db.users.find_one({"username": payload["id"]})
    doc = {
        "title": title_receive,
        "username": user_info["username"],
        "current": current_time,
        "contents": contents_receive,
        "is_open": 'True'
    }
    db.posting.insert_one(doc)

    return jsonify({"result": "success", 'msg': '저장 완료!'})


@app.route('/profile/<username>')
def get_profile(username):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내껀 True, 다른 사람  False
        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template("profile.html", username=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@ app.route('/detail', methods=['GET'])
def view_posting():
    title = request.args.get('title')
    posting_info_list = list(db.posting.find({'title': title}, {'_id': False}))
    return jsonify({'posting_list': posting_info_list})


@app.route("/get_post", methods=['GET'])
def get_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        user_name = request.args.get("user_name")

        if user_name == "":
            my_post_list = list(db.posting.find({}))
        else:
            my_post_list = list(db.posting.find({"username": user_name}))
            print(my_post_list)

        for my_posts in my_post_list:
            my_posts["_id"] = str(my_posts["_id"])

        return jsonify({'my_post_list': my_post_list})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# 포스팅 카드 삭제
@app.route('/delete/post', methods=['POST'])
def delete_post():
    post_id_receive = request.form['post_id_give']
    db.posting.delete_one({'_id': ObjectId(post_id_receive)})
    return jsonify({"result": "success", 'msg': '삭제 완료!'})

#프로필 업데이트
@app.route('/update_profile', methods=['POST'])
def proflie_update():
    username = request.form['name']
    nickname_receive = request.form['nickname_give']
    about_receive = request.form['about_give']
    print(username, nickname_receive, about_receive)
    db.users.update_one({'username': username}, {'$set': {'nickname': nickname_receive}})
    db.users.update_one({'username': username},{'$set': {'about': about_receive}})
    return jsonify({"result": "success", 'msg': '수정 완료!'})
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

