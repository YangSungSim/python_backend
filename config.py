db = {
'user' :'root',
'password' :'1234',
'host':'localhost',
'port':3306,'database':'minister'
}
DB_URL = "mysql+mysqlconnector://{}:{}@{}:{}/{}?charset=utf8".format(db['user'],db['password'],db['host'],db['port'],db['database'])
 
