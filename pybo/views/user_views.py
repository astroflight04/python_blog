from flask import Blueprint, jsonify, request
from pybo.models import User
from pybo.views.auth_views import login_required

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/search')
@login_required
def search_user():
    query = request.args.get('query', '').strip()
    if len(query) < 3:  # 입력이 5글자 미만인 경우 빈 리스트 반환
        return jsonify([])

    # ID 규칙: 알파벳, 숫자, 밑줄(_)만 허용
    if not query or not query.isalnum():
        return jsonify([])

    # 사용자명 필터링 (대소문자 구분 없이 검색)
    users = User.query.filter(User.username.ilike(f'{query}%')).all()
    user_list = [{'id': user.id, 'username': user.username} for user in users]

    return jsonify(user_list)