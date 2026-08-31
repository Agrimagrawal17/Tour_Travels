from flask import Flask,render_template,request,redirect,url_for,session
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app=Flask(__name__)

app.secret_key=os.getenv("SECRET_KEY","this-is-secure-token-123456")

FASTAPI_URL=os.getenv("FASTAPI_URL")

@app.route("/health")
def backend_health():
    resp=requests.get(FASTAPI_URL+"health")
    return {"message":"Connected To backend ✅","Response":resp.json()}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup",methods=["GET","POST"])
def register():
    if request.method=="POST":
        data={
            "full_name":request.form.get("full_name"),
            "email":request.form.get("email"),
            "phone":request.form.get("phone"),
            "password":request.form.get("password")
        }
        
        response=requests.post(f"{FASTAPI_URL}auth/register",json=data)
        
        if response.status_code==200:
            return redirect(url_for("login"))
        
        
    return render_template("register.html")


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        data={
            "email":email,
            "password":password
        }
        
        try:
            response=requests.post(f"{FASTAPI_URL}auth/login",json=data,timeout=10)
            if response.status_code==200:
                result=response.json()
                
                session["access_token"]=result["access_token"]
                session["full_name"]=result["full_name"]
                print(result)
        
                if email.lower()=="aman@gmail.com":
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for("customer_dashboard"))
        except Exception as e:
            return str(e)
        
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/customers")
def customers():
    token = session.get("access_token")
    if not token:
        return redirect(url_for("login"))
    
    headers={
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response=requests.get(f"{FASTAPI_URL}users/",headers=headers,timeout=10)
        
        if response.status_code==200:
            customer=response.json()
            
            return render_template("customer_list.html",customer=customer)
        
        if response.status_code == 401:
            session.clear()
            return redirect(url_for("login"))
        
        if response.status_code==403:
            return redirect(url_for("home"))
        
        return render_template("customer_list.html",customer=[],error="Unable to fetch customers")
    
    except requests.RequestException:
        return render_template("customer_list.html",customer=[],error="Backend Server in not reachable")

@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/customer-dashboard")
def customer_dashboard():
    return render_template("customer_dashboard.html")

if __name__=="__main__":
    app.run(port=5000,debug=True)