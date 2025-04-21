import json
from datetime import datetime, date
from QLPMT import app, db
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Date, Text, Index
from sqlalchemy.orm import relationship
from enum import Enum as RoleEnum
from flask_login import UserMixin

# Các enum
class UserEnum(RoleEnum):
    PATIENT = 1
    ADMIN = 2
    NURSE = 3
    DOCTOR = 4
    EMPLOYEE = 5

class GenderEnum(RoleEnum):
    MALE = 1
    FEMALE = 2
    OTHER = 3

class AppointmentStatus(RoleEnum):
    PENDING = 1
    CONFIRMED = 2
    CANCELED = 3

# Base class
class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now)
    active = Column(Boolean, default=True)

# Bảng User
class User(Base, UserMixin):
    __tablename__ = "user"
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
class MedicalRecord(Base):
    __tablename__ = "medical_record"
    patient_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    symptoms = Column(String(255), nullable=False)
    diagnosis = Column(String(255), nullable=False)
    appointment_date = Column(Date, nullable=False, default=date.today, index = True)
    medical_fee = Column(Integer, nullable=False, default=100000)
    total_medicine_cost = Column(Integer, nullable=False, default=0)
    paid = Column(Boolean, default=False)  # Mặc định là chưa thanh toán
    receipts = relationship('Receipt', backref='medical_record', lazy='joined')
    details = relationship('ReceiptDetail', backref='medical_record', lazy='joined')

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
    total_amount = Column(Integer, nullable=False)

# Tạo cơ sở dữ liệu
if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()

        with open("data/medicine_type.json", encoding='utf-8') as f:
            medicine_types = json.load(f)
            for mt in medicine_types:
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