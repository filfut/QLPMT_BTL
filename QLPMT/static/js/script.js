function addToPrescription(id, name, price, quantityFieldId = null) {
    let quantity = 1; // Mặc định số lượng là 1 nếu không có ô nhập
    if (quantityFieldId) {
        let quantityInput = document.getElementById(quantityFieldId);
        quantity = quantityInput ? parseInt(quantityInput.value) : 1;
    }

    if (isNaN(quantity) || quantity <= 0) {
        alert("Vui lòng nhập số lượng hợp lệ!");
        return;
    }

    fetch('/api/carts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: id,
            name: name,
            price: parseFloat(price),
            quantity: quantity
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "error") {
            alert("Lỗi: " + data.message);
        } else {
            alert("Thuốc đã được thêm vào giỏ hàng!");
            document.querySelectorAll(".class_counter").forEach(counter => {
                counter.innerText = data.total_quantity;
            });
        }
    })
    .catch(error => {
        console.log("Lỗi khi gửi yêu cầu giỏ hàng: ", error);
        alert("Có lỗi xảy ra, vui lòng thử lại!");
    });
}

function updateCart(id, obj) {
    let quantity = parseInt(obj.value);
    if (isNaN(quantity) || quantity <= 0) {
        alert("Số lượng không hợp lệ!");
        return;
    }

    fetch(`/api/cart/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ "quantity": quantity }),
        headers: { "Content-Type": "application/json" }
    }).then(res => {
        if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
        return res.json();
    }).then(data => {
        if (data.status === "error") {
            alert("Lỗi cập nhật: " + data.message);
        } else {
            document.querySelectorAll(".class_counter").forEach(counter => {
                counter.innerText = data.total_quantity;
            });

            document.querySelectorAll(".class_amount").forEach(amount => {
                amount.innerText = data.total_amount.toLocaleString("vi-VN");
            });
        }
    }).catch(error => {
        console.log("Lỗi cập nhật giỏ hàng: ", error);
        alert("Có lỗi xảy ra, vui lòng thử lại!");
    });
}

function deleteCart(id) {
    if (confirm("Bạn có chắc chắn muốn xóa thuốc này khỏi giỏ hàng?")) {
        fetch(`/api/cart/${id}`, { method: 'DELETE' })
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (data.status === "error") {
                alert("Lỗi xóa thuốc: " + data.message);
            } else {
                document.querySelectorAll(".class_counter").forEach(counter => {
                    counter.innerText = data.total_quantity;
                });

                document.querySelectorAll(".class_amount").forEach(amount => {
                    amount.innerText = data.total_amount.toLocaleString("vi-VN");
                });

                let medicineRow = document.getElementById(`medicine${id}`);
                if (medicineRow) {
                    medicineRow.remove();
                }
            }
        })
        .catch(error => {
            console.log("Lỗi xóa giỏ hàng: ", error);
            alert("Có lỗi xảy ra, vui lòng thử lại!");
        });
    }
}

function submitPrescription() {
    if (confirm("Bạn có chắc chắn muốn xác nhận đơn thuốc?")) {
        fetch("/api/submit-prescription", { method: "POST" })
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (data.status === 200) {
                location.reload();
            } else {
                alert("Lỗi! Vui lòng thử lại.");
            }
        })
        .catch(error => {
            console.log("Lỗi khi gửi đơn thuốc: ", error);
            alert("Có lỗi xảy ra, vui lòng thử lại!");
        });
    }
}
