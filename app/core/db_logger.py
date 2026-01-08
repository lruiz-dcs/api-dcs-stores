from app.core.database import get_connection

def log_db(nivel, modulo, mensaje, detalle=None, idcliente=None, ip=None):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO api_log (nivel, modulo, mensaje, detalle, idcliente, ip)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (
            nivel,
            modulo,
            mensaje,
            detalle,
            idcliente,
            ip
        ))
        conn.commit()
    except:
        pass
    finally:
        try:
            if cursor: cursor.close()
        except: pass
        try:
            if conn: conn.close()
        except: pass
