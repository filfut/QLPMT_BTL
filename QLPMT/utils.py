from flask import session


def medical_record_stats(medical_record):
    if not medical_record or not isinstance(medical_record, dict):
        return {
            "total_quantity": 0,
            "total_amount": 0
        }

    try:
        total_quantity = sum(int(item['quantity']) for item in medical_record.values() if 'quantity' in item)
        total_amount = sum(float(item['quantity']) * float(item['price']) for item in medical_record.values() if 'quantity' in item and 'price' in item)

        session['medical_record_stats'] = {
            "total_quantity": total_quantity,
            "total_amount": total_amount  # ✅ Lưu tổng tiền vào session
        }
        session.modified = True  # Cập nhật session

        return {
            "total_quantity": total_quantity,
            "total_amount": total_amount
        }

    except (ValueError, TypeError) as e:
        print(f"Lỗi khi tính toán phiếu khám: {e}")
        return {
            "total_quantity": 0,
            "total_amount": 0
        }