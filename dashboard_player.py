"""A self-contained, one-button replay of genuine simulation logs."""
import json


def player_html(logs, decisions):
    # Show a short excerpt after online learning has started, not a fabricated run.
    start = next((i for i, row in decisions.iterrows() if row.training_samples >= 6), 0)
    chosen = decisions.iloc[start:start + 5]
    last_index = min(start + 5, len(decisions) - 1)
    end = int(decisions.iloc[last_index].time)
    first = int(chosen.iloc[0].time)
    columns = ['time', 'phase', 'queue_NS', 'queue_EW', 'arrivals_NS', 'arrivals_EW',
               'served_NS', 'served_EW', 'twin_queue_NS', 'twin_queue_EW', 'observation_time']
    payload = dict(decisions=json.loads(chosen.to_json(orient='records')),
                   frames=json.loads(logs.loc[(logs.time >= max(first, 1)) & (logs.time <= end), columns].to_json(orient='records')),
                   end=end, first_decision_number=int(start)+1, total_decisions=len(decisions),
                   window_start=first, window_end=end)
    return TEMPLATE.replace('__DATA__', json.dumps(payload, ensure_ascii=False).replace('</', '<\\/'))


TEMPLATE = r'''<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8"><style>
*{box-sizing:border-box}body{margin:0;font:15px/1.5 system-ui,sans-serif;color:#17283d;background:#f6f8fb}
.shell{border:1px solid #dce3ec;border-radius:20px;padding:22px;background:white}
.top{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}.eyebrow{font-size:12px;letter-spacing:1px;color:#53718b;font-weight:700}.title{font-size:23px;font-weight:750;margin:4px 0}.muted{color:#64748b;font-size:13px}
button{border:0;border-radius:12px;padding:13px 24px;background:#165bd8;color:white;font-size:17px;font-weight:700;cursor:pointer}button:hover{background:#104bb7}button.secondary{background:#eaf0f7;color:#334155;font-size:13px;padding:10px 14px}.actions{display:flex;gap:8px;align-items:center}
.flow{display:grid;grid-template-columns:repeat(6,1fr);gap:5px;margin:18px 0}.step{border-radius:9px;padding:10px 5px;background:#f0f3f7;text-align:center;font-size:12px;color:#64748b;transition:.3s}.step.active{background:#165bd8;color:white;font-weight:700}.step.done{background:#e3f4ed;color:#20704f}

.meta{display:grid;grid-template-columns:1.2fr 1fr 1.3fr;gap:12px;margin-top:18px}.meta-card{border:1px solid #e3eaf2;border-radius:12px;padding:10px 14px;background:#f9fbfd}.meta-card small{display:block;font-size:10px;letter-spacing:1px;color:#6d7e92;font-weight:750}.meta-card strong{font-size:18px;font-variant-numeric:tabular-nums}.meta-card span{font-size:12px;color:#65758a}.progress{height:4px;background:#e9eef5;border-radius:9px;overflow:hidden;margin-top:14px}.progress i{display:block;height:100%;background:linear-gradient(90deg,#2268df,#40b2c6);transition:width .45s linear}
.scene{display:grid;grid-template-columns:1.15fr 1fr;gap:18px;align-items:stretch}.roadbox{background:#e5eee4;border:1px solid #dbe5db;border-radius:16px;overflow:hidden;position:relative;height:370px;isolation:isolate}.map{position:absolute;width:100%;height:100%;inset:0}.road-heading{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;font-size:12px;color:#61758a}.legend-dot{width:8px;height:8px;border-radius:50%;background:#3a8bdf;display:inline-block;margin-right:5px}.legend-dot.ew{background:#e6ae43;margin-left:12px}.tag{position:absolute;background:#fffffff2;backdrop-filter:blur(4px);border:1px solid #dce5de;border-radius:9px;padding:6px 10px;font-size:12px;font-weight:700;box-shadow:0 3px 9px #233c2210;z-index:4}.ns-tag{left:12px;top:12px;border-left:3px solid #4599e7}.ew-tag{right:12px;bottom:12px;border-left:3px solid #e5ac3c}.counter{position:absolute;left:12px;bottom:12px;background:#fffffff0;border-radius:8px;padding:5px 9px;font-size:11px;color:#486079;z-index:4}#cars{position:absolute;inset:0;z-index:2;pointer-events:none}.car{position:absolute;width:28px;height:16px;background:linear-gradient(180deg,#ffe296,#edb344 35%,#d99727);border:1px solid #b37b22;border-radius:5px 7px 7px 5px;box-shadow:0 3px 4px #101d3650;will-change:left,top;transform:translate(-50%,-50%)}.car::before{content:"";position:absolute;right:6px;top:2px;width:5px;height:10px;background:linear-gradient(90deg,#47778f,#b5d7e8);border-radius:1px 3px 3px 1px;box-shadow:-9px 0 0 -1px #547c94}.car::after{content:"";position:absolute;left:4px;top:-3px;width:5px;height:3px;background:#1c2731;border-radius:1px;box-shadow:14px 0 #1c2731,0 17px #1c2731,14px 17px #1c2731}.car .headlights{position:absolute;right:-1px;top:2px;width:2px;height:3px;background:#fff8d7;border-radius:1px;box-shadow:0 7px #fff8d7}.car .taillights{position:absolute;left:-1px;top:2px;width:2px;height:3px;background:#e95e51;box-shadow:0 7px #e95e51}.car.ns{background:linear-gradient(180deg,#a9dcff,#5eabeb 35%,#3285d1);border-color:#2872b0;transform:translate(-50%,-50%) rotate(90deg)}
.light{position:absolute;width:29px;padding:6px 5px;display:flex;flex-direction:column;gap:5px;background:linear-gradient(90deg,#101820,#35414b 50%,#121b23);border:2px solid #111a22;border-radius:9px;box-shadow:2px 4px 5px #0005;z-index:3}.light::after{content:"";position:absolute;top:100%;left:11px;width:4px;height:18px;background:linear-gradient(90deg,#5d6a75,#a6b0b7,#5d6a75)}.bulb{display:block;width:15px;height:15px;border-radius:50%;border-top:2px solid #0009;box-shadow:inset 0 2px 4px #0009}.bulb.red{background:#4b2528}.bulb.yellow{background:#49402a}.bulb.green{background:#203e33}.light[data-state="red"] .red{background:radial-gradient(circle at 40% 35%,#ffc0b9,#ff453f 55%,#c61b18);box-shadow:0 0 9px #ff453faa}.light[data-state="yellow"] .yellow{background:radial-gradient(circle at 40% 35%,#fff6bd,#ffce32 55%,#d58d0c);box-shadow:0 0 9px #ffce32aa}.light[data-state="green"] .green{background:radial-gradient(circle at 40% 35%,#c0ffe1,#2be48b 55%,#0a9953);box-shadow:0 0 9px #2be48baa}.light.ns{left:59%;top:13%}.light.ew{left:35%;top:67%}.phase-pill{display:inline-block;margin-top:9px;padding:5px 10px;border-radius:20px;background:#eff4fa;font-size:12px;color:#486079;border:1px solid #dce6f1}.phase-pill[data-tone="green"]{background:#e9f7ef;color:#217751}.phase-pill[data-tone="yellow"]{background:#fff6df;color:#956b10}.phase-pill[data-tone="red"]{background:#fff0ef;color:#a34d49}
.twin{border:2px solid #dce6f3;border-radius:15px;padding:17px;transition:.3s}.twin.active{border-color:#165bd8;box-shadow:0 0 0 4px #165bd810}.twintitle{font-size:17px;font-weight:750}.values{display:flex;gap:12px;margin:12px 0}.value{flex:1;border-radius:9px;background:#f1f5fa;padding:10px}.value strong{font-size:24px;display:block}.candidates{display:flex;gap:7px;margin-top:12px}.candidate{flex:1;padding:9px 5px;border:1px solid #dce3ec;border-radius:10px;text-align:center;font-size:12px}.candidate strong{display:block;font-size:19px}.candidate.chosen{border:2px solid #21966b;background:#eaf8f2}.explanation{margin-top:16px;background:#edf4ff;border-radius:13px;padding:17px;min-height:112px}.explanation h3{margin:0 0 6px;font-size:19px}.explanation p{margin:0;font-size:15px}.footer{margin-top:12px;font-size:12px;color:#64748b}.badge{color:#20704f;font-weight:700;font-size:12px;margin-top:10px}
@media(max-width:650px){.scene{grid-template-columns:1fr}.roadbox{height:310px}.meta{grid-template-columns:1fr 1fr}.meta-card:last-child{grid-column:1/-1}.flow{grid-template-columns:repeat(3,1fr)}.title{font-size:20px}.shell{padding:12px}}
</style></head><body><div class="shell">
<div class="top"><div><div class="eyebrow">MỘT GIAO LỘ · MỘT VÒNG ĐIỀU KHIỂN</div><div class="title">Xe đang chờ. Twin sẽ chọn đèn thế nào?</div><div class="muted">Bấm bắt đầu, rồi xem luồng tự chạy và đọc lời giải thích bên dưới.</div></div><div class="actions"><button id="play">▶ Bắt đầu demo</button><button id="reset" class="secondary" title="Xem lại từ đầu">↺ Xem lại</button></div></div>
<div class="meta"><div class="meta-card"><small>KHUNG GIỜ ĐOẠN DEMO</small><strong id="window"></strong><br><span>Trích từ buổi mô phỏng 07:00–09:00</span></div><div class="meta-card"><small>THỜI ĐIỂM ĐANG XEM</small><strong id="now"></strong><br><span id="play-status">Sẵn sàng phát lại · tốc độ xe 2×</span></div><div class="meta-card"><small>LƯỢT QUYẾT ĐỊNH</small><strong id="round"></strong><br><span id="global-round"></span></div></div><div class="progress"><i id="progress"></i></div><div class="flow" id="flow"></div>
<div class="scene"><div><div class="road-heading"><strong>GIAO LỘ MÔ PHỎNG</strong><span><i class="legend-dot"></i>Bắc–Nam<i class="legend-dot ew"></i>Đông–Tây</span></div><div class="roadbox"><svg class="map" viewBox="0 0 600 400" preserveAspectRatio="none" aria-hidden="true"><defs><pattern id="grass" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M3 8l2-3m12 15l2-3" stroke="#c4d6bf" stroke-width="1" opacity=".6"/></pattern><pattern id="paving" width="14" height="14" patternUnits="userSpaceOnUse"><path d="M0 0h14v14H0z" fill="#e5e5de" stroke="#d4d6cf" stroke-width=".6"/></pattern><filter id="shadow"><feDropShadow dx="1" dy="3" stdDeviation="2" flood-opacity=".16"/></filter></defs><rect width="600" height="400" fill="url(#grass)"/><path d="M234 0h132v134h234v132H366v134H234V266H0V134h234z" fill="url(#paving)"/><path d="M252 0h96v152h252v96H348v152h-96V248H0v-96h252z" fill="#65737c"/><path d="M257 0h86v157h257v86H343v157h-86V243H0v-86h257z" fill="#3a4954"/><g stroke="#bdc6ca" stroke-width="2" stroke-dasharray="12 11" opacity=".7"><path d="M300 0v140m0 120v140M0 200h240m120 0h240"/></g><g stroke="#e4c96c" stroke-width="1.5" opacity=".75"><path d="M297 0v142m6-142v142m-6 116v142m6-142v142M0 197h240M0 203h240m120-6h240m-240 6h240"/></g><g fill="#edf0e9"><rect x="258" y="140" width="36" height="4"/><rect x="238" y="159" width="4" height="34"/><rect x="306" y="256" width="36" height="4"/><rect x="358" y="207" width="4" height="34"/></g><g fill="#e0e6df" opacity=".7"><path d="M273 70h5v17h5l-7.5 9-7.5-9h5z"/><path d="M140 174v5h17v5l9-7.5-9-7.5v5z"/><path d="M322 330h5v-17h5l-7.5-9-7.5 9h5z"/><path d="M460 222v5h-17v5l-9-7.5 9-7.5v5z"/></g><g filter="url(#shadow)"><g fill="#91af82"><circle cx="54" cy="86" r="21"/><circle cx="167" cy="46" r="17"/><circle cx="535" cy="62" r="24"/><circle cx="439" cy="107" r="14"/><circle cx="67" cy="326" r="23"/><circle cx="187" cy="303" r="17"/><circle cx="480" cy="325" r="22"/><circle cx="554" cy="290" r="15"/></g><g fill="#a9c49a"><circle cx="49" cy="80" r="13"/><circle cx="530" cy="55" r="15"/><circle cx="61" cy="319" r="14"/><circle cx="474" cy="320" r="13"/></g></g></svg><div id="cars"></div><div class="light ns" id="light-ns" role="img"><span class="bulb red"></span><span class="bulb yellow"></span><span class="bulb green"></span></div><div class="light ew" id="light-ew" role="img"><span class="bulb red"></span><span class="bulb yellow"></span><span class="bulb green"></span></div><div class="tag ns-tag" id="ns"></div><div class="tag ew-tag" id="ew"></div><div class="counter" id="clock"></div></div><div id="phase-status" class="phase-pill"></div><div class="muted" id="road-note" style="margin-top:6px"></div></div>
<div class="twin" id="twin"><div class="eyebrow">BẢN SAO SỐ CỦA GIAO LỘ</div><div class="twintitle">Digital Twin</div><div class="muted">Nhận số xe chờ, dự báo và thử phương án trước khi ra lệnh.</div><div class="values"><div class="value">Bắc–Nam đang chờ<strong id="t-ns">—</strong></div><div class="value">Đông–Tây đang chờ<strong id="t-ew">—</strong></div></div><div class="muted" id="sync"></div><div id="forecast" class="badge"></div><div class="candidates" id="candidates"></div><div class="muted" id="candidate-note" style="margin-top:8px"></div></div></div>
<div class="explanation" aria-live="polite"><h3 id="heading"></h3><p id="explain"></p></div>
<div class="footer">Phát lại một đoạn log đã mô phỏng, sau giai đoạn ML học ban đầu. Hàng đợi vẽ tối đa 4 xe/nhóm; số đếm thể hiện đầy đủ. Xe đã qua vạch tiếp tục đi ra khỏi khung. Xe minh họa chuyển động theo lượt đến/phục vụ trong log. Hai đường đại diện hai nhóm hướng, không phải hình học giao lộ thật.</div>
</div><script>
const data=__DATA__;
const steps=['Xe đến','Quan sát','Đồng bộ Twin','Dự báo & thử','Chọn đèn','Xe đi & phản hồi'];
const $=id=>document.getElementById(id);
let round=0, stage=0, frame=0, running=false, finished=false, timer=null;
const frames=new Map(data.frames.map(r=>[r.time,r]));
const num=n=>Math.round(n).toLocaleString('vi-VN');
function clock(t){return `${String(7+Math.floor(t/3600)).padStart(2,'0')}:${String(Math.floor(t%3600/60)).padStart(2,'0')}:${String(t%60).padStart(2,'0')}`;}
function endTime(){return round+1<data.decisions.length?data.decisions[round+1].time:data.end;}
const visualQueues={NS:[],EW:[]};
let lastSceneTime=null;
function putCar(group,x,y){
 const el=document.createElement('span');el.className='car '+group.toLowerCase();
 el.innerHTML='<i class="headlights"></i><i class="taillights"></i>';
 $('cars').append(el);el.style.left=x+'%';el.style.top=y+'%';return {el,x,y};
}
function moveCar(car,x,y,duration){
 if(car.x===x&&car.y===y)return;
 const parent=$('cars').getBoundingClientRect(),box=car.el.getBoundingClientRect();
 const fromX=(box.left+box.width/2-parent.left)/parent.width*100;
 const fromY=(box.top+box.height/2-parent.top)/parent.height*100;
 car.el.getAnimations().forEach(a=>a.cancel());
 car.el.style.left=x+'%';car.el.style.top=y+'%';car.x=x;car.y=y;
 if(duration)return car.el.animate([{left:fromX+'%',top:fromY+'%'},{left:x+'%',top:y+'%'}],{duration,easing:'cubic-bezier(.25,.1,.25,1)'});
}
function updateCars(row,moving){
 const newSecond=moving&&lastSceneTime!==null&&row.time>lastSceneTime;
 for(const g of ['NS','EW']){
  const queue=visualQueues[g],target=Math.min(4,row['queue_'+g]);
  if(newSecond&&row['served_'+g]&&queue.length){
   const departing=queue.shift();
   const animation=moveCar(departing,g==='NS'?46.2:108,g==='NS'?108:44.2,1000);
   if(animation)animation.finished.then(()=>departing.el.remove()).catch(()=>{});else departing.el.remove();
  }else if(newSecond&&row['served_'+g]&&!queue.length){
   // A same-second arrival may cross immediately without ever joining a queue.
   const departing=putCar(g,g==='NS'?46.2:37.3,g==='NS'?31:44.2);
   const animation=moveCar(departing,g==='NS'?46.2:108,g==='NS'?108:44.2,1000);
   animation.finished.then(()=>departing.el.remove()).catch(()=>{});
  }
  while(queue.length>target)queue.pop().el.remove();
  while(queue.length<target){
   const i=queue.length,x=g==='NS'?46.2:(224-i*36)/6,y=g==='NS'?(124-i*32)/4:44.2;
   const car=putCar(g,newSecond?(g==='NS'?x:-5):x,newSecond?(g==='NS'?-5:y):y);
   queue.push(car);moveCar(car,x,y,newSecond?650:0);
  }
  queue.forEach((car,i)=>moveCar(car,g==='NS'?46.2:(224-i*36)/6,g==='NS'?(124-i*32)/4:44.2,moving?450:0));
 }
 lastSceneTime=row.time;
}
function scene(row,moving=false){
 $('ns').textContent=`Bắc–Nam: ${row.queue_NS} xe chờ`;$('ew').textContent=`Đông–Tây: ${row.queue_EW} xe chờ`;
 $('clock').textContent='Đường minh họa · số đếm từ log';
 $('window').textContent=`${clock(data.window_start)}–${clock(data.window_end)}`;
 $('now').textContent=clock(row.time);
 $('round').textContent=`${round+1} / ${data.decisions.length} lượt trong demo`;
 $('global-round').textContent=`Lượt ${data.first_decision_number+round} / ${data.total_decisions} của cả buổi 07:00–09:00`;
 $('progress').style.width=(row.time-data.window_start)/(data.window_end-data.window_start)*100+'%';
 $('play-status').textContent=finished?'Đã phát hết đoạn demo':!running?'Đang dừng · bấm nút để phát':stage===5?'Xe đang di chuyển · phát lại 2×':'Tạm dừng thời gian để giải thích flow';
 for(const g of ['NS','EW']){
  const state=row.phase===g+'_GREEN'?'green':row.phase===g+'_YELLOW'?'yellow':'red';
  const light=$('light-'+g.toLowerCase());light.dataset.state=state;
  light.setAttribute('aria-label',`${g==='NS'?'Bắc–Nam':'Đông–Tây'}: đèn ${{green:'xanh',yellow:'vàng',red:'đỏ'}[state]}`);
 }
 updateCars(row,moving);
 const d=data.decisions[round],elapsed=row.time-d.time;
 const group=d.phase.startsWith('NS')?'Bắc–Nam':'Đông–Tây';
 let phaseText='Trước quyết định · quan sát trạng thái cuối giây vừa qua',tone='red';
 if(stage===5){
  if(row.phase.endsWith('_GREEN')){phaseText=`${group} đèn xanh · còn ${Math.max(0,d.chosen_green-elapsed)} giây`;tone='green';}
  else if(row.phase.endsWith('_YELLOW')){phaseText=`${group} đèn vàng · còn ${Math.max(0,d.chosen_green+3-elapsed)} giây`;tone='yellow';}
  else phaseText=`Hai hướng đèn đỏ · chờ chuyển hướng ${Math.max(0,d.chosen_green+5-elapsed)} giây`;
 }
 $('phase-status').textContent=phaseText;$('phase-status').dataset.tone=tone;
 $('road-note').textContent=stage===5?`Giây này: ${row.arrivals_NS+row.arrivals_EW} xe đến · ${row.served_NS+row.served_EW} xe đi qua. Hàng đợi và đèn thay đổi theo log.`:'Xe đứng trước vạch dừng. Khi áp dụng quyết định, xe đầu hàng đi qua và các xe sau tiến lên.';
}
function render(){
 const d=data.decisions[round], before=frames.get(d.time)||data.frames[0];
 const row=stage===5?(frames.get(frame)||before):before;
 $('flow').innerHTML=steps.map((s,i)=>`<div class="step ${i===stage?'active':i<stage?'done':''}">${i+1}. ${s}${i<5?' →':''}</div>`).join('');
 scene(row,stage===5&&running);
 $('twin').classList.toggle('active',stage>=2&&stage<=4);
 const synchronized=stage>=2;
 $('t-ns').textContent=synchronized?(stage===5?row.twin_queue_NS:d.queue_NS):'—';
 $('t-ew').textContent=synchronized?(stage===5?row.twin_queue_EW:d.queue_EW):'—';
 $('sync').textContent=synchronized?`Đã nhận quan sát lúc ${clock(stage===5?row.observation_time:d.time)}. Trạng thái Twin được lưu riêng.`:'Đang chờ nhận thông tin từ giao lộ.';
 $('forecast').textContent=stage>=3?`ML ước lượng: Bắc–Nam ${(d.rate_NS*60).toFixed(1)} · Đông–Tây ${(d.rate_EW*60).toFixed(1)} xe/phút`:'';
 $('candidates').innerHTML=stage>=3?[15,30,45].map(g=>`<div class="candidate ${stage>=4&&g===d.chosen_green?'chosen':''}"><strong>${g}s</strong>Điểm chờ<br>${num(d['score_'+g])}${stage>=4&&g===d.chosen_green?'<br>✓ Được chọn':''}</div>`).join(''):'';
 $('candidate-note').textContent=stage>=3?'Điểm chờ = tổng hàng đợi dự báo trong 120 giây (xe·giây). Điểm thấp hơn được ưu tiên.':'';
 const group=d.phase.startsWith('NS')?'Bắc–Nam':'Đông–Tây';
 const startTotal=d.queue_NS+d.queue_EW, total=row.queue_NS+row.queue_EW;
 const headings=['1. Xe đến và xếp hàng','2. Quan sát: đang có bao nhiêu xe chờ?','3. Đồng bộ: cập nhật bản sao số','4. Dự báo: thử trước 3 cách bật đèn','5. Quyết định: gửi lệnh về giao lộ','6. Phản hồi: xe đi, hàng đợi thay đổi'];
 const descriptions=[
 `Xe được đưa vào giao lộ từ dữ liệu lưu lượng. Tại ${clock(d.time)}, có ${d.queue_NS} xe Bắc–Nam và ${d.queue_EW} xe Đông–Tây đang chờ. Đèn đỏ thì xe dừng; đèn xanh thì xe được đi.`,
 `Cảm biến ảo đếm được ${startTotal} xe đang chờ và gửi số xe từng hướng, trạng thái đèn cùng các lượt xe đã đến cho Twin. Trong demo này, cảm biến lấy số liệu từ mô phỏng.`,
 `Twin là bản sao số của giao lộ. Nó cập nhật hàng đợi Bắc–Nam = ${d.queue_NS}, Đông–Tây = ${d.queue_EW}. Bản sao này dùng để tính thử phương án trước khi điều khiển giao lộ.`,
 `ML học từ những lượt xe đã đến để ước lượng lưu lượng sắp tới. Twin dùng ước lượng đó để thử cho hướng ${group} xanh 15, 30 hoặc 45 giây và tính tổng chờ trong cùng 120 giây. Việc thử diễn ra trong bản sao, chưa tác động đến giao lộ.`,
 `Phương án có điểm chờ dự báo thấp nhất là cho ${group} xanh ${d.chosen_green} giây. Twin gửi lựa chọn này cho bộ điều khiển đèn. Bây giờ hãy nhìn xe trên giao lộ bắt đầu di chuyển.`,
 `Đang phát lại diễn biến sau lệnh: ${group} được xanh ${d.chosen_green} giây, sau đó vàng 3 giây và đỏ toàn bộ 2 giây. Hàng đợi hiện là ${total} xe; lúc chọn đèn là ${startTotal} xe. Xe mới vẫn có thể đến, nên hàng đợi không nhất thiết giảm. Quan sát mới tiếp tục quay về Twin.`
 ];
 $('heading').textContent=headings[stage];$('explain').textContent=descriptions[stage];
}
function tick(){
 if(!running)return;
 if(stage===5){
   if(frame<endTime()){frame++;render();timer=setTimeout(tick,500);return;}
   if(round===data.decisions.length-1){running=false;finished=true;$('play-status').textContent='Đã phát hết đoạn demo';$('play').textContent='▶ Xem lại demo';$('heading').textContent='Đã xem xong vòng lặp Digital Twin';$('explain').textContent=`Xe đến → quan sát → cập nhật bản sao → dự báo và thử phương án → điều khiển đèn → nhận phản hồi. Demo đã phát lại ${data.decisions.length} quyết định, từ ${clock(data.window_start)} đến ${clock(data.window_end)}. Đây là cách Twin hỗ trợ chọn đèn trước khi áp dụng vào môi trường.`;return;}
   round++;stage=0;
 }else{stage++;if(stage===5)frame=data.decisions[round].time;}
 render();schedule();
}
function schedule(){timer=setTimeout(tick,stage===5?500:stage===3?6500:stage===0?3500:4500);}
function reset(){clearTimeout(timer);document.getAnimations().forEach(a=>a.cancel());$('cars').replaceChildren();visualQueues.NS=[];visualQueues.EW=[];lastSceneTime=null;round=0;stage=0;frame=0;running=false;finished=false;$('play').textContent='▶ Bắt đầu demo';render();}
$('play').onclick=()=>{if(finished)reset();running=!running;clearTimeout(timer);$('play').textContent=running?'Ⅱ Tạm dừng':'▶ Tiếp tục';render();document.getAnimations().forEach(a=>running?a.play():a.pause());if(running)schedule();};
$('reset').onclick=reset;
render();
</script></body></html>'''
