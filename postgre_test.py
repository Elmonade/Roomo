import psycopg2

try:
    conn = psycopg2.connect("dbname=RPi user=postgres password=postgres")
    if conn is not None:
        print('Connection established!')
    else:
        print('Connection not established!')
except (Exception, psycopg2.DatabaseError) as error:
    print(error)

finally:
    if conn is not None:
        conn.close()
        print('Finally, connection closed')
