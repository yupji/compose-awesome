from flask import Flask
import pymysql

# db host는 -> `db`:컴포즈에 기술한 컨테이너명
app = Flask(__name__)

# 디비 root 비밀번호 로드
root_password = None
with open('/run/secrets/db-password') as f:
    root_password = f.read()

# 데이터베이스 연동 코드 추가해서, 도커컴포즈로 구성된 컨테이너간 디비 연동이 잘되는지 체크

def db_init():
    try:
        # mysql -u root -p
        # password:
        connection = pymysql.connect(host        = 'db',
                                     user        = 'root',
                                     password    = root_password,
                                     charset     = 'utf8'
                                     )
        # mysql[None]:>
        with connection: # 커넥션은 with문을 나가면 자동으로 닫힌다
            with connection.cursor() as cur: # 커서는 with문을 나가면 자동으로 닫힌다
                # 1. 데이터베이스 생성
                cur.execute('create database if not EXISTS ml_db;')
                # 2. 커밋 -> 데이터베이스(물리적)에 변동을 가하면(db생성, 테이블생성, 데이터입력/수정/삭제)
                connection.commit()
                # 3. 데이터베이스 사용 지정
                cur.execute('use ml_db;')
                # mysql[ml_db]:>
                # 4. 테이블 생성
                cur.execute('''
                    create table dumy (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(256)
                    );
                ''')
                # 5. 커밋
                connection.commit()

    except Exception as e:
        print( '접속 오류', e )

db_init()

# 더미 데이터 삽입 및 조회
def db_insert_select():
    rows = []
    try:
        # 커넥션
        connection = pymysql.connect(host        = 'db',
                                     user        = 'root',
                                     password    = root_password,
                                     database    = 'ml_db',
                                     charset     = 'utf8',
                                     cursorclass = pymysql.cursors.DictCursor
                                     )
        with connection: 
            with connection.cursor() as cur:
                # 더미 데이터 삽입 -> row가 변했다 -> 커밋행위 확정
                cur.execute("insert into dumy (title) VALUES ('test');")
                # 커밋
                connection.commit()
                # 모든 데이터 조회
                cur.execute('select title from dumy')
                # 조회 데이터 획득
                rows = cur.fetchall()
    except Exception as e:
        print( e )
    finally:
        # 응답
        return rows

@app.route('/')
def home():
    rows = db_insert_select()
    return f"hello Container - 데이터수: { len(rows) }"