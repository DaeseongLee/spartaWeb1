from flask import Flask, render_template, request, jsonify, make_response

from pymongo import MongoClient
import hashlib
import datetime
import jwt

client = MongoClient('localhost', 27017)
app = Flask(__name__)
db = client.sparataWeb1
secret_key = 'secret_key'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}



# 틀린 비밀번호 횟수를 저장하는 쿠키를 생성 합니다.
def wrongAuthNum(num) :
    # 비밀번호틀린 횟수 저장하는 쿠키 생성
    res = make_response("settingCookie")
    res.set_cookie("loginChance", num, max_age=None)

##틀린 비밀번호 횟수를 저장하는 쿠키를 생성하는 함수를 관리합니다.
# 3회 이상 틀릴시 1분 유지되는 토큰을 생성해서 쿠키에 추가 하고
# 틀린 비밀번호 횟수는 초기화 합니다.
def handleWrongAuth(num):
    if num==3:
        payload = {
            'id': 'lockAcount',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=86400)
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        wrongAuthNum(token)
        wrongAuthNum(0)

    else :
         wrongAuthNum(num)


##토큰을 확인하고 로그인을 할 수 있게 해주는 기능입니다.
##토큰기간이 만료되는등 에러가 발생하면 토큰이 담긴 쿠키를 삭제 합니다.
##로그인을 할 수 있으면 true를 반환하고, 없으면 false를 반환 합니다.
def checkAuth():
    try:
        token = request.cookies.get('loginChance')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return False
    except Exception as e:
        res = make_response("removeCookie")
        res.set_cookie('loginChance', '', max_age=0)
        return True



# 토큰을 확인해서 유저정보를 확인 하는 인증 함수 메세지 파라미터는 사용자에게 보낼 메세지 입니다.
def auth(msg):
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user = db.user.find_one({"nickName": payload['nickName']}, {'_id': False})
        print(user)
        if user == {}:
            return render_template("login.html")
        else:
            return render_template('main.html', nser=user,msg=msg)
    except Exception as e:
        print(e)
        return render_template("login.html")


## 첫 페이지 입장 했을때 입니다.
## 제대로 된 토큰이 있으면 main 페이지로 없으면 login 페이지로 보냅니다.
@app.route('/')
def home():
    return auth("")


# / 로그인 페이지 get 받았을때 실행 됩니다.
@app.route('/user/login', methods=['GET'])
def login():
    ##로그인페이지로 들어오면 로그인이 이미 되 있으면 메인화면으로 넘어갑니다.
    # 로그인 페이지로 들어올때 로그인이 되어 있으면 이미 로그인이 되어있다는 메세지와 함께 메인화면으로 보내집니다.
    return auth("이미 로그인 되어 있습니다.")




# / 로그인 post 페이지 입니다. 닉네임과 비밀번호를 처리합니다.
@app.route('/user/login', methods=['POST'])
def postLogin():
    nickName = request.form['nickName']
    password = request.form['password']

    # 비밀번호를 암호화 합니다.
    hashPassword = hashlib.sha256(password.encode('utf-8')).hexdigest();

    # 닉네임을 갖고있는 유저가 있는지 검색 합니다. 유저가 없으면 에러 메세지를 반환합니다.
    isUserExist = db.user.find_one({'nickName': nickName}, {'_id': False})
    if isUserExist is None:
        return jsonify({'ok': False, 'err': '1'})
    elif isUserExist is not None:
        # 비밀번호와 닉네임을 비교하고 결과를 반환합니다. 비밀번호가 다르면 에러 메세지를 반환합니다.
        isPasswordCorrect = isUserExist['password'] == hashPassword
        if isPasswordCorrect == False:
            # 비밀번호가 틀릴때마다 횟수는 누적됩니다.
            handleWrongAuth(num=+1)
            if checkAuth()==False:
                return jsonify({'ok': False, 'err': '2'})

    # 닉네임과 비밀번호가 확인되면 메인 페이지를 jwt 토큰과 유저 정보를 반환 합니다.
    # 토큰 만료일은 하루 입니다.(60*24*60=86400)
    payload = {
        'nickName': nickName,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=86400)
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return jsonify({'token': token, 'user': isUserExist, 'ok': True})

##대성님 파트 회원가입 입니다.
@app.route("/user/join")
def joinForm():
    # //랜더링 되는 페이지가 달라서 코드를 다시 다 넣었습니다.
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_info = db.user.find_one({"nickName": payload['nickName']}, {'_id': False})
        if user_info == {}:
            return render_template("join.html")
        else:
            return render_template('main.html', user=user_info, msg="이미 가입되어 있으십니다.")
    except Exception as e:
        print(e)
        return render_template("join.html")



##회원가입 버튼을 눌렀을때 작동합니다.
@app.route("/user/join", methods=['POST'])
def createAccount():
    data = request.form
    doc = {'nickName': data['nickName'],
           'password': hashlib.sha256(data['password'].encode('utf-8')).hexdigest(),
           }
    db.user.insert_one(doc)
    return jsonify({"result": "success"})


@app.route("/user/dupCheck", methods=['GET'])
def dupCheck():
    data = request.args.get('nickName')
    user = db.user.find_one({'nickName': data})
    result = True
    if user is not None:
        result = False
    return jsonify({"result": result})


##대성님 추가파트 메인화면 get 요청을 받을시 작동합니다.
@app.route('/main', methods=['GET'])
def main():
    return auth("")


@app.route('/main/list', methods=['GET'])
def content_list():
    contents = list(db.board.find({}, {'_id': False}))
    return jsonify({'result': contents})


@app.route('/main', methods=['POST'])
def content():
    data = request.form
    doc = {'title': data['title'],
           'content': data['content'],
           'reference': data['content'],
           }
    db.board.insert_one(doc)
    return jsonify({"message": "글을 작성하였습니다."})


########디페일 페이지 디페일 페이지 마지막###########
@app.route("/detail", methods=['GET'])
def show_column():
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user = db.user.find_one({'nickName': payload['nickName']})
        if user is not None:
            return render_template("deatil.html", user=user)
        else:
            return render_template("login")

    except Exception as e:
        return render_template("login.html")


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)