from flask import redirect, session, request
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from models import MedicineType, Medicine, UserEnum, Receipt, MedicalRecord, User
from QLPMT import app, db, dao
from flask_login import logout_user, current_user
from sqlalchemy.orm import aliased
from datetime import date, datetime
from sqlalchemy import func, cast, Date

class AuthenticatedView(ModelView):
    """ ✅ Chỉ Admin mới có thể truy cập """

    def is_accessible(self):
        return current_user.is_authenticated and dao.check_user_role(current_user.id, 2)

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')  # 🚫 Chuyển hướng nếu không phải Admin


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

class LogoutAdmin(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        session.pop('admin_logged_in', None)  # ✅ Xóa trạng thái đăng nhập Admin
        return redirect('/login')



from sqlalchemy import func
from datetime import datetime
from flask import request

class StatsView(BaseView):
    """ ✅ Thống kê báo cáo doanh thu theo tháng được chọn """

    @expose('/')
    def index(self):
        selected_month = request.args.get('month', datetime.today().month)  # ✅ Lấy tháng từ URL

        # ✅ Lấy tổng doanh thu của tháng
        total_revenue = db.session.query(
            func.sum(Receipt.total_amount)
        ).filter(func.extract('month', Receipt.created_date) == selected_month).scalar()

        # ✅ Lấy thống kê doanh thu từng ngày
        receipts = db.session.query(
            func.date(Receipt.created_date).label("date"),
            func.count(Receipt.medical_record_id).label("patient_count"),
            func.sum(Receipt.total_amount).label("total_revenue"),
            (func.sum(Receipt.total_amount) / total_revenue * 100).label("percentage")  # ✅ Tính tỷ lệ
        ).filter(func.extract('month', Receipt.created_date) == selected_month) \
        .group_by(func.date(Receipt.created_date)) \
        .all()


        return self.render('/admin/stats.html', receipts=receipts, month=selected_month, total_revenue=total_revenue)

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        today = date.today()  # ✅ Đã định nghĩa đúng

        receipts = db.session.query(
            Receipt.medical_record_id,
            User.name.label("employee_name"),
            Receipt.total_amount
        ).join(User, Receipt.employee_id == User.id) \
        .filter(cast(Receipt.created_date, Date) == today) \
        .all()

        print(f"Dữ liệu hóa đơn hôm nay: {receipts}")  # 📌 Kiểm tra dữ liệu trước khi hiển thị

        return self.render('admin/index.html', receipts=receipts)

# ✅ Khởi tạo Admin với giao diện Bootstrap4
admin = Admin(app=app, name="Hệ thống phòng khám", template_mode="bootstrap4", index_view=MyAdminIndexView())

# ✅ Thêm các view vào Admin
admin.add_view(MyMedicineTypeView(MedicineType, db.session))  # Quản lý loại thuốc
admin.add_view(MyMedicineView(Medicine, db.session))  # Quản lý thuốc
admin.add_view(StatsView(name="Thống kê"))  # ✅ Thống kê doanh thu
admin.add_view(LogoutAdmin(name="Đăng xuất"))