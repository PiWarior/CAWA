import psycopg2

def connec():
    # Connexion à PostgreSQL
    conn = psycopg2.connect(dbname="cars", user="postgres", password="cawa", host="localhost")
    cursor = conn.cursor()
    return conn, cursor