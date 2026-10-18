"""Reuse the same road/car visuals, fed by a running Python environment."""
from functools import lru_cache
import json

from dashboard_player import TEMPLATE


@lru_cache(maxsize=1)
def live_html():
    markup, script = TEMPLATE.split('<script>', 1)
    # Car identities, exact arrival/departure animation, and responsive layout
    # are shared with the offline case player; state/controls here are live.
    drawing = script[:script.index('function explainTraffic')]
    dummy = dict(frames=[dict(time=0, queue_NS=0, queue_EW=0)], decisions=[], end=7200)
    drawing = drawing.replace('__DATA__', json.dumps(dummy))
    markup = markup.replace('MỘT GIAO LỘ · MỘT VÒNG ĐIỀU KHIỂN', 'GIẢ LẬP THỜI GIAN THỰC · CẢM BIẾN ẢO')
    markup = markup.replace('Xe đang chờ. Twin sẽ chọn đèn thế nào?', 'Giao lộ hoạt động liên tục')
    markup = markup.replace('Mỗi case bắt đầu từ một hàng đợi riêng. Xem chọn đèn, xe đi qua và phản hồi; demo dừng ở cuối case.', 'Bấm bắt đầu: xe đến từng giây, cảm biến đếm xe, Twin chọn đèn. 1 giây mô phỏng ≈ 1 giây thực.')
    markup = markup.replace('▶ Bắt đầu case', '▶ Bắt đầu real-time').replace('↺ Xem lại case', '↺ Chạy lại từ 07:00').replace('Khởi động lại case hiện tại', 'Bắt đầu lại mô phỏng từ 07:00')
    markup = markup.replace('<button id="next-case" class="secondary" disabled>Case tiếp theo →</button>', '')
    markup = markup.replace('KHUNG GIỜ CASE NÀY', 'KHUNG GIỜ MÔ PHỎNG').replace('CASE ĐANG XEM', 'QUYẾT ĐỊNH ĐÈN')
    markup = markup.replace('Sẵn sàng phát lại · tốc độ xe 2×', 'Sẵn sàng · tốc độ 1×')
    markup = markup.replace('Nhận số xe chờ, dự báo và thử phương án trước khi ra lệnh.', 'Cảm biến ảo gửi số xe mỗi giây. Twin thử phương án mới khi bắt đầu một pha xanh.')
    start = markup.index('<div class="footer">')
    markup = markup[:start] + '<div class="footer">Đây là mô phỏng đang được tính từng giây trên máy, không phải log phát lại hay giao lộ thật. Tổng xe 15 phút là dữ liệu công bố; thời điểm xe đến từng giây là giả lập. Mỗi hình xe = 1 xe. Giữ trang đang kết nối để chạy; tạm dừng sẽ dừng đồng hồ mô phỏng.</div></div>'
    return markup + '<script>' + drawing + LIVE_JS + '</script></body></html>'


