import mariadb
from flask import Flask, request, Response
import json
import dbcreds
from flask_cors import CORS
import random
import string

app = Flask(__name__)
CORS(app)
def generateToken():
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(56))
    return result_str
print (generateToken())
#USER_GET#####################################################USER_GET!#######################USER_GET#############################
@app.route('/api/users', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def user_endpoint():
    if request.method == 'GET':
        conn = None
        cursor = None
        user = None
        user_id = request.args.get("userId")
        try :
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if user_id != None:
                cursor.execute("SELECT * FROM user WHERE id = ?", [user_id],)
            else:   
                cursor.execute("SELECT * FROM user")
            users =cursor.fetchall()
        except Exception as error:  
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(users != None):
                empty = []
                for user in users : 
                    element = { 
                        "userId":user[4],
                        "email":user[1],
                        "username":user[0],
                        "bio":user[2],
                        "birthday":user[3]


                    }

                    empty.append(element)
                return Response(json.dumps(empty, default=str), mimetype="application/json", status=200)
            else:
                return Response("Look's like you F'd up! GET ERROR", mimetype="text/html", status=505)            
#USER_POST#############################################USER_POST########################USER_POST#############################################
    elif request.method == 'POST':
        conn = None
        cursor = None
        username = request.json.get("username")
        bio = request.json.get("bio")
        birthdate = request.json.get("birthdate")
        email = request.json.get("email")
        password = request.json.get("password")
        loginToken = generateToken()
        rows = None
        user = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor() 
            if username != None and username!= "" and email != None and email!= "" and birthdate != None and birthdate!= "" and password != None and password!= "" and bio != None and bio!= "":
                cursor.execute("INSERT INTO user(username, bio, birthdate, email, password) VALUES (?,?,?,?,?)", [username, bio, birthdate, email, password])
                conn.commit()
                user_id = cursor.lastrowid
                cursor.execute("INSERT INTO user_session(login_token, user_id) VALUES (?,?)", [loginToken, user_id])
                conn.commit()
                rows = cursor.rowcount                                                                                            
        except Exception as error:
            print("Sorry you're F'ed.  Intrnal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                user = {
                     "userId":user_id,
                     "email": email,
                    "username":username,
                    "bio":bio,
                    "birthdate":birthdate,
                    "loginToken": loginToken                   
                }
                print(user)
                return Response (json.dumps(user, default=str), mimetype="application/json", status="210")
            else:
                return Response("Look's like you F'd up! POST ERROR", mimetype="text/html", status=510) 
#USER_PATCH#####################################################USER_PATCH####################################USER_PATCH######################################
    elif request.method == "PATCH":
        conn = None
        cursor = None
        username = request.json.get("username")
        bio = request.json.get("bio")
        birthdate = request.json.get("birthdate")
        email = request.json.get("email")
        password = request.json.get("password")
        loginToken = request.json.get("loginToken")
        rows = None
        user = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute ("SELECT user_id from user_session WHERE login_token =?", [loginToken])
            user_id = cursor.fetchone()[0]
            print (user_id)
            if username!= "" and username != None:
                cursor.execute("UPDATE user SET username=? WHERE id=?", [username, user_id])
            if bio != "" and bio != None:
                cursor.execute("UPDATE user SET bio=? WHERE id=?", [bio, user_id])
            if birthdate != "" and birthdate != None:
                cursor.execute("UPDATE user SET birthdate=? WHERE id=?", [birthdate, user_id])
            if email != "" and email != None:
                cursor.execute("UPDATE user SET email=? WHERE id=?", [email, user_id])
            if password != "" and password != None:
                cursor.execute("UPDATE user SET password=? WHERE id=?", [password, user_id])
            conn.commit()
            rows = cursor.rowcount
            cursor.execute("SELECT * FROM user WHERE id=?", [user_id])
            user = cursor.fetchone()
        except Exception as error:
            print("Something went wrong (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if(rows == 1):
                myuser = {
                     "userId":user_id,
                     "email": user[1],
                    "username":user[0],
                    "bio":user[2],
                    "birthdate":user[3],                  
                }
                return Response (json.dumps(myuser, default=str), mimetype="application/json", status="215")
            else:
                return Response("Look's like you F'd up! PATCH ERROR ", mimetype="text/html", status=515)            
#USER_DELETE############################################################################################################
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        password = request.json.get("password")
        loginToken = request.json.get("loginToken")
        try :
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE login_token = ?", [loginToken,])
            user_id = cursor.fetchone()[0]
            cursor.execute("DELETE FROM user WHERE id = ? AND password = ?", [user_id, password,])
            conn.commit()
            rows = cursor.rowcount
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("Guess What?!? USER DELETED...", mimetype="text/html", status=204)
            else:
                return Response("Look's like you F'd up! DELETE ERROR", mimetype="text/html", status=520)
            
########################END OF @USER#####################################################END OF @USER########################
########################LOGIN_PATCH######################################################LOGIN_PATCH#########################
@app.route('/api/login', methods=['POST', 'DELETE'])
def login_endpoint():
    
    if request.method == 'POST':
        conn = None
        cursor = None
        email = request.json.get("email")
        password = request.json.get("password")
        loginToken = generateToken()
        rows = None
        user = None
        user_id = None
        
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor() 
            cursor.execute ("SELECT id, bio, username, birthdate, email FROM user WHERE email=? AND password=?", [email, password])
            # print (cursor.fetchall())
            user = cursor.fetchall()
            user_id = user[0][0]
            cursor.execute("INSERT INTO user_session(login_token, user_id) VALUES (?,?)", [loginToken, user_id])
            conn.commit()
            rows = cursor.rowcount                                                                                          
        except Exception as error:
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                user = {
                     "userId":user_id,
                     "bio" : user[0][1],
                     "username": user[0][2],
                     "birthdate": user[0][3],
                     "email": user[0][4],
                    "loginToken": loginToken                   
                }
                return Response (json.dumps(user, default=str), mimetype="application/json", status="210")
            else:
                return Response("Look's like you F'd up! POST ERROR", mimetype="text/html", status=510)
            
#DELETE_LOGIN##################################################################################DELETE_LOGIN##################################
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        loginToken = request.json.get("loginToken")
       
        try :
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute ("DELETE from user_session WHERE login_token =?", [loginToken])
            conn.commit()
            rows = cursor.rowcount            
        except Exception as error:  
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("Guess What?!? loged out...", mimetype="application/json", status=220)
            else:
                return Response("Look's like you F'd up! DELETE ERROR", mimetype="text/html", status=520)
            
#END OF @LOGIN###########################################################################END OF @LOGIN##########################################
#TWEET_GET################################################################################TWEET_GET#########################################
@app.route('/api/tweets', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def tweets_endpoint():
    if request.method == 'GET':
        conn = None
        cursor = None
        tweet = None
        password = None
        userId = request.args.get("userId")
        
        try :
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if userId != None :
                cursor.execute("SELECT * FROM tweet INNER JOIN user ON tweet.user_id=user.id WHERE user.id = ?",[userId])
            else:
                cursor.execute("SELECT * FROM tweet INNER JOIN user ON tweet.user_id=user.id")
            tweets =cursor.fetchall()
        except Exception as error:  
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(tweets != None):
                myTweets = []
                for tweet in tweets : 
                    myTweet ={ 
                        "tweetId": tweet[0],
                        "userId": tweet[2],
                        "username": tweet[4],
                        "content": tweet[1],
                        "createdAt": tweet[3],
                        }
                    myTweets.append(myTweet)

            
                return Response(json.dumps(myTweets, default=str), mimetype="application/json", status=205)
            else:
                return Response("Look's like you F'd up! GET ERROR", mimetype="text/html", status=505)
#TWEET_POST##########################################################################################TWEET_POST#############################
    elif request.method == 'POST':
        conn = None
        cursor = None
        content = request.json.get("content")
        loginToken = request.json.get("loginToken")
        rows = None
        user = None
        user_id = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor() 
            cursor.execute("SELECT user_id FROM user_session WHERE login_token =?", [loginToken])
            user_id = cursor.fetchone()[0]
            cursor.execute("SELECT username FROM user WHERE id=?", [user_id])
            username = cursor.fetchone()[0]
            print(user_id)
            cursor.execute("INSERT INTO tweet(user_id, content) VALUES (?,?)", [user_id, content])
            conn.commit()
            rows = cursor.rowcount
            tweetId = cursor.lastrowid
            cursor.execute("SELECT created_at FROM tweet WHERE id=?", [tweetId])
            created_at = cursor.fetchone()[0]
           
        except Exception as error:
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                tweet = {
                    "tweetId": tweetId,
                    "userId": user_id, 
                    "username": username,
                    "content": content,
                    "created_at": created_at,
                }
                return Response (json.dumps(tweet, default=str), mimetype="application/json", status="210")
            else:
                return Response("Look's like you F'd up! POST ERROR", mimetype="text/html", status=510) 
#TWEET_PATCH#################################################################################################TWEET_PATCH###############################
    elif request.method == "PATCH":
        conn = None
        cursor = None
        tweetId = request.json.get("tweetId")
        content = request.json.get("content")
        loginToken = request.json.get("loginToken")
        rows = None
        username = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute ("SELECT user_id from user_session WHERE login_token =?", [loginToken])
            user_id = cursor.fetchone()[0]
            
            print (user_id)
            print(tweetId)
            print(content)
            if content!= "" and content != None and tweetId !=None:
                cursor.execute("UPDATE tweet SET content =? WHERE id=? AND user_id=?", [content, tweetId,user_id])
            conn.commit()
            rows = cursor.rowcount
            print(rows)
            cursor.execute("SELECT * FROM user WHERE id=?", [user_id])
            username = cursor.fetchall()[0][0]
        except Exception as error:
            print("Something went wrong (THIS IS LAZY)")
            print(error)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.rollback()
                conn.close()
            if(rows == 1):
                tweet = {
                    "tweetId": tweetId,
                    "content": content,
                    
                }
                return Response (json.dumps(tweet, default=str), mimetype="application/json", status="215")
            else:
                return Response("Look's like you F'd up! PATCH ERROR ", mimetype="text/html", status=515)
#TWEET_DELETE####################################################################################TWEET_DELETE#############################################
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        loginToken = request.json.get("loginToken")
        tweet_id = request.json.get("tweetId")
        try :
            
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute ("SELECT user_id from user_session WHERE login_token =?", [loginToken])
            user_id = cursor.fetchone()[0]
            print(user_id)
            cursor.execute("DELETE FROM tweet WHERE user_id =? AND id=?", [user_id, tweet_id])            
            conn.commit()
            rows = cursor.rowcount            
        except Exception as error:  
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("Guess What?!?  DELETED...", mimetype="application/json", status=220)
            else:
                return Response("Look's like you F'd up! DELETE ERROR", mimetype="text/html", status=520)
#END OF @TWEET#################################################################################END OF @TWEET###############################
#TWEETCOMMENT_GET#############################################################################TWEETCOMMENT_GET###########################################################
@app.route('/api/comments', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def comment_endpoint():
    if request.method == 'GET':
        conn = None
        cursor = None
        comment = None
        tweetId = request.args.get("tweetId")
        try :
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if tweetId != None :
                cursor.execute("SELECT * FROM comment INNER JOIN user ON comment.user_id = user.id WHERE comment.tweet_id=?",[tweetId])
                comments =cursor.fetchall()
        except Exception as error:  
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(comments != None):
                myComments = []
                for comment in comments:
                    myComment = {
                        "commentId":comment[0],
                        "tweetId":comment[2],
                        "userId":comment[3],
                        "username":comment[5],
                        "content":comment[4],
                        "createdAt":comment[1]
                    }
                    myComments.append(myComment)
                return Response(json.dumps(myComments, default=str), mimetype="application/json", status=205)
            else:
                return Response("Look's like you F'd up! GET ERROR", mimetype="text/html", status=505)
#COMMENT_POST#############################################################################################COMMENT_POST#####################################
    elif request.method == 'POST':
        conn = None
        cursor = None
        content = request.json.get("content")
        loginToken = request.json.get("loginToken")
        rows = None
        comment = None
        tweet_id = request.json.get("tweetId")
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor() 
            cursor.execute("SELECT user_id FROM user_session WHERE login_token =?", [loginToken])
            user_id = cursor.fetchone()[0]
            cursor.execute("SELECT username FROM user WHERE id =?", [user_id])
            username = cursor.fetchone()[0]
            cursor.execute("INSERT INTO comment(user_id,tweet_id , content) VALUES (?,?,?)", [user_id, tweet_id, content])
            conn.commit()
            rows = cursor.rowcount
            commentId = cursor.lastrowid
            cursor.execute("SELECT created_at FROM comment WHERE id=?", [commentId])
            created_at = cursor.fetchone()[0]
            conn.commit()
        except Exception as error:
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                comment = {
                    "commentId": commentId,
                    "tweetId": tweet_id, 
                    "userId": user_id,
                    "username": username,
                    "content": content,
                    "created_at": created_at,
                }
                return Response (json.dumps(comment, default=str), mimetype="application/json", status="210")
            else:
                return Response("Look's like you F'd up! POST ERROR", mimetype="text/html", status=510)   
#COMMENT_PATCH##########################################################################################COMMENT_PATCH##################################
    
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        rows = None
        loginToken = request.json.get("loginToken")
        comment_id = request.json.get("commentId")
        content = request.json.get("content")
        comment = None
        try:
            conn = mariadb.connect(host = dbcreds.host, password = dbcreds.password, user = dbcreds.user, port = dbcreds.port, database = dbcreds.database)
            cursor = conn.cursor()
            cursor.execute ("SELECT user_id from user_session WHERE login_token =?", [loginToken])
            user_id = cursor.fetchone()[0]
            print(user_id)
            cursor.execute("UPDATE comment SET content = ? WHERE id = ? AND user_id", [content, comment_id, user_id])
            conn.commit()
            rows = cursor.rowcount
            if rows != None:
                cursor.execute("SELECT comment.*, user.username FROM user INNER JOIN comment ON user.id = comment.user_id WHERE comment.id = ?", [comment_id,])
                comment = cursor.fetchone()
                print(comment)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if (rows == 1):
                comment_dictionary = {
                    "commentId": comment[0],
                    "tweetId": comment[2],
                    "userId": comment[3],
                    "username": comment[4],
                    "content": comment[3],
                    "createdAt": comment[1]
                }
                return Response(json.dumps(comment_dictionary, default = str), mimetype = "application/json", status = 200)
            else:
                return Response("Something went wrong...please try again.", mimetype = "text/html", status = 500)
#COMMENT_DELETE######################################################################################################################
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        rows = None
        loginToken = request.json.get("loginToken")
        comment_id = request.json.get("commentId")
        try :
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            cursor.execute ("SELECT user_id from user_session WHERE login_token =?", [loginToken])
            user_id = cursor.fetchone()[0]
            cursor.execute("DELETE FROM comment WHERE user_id =? AND id=?", [user_id, comment_id])            
            conn.commit()
            rows = cursor.rowcount            
        except Exception as error:  
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
                return Response("Guess What?!? USER DELETED...", mimetype="application/json", status=220)
            else:
                return Response("Look's like you F'd up! DELETE ERROR", mimetype="text/html", status=520)   
#END OF @COMMENTS########################################################################################################################################    
#TWEET_LIKES_GET################################################################################TWEET_LIKES_GET#########################################################
@app.route('/api/tweet-likes', methods=['GET', 'POST', 'DELETE'])
def tweetlikes_endpoint():
    if request.method == 'GET':
        conn = None
        cursor = None
        tweet_id = request.args.get("tweetId")
        tweet_likes = None
        all_tweet_likes = None

        try :
            conn = mariadb.connect(host=dbcreds.host,password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if tweet_id != "" and tweet_id != None:
                cursor.execute("SELECT t.tweet_id, u.id, u.username FROM tweet_like t INNER JOIN user u ON t.user_id = u.id WHERE t.tweet_id =?",[tweet_id])   
            else:
                cursor.execute("SELECT t.tweet_id, u.id, u.username FROM tweet_like t INNER JOIN user u ON t.user_id = u.id ")
            tweet_likes =cursor.fetchall()
            print(tweet_likes)
        except Exception as error:  
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(tweet_likes != None):
                    all_tweet_likes = []
                    for tweet_like in tweet_likes:
                        user_data = {
                            "tweetId": tweet_like[0],
                            "userId": tweet_like[1],
                            "username": tweet_like[2]
                        }
                        
                        all_tweet_likes.append(user_data)
            return Response(json.dumps(all_tweet_likes, default=str), mimetype="application/json", status=205)
######################################################################################################################################
    elif request.method == 'POST':
        conn = None
        cursor = None
        tweet_id = request.json.get("tweetId")
        loginToken = request.json.get("loginToken")
        rows = None
        user_id = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor() 
            cursor.execute("SELECT user_id FROM user_session WHERE login_token =?", [loginToken])
            user_id = cursor.fetchone()[0]
            print(user_id)
            cursor.execute("INSERT INTO tweet_like(user_id, tweet_id) VALUES (?,?)", [user_id, tweet_id])
            # rows = cursor.rowcount
            # tweet_like = cursor.fetchall()
            # cursor.execute("SELECT created_at FROM tweet WHERE id=?", [tweetId])
            # created_at = cursor.fetchone()[0]
            conn.commit()
            rows=cursor.rowcount
        except Exception as error:
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
              
                return Response("Tweet offically liked!", mimetype="text/html", status=201)
            else:
                return Response("Look's like you F'd up! POST ERROR", mimetype="text/html", status=510)
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        tweet_id = request.json.get("tweetId")
        loginToken = request.json.get("loginToken")
        rows = None
        user_id = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor() 
            cursor.execute("SELECT user_id FROM user_session WHERE login_token =?", [loginToken])
            user_id = cursor.fetchone()[0]
            print(user_id)
            print(tweet_id)
            cursor.execute("DELETE FROM tweet_like WHERE user_id =? AND tweet_id=?", [user_id, tweet_id])
            conn.commit()
            rows=cursor.rowcount
        except Exception as error:
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
              
                return Response("Tweet LIKE offically deleted!", mimetype="text/html", status=204)
            else:
                return Response("Look's like you F'd up! POST ERROR", mimetype="text/html", status=510)

@app.route('/api/comment-likes', methods=['GET', 'POST', 'DELETE'])
def commentlikes_endpoint():
    if request.method == 'GET':
        conn = None
        cursor = None
        comment_id = request.args.get("commentId")
        comment_likes = None
        all_comment_likes = None

        try :
            conn = mariadb.connect(host=dbcreds.host,password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if comment_id != "" and comment_id != None:
                cursor.execute("SELECT c.comment_id, u.id, u.username FROM comment_like c INNER JOIN user u ON c.user_id = u.id WHERE c.comment_id =?",[comment_id])   
            else:
                cursor.execute("SELECT c.comment_id, u.id, u.username FROM comment_like c INNER JOIN user u ON c.user_id = u.id")
            comment_likes =cursor.fetchall()
            print(comment_likes)
        except Exception as error:  
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(comment_likes != None):
                    all_comment_likes = []
                    for comment_like in comment_likes:
                        user_data = {
                            "commentId": comment_like[0],
                            "userId": comment_like[1],
                            "username": comment_like[2]
                        }
                        
                        all_comment_likes.append(user_data)
            return Response(json.dumps(all_comment_likes, default=str), mimetype="application/json", status=205)
######################################################################################################################################
    elif request.method == 'POST':
        conn = None
        cursor = None
        comment_id = request.json.get("commentId")
        loginToken = request.json.get("loginToken")
        rows = None
        user_id = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor() 
            cursor.execute("SELECT user_id FROM user_session WHERE login_token =?", [loginToken])
            user_id = cursor.fetchone()[0]
            print(user_id)
            cursor.execute("INSERT INTO comment_like(user_id, comment_id) VALUES (?,?)", [user_id, tweet_id])
            # rows = cursor.rowcount
            # tweet_like = cursor.fetchall()
            # cursor.execute("SELECT created_at FROM tweet WHERE id=?", [tweetId])
            # created_at = cursor.fetchone()[0]
            conn.commit()
            rows=cursor.rowcount
        except Exception as error:
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
              
                return Response("comment offically liked!", mimetype="text/html", status=201)
            else:
                return Response("Look's like you F'd up! POST ERROR", mimetype="text/html", status=510)
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        comment_id = request.json.get("commentId")
        loginToken = request.json.get("loginToken")
        rows = None
        user_id = None
        try:
            conn = mariadb.connect(host=dbcreds.host, password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor() 
            cursor.execute("SELECT user_id FROM user_session WHERE login_token =?", [loginToken])
            user_id = cursor.fetchone()[0]
            print(user_id)
            print(tweet_id)
            cursor.execute("DELETE FROM comment_like WHERE user_id =? AND comment_id=?", [user_id, comment_id])
            conn.commit()
            rows=cursor.rowcount
        except Exception as error:
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(rows == 1):
              
                return Response("Comment LIKE offically deleted!", mimetype="text/html", status=204)
            else:
                return Response("Look's like you F'd up! POST ERROR", mimetype="text/html", status=510)
#FOLLOWS_GET################################################################################################################################
@app.route('/api/user_follows', methods=['GET', 'POST', 'DELETE'])
def follows_endpoint():
    if request.method == 'GET':
        conn = None
        cursor = None
        user_id = request.args.get("userId")

        try :
            conn = mariadb.connect(host=dbcreds.host,password=dbcreds.password, user=dbcreds.user, port=dbcreds.port, database=dbcreds.database)
            cursor = conn.cursor()
            if user_id != "" and user_id != None:
                cursor.execute("SELECT u.user_id, u.id, u.username, u.bio, u.email FROM user_follows uf INNER JOIN user u ON user u ON u.id = uf.user_id =?,"[user_id])  
            else:
                cursor.execute("SELECT u.user_id, u.id, u.username, u.bio, u.email FROM user_follows uf INNER JOIN user u ON user u = u.id ")
            tweet_likes =cursor.fetchall()
            print(user_id)
        except Exception as error:  
            print("Sorry you're F'ed.  Internal error and I'm too lazy to log further. HA.")
            print(error)
        finally:
            if(cursor != None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if(user_id != None):
                    user_follows = []
                    for user_follow in user_follows:
                        user_data = {
  "                     "userId": userId,
                        "email": 
                        "username": "TheLorax",
                        "bio": "I am the Lorax, I speak for the trees",
                        "birthdate": "1971-06-23"                           
                        }
                        
                        all_tweet_likes.append(user_data)
            return Response(json.dumps(all_tweet_likes, default=str), mimetype="application/json", status=205)
    


            

