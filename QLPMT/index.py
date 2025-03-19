import math

from flask import render_template, request, redirect, session
import dao
from QLPMT import app, login, admin
from flask_login import login_user, current_user, logout_user
import cloudinary.uploader


@app.route('/')
def index():
    return render_template("index.html")


# Mục đích: Danh mục sản phẩm hiển thị danh sách sản phẩm,
# với khả năng tìm kiếm theo từ khóa (q), theo danh mục (cate_id), và phân trang (page)
@app.route('/medicines-medicine_types')
def product_categories():
    if not current_user.is_authenticated:  # Nếu chưa đăng nhập, chuyển hướng về login
        return redirect('/login')

    if current_user.role != 4:  # Nếu không phải Doctor (role = 4), từ chối truy cập
        return redirect('/')

    # Nếu role = 4, tiếp tục xử lý
    q = request.args.get("q")
    med_type_id = request.args.get("med_type_id")
    page = request.args.get("page")
    medicines = dao.load_medicines(q=q, med_type_id=med_type_id, page=page)

    return render_template("medicines-medicine_types.html", medicines=medicines,
                           pages=int(math.ceil(dao.count_medicine() / app.config["PAGE_SIZE"])))


# Hiển thị chi tiết của sản phẩm
@app.route('/medicines/<int:id>')
def details(id):
    med = dao.get_medicine_by_id(id)

    return render_template('medicine-details.html', med=med)

@app.route('/profile')
def profile():
    pro = dao.get_user_by_id(current_user.id)

    return render_template('profile.html', pro=pro)

# Mục đích: Hàm này sẽ được gọi mỗi khi Flask render một template,
# và dữ liệu trả về sẽ được đưa vào context để sử dụng trong tất cả các template.@app.context_processor
@app.context_processor
def common_attributes():
    return {
        "med_types": dao.load_medicine_type()
    }


# Mục đích: Đăng nhập người dùng.
@app.route('/login', methods=['get', 'post'])
def login_my_user():
    if current_user.is_authenticated:
        return redirect('/')

    err_msg = None
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)

        if user:
            login_user(user)
            return redirect('/')
        else:
            err_msg = "Tài khoản hoặc mật khẩu không khớp!"

    return render_template('login.html', err_msg=err_msg)


# Mục đích: Đăng nhập quản trị viên.
@app.route('/login-admin', methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user)
    else:
        err_msg = "Tài khoản hoặc mật khẩu không khớp!"
    return redirect('/admin')


# Mục đích: Flask-Login yêu cầu phải có một hàm này để lấy thông tin người dùng từ ID.@login.user_loader
@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id=user_id)


# Mục đích: Đăng xuất người dùng.
@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect('/login')


# Mục đích: Đăng ký người dùng mới.
@app.route("/register", methods=['GET', 'POST'])
def register():
    err_msg = None
    if request.method == "POST":
        username = request.form.get('username')

        existing_user = dao.get_user_by_username(username=username)

        if existing_user:
            err_msg = "Tên đăng nhập đã bị trùng!"
        else:
            password = request.form.get('password')
            confirm = request.form.get('confirm')

            if password == confirm:

                name = request.form.get('name')
                avatar = request.files.get('avatar')
                path = None
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    path = res['secure_url']
                dao.add_user(name, username, password, path)
                return redirect('/login')
            else:
                err_msg = "Mật khẩu không khớp!"

    return render_template('register.html', err_msg=err_msg)


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
