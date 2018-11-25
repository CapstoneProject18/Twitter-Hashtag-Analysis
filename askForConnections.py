import pymysql.cursors


# Function return a connection.
def getConnection():
    # You can change the connection arguments.
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='flask',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection
