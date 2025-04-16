import json
<<<<<<< HEAD
from datetime import datetime, date
from QLPMT import app, db
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Date, Text, Index
=======
from datetime import date
from QLPMT import app, db
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Enum, Date, Text
>>>>>>> 27697c343ee30c5ae7c35f759fb58dd33fa43f29
from sqlalchemy.orm import relationship
from enum import Enum as RoleEnum
from flask_login import UserMixin

<<<<<<< HEAD
# Các enum
class UserEnum(RoleEnum):
=======

class UserEnum(RoleEnum):

>>>>>>> 27697c343ee30c5ae7c35f759fb58dd33fa43f29
    PATIENT = 1
    ADMIN = 2
    NURSE = 3
    DOCTOR = 4
    EMPLOYEE = 5

class GenderEnum(RoleEnum):
    MALE = 1
    FEMALE = 2
    OTHER = 3

<<<<<<< HEAD
=======

>>>>>>> 27697c343ee30c5ae7c35f759fb58dd33fa43f29
class AppointmentStatus(RoleEnum):
    PENDING = 1
    CONFIRMED = 2
    CANCELED = 3

<<<<<<< HEAD
# Base class
class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now)
    active = Column(Boolean, default=True)
=======

class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)

    def __str__(self):
        return self.name

>>>>>>> 27697c343ee30c5ae7c35f759fb58dd33fa43f29

# Bảng User
class User(Base, UserMixin):
    __tablename__ = "user"
<<<<<<< HEAD
    name = Column(String(100), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    avatar = Column(String(300), default="https://example.com/default-avatar.webp")
    role = Column(Integer, default=UserEnum.PATIENT.value)
    gender = Column(Integer, default=GenderEnum.MALE.value, nullable=True)
    birth_date = Column(Date, nullable=True)
    address = Column(String(255), nullable=True)
    phone = Column(String(15), nullable=True)

class Admin(User):
    __mapper_args__ = {"polymorphic_identity": 2}

class Nurse(User):
    __mapper_args__ = {"polymorphic_identity": 3}

class Doctor(User):
    __mapper_args__ = {"polymorphic_identity": 4}
    medical_records = relationship('MedicalRecord', backref='doctor', foreign_keys='MedicalRecord.doctor_id', lazy='subquery')

class Patient(User):
    __mapper_args__ = {"polymorphic_identity": 1}
    appointments = relationship('Appointment', backref='patient_appointments', foreign_keys='Appointment.patient_id', lazy='joined')
    medical_records = relationship('MedicalRecord', backref='patient_medical_records', foreign_keys='MedicalRecord.patient_id', lazy='joined')

class Employee(User):
    __mapper_args__ = {"polymorphic_identity": 5}
    receipts = relationship('Receipt', backref='employee', foreign_keys='Receipt.employee_id', lazy='joined')

# Hồ sơ khám bệnh
=======

    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    avatar = Column(
        String(300),
        default="https://res.cloudinary.com/dy1unykph/image/upload/v1740037805/apple-iphone-16-pro-natural-titanium_lcnlu2.webp"
    )
    active = Column(Boolean, default=True)
    role = Column(Integer, default=UserEnum.PATIENT.value)

    __mapper_args__ = {
        "polymorphic_on": role,
    }

# Lớp con kế thừa User (Không tạo bảng riêng, sử dụng chung bảng users)
# Người quản trị
class Admin(User):
    __mapper_args__ = {"polymorphic_identity": UserEnum.ADMIN.value}

# Y tá
class Nurse(User):
    __mapper_args__ = {"polymorphic_identity": UserEnum.NURSE.value}
    appointments = relationship('Appointment', backref='nurse', foreign_keys='Appointment.nurse_id')

# Bác sĩ
class Doctor(User):
    __mapper_args__ = {"polymorphic_identity": UserEnum.DOCTOR.value}
    medical_records = relationship('MedicalRecord', backref='doctor', foreign_keys='MedicalRecord.doctor_id')


# Bệnh nhân
class Patient(User):
    __mapper_args__ = {"polymorphic_identity": UserEnum.PATIENT.value}
    gender = Column(Integer, default=GenderEnum.MALE.value, nullable=True)
    birth_date = Column(Date, nullable=True, default=date.today)
    address = Column(String(255), nullable=True)
    phone = Column(String(100), nullable=True)
    appointments = relationship('Appointment', backref='patient', foreign_keys='Appointment.patient_id')
    medical_records = relationship('MedicalRecord', backref='patient', foreign_keys='MedicalRecord.patient_id')
    receipts = relationship('Receipt', backref='patient')

# Thu nhân
class Employee(User):
    __mapper_args__ = {"polymorphic_identity": UserEnum.EMPLOYEE.value}
    receipts = relationship('Receipt', backref='employee')


# Bảng Phiếu khám bệnh
>>>>>>> 27697c343ee30c5ae7c35f759fb58dd33fa43f29
class MedicalRecord(Base):
    __tablename__ = "medical_record"
    patient_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('user.id'), nullable=False)
<<<<<<< HEAD
    symptoms = Column(String(255), nullable=False)
    diagnosis = Column(String(255), nullable=False)
    receipts = relationship('Receipt', backref='medical_record', lazy='joined')

# Cuộc hẹn
class Appointment(Base):
    __tablename__ = "appointment"
    appointment_date = Column(Date, nullable=False, default=date.today, index = True)
    status = Column(Integer, default=AppointmentStatus.PENDING.value, nullable=False)
    patient_id = Column(Integer, ForeignKey('user.id'), nullable=False, index = True)

    patient = relationship("Patient", foreign_keys=[patient_id], overlaps="appointments,patient_appointments")

    __table_args__ = (
        Index('idx_appointment_date', 'appointment_date'),  # Chỉ mục cho ngày khám
        Index('idx_patient_id', 'patient_id'),  # Chỉ mục cho ID bệnh nhân
    )

# Loại thuốc
class MedicineType(Base):
    __tablename__ = "medicine_type"
    name = Column(String(50), nullable=False, unique=True)
    medicines = relationship('Medicine', backref='medicine_type', lazy='joined')

# Thuốc
class Medicine(Base):
    __tablename__ = "medicine"
    name = Column(String(100), nullable=False)
    price = Column(Float, default=0, nullable=False)
    image = Column(String(300), default="https://example.com/default-medicine.webp")
    ingredients = Column(String(255), nullable=False)
    usage_instructions = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    med_type_id = Column(Integer, ForeignKey(MedicineType.id), nullable=False)
    details = relationship('ReceiptDetail', backref='medicine', lazy='joined')

# Chi tiết hóa đơn
class ReceiptDetail(Base):
    __tablename__ = "receipt_detail"
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    medical_record_id = Column(Integer, ForeignKey('medical_record.id'), nullable=False)
    medicine_id = Column(Integer, ForeignKey('medicine.id'), nullable=False)

# Hóa đơn
class Receipt(Base):
    __tablename__ = "receipt"
    medical_record_id = Column(Integer, ForeignKey('medical_record.id'), nullable=False)
    employee_id = Column(Integer, ForeignKey('user.id'), nullable=False)

# Tạo cơ sở dữ liệu
=======
    examination_date = Column(Date, nullable=False, default=date.today) #Ngày khám
    symptoms = Column(String(255), nullable=False) #Trệu chứng
    diagnosis = Column(String(255), nullable=False) #Dự đoán
    prescriptions = relationship('Prescription', backref='medical_record')

# Bảng Cuộc hẹn
class Appointment(Base):
    __tablename__ = "appointment"
    appointment_date = Column(Date, nullable=False, default=date.today) #Ngày hẹn
    status = Column(Integer, default=AppointmentStatus.PENDING.value, nullable=False) #Trạng thái kiểm duyệt
    patient_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    nurse_id = Column(Integer, ForeignKey('user.id'), nullable=False)

# Bảng Loại thuốc
class MedicineType(Base):
    __tablename__ = "medicine_type"
    name = Column(String(50), nullable=False, unique=True)
    medicines = relationship('Medicine', backref='medicine_type')

# Bảng Thuốc
class Medicine(Base):
    __tablename__ = "medicine"
    name = Column(String(100), nullable=False)
    image = Column(
        String(300),
        default="https://res.cloudinary.com/dy1unykph/image/upload/v1740037805/apple-iphone-16-pro-natural-titanium_lcnlu2.webp"
    )
    price = Column(Float, default=0)
    quantity = Column(String(50), nullable=False)
    med_type_id = Column(Integer, ForeignKey(MedicineType.id), nullable=False)
    prescriptions = relationship('Prescription', backref='medicine')

# Bảng Đơn thuốc
class Prescription(Base):
    __tablename__ = 'prescription'
    medical_record_id = Column(Integer, ForeignKey(MedicalRecord.id), nullable=False)
    medicine_id = Column(Integer, ForeignKey(Medicine.id), nullable=False)
    dosage = Column(String(50), nullable=False)  # Số lượng thuốc
    usage_instructions = Column(Text, nullable=False)  # Cách sử dụng

class Receipt(Base):
    __tablename__ = "receipt"
    examination_fee = Column(Float, default=100000)
    medical_record_id = Column(Integer, ForeignKey(MedicalRecord.id), nullable=False)
    unit_price = Column(Float, default=0)
    employee_id = Column(Integer, ForeignKey('user.id'), nullable=False)

>>>>>>> 27697c343ee30c5ae7c35f759fb58dd33fa43f29
if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()

        with open("data/medicine_type.json", encoding='utf-8') as f:
            medicine_types = json.load(f)
            for mt in medicine_types:
