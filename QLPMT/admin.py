from flask import redirect, session, request
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from models import MedicineType, Medicine, UserEnum, Receipt, MedicalRecord, User, ReceiptDetail
from QLPMT import app, db, dao
from flask_login import logout_user, current_user
from sqlalchemy.orm import aliased
from datetime import date, datetime
from sqlalchemy import func, cast, Date

class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and dao.check_user_role(current_user.id, 2)

class MyMedicineTypeView(AuthenticatedView):
    column_list = ['id', 'name', 'medicines']
    column_filters = ['name']
    column_searchable_list = ['name']
    can_export = True


class MyMedicineView(AuthenticatedView):
    column_list = ['id', 'name', 'price', 'med_type_id']
    column_filters = ['name', 'price']
    column_searchable_list = ['name']
    can_export = True

class MyMedicalRecordView(AuthenticatedView):

    column_list = ['id', 'patient_id', 'doctor_id', 'symptoms', 'diagnosis', 'appointment_date', 'medical_fee', 'total_medicine_cost', 'paid']
    column_filters = ['patient_id', 'doctor_id', 'appointment_date', 'paid']
    column_searchable_list = ['symptoms', 'diagnosis']
    can_export = True

class LogoutAdmin(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/login')

class StatsView(BaseView):
    """ ✅ Thống kê báo cáo doanh thu và sử dụng thuốc theo tháng """

    @expose('/')
    def index(self):
        selected_month = request.args.get('month', datetime.today().month)  # ✅ Lấy tháng từ URL

        # ✅ Lấy tổng doanh thu tháng
        total_revenue = db.session.query(func.sum(Receipt.total_amount)) \
            .filter(func.extract('month', Receipt.created_date) == selected_month).scalar() or 1

        # ✅ Lấy doanh thu từng ngày
        receipts = db.session.query(
            func.date(Receipt.created_date).label("date"),
            func.count(Receipt.medical_record_id).label("patient_count"),
            func.sum(Receipt.total_amount).label("total_revenue"),
            (func.sum(Receipt.total_amount) / total_revenue * 100).label("percentage")
        ).filter(func.extract('month', Receipt.created_date) == selected_month) \
        .group_by(func.date(Receipt.created_date)) \
        .all()

        # ✅ Lấy báo cáo sử dụng thuốc
        drug_reports = db.session.query(
            Medicine.name.label("name"),
            MedicineType.name.label("type"),
            func.sum(ReceiptDetail.quantity).label("quantity"),
            func.count(ReceiptDetail.id).label("usage_count")
        ).join(ReceiptDetail, Medicine.id == ReceiptDetail.medicine_id) \
            .join(MedicineType, Medicine.med_type_id == MedicineType.id) \
            .filter(func.extract('month', ReceiptDetail.created_date) == selected_month) \
            .group_by(Medicine.id, MedicineType.name) \
            .all()

        return self.render('/admin/stats.html', receipts=receipts, drug_reports=drug_reports, month=selected_month, total_revenue=total_revenue)
    def is_accessible(self):
        return current_user.is_authenticated and dao.check_user_role(current_user.id, 2)

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        today = date.today()

        receipts = db.session.query(
            Receipt.medical_record_id,
            User.name.label("employee_name"),
            Receipt.total_amount
        ).join(User, Receipt.employee_id == User.id) \
        .filter(cast(Receipt.created_date, Date) == today) \
        .all()

        print(f"Dữ liệu hóa đơn hôm nay: {receipts}")

        return self.render('admin/index.html', receipts=receipts)

# ✅ Khởi tạo Admin với giao diện Bootstrap4
admin = Admin(app=app, name="Hệ thống phòng khám", template_mode="bootstrap4", index_view=MyAdminIndexView())

# ✅ Thêm các view vào Admin
admin.add_view(MyMedicineTypeView(MedicineType, db.session))  # Quản lý loại thuốc
admin.add_view(MyMedicineView(Medicine, db.session))  # Quản lý thuốc
admin.add_view(MyMedicalRecordView(MedicalRecord, db.session))
admin.add_view(StatsView(name="Thống kê"))  # ✅ Thống kê doanh thu
admin.add_view(LogoutAdmin(name="Đăng xuất"))