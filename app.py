from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Numbers_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

api_key="C92F0A5B17794E88A8C837331C0BCFAB"


class Number_validation(db.Model): #thru a class we create a schema for our database
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(13), nullable=False)
    is_valid = db.Column(db.Boolean, nullable=False)
    country_name = db.Column(db.String(50))
    carrier = db.Column(db.String(50))
    line_type = db.Column(db.String(50))

    def __repr__(self):
        return f'<Number {self.phone_number} - Valid: {self.is_valid}>'


@app.route("/", methods=["GET", "POST"])
def hello_world():
    result=None
    if request.method == "POST":
        phone_number = request.form.get("phone_number")
        if phone_number:
            url = f"https://api.veriphone.io/v2/verify?phone={phone_number}&key={api_key}"
            response = requests.get(url)
            data= response.json()

            is_valid=data.get("phone_valid") 
            if is_valid is None:
                return "Invalid API Response/phone number.", 400  # Default to False if not present
            
            new_entry=Number_validation(
                    phone_number=phone_number,
                    is_valid=data.get("phone_valid"),
                    country_name=data.get("country"),
                    carrier=data.get("carrier"), 
                    line_type=data.get("line_type") or "unknown"
                )     
            db.session.add(new_entry)
            db.session.commit()
            result=new_entry
            #return redirect(url_for("hello_world"))

    # render template with result/and even if no phn number is entered
    return render_template("index.html",result=result)


@app.route("/products")
def products():
    return "This is the products page."

if __name__ == "__main__":
    app.run(debug=True,port=8000)

