from flask import Flask,request,jsonify
from flask.json import JSONEncoder
from sqlalchemy import create_engine,text

## Default JSON encoder cannot be converted set as JSON
## so we should make custom encoder and convert set into list
## make available as JSON

class CustomJSONEncoder(JSONEncoder):
  def default(self, obj):
     if isinstance(obj, set):
        return list(obj)
  
     return JSONEncoder.default(self, obj)

def get_user(user_id):
  user = current_app.database.execute(text("""
    SELECT id,name,email,profile FROM users WHERE id= :user_id"""),
    {'user_id':user_id}).fetchone()

  return  {
      'id': user['id'],
      'name': user['name'],
      'email': user['email'],
      'profile': user['profile'] } if user else None

def insert_user(user):
   return current_app.database.execute(text("""
    INSERT INTO users (name,email,profile,hashed_password)
    VALUES (:name,:email,:profile,:password)"""),user).lastrowid

def insert_tweet(user_tweet):
   return current_app.database.execute(text("""
    INSERT INTO tweets ( user_id, tweet) VALUES ( :id, :tweet) """),
    user_tweet).rowcount

def insert_follow(user_follow):
   return current_app.database.execute(text("""
    INSERT INTO users_follow_list (user_id, follow_user_id) VALUES ( 
    :id, :follow)"""),user_follow).rowcount

def insert_unfollow(user_unfollow):
    return current_app.database.execute(text("""
    DELETE FROM users_follow_list WHERE user_id= :id AND follow_user_id = :unfollow"""),user_unfollow).rowcount

def get_timeline(user_id):
    timeline = current_app.database.execute(text("""
    SELECT t.user_id,t.tweet FROM tweeets t LEFT JOIN users_follow_list ufl ON
    ufl.user_id = :user_id WHERE t.user_id = :user_id OR t.user_id = ufl.follow_user_id"""), {'user_id':user_id}).fetchall()
    return [{
        'user_id' : tweet['user_id'],
        'twweet' : tweet['tweet'] } for tweet in timeline]

def create_app(test_config=None):
  app = Flask(__name__)
  app.json_encoder = CustomJSONEncoder

  if test_config is None:
    app.config.from_pyfile("config.py")
  else:
    app.config.update(test_config)

  database = create_engine(app.config['DB_URL'], encoding='utf-8', max_overflow = 0 )
  app.database = database

  @app.route("/ping",methods=['GET','POST'])
  def ping():
    return "pong"

  @app.route("/sign-up",methods=['GET','POST'])
  def sign_up():
    new_user = request.json
    new_user["id"] = app.id_count
    app.users[app.id_count] = new_user
    app.id_count = app.id_count + 1

    return jsonify(new_user)

  @app.route("/tweet", methods=['GET','POST'])
  def tweet():
    payload = request.json
    user_id = int(payload['id'])
    tweet = payload['tweet']

    if user_id not in app.users:
       return 'user does not exist',400

    if len(tweet) > 300:
       return 'text over 300', 400

    user_id = int(payload['id'])

    app.tweets.append({
      'user_id':user_id,
      'tweet':tweet
    })

    return '',200

  @app.route('/follow', methods=['GET','POST'])
  def follow():
    payload = request.json
    user_id = int(payload['id'])
    user_id_to_follow = int(payload['follow'])

    if user_id not in app.users or user_id_to_follow not in app.users:
      return 'user not exist',400

    user = app.users[user_id]
    user.setdefault('follow',set()).add(user_id_to_follow)

    return jsonify(user)

  @app.route('/unfollow',methods=['GET','POST'])
  def unfollow():
    payload = request.json
    user_id = int(payload['id'])
    user_id_to_follow = int(payload['unfollow'])

    if user_id not in app.users or user_id_to_follow not in app.users:
       return ' user not exist', 400

    user = app.users[user_id]
    user.setdefault('follow', set()).discard(user_id_to_follow)

    return jsonify(user)

  @app.route('/timeline/<int:user_id>',methods=['GET','POST'])
  def timelne(user_id):
    if user_id not in app.users:
      return ' user does not exist', 400

    follow_list = app.users[user_id].get('follow',set())
    follow_list.add(user_id)
    timeline = [tweet for tweet in app.tweets if tweet['user_id'] in follow_list]

    return jsonify({
           'user_id': user_id,
           'timeline' : timeline
    })

  return app









