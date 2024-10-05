import subprocess
import os
import sys
import io
from flask import Blueprint, render_template, request, jsonify, g
import tempfile
from pybo import db
from pybo.models import Codefile
from datetime import datetime

bp = Blueprint('compiler', __name__, url_prefix='/compiler')

# 임시 파일 디렉토리 설정
TEMP_DIR = tempfile.gettempdir()


@bp.route('/compiler', methods=['GET'])
def index():
    codefiles = Codefile.query.filter_by(user_id=g.user.id).order_by(Codefile.saved_date.desc()).all() #20240907
    return render_template('compiler.html', codefiles=codefiles) #20240907


@bp.route('/save_code', methods=['POST'])
def save_code():
    # 파일명 리스트 정의 (사용자는 항상 파일명을 선택한 상태에서 저장)
    FILE_NAMES = [f'{g.user.id}_file{str(i).zfill(2)}' for i in range(1, 6)]
    data = request.get_json()
    code_str = data.get('code', '')
    filename = data.get('filename', '')

    if not code_str or filename not in FILE_NAMES:
        return jsonify(success=False, message=f"Invalid filename. Allowed filenames are {FILE_NAMES}.")

    # 파일명을 고정하여 덮어쓰기 (새로운 파일을 만들지 않음)
    codefile = Codefile.query.filter_by(user_id=g.user.id, filename=filename).first()
    if codefile:
        codefile.set_code(code_str)  # 기존 파일 덮어쓰기
        codefile.saved_date=datetime.now()
    else:
        return jsonify(success=False, message="File does not exist. Please select an existing file.")

    db.session.commit()

    return jsonify(success=True)

@bp.route('/load_code', methods=['GET']) #20240907
def load_code():
    filename = request.args.get('fileid')

    codefile = Codefile.query.filter_by(filename=filename, user_id=g.user.id).first()
    if codefile.get_code():
        return jsonify(success=True, code=codefile.get_code())
    else:
        return jsonify(success=False, message="Code file not found.")

@bp.route('/run_code', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')  # 기본값은 Python
    stdin = data.get('stdin', '')  # stdin 값 추가
    # Python 코드 실행
    if language == 'python':
        return run_python_code(code, stdin)

    # C 코드 실행
    elif language == 'c':
        return run_c_code(code, stdin)

    # Java 코드 실행
    elif language == 'java':
        return run_java_code(code, stdin)

    return jsonify(output='Unsupported language.')

def run_python_code(code, stdin):
    output_buffer = io.StringIO()
    sys.stdout = output_buffer
    sys.stdin = io.StringIO(stdin)  # stdin 처리

    try:
        exec(code)
        output = output_buffer.getvalue()
    except Exception as e:
        output = f'Error: {str(e)}'
    finally:
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__

    return jsonify(output=output)


def run_c_code(code, stdin):
    with tempfile.NamedTemporaryFile(suffix='.c', delete=False, dir=TEMP_DIR) as temp_c_file:
        temp_c_file.write(code.encode('utf-8'))
        temp_c_file.flush()

    executable = temp_c_file.name.replace('.c', '')
    compile_cmd = f"gcc {temp_c_file.name} -o {executable}"

    try:
        # C 코드 컴파일
        compile_output = subprocess.run(compile_cmd, shell=True, check=True, capture_output=True, text=True)

        # 컴파일 성공 시 실행
        run_output = subprocess.run(executable, input=stdin, shell=True, check=True, capture_output=True, text=True)
        output = run_output.stdout
    except subprocess.CalledProcessError as e:
        output = e.stderr
    finally:
        # 프로세스 실행이 완료된 후 파일 삭제
        try:
            os.remove(temp_c_file.name)
            if os.path.exists(executable):
                os.remove(executable)
        except PermissionError as e:
            output += f"\nError cleaning up files: {str(e)}"

    return jsonify(output=output)


def run_java_code(code, stdin):
    # 파일 이름과 클래스 이름을 추출
    classname = None
    lines = code.splitlines()
    if lines:
        first_line = lines[0].strip()
        if first_line.startswith("public class"):
            classname = first_line.split()[2]

    if not classname:
        return jsonify(output="Class name could not be determined.")

    with tempfile.NamedTemporaryFile(suffix='.java', delete=False, dir=TEMP_DIR) as temp_java_file:
        temp_java_file.write(code.encode('utf-8'))
        temp_java_file.flush()

    # 파일 이름을 classname.java로 설정
    java_file_path = os.path.join(TEMP_DIR, f"{classname}.java")
    os.rename(temp_java_file.name, java_file_path)

    compile_cmd = f"javac -encoding UTF-8 {java_file_path}"

    try:
        # Java 코드 컴파일
        compile_output = subprocess.run(compile_cmd, shell=True, check=True, capture_output=True, text=True)

        # 컴파일 성공 시 실행
        run_output = subprocess.run(f"java -cp {TEMP_DIR} {classname}", input=stdin, shell=True, check=True, capture_output=True, text=True)
        output = run_output.stdout
    except subprocess.CalledProcessError as e:
        output = e.stderr
    finally:
        # 파일 정리
        try:
            os.remove(java_file_path)
            class_file = os.path.join(TEMP_DIR, f"{classname}.class")
            if os.path.exists(class_file):
                os.remove(class_file)
        except PermissionError as e:
            output += f"\n파일 정리 중 오류 발생: {str(e)}"

    return jsonify(output=output)
