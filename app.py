# import library flask dkk 
from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api 
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy 
from functools import wraps

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

# konfigurasi secret key 
app.config['SECRET_KEY'] = "inirahasianegara"

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

# membuat decorator
def butuh_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.args.get('datatoken') # http://127.0.0.1:5000/api/blog?datatoken=fkjsldkjflskdjflskd
        if not token:
            return make_response(jsonify({"msg":"Token nggak ada bro !"}), 401)
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return make_response(jsonify({"msg":"Token nggak bener bro / invalid"}), 401)
        return f(*args, **kwargs)
    return decorator

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

        # cek username dan password 
        queryUsername = [data.username for data in AuthModel.query.all()]
        queryPassword = [data.password for data in AuthModel.query.all()]
        if dataUsername in queryUsername and dataPassword in queryPassword :
            # klo login sukses
            # generate token authentikasi untuk user
            token = jwt.encode(
                {
                    "username":queryUsername, "exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
                }, app.config['SECRET_KEY'],  algorithm="HS256"
            )
            return make_response(jsonify({"msg":"Login Sukses", "token":token}), 200)

        # klo login gagal
        return jsonify({"msg":"Login gagal, silahkan coba lagi !!!"})


# membuat endpoint untuk posting artikel baru bagi user yang sudah teregistrasi
# endpoint ini akan diprotect 
class TambahArtikel(Resource):
    # akan diproteksi
    @butuh_token
    def post(self):
        # tambah data artikel blog baru ke dalam database BlogModel
        dataJudul = request.form.get('judul')
        dataKonten = request.form.get('konten')
        dataPenulis = request.form.get('penulis')
        
        data = BlogModel(judul=dataJudul, konten=dataKonten, penulis=dataPenulis)
        db.session.add(data)
        db.session.commit()
        return{"msg":"Artikel berhasil ditambahkan !"}, 200

    # melihat semua artikel yang telah dibuat/publish
    # akan diproteksi
    @butuh_token
    def get(self):
        # query data dari database blogmodel (query semua datanya)
        dataQuery = BlogModel.query.all()
        # lakukan looping datanya ==> list comprehension 
        # list di dalamnya dict
        output = [
            {
                "id":data.id,
                "judul":data.judul,
                "konten":data.konten,
                "penulis":data.penulis
            } for data in dataQuery
        ] 

        return make_response(jsonify(output), 200)

# Routing untuk menghapus / mengedit data berdasarkan id 
class UpdateDataById(Resource):
    # mengedit data sehingga butuh parameter id
    @butuh_token
    def put(self, id):
        # query database berdasarkan id
        query = BlogModel.query.get(id)
        
        # get data dari form / multipart form (front end)
        dataJudul = request.form.get('judul')
        dataKonten = request.form.get('konten')
        dataPenulis = request.form.get('penulis')

        query.judul = dataJudul
        query.konten = dataKonten
        query.penulis = dataPenulis
        db.session.commit()
        return make_response(jsonify({"msg" : "Data berhasil di Update"}), 200)

    # delete data sehingga butuh parameter id (hapus satu data)
    @butuh_token
    def delete(self, id):
        # query database berdasarkan id
        query = BlogModel.query.get(id)
        db.session.delete(query)
        db.session.commit()
        return make_response(jsonify({"msg":"Data berhasil dihapus"}), 200)

    # view data berdasarkan id  (menampilkan satu buah data)
    @butuh_token
    def get(self, id):
        # query data berdasarkan id 
        query = BlogModel.query.get(id) # satu data saja ==> tidak perlu iterasi/looping
        output = {
            "id":query.id,
            "judul":query.judul,
            "konten":query.konten,
            "penulis":query.penulis
        }
        return make_response(jsonify(output), 200)

        
# inisiasi resource api 
api.add_resource(RegisterUser, "/api/register", methods=["POST"])
api.add_resource(LoginUser, "/api/login", methods=["POST"])
api.add_resource(TambahArtikel, "/api/blog", methods=["GET", "POST"])
api.add_resource(UpdateDataById, "/api/blog/<id>", methods=["PUT", "DELETE", "GET"])

# jalankan aplikasi app.py 
if __name__ == "__main__":
    app.run(debug=True)




