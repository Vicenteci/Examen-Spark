import psycopg2

def create_table():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="retail_db",
            user="postgres",
            password="casa1234",
            port=5432
        )

        # Crear la tabla
        createTableString = '''
        CREATE TABLE IF NOT EXISTS Stores (
            store_id SERIAL PRIMARY KEY,
            store_name VARCHAR(255),
            location VARCHAR(255),
            demographics VARCHAR(255)
        );
        '''
        
        with conn.cursor() as cur:
            cur.execute(createTableString)
        conn.commit()

    except (psycopg2.DatabaseError, Exception) as error:
        print("Error: ", error)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    create_table()
