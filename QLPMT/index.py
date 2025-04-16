import math
from flask import render_template, request, redirect, session, jsonify, abort, flash
import dao, utils
from QLPMT import app, login, admin
from flask_login import login_user, current_user, logout_user, login_required
import cloudinary.uploader
from datetime import datetime, date, timedelta


@app.route('/')
def index():
    # Kiểm tra trạng thái đăng nhập
    appointment = None
    if current_user.is_authenticated and dao.check_user_role(current_user.id, 1):
        appointment = dao.get_latest_appointment_by_patient(current_user.id)

    return render_template(
        'index.html',
        appointment=appointment,
        patient=current_user if current_user.is_authenticated else None  # Truyền thông tin nếu đã đăng nhập
    )

@app.route('/medicine-catalog', methods=['GET'])
def medicine_catalog():
    if not current_user.is_authenticated or not dao.check_user_role(current_user.id, 4):
        abort(403)  # Trả về lỗi 403 nếu không phải bác sĩ hoặc quản trị viên

    q = request.args.get("q")
    med_type_id = request.args.get("medicine_type_id")
    page = request.args.get("page")

    medicines = dao.load_medicines(q=q, med_type_id=med_type_id, page=page)
    total_medicines = dao.count_medicines()

    return render_template("medicine_catalog.html", medicines=medicines,
                           pages=int(math.ceil(total_medicines / app.config["PAGE_SIZE"])))

@app.route('/medicines/<int:id>')
def medicine_details(id):
    medicine = dao.get_medicine_by_id(id)
    if not medicine:
        return "Không tìm thấy thuốc", 404
    return render_template('medicine-details.html', medicine=medicine)

@app.context_processor
def common_attributes():
    return {
        "medicine_types": dao.load_medicine_types(),
        "cart_stats": utils.cart_stats(session.get('cart', {}))  # Đảm bảo giỏ hàng luôn là dictionary
    }

@app.route('/login', methods=['GET', 'POST'])
def login_my_user():
    if current_user.is_authenticated:
        return redirect('/')

    err_msg = None
    if request.method == 'POST':
        email = request.form.get('email')  # Lấy email thay vì username
        password = request.form.get('password')

        user = dao.auth_user(email=email, password=password)  # Dùng email thay cho username
        if user:
            login_user(user)
            return redirect('/')
        else:
            err_msg = "Email hoặc mật khẩu không chính xác!"

    return render_template('login.html', err_msg=err_msg)


@app.route("/register", methods=['GET', 'POST'])
def register():
    err_msg = None
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        avatar = request.files.get('avatar')
        role = request.form.get('role', 1)  # Mặc định là bệnh nhân

        # Kiểm tra định dạng email Gmail
        if not email.endswith("@gmail.com"):
            err_msg = "Email phải thuộc Gmail (ví dụ: example@gmail.com)."
        elif dao.is_email_taken(email):  # Kiểm tra email đã tồn tại
            err_msg = "Email đã tồn tại. Vui lòng chọn email khác."
        elif password != confirm:  # Kiểm tra mật khẩu
            err_msg = "Mật khẩu không khớp!"
        else:
            # Xử lý avatar nếu có
            avatar_path = None
            if avatar:
                try:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']
                except Exception as e:
                    err_msg = f"Lỗi khi tải lên ảnh: {e}"

            # Thêm người dùng vào cơ sở dữ liệu
            dao.add_user(name=name, email=email, password=password, avatar=avatar_path, role=role)
            return redirect('/login')

    return render_template('register.html', err_msg=err_msg)

@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id=user_id)

@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect('/login')

@app.route('/login-admin', methods=['post'])
def login_admin_process():
    email = request.form.get('email')
    password = request.form.get('password')

    user = dao.auth_user(email=email, password=password)
    if user:
        login_user(user)
    else:
        err_msg = "Tài khoản hoặc mật khẩu không khớp!"
    return redirect('/admin')

@app.route('/api/carts', methods=['POST'])
@login_required  # Chỉ cho phép người dùng đăng nhập thêm vào giỏ hàng
def add_to_cart():
    cart = session.get('cart', {})

    try:
        medicine_id = str(request.json.get('id'))
        name = request.json.get('name')
        price = request.json.get('price')
        quantity = request.json.get('quantity')

        # Kiểm tra dữ liệu đầu vào
        if quantity is None or not isinstance(quantity, int) or quantity <= 0:
            return jsonify({'status': 'error', 'message': 'Số lượng không hợp lệ'}), 400

        # Cập nhật giỏ hàng
        if medicine_id in cart:
            cart[medicine_id]['quantity'] += quantity
        else:
            cart[medicine_id] = {'id': medicine_id, 'name': name, 'price': price, 'quantity': quantity}

        session['cart'] = cart
        session.modified = True  # Đảm bảo session được cập nhật

    except Exception as e:
        print(f"Lỗi khi thêm vào giỏ hàng: {e}")
        return jsonify({'status': 'error', 'message': 'Lỗi không xác định'}), 500

    return jsonify(utils.cart_stats(cart))

