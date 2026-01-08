@router.get("/{idenvio}")
def obtener_envio(idenvio: int):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            SELECT 
                bdAuxsql.dbo.CodeDircon(convert( int, idenvio + 1000)) AS IDENVIO,
                fechaenvio,
                idtipo,
                urlaudio,
                texto,
                tipotelefono,
                prefijo,
                telefono,
                nombre,
                campo1,
                campo2,
                campo3,
                campo4,
                campo5,
                estado
            FROM envio_api
            WHERE IDENVIO = ?
        """

        cursor.execute(sql, (idenvio,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Registro no encontrado")

        # Convertimos la fila en un diccionario
        columnas = [col[0] for col in cursor.description]
        data = dict(zip(columnas, row))

        return {
            "status": "ok",
            "data": data
        }

    except Exception as e:
        print("ERROR SQL:", repr(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor")

    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if conn:
                conn.close()
        except:
            pass

