import hashlib
<<<<<<< HEAD
from datetime import date

from QLPMT import db, app
from models import User, MedicineType, Medicine, Appointment, Receipt, ReceiptDetail, MedicalRecord, AppointmentStatus
from flask_login import current_user
from sqlalchemy import func


# Load danh mục loại thuốc
def load_medicine_types():
    return MedicineType.query.all()


# Thêm người dùng
def add_user(name, email, password, avatar=None, role=1, gender=1, birth_date=None, address=None, phone=None):
    """
    Thêm một người dùng mới vào cơ sở dữ liệu.

    Args:
        name (str): Họ tên người dùng.
        email (str): Email của người dùng.
        password (str): Mật khẩu người dùng (chưa mã hóa).
        avatar (str): Đường dẫn hình đại diện (nếu có).
        role (int): Vai trò người dùng (mặc định là bệnh nhân - 1).
        gender (int): Giới tính của người dùng (1: Nam, 2: Nữ, 3: Khác). Mặc định là 1 (Nam).
        birth_date (date): Ngày sinh của người dùng (nếu có). Mặc định là None.
        address (str): Địa chỉ của người dùng (nếu có). Mặc định là None.
        phone (str): Số điện thoại của người dùng (nếu có). Mặc định là None.
    """
    hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()

    # Tạo đối tượng người dùng với các giá trị mặc định
    user = User(
        name=name,
        email=email,
        password=hashed_password,
        avatar=avatar,
        role=role,
        gender=gender,
        birth_date=birth_date,
        address=address,
        phone=phone
    )

    db.session.add(user)
    db.session.commit()


# Lấy người dùng theo ID
=======
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


>>>>>>> 27697c343ee30c5ae7c35f759fb58dd33fa43f29
def get_user_by_id(user_id):
    return User.query.get(user_id)


<<<<<<< HEAD
def auth_user(email, password):
    """
    Xác thực người dùng bằng email và mật khẩu.
    """
    hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()
    return User.query.filter(User.email == email, User.password == hashed_password).first()

# Kiểm tra email đã tồn tại
def is_email_taken(email):
    """
    Kiểm tra xem email đã tồn tại trong cơ sở dữ liệu chưa.
    """
    return User.query.filter_by(email=email).first() is not None


# Lấy danh sách thuốc với bộ lọc
def load_medicines(q=None, med_type_id=None, page=None):
=======
def count_medicine():
    return Medicine.query.count()


def auth_user(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username), User.password.__eq__(password)).first()


def load_medicines(q=None, med_type_id=None, page=None):

>>>>>>> 27697c343ee30c5ae7c35f759fb58dd33fa43f29
    query = Medicine.query
    if q:
        query = query.filter(Medicine.name.contains(q))
    if med_type_id:
<<<<<<< HEAD
        query = query.filter(Medicine.med_type_id == med_type_id)

    if page:
        size = app.config.get("PAGE_SIZE", 20)  # Giá trị mặc định nếu không thiết lập PAGE_SIZE
=======
        query = query.filter(Medicine.med_type_id.__eq__(med_type_id))

    if page:
        size = app.config["PAGE_SIZE"]
>>>>>>> 27697c343ee30c5ae7c35f759fb58dd33fa43f29
        start = (int(page) - 1) * size
        query = query.slice(start, start + size)

    return query.all()


<<<<<<< HEAD
# Lấy thuốc theo ID
def get_medicine_by_id(medicine_id):
    return Medicine.query.get(medicine_id)


# Đếm số lượng thuốc
def count_medicines():
    return Medicine.query.count()


# Đếm thuốc theo loại
def count_medicines_by_type():
    query = db.session.query(MedicineType.id, MedicineType.name, func.count(Medicine.id)) \
        .join(Medicine, Medicine.med_type_id == MedicineType.id, isouter=True).group_by(MedicineType.id)
    return query.all()


# Thống kê doanh thu theo thuốc
def stats_revenue_by_medicines(kw=None):
    query = db.session.query(Medicine.id, Medicine.name, func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price)) \
        .join(ReceiptDetail, ReceiptDetail.medicine_id == Medicine.id, isouter=True)

    if kw:
        query = query.filter(Medicine.name.contains(kw))

    return query.group_by(Medicine.id).all()


# Thêm hóa đơn
def add_receipt(cart, medical_record_id, employee_id):
    """
    Tạo hóa đơn từ giỏ hàng.
    """
    if cart:
        receipt = Receipt(medical_record_id=medical_record_id, employee_id=employee_id)
        db.session.add(receipt)

        for c in cart.values():
            detail = ReceiptDetail(quantity=c['quantity'], unit_price=c['price'],
                                   medical_record_id=medical_record_id, medicine_id=c['id'])
            db.session.add(detail)

        db.session.commit()