@app.route('/api/cart/<id>', methods=['DELETE'])
@login_required  # Yêu cầu người dùng phải đăng nhập
def delete_cart(id):
    cart = session.get('cart', {})

    if id not in cart:
        return jsonify({'status': 'error', 'message': 'Không tìm thấy thuốc trong giỏ hàng'}), 404

    try:
        del cart[id]
        session['cart'] = cart
        session.modified = True  # Đảm bảo session được cập nhật
    except Exception as e:
        print(f"Lỗi khi xóa giỏ hàng: {e}")
        return jsonify({'status': 'error', 'message': 'Lỗi không xác định'}), 500

    return jsonify(utils.cart_stats(cart))

@app.route('/api/cart/<id>', methods=['PUT'])
@login_required  # Yêu cầu người dùng phải đăng nhập
def update_cart(id):
    cart = session.get('cart', {})

    if id not in cart:
        return jsonify({'status': 'error', 'message': 'Không tìm thấy thuốc trong giỏ hàng'}), 404

    try:
        quantity = request.json.get('quantity')

        # Kiểm tra dữ liệu đầu vào
        if quantity is None or not str(quantity).isdigit():
            return jsonify({'status': 'error', 'message': 'Thiếu hoặc sai dữ liệu số lượng'}), 400

        quantity = int(quantity)
        if quantity <= 0:
            return jsonify({'status': 'error', 'message': 'Số lượng phải lớn hơn 0'}), 400

        cart[id]['quantity'] = quantity
        session['cart'] = cart
        session.modified = True  # Đảm bảo session được cập nhật
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Dữ liệu số lượng không hợp lệ'}), 400
    except Exception as e:
        print(f"Lỗi khi cập nhật giỏ hàng: {e}")
        return jsonify({'status': 'error', 'message': 'Lỗi không xác định'}), 500

    return jsonify(utils.cart_stats(cart))

@app.route('/api/pay', methods=['POST'])
@login_required  # Yêu cầu người dùng phải đăng nhập
def pay():
    cart = session.get('cart')
    medical_record_id = request.json.get('medical_record_id')

    if not cart or not medical_record_id:
        return jsonify({'status': 'error', 'message': 'Giỏ hàng rỗng hoặc thiếu ID hồ sơ'}), 400

    try:
        dao.add_receipt(cart=cart, medical_record_id=medical_record_id, employee_id=current_user.id)
        del session['cart']  # Xóa giỏ hàng sau khi thanh toán thành công
    except Exception as ex:
        print(f"Lỗi khi thanh toán: {ex}")
        return jsonify({'status': 'error', 'message': 'Có lỗi xảy ra khi thanh toán'}), 500

    return jsonify({'status': 200, 'message': 'Thanh toán thành công'})

@app.route('/cart', methods=['GET'])
def cart():
    if not current_user.is_authenticated or not dao.check_user_role(current_user.id, 4):
        abort(403)  # Trả về lỗi 403 nếu không phải bác sĩ hoặc quản trị viên

    return render_template("cart.html")

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    err_msg = None

    if request.method == 'POST':
        # Lấy thông tin từ form
        name = request.form.get('name')
        email = request.form.get('email')
        gender = request.form.get('gender')
        birth_date = request.form.get('birth_date')
        address = request.form.get('address')
        phone = request.form.get('phone')
        avatar = request.files.get('avatar')  # Xử lý avatar nếu có thay đổi

        # Upload avatar nếu có
        avatar_path = current_user.avatar  # Giữ avatar cũ mặc định
        if avatar:
            if not allowed_file(avatar.filename):  # Kiểm tra định dạng tệp
                err_msg = "Định dạng file không hợp lệ! Vui lòng sử dụng JPG, PNG, hoặc GIF."
            else:
                try:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']
                except Exception as e:
                    err_msg = f"Lỗi khi tải lên avatar: {e}"

        # Cập nhật thông tin người dùng
        if dao.update_user_info(current_user.id, name, email, gender, birth_date, address, phone, avatar_path):
            return redirect('/profile')  # Sau khi cập nhật thành công, reload profile
        else:
            err_msg = "Cập nhật thông tin thất bại."

    return render_template('profile.html', err_msg=err_msg, user=current_user)


