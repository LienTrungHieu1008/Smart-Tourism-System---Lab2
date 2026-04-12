"""
File kiểm thử API bằng thư viện requests.
Chạy: python test_api.py
Yêu cầu: Server đang chạy tại http://127.0.0.1:8000
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

passed = 0
failed = 0


def print_header(text):
    print(f"\n{BOLD}{CYAN}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{RESET}")


def print_result(test_name, success, response=None, error=None):
    global passed, failed
    if success:
        passed += 1
        print(f"  {GREEN}✓ PASS{RESET} - {test_name}")
    else:
        failed += 1
        print(f"  {RED}✗ FAIL{RESET} - {test_name}")
    if error:
        print(f"    {RED}Lỗi: {error}{RESET}")
    if response is not None:
        print(f"    {YELLOW}Status: {response.status_code}{RESET}")
        try:
            body = response.json()
            # Giới hạn output cho dễ đọc
            text = json.dumps(body, ensure_ascii=False, indent=4)
            if len(text) > 800:
                text = text[:800] + "\n    ... (truncated)"
            print(f"    Response: {text}")
        except Exception:
            print(f"    Response: {response.text[:300]}")


# ============================================================
# TEST 1: GET / - Thông tin giới thiệu hệ thống
# ============================================================
print_header("TEST 1: GET / - Thông tin giới thiệu hệ thống")

try:
    resp = requests.get(f"{BASE_URL}/")
    data = resp.json()
    success = (
        resp.status_code == 200
        and "system" in data
        and "model" in data
        and "endpoints" in data
    )
    print_result("Trang chủ trả về thông tin giới thiệu JSON", success, resp)
except Exception as e:
    print_result("Trang chủ trả về thông tin giới thiệu JSON", False, error=str(e))


# ============================================================
# TEST 2: GET /health - Kiểm tra sức khỏe server
# ============================================================
print_header("TEST 2: GET /health - Kiểm tra sức khỏe server")

try:
    resp = requests.get(f"{BASE_URL}/health")
    data = resp.json()
    success = (
        resp.status_code == 200
        and data.get("status") == "healthy"
        and "total_destinations" in data
        and "model_name" in data
    )
    print_result("Health check trả về status healthy", success, resp)
except Exception as e:
    print_result("Health check trả về status healthy", False, error=str(e))


# ============================================================
# TEST 3: POST /predict - Tìm kiếm địa điểm biển (input 1)
# ============================================================
print_header("TEST 3: POST /predict - Tìm kiếm 'bãi biển đẹp lặn san hô'")

try:
    payload = {"query": "bãi biển đẹp lặn san hô", "top_k": 5}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    data = resp.json()
    success = (
        resp.status_code == 200
        and isinstance(data, list)
        and len(data) > 0
        and "name" in data[0]
        and "score" in data[0]
        and "description" in data[0]
    )
    print_result("Tìm kiếm 'bãi biển đẹp lặn san hô' trả về kết quả", success, resp)
except Exception as e:
    print_result("Tìm kiếm 'bãi biển đẹp lặn san hô' trả về kết quả", False, error=str(e))


# ============================================================
# TEST 4: POST /predict - Tìm kiếm núi rừng (input 2)
# ============================================================
print_header("TEST 4: POST /predict - Tìm kiếm 'leo núi ngắm mây ruộng bậc thang'")

try:
    payload = {"query": "leo núi ngắm mây ruộng bậc thang", "top_k": 3}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    data = resp.json()
    success = (
        resp.status_code == 200
        and isinstance(data, list)
        and len(data) > 0
    )
    print_result("Tìm kiếm 'leo núi ngắm mây ruộng bậc thang' thành công", success, resp)
except Exception as e:
    print_result("Tìm kiếm 'leo núi ngắm mây ruộng bậc thang' thành công", False, error=str(e))


# ============================================================
# TEST 5: POST /predict - Tìm kiếm di tích lịch sử (input 3)
# ============================================================
print_header("TEST 5: POST /predict - Tìm kiếm 'chùa cổ kính linh thiêng'")

try:
    payload = {"query": "chùa cổ kính linh thiêng", "top_k": 3}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    data = resp.json()
    success = (
        resp.status_code == 200
        and isinstance(data, list)
        and len(data) > 0
    )
    print_result("Tìm kiếm 'chùa cổ kính linh thiêng' thành công", success, resp)
except Exception as e:
    print_result("Tìm kiếm 'chùa cổ kính linh thiêng' thành công", False, error=str(e))


# ============================================================
# TEST 6: POST /predict - Query rỗng (Validation Error)
# ============================================================
print_header("TEST 6: POST /predict - Query rỗng (lỗi validation)")

try:
    payload = {"query": "", "top_k": 3}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    # Pydantic sẽ validate min_length=1, trả về 422
    success = resp.status_code == 422
    print_result("Query rỗng trả về lỗi 422", success, resp)
except Exception as e:
    print_result("Query rỗng trả về lỗi 422", False, error=str(e))


# ============================================================
# TEST 7: POST /predict - Query chỉ có khoảng trắng (lỗi 400)
# ============================================================
print_header("TEST 7: POST /predict - Query chỉ khoảng trắng (lỗi 400)")

try:
    payload = {"query": "   ", "top_k": 3}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    # Server kiểm tra .strip() và raise 400
    success = resp.status_code == 400
    print_result("Query khoảng trắng trả về lỗi 400", success, resp)
except Exception as e:
    print_result("Query khoảng trắng trả về lỗi 400", False, error=str(e))


# ============================================================
# TEST 8: POST /predict - top_k = 0 (Validation Error)
# ============================================================
print_header("TEST 8: POST /predict - top_k = 0 (lỗi validation)")

try:
    payload = {"query": "núi", "top_k": 0}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    # Pydantic validate gt=0, trả về 422
    success = resp.status_code == 422
    print_result("top_k=0 trả về lỗi 422", success, resp)
except Exception as e:
    print_result("top_k=0 trả về lỗi 422", False, error=str(e))


# ============================================================
# TEST 9: POST /predict - top_k vượt giới hạn (le=20)
# ============================================================
print_header("TEST 9: POST /predict - top_k = 100 (vượt le=20)")

try:
    payload = {"query": "thác nước", "top_k": 100}
    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    # Pydantic validate le=20, trả về 422
    success = resp.status_code == 422
    print_result("top_k=100 trả về lỗi 422", success, resp)
except Exception as e:
    print_result("top_k=100 trả về lỗi 422", False, error=str(e))


# ============================================================
# TEST 10: POST /predict - Thiếu request body
# ============================================================
print_header("TEST 10: POST /predict - Thiếu request body")

try:
    resp = requests.post(f"{BASE_URL}/predict")
    success = resp.status_code == 422
    print_result("Thiếu body trả về lỗi 422", success, resp)
except Exception as e:
    print_result("Thiếu body trả về lỗi 422", False, error=str(e))


# ============================================================
# TEST 11: POST /predict - Sai định dạng JSON
# ============================================================
print_header("TEST 11: POST /predict - Sai định dạng request body")

try:
    resp = requests.post(
        f"{BASE_URL}/predict",
        data="not a json",
        headers={"Content-Type": "application/json"}
    )
    success = resp.status_code == 422
    print_result("Sai định dạng JSON trả về lỗi 422", success, resp)
except Exception as e:
    print_result("Sai định dạng JSON trả về lỗi 422", False, error=str(e))


# ============================================================
# TỔNG KẾT
# ============================================================
print(f"\n{BOLD}{CYAN}{'='*60}")
print(f"  TỔNG KẾT KẾT QUẢ KIỂM THỬ")
print(f"{'='*60}{RESET}")
print(f"  {GREEN} Passed: {passed}{RESET}")
print(f"  {RED} Failed: {failed}{RESET}")
print(f"  Tổng cộng: {passed + failed} test cases")
print(f"{CYAN}{'='*60}{RESET}\n")

if failed > 0:
    sys.exit(1)
else:
    print(f"  {GREEN}{BOLD} Tất cả test cases đều PASS!{RESET}\n")
    sys.exit(0)
