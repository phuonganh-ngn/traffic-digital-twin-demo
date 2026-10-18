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
    markup = markup.replace('<div class="top">', '<div class="top"><div><div class="eyebrow">GIẢ LẬP THỜI GIAN THỰC · CẢM BIẾN ẢO</div><div class="title">Giao lộ hoạt động liên tục</div><div class="muted">Đã có xe chờ sẵn. Lượt đầu: đếm xe → đồng bộ Twin → chọn đèn → xe đi và phản hồi. Sau đó hệ thống tự chạy real-time liên tục.</div></div>', 1)
    markup = markup.replace('▶ Bắt đầu case', '▶ Bắt đầu real-time').replace('↺ Xem lại case', '↺ Chạy lại từ đầu').replace('Khởi động lại case hiện tại', 'Bắt đầu lại với hàng đợi ban đầu')
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
 const row=s.current,d=s.decision,flowStage=s.flow_stage??5,preparing=s.preparing;
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
 document.getAnimations().forEach(a=>running&&!preparing?a.play():a.pause());
 updateCars(row,true);resizeCars();
 replayServed.NS=s.total_served.NS;replayServed.EW=s.total_served.EW;
 // Bound the browser-side packet buffer; the Python model owns the full state.
 for(const t of frames.keys())if(t<row.time-65)frames.delete(t);
 $('play').disabled=false;$('reset').disabled=false;commandPending=false;
 $('play').textContent=s.finished?'Đã đến 09:00':running?'Ⅱ Tạm dừng':'▶ '+(s.has_started?'Tiếp tục real-time':'Bắt đầu real-time');
 $('play').disabled=s.finished;
 $('ns').textContent=`Bắc–Nam: ${row.queue_NS} xe chờ`;$('ew').textContent=`Đông–Tây: ${row.queue_EW} xe chờ`;
 $('clock').textContent='1 hình xe = 1 xe · số đếm cảm biến ảo';
 $('window').textContent=clock(s.start_time)+'–09:00:00';$('now').textContent=clock(row.time);
 $('round').textContent='Lượt '+(s.decision_count+(preparing&&flowStage<4?1:0));
 $('global-round').textContent=s.intro_done?'Đang tự động real-time, không dừng lại các bước':'Giải thích 1 lần, sau đó tự động real-time';
 $('play-status').textContent=s.finished?'Đã kết thúc · xem số xe còn chờ':running?(preparing?'Đang giải thích bước '+(flowStage+1)+' · đồng hồ mô phỏng tạm dừng':'Xe đang chạy · 1 giây mô phỏng ≈ 1 giây thực'):'Đang dừng · đồng hồ mô phỏng không chạy';
 $('progress').style.width=((row.time-s.start_time)/(s.duration-s.start_time)*100)+'%';
 const justDecided=(preparing&&flowStage>=2&&flowStage<=4)||(!preparing&&d&&row.time===d.time+1);
 const showForecast=!!d&&flowStage>=3,showChoice=showForecast&&flowStage>=4;
 const labels=['Xe đang chờ','Cảm biến đếm','Đồng bộ Twin','Thử phương án','Chọn đèn','Xe đi & phản hồi'];
 $('flow').innerHTML=labels.map((text,i)=>`<div class="step ${i===flowStage?'active':i<flowStage?'done':''}">${i+1}. ${text}${i<5?' →':''}</div>`).join('');
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
 $('served-count').textContent=`Đã đi qua từ ${clock(s.start_time)}: Bắc–Nam ${s.total_served.NS} xe · Đông–Tây ${s.total_served.EW} xe.`;
 $('road-note').textContent=`Giây ${clock(row.time)}: xe mới đến NS +${row.arrivals_NS}, EW +${row.arrivals_EW}; đi qua NS ${row.served_NS}, EW ${row.served_EW}. Đèn đỏ thì xe mới đến phải chờ.`;
 $('t-ns').textContent=flowStage>=2?row.twin_queue_NS:'—';$('t-ew').textContent=flowStage>=2?row.twin_queue_EW:'—';
 $('sync').textContent=flowStage>=2?`Cảm biến gửi lúc ${clock(row.observation_time)} · Twin đã đồng bộ số xe.`:flowStage===1?'Cảm biến đang đếm xe để gửi về Twin.':'Chưa đến bước nhận quan sát của lượt này.';
 $('sync-notice').hidden=flowStage<2;$('sync-notice').dataset.stale='false';
 $('sync-notice').textContent='Hai trạng thái được lưu riêng. Bản sao khớp giao lộ sau gói quan sát mới nhất.';
 $('twin').classList.toggle('active',justDecided);
 const group=d?(d.phase.startsWith('NS')?'Bắc–Nam':'Đông–Tây'):'';
 const opposite=d?(d.phase.startsWith('NS')?'Đông–Tây':'Bắc–Nam'):'';
 $('forecast').textContent=showForecast?`Dự báo dùng lúc chọn đèn ${clock(d.time)}\nBắc–Nam: ${(d.rate_NS*60).toFixed(1)} xe MỚI/phút\nĐông–Tây: ${(d.rate_EW*60).toFixed(1)} xe MỚI/phút`:'';
 $('forecast-help').textContent=showForecast?`${d.forecast_method==='past_mean_warmup'?'ML đang học ban đầu; tạm dùng trung bình xe đã đến.':'ML dùng các lượt xe đã quan sát để dự báo.'} Dự báo xe mới đến khác với số xe đang chờ. Hiện có ${s.training_samples} mẫu học.`:'Đã có xe chờ ban đầu. Dự báo sẽ hiện sau khi cảm biến đếm và Twin nhận số xe.';
 $('signal-plan').textContent=showChoice?`Đã chọn: ${group} XANH ${d.chosen_green} giây · ${opposite} ĐỎ`:showForecast?`Đang thử 3 phương án xanh cho ${group}`:'';
 $('candidates').innerHTML=showForecast?[15,30,45].map(g=>`<div class="candidate ${showChoice&&g===d.chosen_green?'chosen':''}"><strong>${g} giây</strong>đèn xanh<br>Điểm chờ<br>${num(d['score_'+g])}${showChoice&&g===d.chosen_green?'<br>✓ Được chọn':''}</div>`).join(''):'';
 $('signal-help').textContent=showForecast?'Thời lượng xanh dành cho cả nhóm hướng. Hết xanh phải qua vàng 3 giây và đỏ toàn bộ 2 giây, rồi Twin mới chọn cho hướng tiếp theo.':'';
 $('candidate-note').textContent=showForecast?'Điểm chờ dự báo trên cùng 120 giây; chọn điểm thấp nhất. Đây là lần thử mới do Python vừa tính, không đọc quyết định từ log.':'';
 const upcoming=s.next_group==='NS'?'Bắc–Nam':'Đông–Tây';
 const headings=['1. Xe đang chờ tại giao lộ','2. Cảm biến quan sát và đếm xe','3. Đồng bộ hàng đợi vào Twin','4. Dự báo và thử 15 / 30 / 45 giây','5. Chọn thời lượng đèn xanh','6. Xe đi qua và gửi phản hồi'];
 const explanations=[
  `Ban đầu đã có ${s.initial_queues.NS} xe Bắc–Nam và ${s.initial_queues.EW} xe Đông–Tây chờ sẵn trên đường. Xe đứng yên trong lúc giải thích; chưa áp dụng đèn mới.`,
  `Cảm biến ảo đếm được Bắc–Nam ${row.queue_NS} xe, Đông–Tây ${row.queue_EW} xe và gửi số xe cùng thời điểm ${clock(row.time)} cho Twin.`,
  `Twin cập nhật bản sao riêng: Bắc–Nam ${row.twin_queue_NS} xe, Đông–Tây ${row.twin_queue_EW} xe. Hai số này đến từ quan sát, không lấy từ lượt xe tương lai.`,
  `Twin dự báo xe mới sắp đến từ dữ liệu đã quan sát, rồi thử cho nhóm ${upcoming} xanh 15, 30 hoặc 45 giây trên cùng 120 giây tương lai. Xe ở giao lộ chưa chạy.`,
  `Đã chọn ${group} XANH ${d?.chosen_green??0} giây; ${opposite} ĐỎ. Phương án có điểm chờ thấp nhất được gửi cho bộ điều khiển. Sau bước này xe mới bắt đầu đi.`,
  `Xe chỉ đi khi đèn xanh; cảm biến gửi hàng đợi mới về Twin làm phản hồi. Từ đây hệ thống tự chạy real-time: tự đổi xanh/vàng/đỏ và chọn phương án mới, không dừng lại các bước 1–5 nữa.`
 ];
 $('heading').textContent=s.finished?'Mô phỏng đã kết thúc':headings[flowStage];
 $('explain').textContent=s.finished?`Đã hết 7.200 giây; còn ${row.queue_NS} xe Bắc–Nam và ${row.queue_EW} xe Đông–Tây chờ.`:explanations[flowStage]+(!running?' Bấm nút bắt đầu/tiếp tục để đi qua từng bước.':'');
 if(preparing){$('phase-status').textContent=`Bước ${flowStage+1}/5 · xe chưa chạy, đồng hồ mô phỏng tạm dừng`;}
 $('traffic-story').hidden=false;
 $('traffic-story').innerHTML='<strong>Xe đến và đi trong lượt chạy này</strong>'+['NS','EW'].map(g=>`<p><b>${g==='NS'?'Bắc–Nam':'Đông–Tây'}:</b> ${s.initial_queues[g]} xe chờ ban đầu + ${s.total_arrived[g]} xe mới đến − ${s.total_served[g]} xe đã qua = <b>${row['queue_'+g]} xe còn chờ</b>.</p>`).join('')+'<strong style="margin-top:10px">Các sự kiện mới nhất</strong><ul>'+s.events.slice(-5).map(event=>`<li><b>${clock(event.time)}</b> · ${event.text}</li>`).join('')+'</ul>';
 if(!running||preparing)document.getAnimations().forEach(a=>a.pause());
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
                arrivals[['arrivals_NS', 'arrivals_EW']].itertuples(index=False, name=None), warmup_seconds=35)
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
            # Controls can arrive during a full-page reconnect as well as a
            # fragment heartbeat; an app rerun is valid in both contexts.
            st.rerun()

    heartbeat()
