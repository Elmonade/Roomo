import psycopg2
import datetime

conn = psycopg2.connect('dbname=rpi')
cur = conn.cursor()

def insert_log(date, humid, temp, light, smoke):
    query = """
    INSERT INTO
        sensors
    VALUES
        (%s, %s, %s, %s, %s )
    """
    values = (date, humid, temp, light, smoke)
    cur.execute(query, values)

date = datetime.datetime.now()
formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")

insert_log(formatted_date, 53, 23, 0.53, False)

cur.execute('select * from sensors')
conn.commit()

results = cur.fetchall()

for i in results:
    print(i)
