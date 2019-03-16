import os
import requests
from flask import Flask, session,render_template,url_for,request,jsonify,redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash,check_password_hash


app = Flask(__name__)

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

app.config["SECRET_KEY"]="geajknejqn"

@app.route("/")
def index():
    return redirect(url_for('login'))

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
            session["user"]=request.form.get("username")
            return redirect(url_for("search")) 
        else:
            return "wrong password"   
            
    else:
          return render_template("login.html",session=session)
    

@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect(url_for("login"))


@app.route("/register",methods=["GET","POST"])
def register():
    if user in session:
        return redirect(url_for("search"))
  
    elif(request.method=="POST"):
        if(not (request.form.get("username")) or not (request.form.get("password")) or not (request.form.get("cpassword"))):
            return "Apology nothing shoud be none"
        elif(not request.form.get("password")==request.form.get("cpassword")):
            return "passwords not same"
        hash=generate_password_hash(request.form.get("password"))

        user=db.execute("SELECT * FROM users where username=:username",{"username":request.form.get("username")}).fetchone()
        if user:
            return "duplicate"
        else:
            session["user"]=request.form.get("username")
            db.execute("INSERT INTO users(username,password)VALUES(:user,:hash)",{"user":request.form.get("username"),"hash":hash})
            db.commit()
            session["username"]=request.form.get("username")
            return redirect(url_for("search"))    
            
    else:
          return render_template("register.html",session=session)


    

@app.route("/search",methods=["GET","POST"])
def search():
     if user not in session:
             return redirect(url_for("login"))
     elif(request.method=="POST"):
            result=db.execute("SELECT * FROM books where isbn LIKE :q or title LIKE :q or author LIKE :q or year LIKE :q",{"q":'%'+request.form.get("search")+'%'}).fetchall()
            if result is None:
                return "NO MATCHES FOUND"
            else:
                return render_template("search.html",result=result)
     else:
             return  render_template("search.html",session=session)

@app.route("/book/<string:isbn>",methods=["GET","POST"])
def books(isbn):
    if user not in session:
        return redirect(url_for("login"))
    elif(request.method=="POST"):
        count=db.execute("SELECT * FROM reviews where id=:id and isbn=:isbn",{"id":session["user"],"isbn":isbn}).fetchone()
        if count is None: 
            db.execute("Insert into reviews(id,review,rating,isbn)VALUES(:id,:review,:rating,:isbn)",{"id":session["user"],"review":request.form.get("review"),"isbn":isbn,"rating":request.form.get("rating")})
            db.commit()
    result=db.execute("SELECT * FROM books where isbn=:isbn",{"isbn":isbn}).fetchone()
    print(session["user"])
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "XGwRVb91C7ZSmbwNetIg", "isbns": isbn}).json()
    review=db.execute("SELECT review,rating from reviews where isbn=:isbn",{"isbn":isbn}).fetchall()
    return  render_template("books.html",result=result,res=res,review=review,session=session)

@app.route("/api/<string:isbn>")
def api(isbn):
    result=db.execute("SELECT * FROM books where isbn=:isbn",{"isbn":isbn}).fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "XGwRVb91C7ZSmbwNetIg", "isbns": isbn}).json()
    return jsonify(
            title=result.title,
            author=result.author,
            year=result.year,
            isbn=result.isbn,
            review_count=res["books"][0]["work_ratings_count"],
            average_score=res["books"][0]["average_rating"]
    )