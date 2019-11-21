from flask import Flask,flash,request,jsonify,json,redirect, render_template,url_for,session
import pymysql
import requests
from flask_cors import CORS

import os
#import magic
import urllib.request
# from app import app
from werkzeug.utils import secure_filename

import re
import string
import math
import json
import time
import threading


app=Flask(__name__)
CORS(app)
#session key has to  be set other wise files wont be uploaded.
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] ='./static'

db=pymysql.connect('127.0.0.1','root','',"blog")
# cursor=db.cursor()

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
cursor=db.cursor()
cursor.execute('set global max_allowed_packet=67108864')
cursor.close()
db.close()

blog_column=["id","send_email","subject","body","date","likes","dislikes","category_id"]
blogger_column=["id","email"]
comment_column=["id","bid","send_email","recv_email","body","date"]
subscribe_colummn=["rev_email","blogger_email"]
user_column=["email","username","password","phonenumber","blockstate"]

@app.route("/")
def redirect_login():
	session["previous_mails"]=[]
	return render_template("login.html")

@app.route("/create_account")
def redirect_create_account():
	return render_template("create_account.html")

@app.route("/home")
def redirect_home():
	return  render_template("home.html")

@app.route("/compose")
def compose():
	return render_template("compose.html")

#200-success #400-login failed.
@app.route("/login",methods=['POST'])
def login():
	db=pymysql.connect('127.0.0.1','root','',"blog")
	cursor=db.cursor()
	email=request.form['email']
	password=request.form['password']
	print(email,password)
	sql="select * from user where email='%s' and password='%s';"%(email,password)
	if(cursor.execute(sql)>0):
		
		print("user and password matched")
		resp=jsonify()
		resp.status_code=200
		cursor.close()
		db.close()
		return resp
	else:
		resp=jsonify(["login-failed"])
		resp.status_code=400
		cursor.close()
		db.close()
		return resp

@app.route("/signup",methods=['POST','GET'])
def signup():
	if(request.method=="POST"):
		username=request.form['username']
		password=request.form["password"]
		email=request.form["email"]
		print(username,password,email)
		db=pymysql.connect('127.0.0.1','root','',"blog")
		cursor=db.cursor()
		sql="insert into user(email,username,password) values('%s','%s','%s')"%(email,username,password)
		if(cursor.execute(sql)>0):
			print("sign-up successful")
		db.commit()
		cursor.close()
		db.close()
		return render_template("home.html")
		# message={}
		# resp=jsonify(message)
		# resp.status_code=200
		# return resp
	elif(request.method=="GET"):
		#checking if the email already exists or not.
		email=request.args["email"]
		db=pymysql.connect('127.0.0.1','root','',"blog")
		cursor=db.cursor()
		sql="select * from user where email='%s'"%(email)
		resp=""
		if(cursor.execute(sql)>0):
			
			resp=jsonify({})
			resp.status_code=400
		else:

			resp=jsonify({})
			resp.status_code=200
		cursor.close()
		db.close()
		return resp

	else:
		pass


#function to get all the emails received by a user.
#200-success|400-failure
@app.route("/getData/<email>",methods=['GET'])
def getData(email):
	print(email)
	#query to extract all the emails received
	db=pymysql.connect('127.0.0.1','root','',"blog")
	cursor=db.cursor()
	sql="select id,send_email,recv_email,subject,body,date,spam,star from email where recv_email='%s' or send_email='%s' order by date desc"%(str(email),str(email))
	cursor.execute(sql)
	rows=cursor.fetchall()
	resp=jsonify()
	message=[]
	
	if(len(rows)>0):
		# print(type(rows))
		for each_mail in rows:
			message.append(dict(zip(email_column,each_mail)))
			
		resp.status_code=200
	else:
		resp.status_code=400
	#print(message)
	resp=jsonify(message)
	
	cursor.close()
	db.close()
	return resp


@app.route("/redirect_display_mail")
def rediret_display_mail():
	return render_template("display_mail.html")

