def cart_stats(cart):
    if not cart or not isinstance(cart, dict):  # Đảm bảo giỏ hàng là một dictionary hợp lệ
        return {
            "total_quantity": 0,
            "total_amount": 0
        }

    try:
        total_quantity = sum(int(item['quantity']) for item in cart.values() if 'quantity' in item)
        total_amount = sum(float(item['quantity']) * float(item['price']) for item in cart.values() if 'quantity' in item and 'price' in item)
    except (ValueError, TypeError) as e:
        print(f"Lỗi khi tính toán giỏ hàng: {e}")
        return {
            "total_quantity": 0,
            "total_amount": 0
        }

    return {
        "total_quantity": total_quantity,
        "total_amount": total_amount
    }