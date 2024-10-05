
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, g, flash
from pybo.views.auth_views import login_required
#from flask_login import login_required, current_user
from pybo import db
from pybo.models import User, Vote
from pybo import create_app

import os
from werkzeug.utils import secure_filename

bp = Blueprint('profile', __name__, url_prefix='/profile')

def allowed_file(filename):    # 파일 확장자가 허용된 확장자인지 확인하는 함수 20231230
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

# 프로필 페이지 로드
@bp.route('/<username>')
@login_required
def profile(username):
    # 프로필 정보 가져오기
    profile_user = User.query.filter_by(username=username).first_or_404()

    # upvote와 downvote 수를 계산
    upvotes = Vote.query.filter_by(target_user_id=profile_user.id, vote_type='upvote').count()
    downvotes = Vote.query.filter_by(target_user_id=profile_user.id, vote_type='downvote').count()

    # 프로필 정보 렌더링
    return render_template('/profile/profile.html', profile=profile_user, upvotes=upvotes, downvotes=downvotes)


# 투표 기록을 조회하는 라우트
@bp.route('/check_vote/<int:target_user_id>', methods=['GET'])
@login_required
def check_vote(target_user_id):
    vote = Vote.query.filter_by(voter_id=g.user.id, target_user_id=target_user_id).first()

    if vote:
        return jsonify({'status': 'success', 'vote_type': vote.vote_type})

    return jsonify({'status': 'none'})


# 업보트 처리
@bp.route('/upvote', methods=['POST'])
@login_required
def upvote():
    data = request.get_json()
    target_user_id = data.get('target_user_id')

    existing_vote = Vote.query.filter_by(voter_id=g.user.id, target_user_id=target_user_id).first()
    if existing_vote:
        if existing_vote.vote_type == 'upvote':
            return jsonify({'status':'fail', 'message':'already upvoted'})

    # 기존의 다운보트 삭제
    existing_vote = Vote.query.filter_by(voter_id=g.user.id, target_user_id=target_user_id,
                                         vote_type='downvote').first()
    if existing_vote:
        db.session.delete(existing_vote)

    # 새 업보트 추가
    new_vote = Vote(voter_id=g.user.id, target_user_id=target_user_id, vote_type='upvote')
    db.session.add(new_vote)
    db.session.commit()

    # 투표 수 업데이트
    upvotes = Vote.query.filter_by(target_user_id=target_user_id, vote_type='upvote').count()
    downvotes = Vote.query.filter_by(target_user_id=target_user_id, vote_type='downvote').count()

    return jsonify({'status': 'success', 'upvotes': upvotes, 'downvotes': downvotes})


# 다운보트 처리
@bp.route('/downvote', methods=['POST'])
@login_required
def downvote():
    data = request.get_json()
    target_user_id = data.get('target_user_id')

    existing_vote = Vote.query.filter_by(voter_id=g.user.id, target_user_id=target_user_id).first()
    if existing_vote:
        if existing_vote.vote_type == 'downvote':
            return jsonify({'status':'fail', 'message':'already downvoted'})

    # 기존의 업보트 삭제
    existing_vote = Vote.query.filter_by(voter_id=g.user.id, target_user_id=target_user_id, vote_type='upvote').first()
    if existing_vote:
        db.session.delete(existing_vote)

    # 새 다운보트 추가
    new_vote = Vote(voter_id=g.user.id, target_user_id=target_user_id, vote_type='downvote')
    db.session.add(new_vote)
    db.session.commit()

    # 투표 수 업데이트
    upvotes = Vote.query.filter_by(target_user_id=target_user_id, vote_type='upvote').count()
    downvotes = Vote.query.filter_by(target_user_id=target_user_id, vote_type='downvote').count()

    return jsonify({'status': 'success', 'upvotes': upvotes, 'downvotes': downvotes})

@bp.route('/edit', methods=['GET', 'POST'])
@login_required  # 로그인된 사용자만 접근 가능
def edit_profile():
    if request.method == 'POST':
        # 프로필 수정 처리 코드 (이름, bio, 사진 업로드 등)
        bio = request.form.get('bio')
        photo = request.files.get('profile_picture')

        # 업데이트 처리
        if bio:  # "code" 필드에 bio 업데이트
            g.user.code = bio  # 여기서 g.user는 현재 로그인한 사용자

        if photo and allowed_file(photo.filename):  # 새로운 사진이 업로드된 경우

            # 기존 프로필 사진 경로
            if g.user.photo:
                old_photo_path = g.user.photo
                # 파일의 안전한 이름 생성
                old_filename = secure_filename(old_photo_path)
                # 파일 저장 경로 설정 __init__.py
                app = create_app()
                old_file_path_abs = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                                 'profile',
                                                 secure_filename(old_filename))
                # 기존 사진 삭제
                if old_photo_path and os.path.exists(old_file_path_abs):
                    os.remove(old_file_path_abs)

            # 새 사진 업로드 처리
            # 파일의 안전한 이름 생성
            filename = secure_filename(photo.filename)
            # 파일 저장 경로 설정 __init__.py
            app = create_app()
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'profile', secure_filename(filename))
            file_path_abs = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], 'profile',
                                         secure_filename(filename))
            photo.save(file_path_abs)
            g.user.photo = filename  # "photo" 필드에 새 경로 업데이트

        # DB에 변경 사항 저장
        db.session.commit()  # SQLAlchemy 세션 커밋

        flash('프로필이 성공적으로 수정되었습니다.')
        return redirect(url_for('profile.profile', username=g.user.username))

    return render_template('/profile/edit_profile.html', profile=g.user)