#get all blogger
@app.route("/get_bloggers",methods=["GET"])
def get_blogger():
	db=pymysql.connect('127.0.0.1','root','',"blog")
	cursor=db.cursor()
	sql="select * from blogger"
	if(cursor.execute(sql)):
		rows=cursor.fetchall()
	else:
		rows=[]
	
	if(len(rows)>0):
		message=[]
		for blogger in  rows:
			message.append(dict(zip(blogger_column,blogger)))
		print(message)
		resp=jsonify(message)
		resp.status_code=200
		
	else:
		resp=jsonify()
		resp.status_code=400
	cursor.close()
	db.close()
	return resp

@app.route("/subscribeToBlog/<email>/<blogger_email>",methods=["POST"])
def subscribeToBlog(email,blogger_email):
	print(email)
	# blogger_email=request.form["bloggers"]
	print(blogger_email)
	db=pymysql.connect('127.0.0.1','root','',"blog")
	cursor=db.cursor()
	sql="select * from subscribe where recv_email='%s' and blogger_email='%s'"%(email,blogger_email)
	resp=" "
	if(cursor.execute(sql)):
		resp=jsonify()
		resp.status_code=400
	else:
		sql="insert into subscribe(recv_email,blogger_email) values('%s','%s')"%(email,blogger_email)
		cursor.execute(sql)
		db.commit()
		resp=jsonify()
		resp.status_code=200
		
	cursor.close()
	db.close()
	return resp


#get a specific mail used to display mail in a new window.
@app.route("/display_mail/<mid>",methods=["GET"])
def display_mail(mid):
	print(mid)
	#query to extract all the emails received
	db=pymysql.connect('127.0.0.1','root','',"blog")
	cursor=db.cursor()
	sql="select * from blog where id='%s'"%(mid)
	if(cursor.execute(sql)):
		rows=cursor.fetchall()
	else:
		rows=[]
	
	if(len(rows)>0):
		message=[]
		for each_mail in  rows:
			message.append(dict(zip(blog_column,each_mail)))
		resp=jsonify(message)
		resp.status_code=200
		
	else:
		resp=jsonify()
		resp.status_code=400
	cursor.close()
	db.close()
	return resp
	


@app.route("/edit_blog")
def edit_blog():
	return render_template("edit_blog.html")

@app.route("/update_blog/<bid>",methods=["POST"])
def update_blog(bid):
	db=pymysql.connect('127.0.0.1','root','',"blog")
	cursor=db.cursor()
	req_data=request.get_json()
	
	sql="select * from blog where id=%d"%(int(bid))
	if(cursor.execute(sql)==0):
		resp=jsonify()
		resp.status_code=400
		cursor.close()
		db.close()
		return resp
	sql="update blog set subject='%s',body='%s' where id=%d"%(req_data["subject"],req_data["body"],int(bid))
	if(cursor.execute(sql)>0):
		print("blog sent")
	db.commit()
	
	resp=jsonify({})
	resp.status_code=200
	cursor.close()
	db.close()
	return resp
#use longpooling to get the latest mails.
@app.route("/getData/<email>/latest",methods=['GET'])
def getLatestData(email):
	if("previous_mails" not in session):
		session["previous_mails"]=list()
		session.modified=True
	db=pymysql.connect('127.0.0.1','root','',"blog")
	cursor=db.cursor()
	for _ in range(3):
		
		sql='''select * from blog where send_email in 
			(select blogger_email from subscribe where recv_email='%s')'''%(email)
		print(cursor.execute(sql))
		data=cursor.fetchall()
		message=[]
		for each_mail in data:
			message.append(dict(zip(blog_column,each_mail)))
		data=message
		# message_to_be_sent=[]
		# for ele in data:
		# 	if(ele not in  session["previous_mails"]):
		# 		message_to_be_sent.append(ele)
		# print(len(message_to_be_sent))
		#session["previous_mails"].extend(message_to_be_sent)
		session.modified=True
		# resp=jsonify(message_to_be_sent)
		resp=jsonify(message)
		# if(len(message_to_be_sent)>0):
		# 	resp.status_code=200
		# 	cursor.close()
		# 	db.close()
		# 	return resp
		if(len(message)>0):
			resp.status_code=200
			cursor.close()
			db.close()
			return resp
		time.sleep(3)
	resp=jsonify()
	resp.status_code=400
	cursor.close()
	db.close()
	return resp


