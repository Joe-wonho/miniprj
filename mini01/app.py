from pymongo import MongoClient
from bson.objectid import ObjectId
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

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
    # mongoDB의 id값은 자료형이 특이해서(ObjectId) rendertamplats 안에 넣으면 오류가 나고 다루기도 어렵습니당
    movie_list = list(db.movie_info.find({'genre': genre}, {'_id': False}))
    return jsonify({'movieList': movie_list})


@app.route('/detail/<title>')
def detail(title):
    # 수정시작-------------------------------
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"username": payload["id"]})
    print(user_info)
    # 수정끝---------------------------------
    title_info = db.movie_info.find_one({"title": title}, {"_id": False})
    print(title_info)
    return render_template("detail.html", list=title_info, user_info=user_info)

@app.route('/detail', methods=['GET'])
def view_posting():
    title = request.args.get('title')
    posting_info_list = list(db.posting.find({'title': title}, {'_id': False}))
    print(posting_info_list)
    return jsonify({'posting_list': posting_info_list})

@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"username": payload["id"]})
    today = datetime.now()
    current_time = today.strftime('%Y-%m-%d-%H-%M-%S')
    contents_receive = request.form['contents_give']
    title_receive = request.form['title_give']
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
    # token_receive = request.cookies.get('mytoken')
    # payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"username": username}, {"_id": False})
    print(user_info)
    return render_template("profile.html", user_info=user_info)

@app.route('/get_post', methods=['GET'])
def get_post():
    title = request.args.get("title")
    print(title)
    my_post_list = list(db.posting.find({'title': title}, {'_id': False}))
    print(my_post_list)
    return jsonify({'my_post_list': my_post_list})



@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    username = payload["id"]
    about_receive = request.form["about_give"]

    new_doc = {
        "profile_info": about_receive,
    }
    if 'file_give' in request.files:
        file = request.files["file_give"]
    filename = secure_filename(file.filename)
    extension = filename.split(".")[-1]
    file_path = f"profile_pics/{username}.{extension}"
    file.save("./static/" + file_path)
    new_doc["profile_pic"] = filename
    new_doc["profile_pic_real"] = file_path
    db.users.update_one({'username': payload['id']}, {'$set': new_doc})
    return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
