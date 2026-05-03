
import requests
import json
import sys
import os

# Fix lỗi encoding tiếng Việt trên Windows Terminal
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

# -------------------------------------------------------------------
# Hướng dẫn lấy Token để test nhóm C:
#   1. Chạy Frontend, bấm Đăng nhập Google.
#   2. Mở DevTools (F12) > Console > gõ:
#      firebase.auth().currentUser.getIdToken().then(t => console.log(t))
#   3. Copy chuỗi dài đó và dán vào biến ID_TOKEN bên dưới.
# -------------------------------------------------------------------
ID_TOKEN = os.environ.get("FIREBASE_TOKEN", "")  # Lấy từ biến môi trường hoặc để trống

# -------------------------------------------------------------------
# Màu sắc cho output Terminal đẹp hơn
# -------------------------------------------------------------------
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BLUE   = "\033[94m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

passed = 0
failed = 0
skipped = 0


def print_header(text):
    print(f"\n{BOLD}{CYAN}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{RESET}")


def print_result(test_name, success, response=None, error=None, skip=False):
    """In kết quả của từng test case."""
    global passed, failed, skipped
    if skip:
        skipped += 1
        print(f"  {YELLOW}⊘ SKIP{RESET} - {test_name} {YELLOW}(cần Token){RESET}")
        return
    if success:
        passed += 1
        print(f"  {GREEN}✓ PASS{RESET} - {test_name}")
    else:
        failed += 1
        print(f"  {RED}✗ FAIL{RESET} - {test_name}")
    if error:
        print(f"    {RED}Lỗi kết nối: {error}{RESET}")
    if response is not None:
        print(f"    {YELLOW}HTTP Status: {response.status_code}{RESET}")
        try:
            body = response.json()
            text = json.dumps(body, ensure_ascii=False, indent=2)
            # Giới hạn chiều dài cho dễ đọc
            if len(text) > 600:
                text = text[:600] + "\n    ... (cắt bớt)"
            print(f"    Response: {text}")
        except Exception:
            print(f"    Response: {response.text[:300]}")


# ===================================================================
# NHÓM A: CÁC ENDPOINT CÔNG KHAI (KHÔNG CẦN TOKEN)
# ===================================================================

print_header("NHÓM A: ENDPOINT CÔNG KHAI")

# A1: GET /
try:
    resp = requests.get(f"{BASE_URL}/")
    data = resp.json()
    # Kiểm tra đúng field mà main.py trả về: "system", "firebase_connected", "message"
    success = (
        resp.status_code == 200
        and "system" in data
        and "firebase_connected" in data
    )
    print_result("A1 - GET /  trả về thông tin hệ thống", success, resp)
except Exception as e:
    print_result("A1 - GET /  trả về thông tin hệ thống", False, error=str(e))


# A2: GET /health
try:
    resp = requests.get(f"{BASE_URL}/health")
    data = resp.json()
    # Kiểm tra đúng field mà main.py trả về: "status", "firebase"
    success = (
        resp.status_code == 200
        and data.get("status") == "healthy"
        and "firebase" in data
    )
    print_result("A2 - GET /health  báo trạng thái healthy", success, resp)
except Exception as e:
    print_result("A2 - GET /health  báo trạng thái healthy", False, error=str(e))


# ===================================================================
# NHÓM B: ENDPOINT TÌM KIẾM AI - POST /predict
# ===================================================================

print_header("NHÓM B: AI SEARCH - POST /predict")

# B1: Tìm kiếm bình thường - biển
try:
    payload = {"query": "bãi biển đẹp lặn san hô", "top_k": 5}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    data = resp.json()
    success = (
        resp.status_code == 200
        and isinstance(data, list)
        and len(data) > 0
        and all(k in data[0] for k in ["name", "score", "description"])
    )
    print_result("B1 - Tìm 'bãi biển đẹp lặn san hô' trả về kết quả AI", success, resp)
except Exception as e:
    print_result("B1 - Tìm 'bãi biển đẹp lặn san hô' trả về kết quả AI", False, error=str(e))


# B2: Tìm kiếm núi rừng
try:
    payload = {"query": "leo núi ngắm mây ruộng bậc thang", "top_k": 3}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    success = resp.status_code == 200 and isinstance(resp.json(), list)
    print_result("B2 - Tìm 'leo núi ngắm mây ruộng bậc thang'", success, resp)
