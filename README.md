# Traffic Digital Twin — Demo giao lộ thông minh

Demo Digital Twin nhỏ cho đồ án IoT/AIoT, chạy hoàn toàn trên máy cá nhân. **Chỉ cần bấm “Bắt đầu demo”** để xem xe đến, xếp hàng, bản sao số dự báo và thử phương án, đèn thay đổi và xe đi qua giao lộ.

- Một giao lộ, hai nhóm hướng: Bắc–Nam (NS) và Đông–Tây (EW).
- Digital Twin có trạng thái riêng, nhận quan sát từ môi trường mô phỏng.
- ML nhẹ: hồi quy Ridge học dần từ các lượt xe đã đến, không dùng dữ liệu tương lai.
- So sánh ba bộ điều khiển trên cùng lượt xe: đèn cố định, điều chỉnh theo hàng đợi, Digital Twin + ML.
- Không cần GPU, phần cứng IoT, camera, database hay dịch vụ trả phí.

## 1. Chuẩn bị

Cần **Python 3.11 trở lên**, trình duyệt và Internet để cài thư viện lần đầu. Cần Git nếu tải bằng `git clone`; nếu tải ZIP trên GitHub thì không cần Git.

Kiểm tra phiên bản:

```bash
python3 --version
```

Trên Windows:

```powershell
py --version
```

Ubuntu/WSL nếu chưa có Python hoặc `venv`:

```bash
sudo apt update
sudo apt install python3 python3-venv git
```

Python sau khi cài vẫn phải từ 3.11 trở lên. Nếu máy đã có `uv`, trình khởi động cũng có thể dùng `uv` để tạo môi trường khi `venv` không có `ensurepip`.

## 2. Tải mã nguồn

Tải repository bằng HTTPS:

```bash
git clone https://github.com/phuonganh-ngn/traffic-digital-twin-demo.git
cd traffic-digital-twin-demo
```

Nếu tài khoản đã có SSH key trên GitHub, có thể dùng `git clone git@github.com:phuonganh-ngn/traffic-digital-twin-demo.git`.

Hoặc chọn **Code → Download ZIP**, giải nén rồi mở Terminal/PowerShell trong thư mục chứa `start.py`.

## 3. Chạy bằng một lệnh

**Linux / macOS / Ubuntu / WSL:**

```bash
python3 start.py
```

**Windows PowerShell / CMD:**

```powershell
py start.py
```

Nếu Windows đã nhận lệnh `python` nhưng không có `py`, dùng `python start.py`.

Script tự tạo môi trường `.venv`, cài thư viện còn thiếu, chuẩn bị lượt xe, chạy mô phỏng cả ba chính sách, tạo báo cáo và khởi động dashboard. Không cần kích hoạt môi trường hoặc cài riêng Streamlit. Lần đầu có thể mất vài phút để cài thư viện; các lần sau vẫn dùng một lệnh trên.

Sau khi terminal hiện địa chỉ, mở **http://localhost:8501**. Giữ terminal đang chạy trong lúc dùng dashboard. Nhấn **Ctrl+C** tại terminal để tắt. `localhost` là máy đang chạy chương trình, không phải website công khai trên Internet.

Repository có sẵn dữ liệu và log của một lần chạy. Trình khởi động dùng lại bảng nguồn đã lưu và sinh lại lượt xe, mô phỏng. Nếu thiếu bảng nguồn hoặc metadata, nó chạy bước lấy dữ liệu; nếu trang nguồn không truy cập được, có bảng dự phòng và ghi rõ phương thức lấy dữ liệu.

## 4. Cách sử dụng và thuyết trình

1. Mở **http://localhost:8501**, bấm **▶ Bắt đầu demo**.
2. Theo dõi flow tự chạy, không cần chọn thông số:

   **Xe đến → Quan sát → Đồng bộ bản sao → Dự báo và thử đèn → Chọn đèn → Xe đi và phản hồi ↺**