@app.route("/like/<bid>/<email>",methods=["GET"])
def like(bid,email):
	print(bid)
	print(email)
	db=pymysql.connect('127.0.0.1','root','',"blog")
	cursor=db.cursor()
	sql="select * from likes where email='%s' and bid=%d"%(email,int(bid));
	if(cursor.execute(sql)):
		resp=jsonify()
		resp.status_code=400
		cursor.close()
		db.close()
		return resp

	sql="select likes from blog where id=%d"%(int(bid))
	cursor.execute(sql);
	likes=int(cursor.fetchone()[0])
	print(likes)
	
	sql="update blog set likes=%d where id=%d"%(likes+1,int(bid))
	cursor.execute(sql)
	db.commit()
	sql="insert into likes(email,bid) values('%s',%d)"%(email,int(bid))
	if(cursor.execute(sql)):
		db.commit()
		print("like incremented")
		db.commit()
		resp=jsonify({})
		resp.status_code=200
		cursor.close()
		db.close()
		return resp
	else:
		db.commit()
		resp=jsonify({})
		resp.status_code=400
		cursor.close()
		db.close()
		return resp

@app.route("/dislike/<bid>/<email>",methods=["GET"])
def dislike(bid,email):
	print(bid)
	print(email)
	db=pymysql.connect('127.0.0.1','root','',"blog")
	cursor=db.cursor()
	sql="select * from dislikes where email='%s' and bid=%d"%(email,int(bid))
	if(cursor.execute(sql)):
		resp=jsonify()
		resp.status_code=400
		cursor.close()
		db.close()
		return resp
	sql="select dislikes from blog where id=%d"%(int(bid))
	cursor.execute(sql);
	dislikes=int(cursor.fetchone()[0])
	print(dislikes)
	sql="update blog set dislikes=%d where id=%d"%(dislikes+1,int(bid))
	cursor.execute(sql)
	db.commit()
	sql="insert into dislikes(email,bid) values('%s',%d)"%(email,int(bid))
	if(cursor.execute(sql)>0):
		print("dislike incremented")
		db.commit()
		resp=jsonify({})
		resp.status_code=200
		cursor.close()
		db.close()
		return resp
	else:
		db.commit()
		resp=jsonify({})
		resp.status_code=400
		cursor.close()
		db.close()
		return resp
	



@app.route("/reply",methods=["POST","GET"])
def add__get_reply():
	if(request.method=="POST"):
		
		print(request.form)
		# genereating id
		id_=0
		db=pymysql.connect('127.0.0.1','root','',"blog")
		cursor=db.cursor()
		sql="select max(id) from comment"
		try:
			if(cursor.execute(sql)>0):
				id_=int(cursor.fetchone()[0])+1
		except:
			pass
		sql='''insert into comment(id,bid,send_email,body) 
				values('%s','%s','%s','%s')'''%(id_,request.form["mid"],request.form["send_email"],request.form["body"])
		if(cursor.execute(sql)>0):
			print("reply sent")
		db.commit()
		resp=jsonify({})
		resp.status_code=200
		cursor.close()
		db.close()
		return resp
	elif(request.method=="GET"):
		db=pymysql.connect('127.0.0.1','root','',"blog")
		cursor=db.cursor()
		mid=int(request.args["mid"])
		reply_id=request.args["id"]
		for i in  range(3):
			sql=" "
			if(reply_id=="null"):
				print("here1")
				sql="select * from comment where bid=%d order by date"%(mid)
			else:
				print("herer2")
				sql="select * from comment where bid=%d and id>%d order by date"%(mid,int(reply_id))
			
			if(cursor.execute(sql)>0):

				data=cursor.fetchall()
				message=[]
				for each_reply in  data:
					message.append(dict(zip(comment_column,each_reply)))
				resp=jsonify(message)
				resp.status_code=200
				cursor.close()
				db.close()
				return resp
			else:
				time.sleep(2)

		resp=jsonify({})
		resp.status_code=400
		cursor.close()
		db.close()
		return  resp
	else:
		resp=jsonify({})
		resp.status_code=400
		cursor.close()
		db.close()
		return resp


	


