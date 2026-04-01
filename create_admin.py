import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='jaikeerthi07a',
        database='m3cars'
    )
    cursor = connection.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT * FROM login WHERE email='admin@m3cars.com'")
    if cursor.fetchone():
        print("User admin@m3cars.com already exists.")
    else:
        cursor.execute("INSERT INTO login (username, email, password) VALUES ('admin', 'admin@m3cars.com', 'adminpassword')")
        connection.commit()
        print("Default user 'admin@m3cars.com' created with password 'adminpassword'.")
    
    cursor.close()
    connection.close()
except Exception as e:
    print(f"Error: {e}")
