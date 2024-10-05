from flask import Blueprint, render_template, url_for #20230617_rndr+ 20230624_url_for 추가
from werkzeug.utils import redirect
from flask import Flask #, send_file
from pybo.models import Question
bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
#    question_list = Question.query.order_by(Question.create_date.desc())
#    return render_template('question/question_list.html', question_list = question_list)
    return redirect(url_for('question._list'))

#@bp.route('/detail/<int:question_id>/')
#def detail(question_id):
#    question = Question.query.get_or_404(question_id)
#    return render_template('question/question_detail.html', question=question)

#@bp.route('/download')
#def Download_File():
#    PATH='test.zip'
#    return send_file(PATH, as_attachment=True)

