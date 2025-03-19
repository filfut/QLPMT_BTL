import hashlib
import json
from QLPMT import db, app
from models import MedicineType, Medicine, User


def load_medicine_type():
    return MedicineType.query.all()


def add_user(name, username, password, avatar):
    u = User(name=name, username=username, password=str(hashlib.md5(password.encode('utf-8')).hexdigest()),
             avatar=avatar)
    db.session.add(u)
    db.session.commit()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def count_medicine():
    return Medicine.query.count()


def auth_user(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username), User.password.__eq__(password)).first()


def load_medicines(q=None, med_type_id=None, page=None):

    query = Medicine.query
    if q:
        query = query.filter(Medicine.name.contains(q))
    if med_type_id:
        query = query.filter(Medicine.med_type_id.__eq__(med_type_id))

    if page:
        size = app.config["PAGE_SIZE"]
        start = (int(page) - 1) * size
        query = query.slice(start, start + size)

    return query.all()


def get_medicine_by_id(id):
    return Medicine.query.get(id)

def get_user_by_username(username):
    """Trả về thông tin người dùng dựa trên username."""
    return User.query.filter_by(username=username).first()

if __name__ == "__main__":
    with app.app_context():
        print(get_user_by_username('admin'))