#send email
@app.route("/compose_send",methods=["POST"])
def compose_send():
	db=pymysql.connect('127.0.0.1','root','',"blog")
	cursor=db.cursor()
	req_data=request.get_json()
	#print(req_data)
	# genereating id 
	
	#making the user a blogger
	sql="select * from  blogger where email='%s'"%(req_data["send_email"])
	if(cursor.execute(sql)==0):
		sql="insert into blogger(email) values('%s')"%(req_data["send_email"])
		cursor.execute(sql)
		db.commit()
	id_=0
	sql="select max(id) from blog"
	try:
		if(cursor.execute(sql)>0):
			id_=int(cursor.fetchone()[0])+1
	except:
		pass
	sql="insert into blog(id,send_email,subject,body) values(%s,'%s','%s','%s')"%(id_,req_data["send_email"],req_data["subject"],req_data["body"])
	if(cursor.execute(sql)>0):
		print("blog sent")
	db.commit()
	
	resp=jsonify({})
	resp.status_code=200
	cursor.close()
	db.close()
	return resp

@app.route("/delete_mail/<mid>",methods=["DELETE"])
def delete_mail(mid):
	print("in delete mail method")
	db=pymysql.connect('127.0.0.1','root','',"blog")
	cursor=db.cursor()
	mail_id=mid
	print("deleting"+mail_id)
	sql="delete from spam_check_log where id=%d"%(int(mail_id))
	
	if(cursor.execute(sql)>0):
		print("deleted from spam_check_log")
		db.commit()
	else:
		pass
	sql="delete from reply where mid=%d"%(int(mail_id))
	cursor.execute(sql)
	db.commit()
	sql="delete from email where id=%d"%(int(mail_id))
	if(cursor.execute(sql)>0):
		print("mail deleted from email table")
		db.commit()
		resp=jsonify({})
		resp.status_code=200
		cursor.close()
		db.close()
		return  resp
	else:
		resp=jsonify({})
		resp.status_code=400
		cursor.close()
		db.close()
		return  resp
	
#function to star or un-star a mail
@app.route("/star/<mid>",methods=["GET"])
def star(mid):
	print(mid)
	db=pymysql.connect('127.0.0.1','root','',"blog")
	cursor=db.cursor()
	sql='''update email set star=	CASE  
									when star=1 then 0
									when star=0 then 1
									end
			where id=%s'''%(mid)
	resp=jsonify()
	if(cursor.execute(sql)>0):
		print("mail stared/un-stared")
		db.commit()
		resp.status_code=200
		cursor.close()
		db.close()
		return  resp
	else:
		resp.status_code=400
		cursor.close()
		db.close()
		return resp

#function to set spam 
@app.route("/spam/<mid>",methods=["GET"])
def spam(mid):
	db=pymysql.connect('127.0.0.1','root','',"blog")
	cursor=db.cursor()
	print(mid)
	sql='''update email set spam=	CASE  
									when spam=1 then 0
									when spam=0 then 1
									end
			where id=%s'''%(mid)
	resp=jsonify()
	if(cursor.execute(sql)>0):
		print("mail spam/un-unspam")
		db.commit()
		resp.status_code=200
		cursor.close()
		db.close()
		return  resp
	else:
		cursor.close()
		db.close()
		resp.status_code=400
		return resp


