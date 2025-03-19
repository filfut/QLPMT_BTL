import json
from datetime import date
from QLPMT import app, db
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Enum, Date, Text
from sqlalchemy.orm import relationship
from enum import Enum as RoleEnum
from flask_login import UserMixin


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


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)

    def __str__(self):
        return self.name


# Bảng User
class User(Base, UserMixin):
    __tablename__ = "user"

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
class MedicalRecord(Base):
    __tablename__ = "medical_record"
    patient_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('user.id'), nullable=False)
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

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()

        with open("data/medicine_type.json", encoding='utf-8') as f:
            medicine_types = json.load(f)
            for mt in medicine_types:
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