3. Bên trái là giao lộ, xe chờ, đèn đỏ–vàng–xanh và giây còn lại của pha. Bên phải là bản sao số, lưu lượng dự báo và điểm của ba phương án xanh 15/30/45 giây. Lời giải thích tiếng Việt tự thay đổi theo từng bước.
4. Phía trên có **khung giờ của đoạn demo**, **giờ đang xem**, **lượt trong đoạn demo** và **số thứ tự quyết định trên toàn buổi 07:00–09:00**. Ví dụ “1/5 lượt trong demo” và “Lượt 4/207 của cả buổi” là hai số đếm khác nhau.
5. Bấm **Ⅱ Tạm dừng** để đọc hoặc giải thích; bấm **▶ Tiếp tục** để chạy tiếp. **↺ Xem lại** trở về đầu và chờ bấm bắt đầu.
6. Đoạn demo phát lại **5 quyết định**, bắt đầu sau giai đoạn học ban đầu của ML, rồi tự dừng. Đoạn xe di chuyển ở tốc độ **2×**; các bước giải thích tạm dừng đồng hồ mô phỏng để người xem đọc.
7. Kéo xuống xem bảng so sánh ba bộ điều khiển. Mở các mục thu gọn để xem biểu đồ, dữ liệu nguồn và giải thích kỹ thuật.

Xe đầu hàng đi qua khi được phục vụ, xe sau tiến lên và xe mới nhập cuối hàng. Hàng đợi chỉ vẽ tối đa **4 xe mỗi nhóm** để hình dễ đọc; **số đếm mới là hàng đợi đầy đủ**. Xe đã đi qua vạch tiếp tục ra khỏi khung. Hai đường minh họa hai nhóm hướng, không tái tạo chính xác làn đường/hướng rẽ của giao lộ nguồn.

**Gợi ý lời giới thiệu:** “Giao lộ mô phỏng gửi số xe chờ cho một bản sao số. Bản sao dùng ML ước lượng xe sắp đến, thử ba thời lượng đèn xanh rồi chọn phương án có tổng chờ dự báo thấp nhất. Sau khi áp dụng, giao lộ gửi quan sát mới trở lại bản sao.”

## 5. Dữ liệu và cách đọc kết quả