@app.route('/register-appointment', methods=['GET', 'POST'])
@login_required
def register_appointment():
    # Kiểm tra vai trò: chỉ bệnh nhân mới được phép đăng ký
    if not current_user.is_authenticated or not dao.check_user_role(current_user.id, 1):
        abort(403)  # Trả về lỗi 403 nếu không phải bác sĩ hoặc quản trị viên

    err_msg = None

    if request.method == 'POST':
        appointment_date = request.form.get('appointment_date')

        # Chuyển đổi ngày nhập thành dạng `date` để kiểm tra
        try:
            selected_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        except ValueError:
            err_msg = "Định dạng ngày không hợp lệ, vui lòng nhập đúng!"
            return render_template('register_appointment.html', err_msg=err_msg)

        # Kiểm tra nếu ngày đã nhập nhỏ hơn ngày hiện tại
        if selected_date < date.today():
            err_msg = f"Ngày {selected_date} không hợp lệ! Vui lòng chọn một ngày từ hôm nay trở đi."
            return render_template('register_appointment.html', err_msg=err_msg)

        # Thêm lịch khám vào cơ sở dữ liệu
        try:
            dao.add_appointment(selected_date, current_user.id)
            return redirect('/')  # Chuyển hướng về trang chủ sau khi đăng ký thành công
        except Exception as ex:
            print(f"Lỗi khi thêm lịch khám: {ex}")
            err_msg = "Đăng ký lịch khám thất bại, vui lòng thử lại!"
            return render_template('register_appointment.html', err_msg=err_msg)

    return render_template('register_appointment.html')

@app.route('/appointment-list', methods=['GET', 'POST'])
@login_required
def appointment_list():
    # Kiểm tra quyền truy cập
    if not current_user.is_authenticated or not dao.check_user_role(current_user.id, 3):
        abort(403)
    dao.delete_old_appointments()
    err_msg = None

    # Lấy danh sách ngày khám từ cơ sở dữ liệu
    appointment_dates = dao.get_all_appointment_dates()

    # Xử lý ngày được chọn từ query string hoặc session
    today = datetime.today().strftime('%Y-%m-%d')  # Ngày hiện tại
    selected_date = request.args.get('appointment_date')  # Lấy ngày từ query string
    if selected_date:  # Cập nhật ngày vào session nếu được chọn
        session['selected_date'] = selected_date
        session.modified = True
    else:  # Nếu không có query string, mặc định là ngày hôm nay hoặc ngày lưu trong session
        selected_date = session.get('selected_date', today)

    # Nếu không có ngày khám nào trong hệ thống
    if not appointment_dates:
        err_msg = "Không có ngày khám nào trong hệ thống. Vui lòng kiểm tra cơ sở dữ liệu!"
        appointments = []
    else:
        # Nếu người dùng chưa chọn ngày hợp lệ
        if not selected_date:
            err_msg = "Vui lòng chọn một ngày khám từ danh sách."
            appointments = []
        else:
            # Lấy danh sách bệnh nhân theo ngày được chọn
            appointments = dao.get_appointments_by_date(selected_date)

    # Xử lý các hành động POST (xóa hoặc lưu trạng thái)
    if request.method == 'POST':
        action = request.form.get('action')
        appointment_id = request.form.get('appointment_id')

        try:
            if action == 'delete':
                dao.cancel_appointment(appointment_id)
                flash(f"Lịch hẹn ID {appointment_id} đã bị hủy!", "success")
            elif action == 'confirm':  # Thay 'save' thành 'confirm'
                dao.confirm_appointment(appointment_id)
                flash(f"Lịch hẹn ID {appointment_id} đã được chấp nhận!", "success")

            # Tải lại danh sách sau khi cập nhật
            appointments = dao.get_appointments_by_date(selected_date)

        except Exception as ex:
            print(f"Lỗi khi thực hiện hành động {action}: {ex}")
            err_msg = f"Không thể thực hiện hành động {action}, vui lòng thử lại!"
    # Render giao diện danh sách khám
    return render_template(
        'appointment_list.html',
        appointment_dates=appointment_dates,  # Danh sách ngày khám
        selected_date=selected_date,  # Ngày được chọn hoặc giá trị None
        appointments=appointments,  # Danh sách bệnh nhân (có thể trống)
        err_msg=err_msg  # Lỗi (nếu có)
    )

@app.route('/debug-session')
@login_required
def debug_session():
    # In toàn bộ nội dung của session
    return f"Session hiện tại: {dict(session)}"

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