<<<<<<< HEAD
                db.session.add(MedicineType(**mt))

        with open("data/medicine.json", encoding='utf-8') as f:
            medicines = json.load(f)
            for med in medicines:
                db.session.add(Medicine(**med))

        import hashlib
        # Tạo người dùng
        u1 = Employee(name="Hau", email="hau.employee@example.com",  # Sử dụng email
                      password=hashlib.md5("123".encode('utf-8')).hexdigest(),
                      gender=GenderEnum.MALE.value, birth_date=date(1985, 5, 22),
                      address="123 Main Street", phone="0909123456",
                      role=UserEnum.EMPLOYEE.value,
                      avatar="https://res.cloudinary.com/dwrl7e8y8/image/upload/v1744709918/1012252_vpkfmn.png")

        u2 = Admin(name="Hau Nguyen", email="hau.admin@example.com",  # Sử dụng email
                   password=hashlib.md5("123".encode('utf-8')).hexdigest(),
                   gender=GenderEnum.MALE.value, birth_date=date(1980, 7, 15),
                   address="456 Admin Lane", phone="0909876543",
                   role=UserEnum.ADMIN.value,
                   avatar="https://res.cloudinary.com/dwrl7e8y8/image/upload/v1744709918/1012252_vpkfmn.png")

        u3 = Doctor(name="Le Cuong", email="cuong.doctor@example.com",  # Sử dụng email
                    password=hashlib.md5("123".encode('utf-8')).hexdigest(),
                    gender=GenderEnum.MALE.value, birth_date=date(1990, 8, 10),
                    address="789 Doctor Street", phone="0909223344",
                    role=UserEnum.DOCTOR.value,
                    avatar="https://res.cloudinary.com/dwrl7e8y8/image/upload/v1744709918/1012252_vpkfmn.png")

        u4 = Nurse(name="Phu", email="phu.nurse@example.com",  # Sử dụng email
                   password=hashlib.md5("123".encode('utf-8')).hexdigest(),
                   gender=GenderEnum.FEMALE.value, birth_date=date(1995, 9, 12),
                   address="321 Nurse Road", phone="0909334455",
                   role=UserEnum.NURSE.value,
                   avatar="https://res.cloudinary.com/dwrl7e8y8/image/upload/v1744709918/1012252_vpkfmn.png")

        u5 = Patient(name="Cuong", email="veve3729@gmail.com",  # Sử dụng email
                   password=hashlib.md5("123".encode('utf-8')).hexdigest(),
                   gender=GenderEnum.FEMALE.value, birth_date=date(1995, 9, 12),
                   address="321 Nurse Road", phone="0909334455",
                   avatar="https://res.cloudinary.com/dwrl7e8y8/image/upload/v1744709918/1012252_vpkfmn.png")


        db.session.add_all([u1, u2, u3, u4, u5])
        db.session.commit()
        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()
=======
                medicine_type = MedicineType(**mt)
                db.session.add(medicine_type)

        with open("data/medicine.json", encoding='utf-8') as f:
            medicines = json.load(f)
            for m in medicines:
                med = Medicine(**m)
                db.session.add(med)

        with open("data/appointment.json", encoding='utf-8') as f:
            appointments = json.load(f)
            for a in appointments:
                appoint = Appointment(**a)
                db.session.add(appoint)

        with open("data/medical_record.json", encoding='utf-8') as f:
            medicals = json.load(f)
            for mr in medicals:
                med_record = MedicalRecord(**mr)
                db.session.add(med_record)

        with open("data/prescription.json", encoding='utf-8') as f:
            prescriptions = json.load(f)
            for p in prescriptions:
                pres = Prescription(**p)
                db.session.add(pres)

        with open("data/receipt.json", encoding='utf-8') as f:
            receipts = json.load(f)
            for r in receipts:
                re = Receipt(**r)
                db.session.add(re)

        import hashlib

        u1 = Employee(name="Hau", username="employee", password=hashlib.md5("123".encode('utf-8')).hexdigest())
        u2 = Admin(name="Hau Nguyen", username="admin", password=hashlib.md5("123".encode('utf-8')).hexdigest())
        u3 = Doctor(name="Le Cuong", username="doctor", password=hashlib.md5("123".encode('utf-8')).hexdigest())
        u4 = Nurse(name="Phu", username="nurse", password=hashlib.md5("123".encode('utf-8')).hexdigest())
        u5 = Patient(name="Hu Chi", username="patient", password=hashlib.md5("123".encode('utf-8')).hexdigest(),
                     birth_date="1990-01-01", gender=GenderEnum.MALE.value)

        db.session.add_all([u1, u2, u3, u4, u5])

        db.session.commit()
>>>>>>> 27697c343ee30c5ae7c35f759fb58dd33fa43f29