Nguồn: [HCM Guide, Exhibit 2-27 — Shenendehowa Campus AM peak volumes](https://hcmguide.com/Case2/techprob03/subproblem03a/prob3a2.htm).

- **Dữ liệu quan sát thật:** 8 tổng xe theo 15 phút từ 07:00 đến 09:00, tổng cộng 3.785 xe; giữ nguyên số xe nhỏ ở hướng Nam.
- **Dữ liệu tổng hợp:** phân bổ xe vào 7.200 giây bằng multinomial, seed 42, bảo toàn chính xác tổng xe từng khoảng.
- **Kết quả mô phỏng:** hàng đợi, tín hiệu đèn, số xe phục vụ và tổng chờ. Đây không phải phép đo hàng đợi hoặc độ trễ ngoài thực địa.
- **Nguồn gốc dữ liệu:** `data/source_metadata.json` ghi thời điểm lấy, URL và trạng thái `web_extracted` hoặc `fallback_from_published_table`. Chạy demo từ dữ liệu đã lưu không đồng nghĩa vừa lấy lại từ web.

Kết quả đã tạo trong repository:

| Bộ điều khiển | Tổng chờ (xe·giây) | Xe đã đi qua | Xe còn chờ cuối buổi |
|---|---:|---:|---:|
| Đèn cố định | 1.197.927 | 3.416 | 369 |
| Điều chỉnh theo hàng đợi | 82.447 | 3.778 | 7 |
| Digital Twin + ML | 42.973 | 3.781 | 4 |

Tổng chờ là tổng hàng đợi sau phục vụ mỗi giây. Ví dụ 10 xe cùng chờ 3 giây = 30 xe·giây. Dừng đúng 7.200 giây, không tự coi xe còn lại là đã đi hết. Các chính sách dùng cùng chuỗi xe đến, năng lực phục vụ và thời gian vàng/đỏ. Twin không được đảm bảo luôn thắng; bảng kết quả thực của mỗi lần chạy nằm trong `results/summary.csv`.

ML là Ridge nhỏ bằng NumPy, học từ các khối 10 giây đã quan sát. Sau ít nhất sáu mẫu học, dự báo không âm được kết hợp 50/50 với trung bình quá khứ tối đa 60 giây. Trong thời gian khởi động dùng trung bình đã quan sát. Twin thử 15/30/45 giây trên cùng chân trời 120 giây, có tính vàng 3 giây, đỏ toàn bộ 2 giây và các pha đối diện; những pha xanh tiếp theo dùng mặc định 30 giây.

## 6. Cấu trúc dự án

```text
start.py                    # Khởi động bằng một lệnh
app.py                      # Dashboard Streamlit, đọc log đã lưu
dashboard_player.py         # Giao lộ, chuyển động xe và phát lại flow
get_data.py                 # Lấy bảng nguồn hoặc bảng dự phòng, ghi metadata
prepare_arrivals.py         # Phân bổ tổng xe thành lượt đến từng giây
simulator.py                # Môi trường giao lộ, hàng đợi và chu kỳ đèn
digital_twin.py             # Trạng thái Twin, ML và dự báo what-if
controllers.py              # Ba chính sách điều khiển
run_demo.py                 # Chạy so sánh, lưu log và tạo báo cáo
requirements.txt            # Thư viện cần cài
data/                       # Bảng nguồn, metadata và lượt xe đến
results/                    # Kết quả, log từng giây/quyết định/đồng bộ
docs/ARCHITECTURE.md         # Sơ đồ và giải thích kiến trúc
docs/REPORT_SECTION_2_7.md   # Báo cáo tiếng Anh từ kết quả đã chạy
tests/test_demo.py          # Kiểm tra tính đúng của demo
flow.md                     # Yêu cầu ban đầu; ML/UI được bổ sung sau
```

Không đưa `.venv`, cache Python, thông tin tài khoản hoặc file `.env` lên Git.

## 7. Chạy từng bước hoặc kiểm tra

Thường chỉ cần `start.py`. Nếu muốn chạy lại từng bước sau khi môi trường đã được tạo:

**Linux/macOS/WSL:**

```bash
.venv/bin/python get_data.py
.venv/bin/python prepare_arrivals.py
.venv/bin/python run_demo.py
.venv/bin/python -m pytest -q
.venv/bin/python -m streamlit run app.py
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe get_data.py
.\.venv\Scripts\python.exe prepare_arrivals.py
.\.venv\Scripts\python.exe run_demo.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

`get_data.py` yêu cầu lấy lại bảng nguồn và ghi lại metadata. `run_demo.py` tạo lại CSV kết quả và [báo cáo mục 2.7](docs/REPORT_SECTION_2_7.md). Bộ test kiểm tra bảng nguồn, bảo toàn số xe, chu kỳ đèn, đầu vào giống nhau, Twin tách biệt, không dùng tương lai và dashboard đọc đúng log. Lần kiểm tra hiện tại: **11 tests pass**. Playwright chỉ được dùng khi phát triển để kiểm tra giao diện, không cần cài để chạy demo.

## 8. Lỗi thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| `python` không tìm thấy trên Linux | Dùng `python3 start.py`. |
| Python thấp hơn 3.11 | Cài Python 3.11+ rồi chạy lại bằng phiên bản mới. |
| `ensurepip is not available` | Ubuntu/WSL: cài `python3-venv`, hoặc dùng `uv` đã có. Nếu `.venv` bị tạo dở, đổi tên thư mục đó trước khi chạy lại. |
| Cài thư viện thất bại | Kiểm tra kết nối Internet và chạy lại `start.py`; chương trình tự cài khi còn thiếu thư viện. |
| `Port 8501 is not available` | Có phiên dashboard khác đang chạy: mở http://localhost:8501 hoặc Ctrl+C ở terminal cũ trước khi chạy lại. |
| Muốn dùng cổng khác | Sau khi có dữ liệu, chạy `.venv/bin/python -m streamlit run app.py --server.port 8502` rồi mở http://localhost:8502. Windows thay `.venv/bin/python` bằng `.\.venv\Scripts\python.exe`. |
| Vẫn thấy giao diện cũ | Nhấn Ctrl+F5. Nếu vừa thay mã nguồn, dừng server bằng Ctrl+C rồi chạy lại `start.py`. |
| Không lấy được bảng nguồn | Script tự dùng bảng dự phòng và ghi rõ lỗi trong metadata; không cần sửa số liệu. |
| Không mở được web sau khi dừng terminal | Chạy lại `start.py`; dashboard cần server đang hoạt động. |

## 9. Phạm vi và giới hạn

Đây là prototype offline: Python thay giao lộ thực; cảm biến ảo lý tưởng; không có camera, video, phần cứng hoặc cấu trúc giao lộ thật. ML chưa được kiểm định cho dự báo giao thông thực tế. Đồ họa phát lại log, không trực tiếp điều khiển thiết bị. Kết quả minh họa nguyên lý quan sát → đồng bộ → thử phương án → quyết định → phản hồi của Digital Twin, không chứng minh mức giảm tắc đường ngoài thực địa.
