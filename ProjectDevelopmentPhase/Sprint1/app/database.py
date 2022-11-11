import ibm_db

dsn_hostname = "2f3279a5-73d1-4859-88f0-a6c3e6b4b907.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud"
dsn_uid = "qst27374"
dsn_pwd = "cVc0GeCrJ5QOlOBk"
dsn_driver =  "{IBM DB2 ODBC DRIVER}"
dsn_database = "bludb"
dsn_port = 30756
dsn_protocol = "TCPIP"

dsn = (
    "DRIVER={0};"
    "DATABASE={1};"
    "HOSTNAME={2};"
    "PORT={3};"
    "PROTOCOL={4};"
    "UID={5};"
    "PWD={6};"
    "SECURITY=SSL"
).format(dsn_driver, dsn_database, dsn_hostname, dsn_port, dsn_protocol, dsn_uid, dsn_pwd)



def connect_db():
    conn = ibm_db.connect(dsn,"","")
    return conn

def fetchResults(res):
    result_set = []
    d = ibm_db.fetch_assoc(res)
    while  d != False:
        result_set.append(d)
        d = ibm_db.fetch_assoc(res)
    return result_set

def fetchUserById(id):
    conn = connect_db()
    query = 'SELECT * FROM user_credentials WHERE id = ?'
    stmt = ibm_db.prepare(conn, query)
    param = (id,)
    ibm_db.execute(stmt,param)
    result_set = fetchResults(stmt)
    ibm_db.close(conn)
    return result_set

def insert_user_credential(email, username):
    conn = connect_db()
    query = 'INSERT INTO user_credentials (email, password) VALUES (?, ?)'
    stmt = ibm_db.prepare(conn, query)
    param = (email, username)
    res = ibm_db.execute(stmt,param)
    return res

def insert_user_profile(login_id):
    conn = connect_db()
    query = 'INSERT INTO user_profile (login_id) VALUES (?)'
    stmt = ibm_db.prepare(conn, query)
    param = (login_id,)
    res = ibm_db.execute(stmt, param)
    return res

def fetchUserByEmail(email):
    conn = connect_db()
    query = 'SELECT * FROM user_credentials WHERE email = ?'
    stmt = ibm_db.prepare(conn, query)
    param = (email,)
    ibm_db.execute(stmt,param)
    result_set = fetchResults(stmt)
    ibm_db.close(conn)
    return result_set
