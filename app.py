from flask import Flask, render_template, request, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import requests
import csv
import os
from io import StringIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Numbers_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api_key = "CC3A7AFC43DD4FE5A6EAC74684A48BAA"

class Number_validation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(13), nullable=False)
    Validity = db.Column(db.Boolean, nullable=False)
    Country_name = db.Column(db.String(50))
    Carrier = db.Column(db.String(50))

    def __repr__(self):
        return f'<Number {self.phone_number} - Valid: {self.Validity}>'

@app.route("/")
def home():
    return render_template("index.html", result=None, download_link=None)

@app.route("/", methods=["POST"])
def phone_check():
    result = None
    download_link = None
    phone_number = request.form.get("phone_number")
    if phone_number:
        url = f"https://api.veriphone.io/v2/verify?phone={phone_number}&key={api_key}"
        response = requests.get(url)
        data = response.json()
        Validity = data.get("phone_valid")
        if Validity is None:
            return "Invalid API Response/phone number.", 400
        new_entry = Number_validation(
            phone_number=phone_number,
            Validity=data.get("phone_valid"),
            Country_name=data.get("country"),
            Carrier=data.get("carrier")
        )
        db.session.add(new_entry)
        db.session.commit()
        result = new_entry
    return render_template("index.html", result=result, download_link=download_link)

@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    if "csv_file" not in request.files:
        return "No file uploaded.", 400
    file = request.files["csv_file"]
    if file.filename == '':
        return "No file selected.", 400

    filename = os.path.splitext(file.filename)[0]
    stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
    reader = csv.DictReader(stream)
    input_fieldnames = reader.fieldnames

    api_fields = ["Validity", "Country_name", "Carrier"]
    output_fieldnames = input_fieldnames + api_fields

    results = []

    for row in reader:
        phone_col = None
        for col in input_fieldnames:
            if "phone" in col.lower():
                phone_col = col
                break
        if not phone_col or not row.get(phone_col):
            for f in api_fields:
                row[f] = ''
            results.append(row)
            continue

        phone_number = row[phone_col]
        api_url = f"https://api.veriphone.io/v2/verify?phone={phone_number}&key={api_key}"
        try:
            response = requests.get(api_url, timeout=10)
            data = response.json()
            row["Validity"] = str(data.get("phone_valid", ""))
            row["Country_name"] = data.get("country", "")
            row["Carrier"] = data.get("carrier", "")
        except Exception:
            row["Validity"] = ''
            row["Country_name"] = ''
            row["Carrier"] = ''
        results.append(row)

    os.makedirs("uploads", exist_ok=True)
    result_filename = f"{filename}_results.csv"
    output_path = os.path.join("uploads", result_filename)

    output_csv = StringIO()
    writer = csv.DictWriter(output_csv, fieldnames=output_fieldnames)
    writer.writeheader()
    writer.writerows(results)

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        f.write(output_csv.getvalue())

    return render_template(
        "index.html",
        result=None,
        download_link=url_for("download_csv", filename=result_filename)
    )

@app.route("/download_csv/<filename>")
def download_csv(filename):
    file_path = os.path.join("uploads", filename)
    if not os.path.exists(file_path):
        return "File not found.", 404
    return send_file(file_path, as_attachment=True)

@app.route("/products")
def products():
    return "This is the products page."

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact-us")
def contact_us():
    return render_template("contact_us.html")

if __name__ == "__main__":
    app.run(debug=True, port=1000)
