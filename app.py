from flask import Flask,render_template,request,jsonify,redirect,url_for

from pymongo import MongoClient
import hashlib
import datetime
import jwt
from datetime import datetime

client = MongoClient('localhost', 27017)
app = Flask(__name__)
db = client.sparataWeb1
secret_key='secret_key'


## 첫 페이지 입장 했을때 입니다.
## 제대로 된 토큰이 있으면 main 페이지로 없으면 login 페이지로 보냅니다.
@app.route('/')
def home():
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_info = db.user.find_one({"nickName": payload['nickName']},{'_id':False})
        if user_info == {}:
            return render_template("login.html")
        else :
            return render_template('main.html', nickname=user_info)
    except Exception as e:
        print(e)
        return render_template("login.html")



# / 로그인 get 페이지 입니다.
@app.route('/user/login', methods=['GET'])
def login():
    ##로그인페이지로 들어오면 로그인이 이미 되 있으면 메인화면으로 넘어갑니다.

    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_info = db.user.find_one({"nickName": payload['nickName']}, {'_id': False})
        if user_info == {}:
            return render_template("login.html")
        else:
            return render_template('main.html', nickname=user_info['nickName'],msg="이미 로그인 되어 있습니다.")
    except Exception as e:
        print(e)
        return render_template("login.html")


    return render_template("login.html")

# / 로그인 post 페이지 입니다. 닉네임과 비밀번호를 처리합니다.
@app.route('/user/login', methods=['POST'])
def postLogin():
    nickName = request.form['nickName']
    password = request.form['password']

    # 비밀번호를 암호화 합니다.
    hashPassword = hashlib.sha256(password.encode('utf-8')).hexdigest();

    # 닉네임을 갖고있는 유저가 있는지 검색 합니다. 유저가 없으면 에러 메세지를 반환합니다.
    isUserExist = db.user.find_one({'nickName':nickName},{'_id':False})
    if isUserExist is None:
        return jsonify({'ok':False,'err':'1'})
    else:
        # 비밀번호와 닉네임을 비교하고 결과를 반환합니다. 비밀번호가 다르면 에러 메세지를 반환합니다.
        isPasswordCorrect = isUserExist['password']==hashPassword
        if isPasswordCorrect is None:
            return jsonify({'ok':False,'err':'2'})


    # 닉네임과 비밀번호가 확인되면 메인 페이지를 jwt 토큰과 유저 정보를 반환 합니다.
    # 토큰 만료일은 하루 입니다.(60*24*60=86400)
    payload = {
        'nickName': nickName,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=86400)
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return jsonify({'token':token,'user':isUserExist,'ok':True})

##대성님 파트 회원가입 입니다.
@app.route("/user/join")
def joinForm():
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_info = db.user.find_one({"nickName": payload['nickName']}, {'_id': False})
        if user_info == {}:
            return render_template("join.html")
        else:
            return render_template('main.html', nickname=user_info,msg="이미 가입되어 있으십니다.")
    except Exception as e:
        print(e)
        return render_template("join.html",err="3")



    return render_template("join.html")


@app.route("/user/join", methods=['POST'])
def createAccount():
    data = request.form
    doc = {'nickName': data['nickName'],
           'password': hashlib.sha256(data['password'].encode('utf-8')).hexdigest(),
           }
    db.user.insert_one(doc)
    return jsonify({"result":"success"})

@app.route("/user/dupCheck", methods=['GET'])
def dupCheck():
    data = request.args.get('nickName')
    user = db.user.find_one({'nickName': data})
    result = True
    if user is not None :
        result = False
    return jsonify({"result": result})


##대성님 추가파트
@app.route('/main', methods=['GET'])
def main():
    return render_template("main.html")

@app.route('/main/list', methods=['GET'])
def content_list():
    contents = list(db.board.find({}, {'_id': False}))
    return jsonify({'result': contents})


@app.route('/main', methods=['POST'])
def content():
    now = datetime.now()
    date_time = now.strftime("%Y년 %m월 %d일 %H시 %M분")

    data = request.form
    doc = {'title': data['title'],
           'content': data['content'],
           'reference': data['content'],
           'createdAt': date_time,
           }
    db.board.insert_one(doc)
    return jsonify({"message": "글을 작성하였습니다." })

@app.route('/detail/<keyword>')
def detail(keyword):
    return render_template("detail.html", word=keyword)


##상필님 작업
@app.route("/user/mypage", methods=['GET'])
def show_column():
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user = db.user.find_one({'nickName': payload['nickName']})
        if user is not None :
            return render_template("mypage.html")
        else :
            return render_template("login")

    except Exception as e:
        return render_template("login.html")




if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)






