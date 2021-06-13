# :pushpin: 기억보다는 기록을
>
>http://kingstar.shop/

</br>

## 1. 제작 기간 & 참여 인원
- 2021년 6월 7일 ~ 6월 9일
- 팀 프로젝트 (4명)

</br>

## 2. 사용 기술
#### `Back-end`
  - Python 3.8
  - MongoDB 3.6.3
  - Flask 2.0.1
  
#### `Front-end`
  - HTML, CSS, Javascript
  - Bootstrap

</br>

## 3. ERD 설계
![drawSQL-export-2021-06-13_14_43](https://user-images.githubusercontent.com/47413926/121796657-bb348580-cc55-11eb-8d2b-2a149beac7ee.png)


</br>

## 4. 핵심 기능
   - 글 등록
   - 특정 글에 대한 리뷰 작성하기
   - 특정 글에 대해 좋아요 하기
   - 사용자 별로 본인이 좋아한 리스트 확인하기

</br>


## 5. 핵심 트러블 슈팅
### 5.1. 로그아웃 했을 시 가끔 로그 아웃 안되는 현상
- 현상: my page, 또는 main page에서 로그 아웃 했을 시, 가끔 로그 아웃이 안되고 main page로 돌아감.

- 원인: 1. 기존 쿠키를 삭제하는 코드를 쿠키 만기일을 이전날짜로 정함.
        2. 로그 아웃을 하면 token정보를 가져오는 로직을 타면서 가끔씩 쿠기가 사라지기 전, 쿠키가 있는 것으로 생각 되어 main페이지로 이동하게 됨.
- 해결방법: 로그 아웃 했을 시, 쿠키를 삭제하고 바로 login 페이지로 랜더링하도록 수정.
        
<details>
<summary><b>기존 코드</b></summary>
<div markdown="1">
  
~~~javascript

/**
 * <main.html>
 * 
 *로그아웃
 */
 function logout() {
            document.cookie = 'token' + '=; expires=Thu, 01 Jan 1999 00:00:10 GMT;';
            window.location.href = '/user/login'
 }
/**
 * <app.py>
 *
 * 로그아웃 요청이 들어오면 login page로 랜더링되도록 하는 함수
 */
# / 
@app.route('/user/login', methods=['GET'])
def login():
    return auth("이미 로그인 되어 있습니다.")
  
  
//토큰을 확인해서 유저정보를 확인 하는 인증 함수 메세지 파라미터는 사용자에게 보낼 메세지 입니다.
def auth(msg):
    try:
        token = request.cookies.get('token')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user = db.user.find_one({"nickName": payload['nickName']}, {'_id': False, 'password': False})
        if user == {}:
            return render_template("login.html")
        else:
            return render_template('main.html',  data=json.dumps(user), msg=msg, user=user)
    except Exception as e:
        return render_template("login.html")
~~~

</div>
</details>

<details>
<summary><b>개선된 코드</b></summary>
<div markdown="1">

~~~javascript
**
 * <main.html>
 * 
 *로그아웃
 */
 function logout() {
            document.cookie = 'token' + '=; expires=Thu, 01 Jan 1999 00:00:10 GMT;';
            window.location.href = '/user/logout'
 }
/**
 * <app.py>
 *
 * 로그아웃 요청이 들어오면 login page로 랜더링되도록 하는 함수
 */
# / 
@app.route('/user/logout')
def logout():
    return render_template('login.html')
~~~

</div>
</details>
</br>

## 6. 그 외 트러블 슈팅
<details>
<summary>Object of type ObjectId is not JSON serializable.</summary>
<div markdown="1">
  
  - 원인: 상세 게시물을 조회 할 때 필요한 키값으로 mongodb에서 생성 되는 _id를 가지고와서 설정할려 고 했는데, object type은 직렬화 하지 못해 발생한 에러
  - 해결: 임시방편이지만 key 값을 글을 생성하는 날짜로 수정.
</div>
</details>

<details>
<summary>400 Bad request</summary>
<div markdown="1">
  
  - 원인:  
    - flask에서 받아들여야 하는 POST parameter가 없을 때 발생
    - 분명, formData에 필요한 parameter를 담아서 보냈는 데, 계속 오류 발생
    - 알고보니, flask에서 받아들이는 request.form['파라미터_이름']의 파라미터 이름이 form에서 전송하는 파라미터 이름과 동일 해야됨.
  - 해결: form에서 전송하려는 input name을 올바르게 수정함

  
</div>
</details>

</br>

## 6. 회고 / 느낀점
>프로젝트 개발 회고 글: https://devkingstar.tistory.com/34
