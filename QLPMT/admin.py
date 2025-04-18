from flask import redirect
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from models import MedicineType, Medicine, UserEnum
from QLPMT import app, db, dao
from flask_login import logout_user, current_user


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserEnum.ADMIN.value  # Đảm bảo chỉ ADMIN truy cập


class MyMedicineTypeView(AuthenticatedView):
    column_list = ['id', 'name', 'medicines']  # Hiển thị các trường của loại thuốc
    column_filters = ['name']
    column_searchable_list = ['name']
    can_export = True  # Cho phép xuất dữ liệu


class MyMedicineView(AuthenticatedView):
    column_list = ['id', 'name', 'price', 'med_type_id']  # Hiển thị các trường thuốc
    column_filters = ['name', 'price']
    column_searchable_list = ['name']
    can_export = True


class LogoutAdmin(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


class StatsView(BaseView):
    @expose('/')
    def index(self):
        stats = dao.count_medicines_by_type()  # Thống kê số lượng thuốc theo loại
        return self.render('/admin/stats.html', stats=stats)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserEnum.ADMIN.value


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        stats = dao.count_medicines_by_type()  # Thống kê số lượng thuốc theo loại
        return self.render('admin/index.html', stats=stats)


# Khởi tạo Admin với giao diện Bootstrap4
admin = Admin(app=app, name="Hệ thống phòng khám", template_mode="bootstrap4", index_view=MyAdminIndexView())

# Thêm các view vào Admin
admin.add_view(MyMedicineTypeView(MedicineType, db.session))  # Quản lý loại thuốc
admin.add_view(MyMedicineView(Medicine, db.session))  # Quản lý thuốc
admin.add_view(StatsView(name="Thống kê"))
admin.add_view(LogoutAdmin(name="Đăng xuất"))