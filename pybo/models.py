import base64 #20240907
from pybo import db

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)    #primary key
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    uploaded_img_file = db.Column(db.String(255), nullable=True)  #20231230
    create_date = db.Column(db.DateTime(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('question_set'))

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)    #primary key
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'))   #FK: id from question table
    question = db.relationship('Question', backref=db.backref('answer_set'))    #linking /w Qstn
    #question = db.relationship('Question', backref=db.backref('answer_set', cascade='all, delete-oprhan'))
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('answer_set'))

#20230715
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)  # null  => 아무것도 없는, 빈   -able : ~ 할 수 있는  ==> nullable
    password = db.Column(db.String(200), nullable=False)        #db.String  ==> String: 문자열 , Integer:숫자
    code = db.Column(db.Text, nullable=True)  # 20240921
    email = db.Column(db.String(120), unique=True, nullable=False)
    photo = db.Column(db.String(200), nullable=True)  # 사진 파일 경로

#20240825
class Codefile(db.Model):
    fileid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(150), unique=True, nullable=False)  # null  => 아무것도 없는, 빈   -able : ~ 할 수 있는  ==> nullable
    code = db.Column(db.Text, nullable=True)  # 코드 데이터를 저장할 필드 추가 20240907
    saved_date = db.Column(db.DateTime(), nullable=False)
    def set_code(self, code_str): #20240907
        # 코드를 Base64로 인코딩하여 저장
        encoded_code = base64.b64encode(code_str.encode('utf-8')).decode('utf-8')
        self.code = encoded_code

    def get_code(self): #20240907
        # 저장된 Base64 인코딩 코드를 디코딩하여 원본 코드로 복원
        if self.code:
            return base64.b64decode(self.code.encode('utf-8')).decode('utf-8')
        return None

#20240921
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 투표한 사용자
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 투표 대상 사용자
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' 또는 'downvote'
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())