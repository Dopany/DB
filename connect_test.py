import psycopg2

def test_database_connection(dbname, user, password, host, port):
    try:
        # 데이터베이스에 연결
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        # 연결이 성공하면 메시지를 출력
        print("데이터베이스 연결 성공!")
        # 연결 닫기
        conn.close()
    except Exception as e:
        # 연결 실패 시 오류 메시지 출력
        print(f"데이터베이스 연결 실패: {e}")

# 연결을 테스트할 연결 정보
dbname = "postgres"
user = "kimseunghyun"
password = ""
host = "localhost"
port = "5432"

# 데이터베이스 연결 테스트 실행
test_database_connection(dbname, user, password, host, port)