LIVE_JS = r'''
let liveEpoch=null,liveState=null,commandPending=false;
function requestAction(action){
 if(commandPending)return;
 commandPending=true;$('play').disabled=true;$('reset').disabled=true;
 window.parent.postMessage({type:'traffic:action',action},'*');
}
$('play').onclick=()=>requestAction(liveState&&liveState.running?'pause':'start');
$('reset').onclick=()=>requestAction('reset');
function clearLiveCars(){
 $('cars').querySelectorAll('.car').forEach(el=>{el.getAnimations().forEach(a=>a.cancel());el.remove();});
 visualQueues.NS=[];visualQueues.EW=[];lastSceneTime=null;frames.clear();
 replayServed.NS=0;replayServed.EW=0;
}
function liveHeight(){
 window.parent.postMessage({type:'traffic:height',height:document.querySelector('.shell').getBoundingClientRect().height+2},'*');
}
if('ResizeObserver' in window)new ResizeObserver(()=>requestAnimationFrame(liveHeight)).observe(document.querySelector('.shell'));
window.addEventListener('resize',()=>requestAnimationFrame(liveHeight));
function renderLive(s){
 const row=s.current,d=s.decision;
 if(liveEpoch!==s.epoch){clearLiveCars();queueLayout.NS.step=32;queueLayout.EW.step=36;liveEpoch=s.epoch;}
 for(const r of s.frames)frames.set(r.time,r);
 // Reconnection uses the current sensor snapshot; do not invent missed animations.
 if(lastSceneTime!==null&&row.time>lastSceneTime){
  for(let t=lastSceneTime+1;t<=row.time;t++)if(!frames.has(t)){clearLiveCars();for(const r of s.frames)frames.set(r.time,r);break;}
 }
 for(const g of ['NS','EW']){
  const maximum=Math.max(1,row['queue_'+g],...visualQueues[g].map((_,i)=>i+1));
  const normal=g==='NS'?32:36,available=g==='NS'?112:208;
  queueLayout[g].step=Math.min(queueLayout[g].step,normal,available/Math.max(1,maximum-1));
  queueLayout[g].scale=queueLayout[g].step/normal;
 }
 running=s.running;stage=5;
 document.getAnimations().forEach(a=>running?a.play():a.pause());
 updateCars(row,true);resizeCars();
 replayServed.NS=s.total_served.NS;replayServed.EW=s.total_served.EW;
 // Bound the browser-side packet buffer; the Python model owns the full state.
 for(const t of frames.keys())if(t<row.time-65)frames.delete(t);
 $('play').disabled=false;$('reset').disabled=false;commandPending=false;
 $('play').textContent=s.finished?'Đã hết 2 giờ mô phỏng':running?'Ⅱ Tạm dừng':'▶ '+(row.time?'Tiếp tục real-time':'Bắt đầu real-time');
 $('play').disabled=s.finished;
 $('ns').textContent=`Bắc–Nam: ${row.queue_NS} xe chờ`;$('ew').textContent=`Đông–Tây: ${row.queue_EW} xe chờ`;
 $('clock').textContent='1 hình xe = 1 xe · số đếm cảm biến ảo';
 $('window').textContent='07:00:00–09:00:00';$('now').textContent=clock(row.time);
 $('round').textContent=s.decision_count?'Lần '+s.decision_count:'Chờ bắt đầu';
 $('global-round').textContent='Tự chọn lại ở đầu mỗi pha xanh';
 $('play-status').textContent=s.finished?'Đã kết thúc · xem số xe còn chờ':running?'Đang chạy · 1 giây mô phỏng ≈ 1 giây thực':'Đang dừng · đồng hồ mô phỏng không chạy';
 $('progress').style.width=(row.time/s.duration*100)+'%';
 const justDecided=d&&row.time===d.time+1;
 const labels=['Xe đến','Cảm biến đếm','Đồng bộ Twin','Thử phương án','Điều khiển đèn','Phản hồi'];
 $('flow').innerHTML=labels.map((text,i)=>`<div class="step ${i===(justDecided?4:5)?'active':'done'}">${i+1}. ${text}${i<5?' →':''}</div>`).join('');
 for(const g of ['NS','EW']){
  const light=$('light-'+g.toLowerCase()),state=row.phase===g+'_GREEN'?'green':row.phase===g+'_YELLOW'?'yellow':'red';
  light.dataset.state=state;light.setAttribute('aria-label',`${g==='NS'?'Bắc–Nam':'Đông–Tây'}: đèn ${{green:'xanh',yellow:'vàng',red:'đỏ'}[state]}`);
 }
 let phaseText='Chờ bấm bắt đầu để khởi động đèn',tone='red';
 if(d){
  const elapsed=row.time-d.time,group=d.phase.startsWith('NS')?'Bắc–Nam':'Đông–Tây';
  if(row.phase.endsWith('_GREEN')){phaseText=`${group} XANH · còn ${Math.max(0,d.chosen_green-elapsed)} giây`;tone='green';}
  else if(row.phase.endsWith('_YELLOW')){phaseText=`${group} VÀNG · còn ${Math.max(0,d.chosen_green+3-elapsed)} giây`;tone='yellow';}
  else phaseText=`Hai hướng ĐỎ · chờ ${Math.max(0,d.chosen_green+5-elapsed)} giây trước khi đổi hướng`;
 }
 $('phase-status').textContent=phaseText;$('phase-status').dataset.tone=tone;
 $('served-count').textContent=`Đã đi qua từ 07:00: Bắc–Nam ${s.total_served.NS} xe · Đông–Tây ${s.total_served.EW} xe.`;
 $('road-note').textContent=`Giây ${clock(row.time)}: xe mới đến NS +${row.arrivals_NS}, EW +${row.arrivals_EW}; đi qua NS ${row.served_NS}, EW ${row.served_EW}. Đèn đỏ thì xe mới đến phải chờ.`;
 $('t-ns').textContent=row.twin_queue_NS;$('t-ew').textContent=row.twin_queue_EW;
 $('sync').textContent=`Cảm biến gửi lúc ${clock(row.observation_time)} · Twin nhận số xe sau mỗi giây mô phỏng.`;
 $('sync-notice').hidden=false;$('sync-notice').dataset.stale='false';
 $('sync-notice').textContent='Hai trạng thái được lưu riêng. Bản sao khớp giao lộ sau gói quan sát mới nhất.';
 $('twin').classList.toggle('active',justDecided);
 const group=d?(d.phase.startsWith('NS')?'Bắc–Nam':'Đông–Tây'):'';
 const opposite=d?(d.phase.startsWith('NS')?'Đông–Tây':'Bắc–Nam'):'';
 $('forecast').textContent=d?`Dự báo dùng lúc chọn đèn ${clock(d.time)}\nBắc–Nam: ${(d.rate_NS*60).toFixed(1)} xe MỚI/phút\nĐông–Tây: ${(d.rate_EW*60).toFixed(1)} xe MỚI/phút`:'';
 $('forecast-help').textContent=d?`${d.forecast_method==='past_mean_warmup'?'ML đang học ban đầu; tạm dùng trung bình xe đã đến.':'ML dùng các lượt xe đã quan sát để dự báo.'} Dự báo xe mới đến khác với số xe đang chờ. Hiện có ${s.training_samples} mẫu học.`:'Bắt đầu từ hàng đợi rỗng; mô hình chỉ học khi xe đã xuất hiện.';
 $('signal-plan').textContent=d?`Quyết định gần nhất: ${group} XANH ${d.chosen_green} giây · ${opposite} ĐỎ`:'';
 $('candidates').innerHTML=d?[15,30,45].map(g=>`<div class="candidate ${g===d.chosen_green?'chosen':''}"><strong>${g} giây</strong>đèn xanh<br>Điểm chờ<br>${num(d['score_'+g])}${g===d.chosen_green?'<br>✓ Được chọn':''}</div>`).join(''):'';
 $('signal-help').textContent=d?'Thời lượng xanh dành cho cả nhóm hướng. Hết xanh phải qua vàng 3 giây và đỏ toàn bộ 2 giây, rồi Twin mới chọn cho hướng tiếp theo.':'';
 $('candidate-note').textContent=d?'Điểm chờ dự báo trên cùng 120 giây; chọn điểm thấp nhất. Đây là lần thử mới do Python vừa tính, không đọc quyết định từ log.':'';
 $('heading').textContent=s.finished?'Mô phỏng đã kết thúc':!running?'Sẵn sàng chạy giao lộ liên tục':justDecided?'Twin vừa chọn phương án đèn mới':'Cảm biến → Twin → đèn → phản hồi đang chạy liên tục';
 $('explain').textContent=s.finished?`Đã hết 7.200 giây; còn ${row.queue_NS} xe Bắc–Nam và ${row.queue_EW} xe Đông–Tây chờ. Bấm chạy lại để bắt đầu từ 07:00.`:!running?'Bấm bắt đầu hoặc tiếp tục. Khi chạy, mỗi giây thêm xe, phục vụ xe ở hướng xanh, cảm biến đếm hàng đợi và gửi về Twin.':d?`Hiện đang áp dụng quyết định ${group} xanh ${d.chosen_green} giây. Xe mới vẫn đến, hàng đợi có thể tăng hoặc giảm. Khi hết xanh/vàng/đỏ, hệ thống tự chọn cho hướng còn lại, không cần chuyển case.`:'Đang chờ giây mô phỏng đầu tiên.';
 $('traffic-story').hidden=false;
 $('traffic-story').innerHTML='<strong>Xe đến và đi trong lượt chạy này</strong>'+['NS','EW'].map(g=>`<p><b>${g==='NS'?'Bắc–Nam':'Đông–Tây'}:</b> ${s.total_arrived[g]} xe đã đến − ${s.total_served[g]} xe đã qua = <b>${row['queue_'+g]} xe còn chờ</b>.</p>`).join('')+'<strong style="margin-top:10px">Các sự kiện mới nhất</strong><ul>'+s.events.slice(-5).map(event=>`<li><b>${clock(event.time)}</b> · ${event.text}</li>`).join('')+'</ul>';
 if(!running)document.getAnimations().forEach(a=>a.pause());
 liveState=s;requestAnimationFrame(liveHeight);
}
window.addEventListener('message',event=>{
 if(event.source===window.parent&&event.data&&event.data.type==='traffic:state')renderLive(event.data.state);
});
$('next-case')?.remove();$('case-feedback').hidden=true;
$('heading').textContent='Đang kết nối cảm biến ảo…';
requestAnimationFrame(liveHeight);
'''


def show_realtime():
    """Render a persistent component updated by a small periodic Python fragment."""
    import streamlit as st
    import streamlit.components.v1 as components
    import pandas as pd
    from get_data import ROOT
    from realtime import RealtimeSimulation

    component = components.declare_component('traffic_realtime', path=str(ROOT / 'live_frontend'))

    @st.fragment(run_every=1)
    def heartbeat():
        if 'traffic_runtime' not in st.session_state:
            arrivals = pd.read_csv(ROOT / 'data/arrivals_by_second.csv')
            st.session_state.traffic_runtime = RealtimeSimulation(
                arrivals[['arrivals_NS', 'arrivals_EW']].itertuples(index=False, name=None))
        runtime = st.session_state.traffic_runtime
        runtime.poll()
        action = component(html=live_html(), state=runtime.snapshot(), default=None, key='traffic-live')
        if action and action.get('id') != st.session_state.get('traffic_last_action'):
            st.session_state.traffic_last_action = action['id']
            if action.get('action') == 'start':
                runtime.start()
            elif action.get('action') == 'pause':
                runtime.pause()
            elif action.get('action') == 'reset':
                runtime.reset()
            st.rerun(scope='fragment')

    heartbeat()