#checkc whether a mail is read or not
@app.route("/email_read/<mid>/<email>",methods=["GET","POST"])
def email_read(mid,email):

	if(request.method=="GET"):
		#chekc who has sent the mail to whome
		db=pymysql.connect('127.0.0.1','root','',"blog")
		cursor=db.cursor()
		sql="select * from email where id=%s"%(int(mid));
		if(cursor.execute(sql)>0):
			data=cursor.fetchall()[0]
			message=dict(zip(email_column,data))
			data=message
			if(email==data["recv_email"]):
				message=[data["recv_eread"]]
			else:
				message=[data["send_eread"]]
				#check whether the receiver has read the email or not
			resp=jsonify(message)
			resp.status_code=200
			cursor.close()
			db.close()
			return resp
		else:
			cursor.close()
			db.close()
			resp=jsonify()
			resp.status_code=400
			return resp
	elif(request.method=="POST"):
		#the receivers email/ whoever is viewing the mail has to be methioned in the route 
		db=pymysql.connect('127.0.0.1','root','',"blog")
		cursor=db.cursor()
		sql="select * from email where id=%d"%(int(mid));
		
		if(cursor.execute(sql)>0):
			data=cursor.fetchall()[0]
			message=dict(zip(email_column,data))
			data=message
			sql=" "
			if(email==data["recv_email"]):
				sql="update email set recv_eread=1 where recv_email='%s' and id=%d"%(email,int(mid));
			else:
				sql="update email set send_eread=1 where send_email='%s' and id=%d"%(email,int(mid));

			resp=" "
			
			if(cursor.execute(sql)>0):
				resp=jsonify()
				db.commit()

				resp.status_code=200
				
			else:
				resp=jsonify()
				resp.status_code=400
			
			cursor.close()
			db.close()
			return resp
		else:
			resp=jsonify()
			resp.status_code=400
			cursor.close()
			db.close()
			return resp

	else:
		pass


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS	

@app.route('/editor', methods=['POST'])
def upload_file():
	# print("here")
	message={}
	resp=jsonify(message)
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			print('No file part')
			resp.status_code=400
			return resp
		file = request.files['file']
		if file.filename == '':
			print('No file selected for uploading')
			resp.status_code=400
			return resp
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file_path=app.config['UPLOAD_FOLDER']+"/"+filename
			print(file_path)
			file.save(file_path)
			print('File successfully uploaded')
			message=[file_path]
			resp=jsonify(message)
			resp.status_code=200
			return resp
		else:
			print('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
			resp.status_code=400
			return resp

def spam_check():
	for _ in range(10):
		db=pymysql.connect('127.0.0.1','root','',"blog")
		cursor=db.cursor()
		print("Spam check active")
		sql="select * from spam_check_log"
		if(cursor.execute(sql)>0):
			data=cursor.fetchall()
			ids=[ele[0] for ele in data]
			# ids=list(cursor.fetchall()[0].values())
			sql="select id,subject,body from  email where id in (%s)"%(','.join(list(map(str,ids))))
			if(len(ids)>0 and cursor.execute(sql)>0):
				data=cursor.fetchall()
				message=[]
				for each_mail in data:
					message.append(dict(zip(["id","subject","body"],each_mail)))
				data=message
				data_list=list()
				#order of ids
				ids=list()
				for ele in data:
					#print(ele)
					ids.append(ele['id'])
					data_list.append("Subject:{}\n{}".format(ele["subject"],ele["body"]))

				#checking whether the mailes are spam or not.
				labels=predict(data_list)
				print("labels {}".format(labels))
				spam_id=[val for i,val in enumerate(ids) if labels[i]==1]
				sql="update email set spam=1 where id in ('%s')"%(','.join(list(map(str,spam_id))))
				if(cursor.execute(sql)>0):
					print("spam set")
				db.commit()

				
				#deleting entires from  spma_check_log file
				sql="delete from spam_check_log where id in ('%s')"%(','.join(list(map(str,spam_id))))
				if(cursor.execute(sql)>0):
					print("log cleared")
				db.commit()
		else:
			print("EMPTY LOG")
		cursor.close()
		time.sleep(10)
		print("Spam check done")
		db.close()
		return 


# t=threading.Thread(target=spam_check)
# t.start()
app.run(debug=True,host="0.0.0.0",port=1000)
