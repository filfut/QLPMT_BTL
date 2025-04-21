function addToMedicalRecord(id, name, price, quantityFieldId = null, unit, usageInstructions) {
    let quantity = 1; // Mặc định số lượng là 1 nếu không có ô nhập
    if (quantityFieldId) {
        let quantityInput = document.getElementById(quantityFieldId);
        quantity = quantityInput ? parseInt(quantityInput.value) : 1;
    }

    if (isNaN(quantity) || quantity <= 0) {
        alert("Vui lòng nhập số lượng hợp lệ!");
        return;
    }

    fetch('/api/medical_records', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id: id,
            name: name,
            price: parseFloat(price),
            quantity: quantity,
            unit: unit,
            usageInstructions: usageInstructions
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "error") {
            alert("Lỗi: " + data.message);
        } else {
            alert(`Thuốc "${name}" (${unit}) đã được thêm vào phiếu khám!\nHướng dẫn: ${usageInstructions}`);
            document.querySelectorAll(".class_counter").forEach(counter => {
                counter.innerText = data.total_quantity;
            });
        }
    })
    .catch(error => {
        console.log("Lỗi khi gửi yêu cầu phiếu khám:", error);
        alert("Có lỗi xảy ra, vui lòng thử lại!");
    });
}

function updateMedicalRecord(id, obj) {
    let quantity = parseInt(obj.value);
    if (isNaN(quantity) || quantity <= 0) {
        alert("Số lượng không hợp lệ!");
        return;
    }

    fetch(`/api/medical_record/${id}`, {
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
        console.log("Lỗi cập nhật phiếu khám: ", error);
        alert("Có lỗi xảy ra, vui lòng thử lại!");
    });
}

function deleteMedicalRecord(id) {
    if (confirm("Bạn có chắc chắn muốn xóa thuốc này khỏi phiếu khám?")) {
        fetch(`/api/medical_record/${id}`, { method: 'DELETE' })
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
            console.log("Lỗi xóa phiếu khám: ", error);
            alert("Có lỗi xảy ra, vui lòng thử lại!");
        });
    }
}

function storePatientInfo(id, name, appointmentDate) {
    fetch('/api/session/store_patient', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id, name: name, appointment_date: appointmentDate })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            alert("Lập phiếu khám thành công!"); // Hiển thị thông báo
        } else {
            alert("Có lỗi xảy ra: " + data.message);
        }
    })
    .catch(error => {
        console.log("Lỗi khi lưu thông tin bệnh nhân vào session:", error);
        alert("Có lỗi xảy ra, vui lòng thử lại!");
    });
}

function autoSaveMedicalRecord() {
    const symptoms = document.getElementById("symptoms").value;
    const diagnosis = document.getElementById("diagnosis").value;

    fetch('/api/save_medical_record_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptoms: symptoms, diagnosis: diagnosis })
    })
    .catch(error => console.log("Lỗi khi lưu dữ liệu vào session:", error));
}

// Gắn sự kiện tự động lưu
document.getElementById("symptoms").addEventListener("input", autoSaveMedicalRecord);
document.getElementById("diagnosis").addEventListener("input", autoSaveMedicalRecord);

function saveMedicalRecord() {
    if (confirm("Bạn có chắc chắn muốn lưu phiếu khám?")) {
        let totalAmount = document.querySelector(".class_amount").innerText.replace(" VNĐ", "").replace(/,/g, "").trim();

        fetch("/api/save-medical-record", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                symptoms: document.getElementById("symptoms").value.trim(),
                diagnosis: document.getElementById("diagnosis").value.trim(),
                total_amount: totalAmount  // ✅ Gửi tổng tiền thuốc từ giao diện lên API
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                alert("Phiếu khám đã được lưu thành công!");
                location.reload();
            } else {
                alert(`Lỗi: ${data.message}`);
            }
        })
        .catch(error => {
            console.log("Lỗi khi lưu phiếu khám: ", error);
            alert("Có lỗi xảy ra, vui lòng thử lại!");
        });
    }
}

function storePaymentInfo(medicalRecordId, patientName, appointmentDate, medicalFee, totalMedicineCost) {
    let totalAmount = parseFloat(medicalFee) + parseFloat(totalMedicineCost); // ✅ Tính tổng tiền cần thanh toán

    fetch('/api/session/store_payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            medical_record_id: medicalRecordId,
            patient_name: patientName,
            appointment_date: appointmentDate,
            medical_fee: medicalFee,
            total_medicine_cost: totalMedicineCost,
            total_amount: totalAmount
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            alert(`✔ Thông tin thanh toán đã được lưu!\nTên: ${patientName}\nNgày khám: ${appointmentDate}\nTổng tiền: ${totalAmount} VND`);
        } else {
            alert("Có lỗi xảy ra: " + data.message);
        }
    })
    .catch(error => {
        console.log("Lỗi khi lưu thông tin thanh toán vào session:", error);
        alert("Có lỗi xảy ra, vui lòng thử lại!");
    });
}

function storePaymentInfo(medicalRecordId, patientName, appointmentDate, medicalFee, totalMedicineCost) {
    let totalAmount = parseFloat(medicalFee) + parseFloat(totalMedicineCost);

    fetch('/api/session/store_payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            medical_record_id: medicalRecordId,
            patient_name: patientName,
            appointment_date: appointmentDate,
            medical_fee: medicalFee,
            total_medicine_cost: totalMedicineCost,
            total_amount: totalAmount
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            console.log("✅ Đã lưu session, chuyển hướng...");
            window.location.href = `/invoice/${medicalRecordId}`;  // ✅ Chuyển hướng ngay sau khi lưu session
        } else {
            alert("Có lỗi xảy ra: " + data.message);
        }
    })
    .catch(error => {
        console.log("Lỗi khi lưu thông tin thanh toán vào session:", error);
        alert("Có lỗi xảy ra, vui lòng thử lại!");
    });
}

function redirectToPayment(medicalRecordId) {
    if (confirm("📌 Xác nhận thanh toán hóa đơn?")) {
        fetch('/api/process-payment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ medical_record_id: medicalRecordId })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                alert("✔ Hóa đơn đã được lưu vào hệ thống!");
                window.location.href = "/today-medical-records";  // ✅ Chuyển về danh sách phiếu khám
            } else {
                alert("❌ Có lỗi xảy ra: " + data.message);
            }
        })
        .catch(error => {
            console.log("Lỗi khi xử lý thanh toán:", error);
            alert("⚠ Có lỗi xảy ra, vui lòng thử lại!");
        });
    }
}