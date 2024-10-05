from datetime import datetime   #답변의 등록시간을 "시간 형태로" 입력하기 위해 참조

from flask import Blueprint, url_for, request, render_template, g   #url_for는 리다이렉트(redirect, 지정한 페이지로 전환)와 함께 쓰기위해,
                                                #requst는 html의 form 태그에서 전송되는 데이터를 객체(의 값)로 받아오기위해
from werkzeug.utils import redirect             #create 처리 후 지정한 화면으로 전환처리를 위해 참조

from pybo import db
from pybo.models import Question, Answer
from pybo.forms import AnswerForm
from .auth_views import login_required

bp = Blueprint('answer', __name__, url_prefix='/answer')


@bp.route('/create/<int:question_id>', methods=('POST',))
@login_required
def create(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    if form.validate_on_submit():
        content = request.form['content']
        answer = Answer(content=content, create_date=datetime.now(), user=g.user)
        question.answer_set.append(answer)
        db.session.commit()
        return redirect(url_for('question.detail', question_id=question_id))
    return render_template('question/question_detail.html', question=question, form=form)