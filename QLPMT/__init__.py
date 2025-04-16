from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary
<<<<<<< HEAD
from flask_session import Session
from datetime import timedelta

=======
>>>>>>> 27697c343ee30c5ae7c35f759fb58dd33fa43f29

app = Flask(__name__)

app.secret_key = "%$@%^@%#^VGHGD"
<<<<<<< HEAD
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Admin123@localhost/qlpmtdb?charset=utf8mb4"
=======
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Admin123@localhost/qlpmt_db?charset=utf8mb4"
>>>>>>> 27697c343ee30c5ae7c35f759fb58dd33fa43f29
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

app.config["PAGE_SIZE"] = 8

db = SQLAlchemy(app)
login = LoginManager(app)

<<<<<<< HEAD
cloudinary.config(cloud_name='dwrl7e8y8',
    api_key='599816851137843',
    api_secret='mizIuXGyAzGvcBg4DI8Fnxd4Wu8')

# Cấu hình Session
app.config['SESSION_TYPE'] = 'filesystem'  # Lưu session trong hệ thống file
app.config['SESSION_PERMANENT'] = False   # Session không lưu dài hạn
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Session tồn tại trong 1 giờ
Session(app)  # Khởi tạo session

=======
cloudinary.config(cloud_name='dy1unykph',
                  api_key='238791983534257',
                  api_secret='_J2MkfDJ1DwRe1uAn5TKozXup0U')
>>>>>>> 27697c343ee30c5ae7c35f759fb58dd33fa43f29
