import os  # 파일 입출력, 경로 참조 등을 위해서 os import

BASE_DIR = os.path.dirname(__file__)    #데이터베이스 파일이 있는 기본 위치를 확인

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'pybo.db'))  #데이터베이스 파일의 실제 경로를 URI형식
                                                                                    #으로 접근
                                                                                    #URI는 http://www.naver.com/aa 형식
                                                                                    #sqlite:///{}
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = "md5"

