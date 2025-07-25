from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Numbers_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

class Number_validation(db.Model): #thru a class, we define a schema for the database
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(13), nullable=False)
    is_valid = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<Number {self.phone_number} - Valid: {self.is_valid}>'

@app.route("/", methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        phone_number = request.form.get("phone_number")
        if phone_number:
            Numbers_data = Number_validation(phone_number=phone_number, is_valid=True)
            db.session.add(Numbers_data)
            db.session.commit()
            return redirect(url_for("hello_world"))

    # For GET requests or if phone_number not provided, simply render the template
    return render_template("index.html")




@app.route("/products")
def products():
    return "This is the products page."

if __name__ == "__main__":
    app.run(debug=True,port=8000)

