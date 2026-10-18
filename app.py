"""A simple realtime Digital Twin dashboard with saved comparison metrics."""
import json
import pandas as pd
import streamlit as st
from get_data import ROOT
from controllers import POLICIES
from live_dashboard import show_realtime

LABELS = {'fixed_time': 'Đèn cố định', 'direct_adaptive': 'Điều chỉnh theo hàng đợi',
          'digital_twin': 'Digital Twin + ML'}


def load_artifacts():
    return (
        pd.read_csv(ROOT / 'data/traffic_counts.csv'),
        json.loads((ROOT / 'data/source_metadata.json').read_text()),
        pd.read_csv(ROOT / 'results/summary.csv'),
        {p: pd.read_csv(ROOT / f'results/timeseries_{p}.csv') for p in POLICIES},
        pd.read_csv(ROOT / 'results/decisions_digital_twin.csv'),
    )


def main():
    st.set_page_config(page_title='Mô phỏng đèn giao thông — Digital Twin', layout='wide')
    st.markdown('<style>.block-container{padding-top:2rem}</style>', unsafe_allow_html=True)
    st.title('Mô phỏng điều khiển đèn giao thông bằng Digital Twin')
    st.write('Quan sát hàng đợi, lựa chọn thời gian đèn xanh và kết quả xe đi qua trong từng tình huống mô phỏng.')
    try:
        counts, metadata, summary, logs, decisions = load_artifacts()
    except FileNotFoundError:
        st.error('Chạy python3 start.py để tự chuẩn bị dữ liệu và mở demo.')
        st.stop()

    st.header('1. Mô phỏng giao lộ')
    show_realtime()
    st.caption('Môi trường và Twin đang được Python tính dần từng giây, cảm biến ảo cập nhật mỗi giây. Xe đến được giả lập từ tổng lưu lượng 15 phút; không có cảm biến giao thông thật.')

    st.header('2. Cách này có giúp xe bớt chờ không?')
    st.write('Bảng dưới là kết quả so sánh đã chạy đủ hai giờ trên cùng lượng xe đến, độc lập với lượt giả lập thời gian thực phía trên. Xem tổng thời gian xe phải xếp hàng và số xe còn chưa đi hết.')
    readable = summary[['policy', 'total_waiting_vehicle_seconds', 'total_served', 'final_backlog']].copy()
    readable['policy'] = readable.policy.map(LABELS)
    readable.columns = ['Cách điều khiển', 'Tổng chờ (xe·giây)', 'Xe đã đi qua', 'Xe còn chờ cuối buổi']
    st.dataframe(readable, hide_index=True, width='stretch')
    st.caption('Ví dụ: 10 xe cùng chờ 3 giây = 30 xe·giây. Số nhỏ hơn nghĩa là tổng chờ ít hơn. Kết quả này thuộc mô phỏng; không đảm bảo hiệu quả ngoài thực tế.')
    with st.expander('Xem biểu đồ và cách hoạt động của ba bộ điều khiển'):
        st.write('**Đèn cố định:** mỗi hướng xanh 30 giây. **Điều chỉnh theo hàng đợi:** nhìn số xe đang chờ để chọn xanh ngắn hoặc dài. **Digital Twin + ML:** dự báo xe sắp tới, thử ba phương án trong bản sao rồi chọn.')
        waiting = summary.set_index('policy').total_waiting_vehicle_seconds.rename(index=LABELS)
        st.bar_chart(waiting, y_label='Tổng chờ mô phỏng (xe·giây)')
        chart = pd.DataFrame({LABELS[p]: f.queue_NS + f.queue_EW for p, f in logs.items()})
        chart.index = logs['digital_twin'].time
        st.line_chart(chart, x_label='Giây mô phỏng', y_label='Tổng xe đang chờ')

    st.header('3. Xe trong demo đến từ đâu?')
    st.write('Nguồn công bố có **8 mốc đếm xe, mỗi mốc 15 phút, từ 07:00 đến 09:00**. Demo phân bổ các tổng xe này thành từng giây để tạo lượt xe đến. Số xe từng mốc được giữ nguyên.')
    with st.expander('Xem bảng dữ liệu gốc'):
        st.markdown(f"Nguồn: [HCM Guide — Exhibit 2-27]({metadata['source_url']})")
        method = 'Đã lấy trực tiếp từ trang nguồn' if metadata['acquisition_method'] == 'web_extracted' else 'Dùng bảng dự phòng đã đối chiếu nguồn'
        st.write(method)
        if metadata['retrieval_error']:
            st.caption(f"Lỗi truy xuất: {metadata['retrieval_error']}")
        st.dataframe(counts, hide_index=True, width='stretch')
        st.bar_chart(counts.set_index('start_time')[['arrivals_NS', 'arrivals_EW']])


if __name__ == '__main__':
    main()