# Kiểm tra vai trò người dùng
def check_user_role(user_id, required_role):
    """
    Kiểm tra vai trò của người dùng.

    Args:
        user_id (int): ID của người dùng.
        required_role (int): Vai trò yêu cầu (số).

    Returns:
        bool: True nếu vai trò khớp, False nếu không.
    """
    user = get_user_by_id(user_id)
    return user.role == required_role if user else False

def update_user_info(user_id, name, email, gender, birth_date, address, phone, avatar):
    """
    Cập nhật thông tin người dùng.

    Args:
        user_id (int): ID của người dùng cần cập nhật.
        name (str): Họ tên người dùng.
        email (str): Email của người dùng.
        gender (int): Giới tính của người dùng (1: Nam, 2: Nữ, 3: Khác).
        birth_date (date): Ngày sinh của người dùng.
        address (str): Địa chỉ của người dùng.
        phone (str): Số điện thoại của người dùng.
        avatar (str): Đường dẫn hình đại diện của người dùng.

    Returns:
        bool: True nếu cập nhật thành công, False nếu xảy ra lỗi.
    """
    try:
        user = User.query.get(user_id)
        if user:
            user.name = name
            user.email = email
            user.gender = gender
            user.birth_date = birth_date
            user.address = address
            user.phone = phone
            user.avatar = avatar

            db.session.commit()
            return True
    except Exception as e:
        print(f"Lỗi khi cập nhật thông tin người dùng: {e}")
    return False
# Xử lý của bệnh nhân
def add_appointment(appointment_date, patient_id):
    """
    Thêm lịch khám mới vào cơ sở dữ liệu.
    """
    try:
        appointment = Appointment(
            appointment_date=appointment_date,
            patient_id=patient_id,
            status=AppointmentStatus.PENDING.value  # Mặc định trạng thái là PENDING
        )
        db.session.add(appointment)
        db.session.commit()
    except Exception as ex:
        print(f"Lỗi khi thêm lịch khám: {ex}")
        raise ex  # Ném lỗi lên để xử lý ở route

def get_latest_appointment_by_patient(patient_id):
    """
    Lấy lịch khám gần nhất của bệnh nhân.
    """
    return Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.appointment_date.desc()).first()

# Xử lý của y tá
def get_all_appointment_dates():
    """
    Lấy danh sách các ngày đã được lưu trong lịch hẹn (không trùng lặp).
    """
    return [row[0] for row in db.session.query(Appointment.appointment_date).distinct().order_by(Appointment.appointment_date).all()]

def get_appointments_by_date(appointment_date):
    """
    Lấy danh sách bệnh nhân theo ngày khám.
    """
    return Appointment.query.filter_by(appointment_date=appointment_date).all()

def cancel_appointment(appointment_id):
    """
    Chuyển trạng thái của lịch hẹn sang CANCELED.
    """
    try:
        appointment = Appointment.query.get(appointment_id)
        if appointment:
            appointment.status = AppointmentStatus.CANCELED.value
            db.session.commit()
    except Exception as ex:
        print(f"Lỗi khi hủy lịch hẹn: {ex}")
        raise ex

def confirm_appointment(appointment_id):
    try:
        appointment = Appointment.query.get(appointment_id)
        if appointment:
            appointment.status = AppointmentStatus.CONFIRMED.value
            db.session.commit()
    except Exception as ex:
        print(f"Lỗi khi xác nhận lịch hẹn: {ex}")
        raise ex

def delete_old_appointments():
    """
    Xóa các lịch hẹn có ngày khám nhỏ hơn ngày hôm nay.
    """
    today = date.today()  # Ngày hiện tại
    try:
        db.session.query(Appointment).filter(Appointment.appointment_date < today).delete(synchronize_session=False)
        db.session.commit()
        print("Đã xóa các lịch hẹn cũ thành công.")
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi xóa lịch hẹn cũ: {e}")

if __name__ == "__main__":
    with app.app_context():
        # Testing example
        print("Danh sách ngày khám:", get_all_appointment_dates())
=======
def get_medicine_by_id(id):
    return Medicine.query.get(id)

def get_user_by_username(username):
    """Trả về thông tin người dùng dựa trên username."""
    return User.query.filter_by(username=username).first()

if __name__ == "__main__":
    with app.app_context():
        print(get_user_by_username('admin'))
>>>>>>> 27697c343ee30c5ae7c35f759fb58dd33fa43f29
