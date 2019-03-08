import os

from flask import Flask, session,render_template,url_for,request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash,check_password_hash


app = Flask(__name__)
app.secret_key='b17nvd^nksc'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("layout.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if(request.method=="POST"):
        if(not (request.form.get("username")) or not (request.form.get("password"))):
            return "Apology nothing shoud be none"
        user=db.execute("SELECT * FROM users where username=:username",{"username":request.form.get("username")}).fetchone()
        if not user:
            return "username not found"
    
        hash=db.execute("SELECT password FROM users WHERE username=:username",{"username":request.form.get("username")}).fetchone()
        
        if(check_password_hash(hash["password"],request.form.get("password"))):
            return "success" 
        else:
            return "wrong password"   
            
    else:
          return render_template("login.html")
    
  

@app.route("/register",methods=["GET","POST"])
def register():
  
    if(request.method=="POST"):
        if(not (request.form.get("username")) or not (request.form.get("password")) or not (request.form.get("cpassword"))):
            return "Apology nothing shoud be none"
        elif(not request.form.get("password")==request.form.get("cpassword")):
            return "passwords not same"
        hash=generate_password_hash(request.form.get("password"))

        user=db.execute("SELECT * FROM users where username=:username",{"username":request.form.get("username")}).fetchone()
        if user:
            return "duplicate"
        else:
            db.execute("INSERT INTO users(username,password)VALUES(:user,:hash)",{"user":request.form.get("username"),"hash":hash})
            db.commit()
            session["username"]=request.form.get("username")
            return "success"    
            
    else:
          return render_template("register.html")