except Exception as e:
    print_result("B2 - Tìm 'leo núi ngắm mây ruộng bậc thang'", False, error=str(e))


# B3: Tìm kiếm chùa
try:
    payload = {"query": "chùa cổ kính linh thiêng", "top_k": 3}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    success = resp.status_code == 200 and isinstance(resp.json(), list)
    print_result("B3 - Tìm 'chùa cổ kính linh thiêng'", success, resp)
except Exception as e:
    print_result("B3 - Tìm 'chùa cổ kính linh thiêng'", False, error=str(e))


# B4: Score phải nằm trong khoảng [0, 1]
try:
    payload = {"query": "ăn hải sản tươi sống", "top_k": 5}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    data = resp.json()
    scores_ok = all(0.0 <= item["score"] <= 1.0 for item in data)
    success = resp.status_code == 200 and scores_ok
    print_result("B4 - Điểm số (score) trả về nằm trong khoảng [0.0 - 1.0]", success, resp)
except Exception as e:
    print_result("B4 - Điểm số (score) trả về nằm trong khoảng [0.0 - 1.0]", False, error=str(e))


# B5: Số kết quả không vượt quá top_k yêu cầu
try:
    payload = {"query": "khu nghỉ dưỡng 5 sao", "top_k": 3}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    data = resp.json()
    success = resp.status_code == 200 and len(data) <= 3
    print_result("B5 - Số kết quả trả về không vượt quá top_k=3", success, resp)
except Exception as e:
    print_result("B5 - Số kết quả trả về không vượt quá top_k=3", False, error=str(e))


# ===================================================================
# NHÓM C: ENDPOINT BẢO MẬT (CẦN TOKEN) - /auth/me, /favorites, /history
# ===================================================================

print_header("NHÓM C: ENDPOINT BẢO MẬT (cần Firebase Token)")

if not ID_TOKEN:
    print(f"  {YELLOW}ℹ  Chưa có Token → Bỏ qua toàn bộ nhóm C.")
    print(f"     Xem hướng dẫn lấy Token ở đầu file test_api.py{RESET}")
    # Đánh dấu skip cho cả nhóm
    for name in [
        "C1 - GET /auth/me  trả về thông tin user",
        "C2 - GET /auth/me  không có Token → lỗi 403",
        "C3 - POST /favorites  lưu địa điểm yêu thích",
        "C4 - GET /favorites  đọc danh sách yêu thích",
        "C5 - GET /history  đọc lịch sử tìm kiếm",
    ]:
        print_result(name, False, skip=True)
else:
    auth_headers = {"Authorization": f"Bearer {ID_TOKEN}"}

    # C1: GET /auth/me - có Token
    try:
        resp = requests.get(f"{BASE_URL}/auth/me", headers=auth_headers)
        data = resp.json()
        success = (
            resp.status_code == 200
            and "uid" in data
            and "email" in data
        )
        print_result("C1 - GET /auth/me  trả về thông tin user", success, resp)
    except Exception as e:
        print_result("C1 - GET /auth/me  trả về thông tin user", False, error=str(e))

    # C2: GET /auth/me - không có Token → phải trả 403
    try:
        resp = requests.get(f"{BASE_URL}/auth/me")
        success = resp.status_code == 403
        print_result("C2 - GET /auth/me  không có Token → lỗi 403", success, resp)
    except Exception as e:
        print_result("C2 - GET /auth/me  không có Token → lỗi 403", False, error=str(e))

    # C3: POST /favorites - lưu địa điểm yêu thích
    try:
        payload = {"destination_id": 1, "destination_name": "Vịnh Hạ Long"}
        resp = requests.post(f"{BASE_URL}/favorites", json=payload, headers=auth_headers)
        success = resp.status_code == 200 and "message" in resp.json()
        print_result("C3 - POST /favorites  lưu địa điểm yêu thích", success, resp)
    except Exception as e:
        print_result("C3 - POST /favorites  lưu địa điểm yêu thích", False, error=str(e))

    # C4: GET /favorites - đọc danh sách yêu thích
    try:
        resp = requests.get(f"{BASE_URL}/favorites", headers=auth_headers)
        data = resp.json()
        success = resp.status_code == 200 and "favorites" in data
        print_result("C4 - GET /favorites  đọc danh sách yêu thích", success, resp)
    except Exception as e:
        print_result("C4 - GET /favorites  đọc danh sách yêu thích", False, error=str(e))

    # C5: GET /history - đọc lịch sử tìm kiếm
    try:
        resp = requests.get(f"{BASE_URL}/history", headers=auth_headers)
        data = resp.json()
        success = resp.status_code == 200 and "history" in data
        print_result("C5 - GET /history  đọc lịch sử tìm kiếm", success, resp)
    except Exception as e:
        print_result("C5 - GET /history  đọc lịch sử tìm kiếm", False, error=str(e))


