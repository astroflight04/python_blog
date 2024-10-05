from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed #20231230
from wtforms import StringField, TextAreaField, PasswordField, EmailField, FileField #20230715, 20231230
from wtforms.validators import DataRequired, Length, EqualTo, Email #20230715, 20231230

class QuestionForm(FlaskForm):
    subject = StringField('제목', validators=[DataRequired()])    #필수 값인 경우 DataRequied   (msg)
    content = TextAreaField('내용', validators=[DataRequired()])
    uploaded_img_file = FileField('이미지 파일 업로드', validators=[FileAllowed(['jpg', 'png', 'jpeg'], '이미지 파일만 업로드 가능합니다')])

class AnswerForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수입력 항목입니다.')])

#20230715
class UserCreateForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired(), Length(min=3, max=25)])   # validator = 입력값이 정해진 규칙대로 들어오는지 확인
    password1 = PasswordField('비밀번호', validators=[
        DataRequired(), EqualTo('password2', '비밀번호가 일치하지 않습니다')])
    password2 = PasswordField('비밀번호확인', validators=[DataRequired()])
    email = EmailField('이메일', validators=[DataRequired(), Email()])

class UserLoginForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('비밀번호', validators=[DataRequired()])