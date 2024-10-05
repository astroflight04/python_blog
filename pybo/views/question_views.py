import os   #20231230, flask app도 추가
from pybo import create_app
from flask import Blueprint, render_template, request, url_for, g, flash, jsonify  # 블루프린트는 페이지 라우팅을 위해서, render_template은 html 문서를 불러와서 웹 브라우저에 표현하기 위해서 import
from pybo.models import Question    #models(데이터 베이스)에 정의한 Question class를 가져다 쓰자
from pybo.forms import QuestionForm, AnswerForm
from pybo import db
from datetime import datetime
from werkzeug.utils import redirect, secure_filename #20231230 secure_filename 추가
from pybo.views.auth_views import login_required
import urllib.parse

bp = Blueprint('question', __name__, url_prefix='/question')    # /question이라는 경로로(웹 브라우저)

@bp.route('/list/') #라우팅 설정
def _list():
    page = request.args.get('page', type=int, default=1)  # 페이지  --> 127.0.0.1:5000/pybo/question/list/?page=1
    query = request.args.get('query')  # URL 쿼리 매개변수에서 검색어 가져오기
    if query:
        # 검색어가 있는 경우, 해당하는 질문 목록을 검색
        question_list = Question.query.filter(Question.subject.contains(query)).order_by(Question.create_date.desc())
    else:
        question_list = Question.query.order_by(Question.create_date.desc())    # 질문 목록은 desc로 정렬
    question_list = question_list.paginate(page=page, per_page=10)
    return render_template('question/question_list.html', question_list=question_list, query=query)  # question_list.html 파일을 "기초"로
                                                                                        # question_list를 불러와서 화면을 구성한다


@bp.route('/detail/<int:question_id>/') # 질문 목록의 세부내용 (detail)을 표기하기 위한 라우팅(전환) 설정
def detail(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)   # Question 테이블에서 question_id를 기준으로 data를 가져오고(get) 없으면 404(찾을 수 없음) 에러 표기
    return render_template('question/question_detail.html', question=question, form=form)  # question_detail.html 파일을 "기초"로
                                                                                # question의 세부 내용을 불러와서 화면을 구성한다
# werkzeug = request, response 같은 명령의 실행을 (규약을 준수해서 설계할 수 있게) 도와주는 도구

def allowed_file(filename):    # 파일 확장자가 허용된 확장자인지 확인하는 함수 20231230
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

@bp.route('/create/', methods=('GET','POST'))
@login_required
def create():
    form = QuestionForm()
    if request.method == 'POST' and form.validate_on_submit():  # input text 값이 반드시 있어야 한다 -- 규칙 -- 지켰는가 체크
        # 파일이 업로드되었는지 확인
        if 'uploaded_img_file' in request.files:
            file = request.files['uploaded_img_file']
            # 파일이 비어있지 않고, 허용된 확장자인지 확인
            if file and allowed_file(file.filename):
                # 파일의 안전한 이름 생성
                filename = secure_filename(file.filename)
                # 파일 저장 경로 설정 __init__.py
                app = create_app()
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
                file_path_abs = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                         secure_filename(filename))
                file.save(file_path_abs)
                # 저장된 파일 이름을 데이터베이스에 저장
                question = Question(subject=form.subject.data, content=form.content.data,
                                    uploaded_img_file=file_path,  # 추가된 부분
                                    create_date=datetime.now(), user=g.user)
                db.session.add(question)
                db.session.commit()
                return (redirect(url_for('main.index')))
            else:
                flash('이미지가 없거나 허용된 이미지 파일 형식이 아닙니다.')
        else:
            flash('이미지 파일이 첨부되지 않았습니다.')
        question = Question(subject=form.subject.data, content=form.content.data,
                            uploaded_img_file='default.jpg',  # 추가된 부분
                            create_date=datetime.now(), user=g.user)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))
    if request.method == 'GET':
        code = request.args.get('code', '')
        language = request.args.get('language', '')
        # Markdown으로 변환
        if code: markdown_code = f"```{language}\n{urllib.parse.unquote(code)}\n```"
        else: markdown_code = ''
        form.content.data = markdown_code
    return render_template('question/question_form.html', form=form)


@bp.route('/modify/<int:question_id>', methods=('GET', 'POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)

    if g.user != question.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))

    form = QuestionForm()

    if request.method == 'POST' and form.validate_on_submit():
        # 파일이 업로드되었는지 확인
        if 'uploaded_img_file' in request.files:
            file = request.files['uploaded_img_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                app = create_app()
                file_path_abs = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                             filename)
                file.save(file_path_abs)
                question.uploaded_img_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            else:
                flash('허용된 이미지 파일 형식이 아닙니다.')
                # 이미지 파일이 잘못된 경우, 파일명을 변경하지 않음
        else:
            flash('이미지 파일이 첨부되지 않았습니다.')
            # 파일이 첨부되지 않은 경우, 기본 이미지 사용
            if not question.uploaded_img_file:
                question.uploaded_img_file = 'default.jpg'

        # 폼 데이터와 질문 객체 업데이트
        question.subject = form.subject.data
        question.content = form.content.data
        question.modify_date = datetime.now()
        print(question.uploaded_img_file)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'데이터베이스 오류: {str(e)}')
            return redirect(url_for('question.detail', question_id=question_id))

        return redirect(url_for('question.detail', question_id=question_id))

    # GET 요청 처리
    form = QuestionForm(obj=question)
    return render_template('question/question_form.html', form=form)


@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))