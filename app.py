"""A beginner-friendly replay; all counts and decisions come from saved logs."""
import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from get_data import ROOT
from controllers import POLICIES
from dashboard_player import player_html

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
    st.set_page_config(page_title='Giao lộ thông minh — Digital Twin', layout='wide')
    st.markdown('<style>.block-container{padding-top:2rem}</style>', unsafe_allow_html=True)
    st.title('Giao lộ thông minh hoạt động như thế nào?')
    st.write('Hãy xem xe đến giao lộ, chờ đèn và đi qua. **Digital Twin** là bản sao số giúp thử các cách bật đèn trước khi áp dụng vào giao lộ.')
    try:
        counts, metadata, summary, logs, decisions = load_artifacts()
    except FileNotFoundError:
        st.error('Chạy python3 start.py để tự chuẩn bị dữ liệu và mở demo.')
        st.stop()

    st.header('1. Bấm bắt đầu để xem từng case')
    components.html(player_html(logs['digital_twin'], decisions), height=1510, scrolling=True)
    st.caption('Demo minh họa: Python thay giao lộ thật; cảm biến là cảm biến ảo. Hình xe phát lại kết quả đã mô phỏng, không phải camera hoặc dữ liệu giao thông trực tiếp.')

    st.header('2. Cách này có giúp xe bớt chờ không?')
    st.write('Cùng một lượng xe đến, thử ba cách điều khiển trong hai giờ mô phỏng. Xem tổng thời gian xe phải xếp hàng và số xe còn chưa đi hết.')
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
    with st.expander('Xem bảng dữ liệu và thông tin kỹ thuật'):
        st.markdown(f"Nguồn: [HCM Guide — Exhibit 2-27]({metadata['source_url']})")
        method = 'Đã lấy trực tiếp từ trang nguồn' if metadata['acquisition_method'] == 'web_extracted' else 'Dùng bảng dự phòng đã đối chiếu nguồn'
        st.write(method)
        if metadata['retrieval_error']:
            st.caption(f"Lỗi truy xuất: {metadata['retrieval_error']}")
        st.dataframe(counts, hide_index=True, width='stretch')
        st.bar_chart(counts.set_index('start_time')[['arrivals_NS', 'arrivals_EW']])
        st.write('ML là hồi quy Ridge nhỏ, học dần từ các lượt xe đã quan sát. Dự báo được kết hợp với trung bình quá khứ; không đọc trước lượt xe tương lai. Twin cập nhật mỗi 10 giây và tại điểm chọn đèn. Mỗi phương án 15/30/45 giây được đánh giá trên cùng 120 giây tương lai.')
        st.caption('Bản phát lại bắt đầu sau giai đoạn học ban đầu và có 5 case độc lập. Mỗi case dừng sau khoảng xanh để xem phản hồi; chỉ chuyển case khi bấm nút. Xe vẽ trên hai đường đại diện hai nhóm NS/EW; không tái tạo chính xác các làn hoặc hướng rẽ. Tổng chờ tính từ hàng đợi sau phục vụ mỗi giây. Các xe còn lại cuối hai giờ được báo cáo riêng, không giả định đã đi hết.')


if __name__ == '__main__':
    main()