# ===================================================================
# NHÓM D: KIỂM TRA LỖI / EDGE CASES
# ===================================================================

print_header("NHÓM D: KIỂM TRA LỖI & EDGE CASES")

# D1: Query rỗng → 422 Validation Error
try:
    resp = requests.post(f"{BASE_URL}/predict", json={"query": "", "top_k": 3})
    success = resp.status_code == 422
    print_result("D1 - Query rỗng  → lỗi 422 Validation", success, resp)
except Exception as e:
    print_result("D1 - Query rỗng  → lỗi 422 Validation", False, error=str(e))


# D2: top_k = 0 → 422
try:
    resp = requests.post(f"{BASE_URL}/predict", json={"query": "núi", "top_k": 0})
    success = resp.status_code == 422
    print_result("D2 - top_k=0  → lỗi 422 Validation", success, resp)
except Exception as e:
    print_result("D2 - top_k=0  → lỗi 422 Validation", False, error=str(e))


# D3: top_k vượt 20 → 422
try:
    resp = requests.post(f"{BASE_URL}/predict", json={"query": "thác nước", "top_k": 100})
    success = resp.status_code == 422
    print_result("D3 - top_k=100  → lỗi 422 Validation", success, resp)
except Exception as e:
    print_result("D3 - top_k=100  → lỗi 422 Validation", False, error=str(e))


# D4: Thiếu body → 422
try:
    resp = requests.post(f"{BASE_URL}/predict")
    success = resp.status_code == 422
    print_result("D4 - Thiếu request body  → lỗi 422", success, resp)
except Exception as e:
    print_result("D4 - Thiếu request body  → lỗi 422", False, error=str(e))


# D5: Sai định dạng JSON → 422
try:
    resp = requests.post(
        f"{BASE_URL}/predict",
        data="not a json string",
        headers={"Content-Type": "application/json"}
    )
    success = resp.status_code == 422
    print_result("D5 - Sai định dạng JSON  → lỗi 422", success, resp)
except Exception as e:
    print_result("D5 - Sai định dạng JSON  → lỗi 422", False, error=str(e))


# D6: Endpoint không tồn tại → 404
try:
    resp = requests.get(f"{BASE_URL}/khong-ton-tai")
    success = resp.status_code == 404
    print_result("D6 - Endpoint không tồn tại  → lỗi 404", success, resp)
except Exception as e:
    print_result("D6 - Endpoint không tồn tại  → lỗi 404", False, error=str(e))


# ===================================================================
# TỔNG KẾT
# ===================================================================
total = passed + failed + skipped
print(f"\n{BOLD}{CYAN}{'='*60}")
print(f"  TỔNG KẾT KẾT QUẢ KIỂM THỬ")
print(f"{'='*60}{RESET}")
print(f"  {GREEN}✓ Passed : {passed}{RESET}")
print(f"  {RED}✗ Failed : {failed}{RESET}")
print(f"  {YELLOW}⊘ Skipped: {skipped}  (cần Token để chạy){RESET}")
print(f"  Tổng cộng: {total} test cases")
print(f"{CYAN}{'='*60}{RESET}\n")

if failed > 0:
    print(f"  {RED}{BOLD}❌ Có {failed} test(s) FAIL. Kiểm tra lại Backend!{RESET}\n")
    sys.exit(1)
else:
    print(f"  {GREEN}{BOLD}🎉 Tất cả test đều PASS hoặc SKIP (cần Token)!{RESET}\n")
    sys.exit(0)
