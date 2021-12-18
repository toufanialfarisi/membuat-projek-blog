# import library flask dkk 
from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api 
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy 

# import library pendukung 
import jwt 
import os 
import datetime 

# inisialisasi objek flask dkk 
app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)
CORS(app)

# konfigurasi database ==> create file db.sqlite 
filename = os.path.dirname(os.path.abspath(__file__))
database = 'sqlite:///' + os.path.join(filename, 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database 

# membuat schema model database authentikasi (login, register)
class AuthModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))

# membuat schema model Blog 
class BlogModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(100))
    konten = db.Column(db.Text)
    penulis = db.Column(db.String(50))

# create model database ke dalam file db.sqlite
db.create_all()

# membuat routing endpoint 
# routing authentikasi 
class RegisterUser(Resource):
    # posting data dari front end untuk disimpan ke dalam database
    def post(self):
        dataUsername = request.form.get('username')
        dataPassword = request.form.get('password')

        # cek apakah username & password ada
        if dataUsername and dataPassword:
            # tulis data authentikasi ke db.sqlite
            dataModel = AuthModel(username=dataUsername, password=dataPassword)
            db.session.add(dataModel)
            db.session.commit()
            return make_response(jsonify({"msg":"Registrasi berhasil"}), 200)
        return jsonify({"msg":"Username / password tidak boleh kosong"})


# routing untuk authentikasi : login 
class LoginUser(Resource):
    def post(self):
        dataUsername = request.form.get('username')
        dataPassword = request.form.get('password')

        # query matching kecocokan data 
        # iterasi authModel 
        query = [data.username for data in AuthModel.query.all()]  # list comprehension
        if dataUsername in query :
            # klo login sukses
            return jsonify({"msg":"Login Sukses"})

        # klo login gagal
        return jsonify({"msg":"Login gagal, silahkan coba lagi !!!"})

# inisiasi resource api 
api.add_resource(RegisterUser, "/api/register", methods=["POST"])
api.add_resource(LoginUser, "/api/login", methods=["POST"])

# jalankan aplikasi app.py 
if __name__ == "__main__":
    app.run(debug=True)




