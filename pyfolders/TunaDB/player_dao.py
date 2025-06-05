from datetime import date
import random
from TunaDB.connect import get_connection

# 등록 확인
def is_registered(player_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = "SELECT 1 FROM Player WHERE player_id = %s"
        cursor.execute(sql, (player_id,))
        result = cursor.fetchone()
        return result is not None
    finally:
        cursor.close()
        conn.close()

# 등록
def register_new_player(player_id, player_name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO Player (player_id, player_name, point) VALUES (%s, %s, %s)"
        cursor.execute(sql, (player_id, player_name, 100))  # 시작 포인트 100
        conn.commit()
    finally:
        cursor.close()
        conn.close()

#조회
def get_player_point(player_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = "SELECT point FROM Player WHERE player_id = %s"
        cursor.execute(sql, (player_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()
        conn.close()

#출첵?
def has_checked_today(player_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = "SELECT last_attendance FROM Player WHERE player_id = %s"
        cursor.execute(sql, (player_id,))
        result = cursor.fetchone()
        if result and result[0] == date.today():
            return True
        return False
    finally:
        cursor.close()
        conn.close()

#출첵
def update_attendance(player_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        bonus = random.randint(10, 20)
        sql = """
        UPDATE Player 
        SET point = point + %s,
            last_attendance = %s
        WHERE player_id = %s
        """
        cursor.execute(sql, (bonus, date.today(), player_id))
        conn.commit()
        return bonus
    finally:
        cursor.close()
        conn.close()

# 삭제제
def delete_player(player_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM Player WHERE player_id = %s"
        cursor.execute(sql, (player_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
