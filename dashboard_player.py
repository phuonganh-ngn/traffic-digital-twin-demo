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
button{border:0;border-radius:12px;padding:13px 24px;background:#165bd8;color:white;font-size:17px;font-weight:700;cursor:pointer}button:hover{background:#104bb7}button.secondary{background:#eaf0f7;color:#334155;font-size:13px;padding:10px 14px}.actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap}button:disabled{opacity:.4;cursor:default}
.flow{display:grid;grid-template-columns:repeat(6,1fr);gap:5px;margin:18px 0}.step{border-radius:9px;padding:10px 5px;background:#f0f3f7;text-align:center;font-size:12px;color:#64748b;transition:.3s}.step.active{background:#165bd8;color:white;font-weight:700}.step.done{background:#e3f4ed;color:#20704f}

.meta{display:grid;grid-template-columns:1.2fr 1fr 1.3fr;gap:12px;margin-top:18px}.meta-card{border:1px solid #e3eaf2;border-radius:12px;padding:10px 14px;background:#f9fbfd}.meta-card small{display:block;font-size:10px;letter-spacing:1px;color:#6d7e92;font-weight:750}.meta-card strong{font-size:18px;font-variant-numeric:tabular-nums}.meta-card span{font-size:12px;color:#65758a}.progress{height:4px;background:#e9eef5;border-radius:9px;overflow:hidden;margin-top:14px}.progress i{display:block;height:100%;background:linear-gradient(90deg,#2268df,#40b2c6);transition:width .45s linear}
.scene{display:grid;grid-template-columns:1.75fr 1fr;gap:18px;align-items:stretch}.roadbox{background:#e5eee4;border:1px solid #dbe5db;border-radius:16px;overflow:hidden;position:relative;height:370px;isolation:isolate}.map{position:absolute;width:100%;height:100%;inset:0}.road-heading{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;font-size:12px;color:#61758a}.legend-dot{width:8px;height:8px;border-radius:50%;background:#3a8bdf;display:inline-block;margin-right:5px}.legend-dot.ew{background:#e6ae43;margin-left:12px}.tag{position:absolute;background:#fffffff2;backdrop-filter:blur(4px);border:1px solid #dce5de;border-radius:9px;padding:6px 10px;font-size:12px;font-weight:700;box-shadow:0 3px 9px #233c2210;z-index:4}.ns-tag{left:12px;top:12px;border-left:3px solid #4599e7}.ew-tag{right:12px;bottom:12px;border-left:3px solid #e5ac3c}.counter{position:absolute;left:12px;bottom:12px;background:#fffffff0;border-radius:8px;padding:5px 9px;font-size:11px;color:#486079;z-index:4}#cars{position:absolute;inset:0;z-index:2;pointer-events:none}.car{position:absolute;width:32px;height:22px;background:transparent;border:0;filter:drop-shadow(0 2px 2px #101d3660);will-change:left,top;transform:translate(-50%,-50%) scale(var(--car-scale,1))}.car::before{content:"";position:absolute;right:6px;top:2px;width:5px;height:10px;background:linear-gradient(90deg,#47778f,#b5d7e8);border-radius:1px 3px 3px 1px;box-shadow:-9px 0 0 -1px #547c94}.car::after{content:"";position:absolute;left:4px;top:-3px;width:5px;height:3px;background:#1c2731;border-radius:1px;box-shadow:14px 0 #1c2731,0 17px #1c2731,14px 17px #1c2731}.car .headlights{position:absolute;right:-1px;top:2px;width:2px;height:3px;background:#fff8d7;border-radius:1px;box-shadow:0 7px #fff8d7}.car .taillights{position:absolute;left:-1px;top:2px;width:2px;height:3px;background:#e95e51;box-shadow:0 7px #e95e51}.car.ns{transform:translate(-50%,-50%) rotate(90deg) scale(var(--car-scale,1))}
.car::before,.car::after{display:none}.car svg{display:block;width:100%;height:100%;overflow:visible}.light{position:absolute;width:29px;padding:6px 5px;display:flex;flex-direction:column;gap:5px;background:linear-gradient(90deg,#101820,#35414b 50%,#121b23);border:2px solid #111a22;border-radius:9px;box-shadow:2px 4px 5px #0005;z-index:3}.light::after{content:"";position:absolute;top:100%;left:11px;width:4px;height:18px;background:linear-gradient(90deg,#5d6a75,#a6b0b7,#5d6a75)}.bulb{display:block;width:15px;height:15px;border-radius:50%;border-top:2px solid #0009;box-shadow:inset 0 2px 4px #0009}.bulb.red{background:#4b2528}.bulb.yellow{background:#49402a}.bulb.green{background:#203e33}.light[data-state="red"] .red{background:radial-gradient(circle at 40% 35%,#ffc0b9,#ff453f 55%,#c61b18);box-shadow:0 0 9px #ff453faa}.light[data-state="yellow"] .yellow{background:radial-gradient(circle at 40% 35%,#fff6bd,#ffce32 55%,#d58d0c);box-shadow:0 0 9px #ffce32aa}.light[data-state="green"] .green{background:radial-gradient(circle at 40% 35%,#c0ffe1,#2be48b 55%,#0a9953);box-shadow:0 0 9px #2be48baa}.light.ns{left:59%;top:13%}.light.ew{left:35%;top:67%}.phase-pill{display:inline-block;margin-top:9px;padding:5px 10px;border-radius:20px;background:#eff4fa;font-size:12px;color:#486079;border:1px solid #dce6f1}.phase-pill[data-tone="green"]{background:#e9f7ef;color:#217751}.phase-pill[data-tone="yellow"]{background:#fff6df;color:#956b10}.phase-pill[data-tone="red"]{background:#fff0ef;color:#a34d49}
.twin{border:2px solid #dce6f3;border-radius:15px;padding:17px;transition:.3s}.twin.active{border-color:#165bd8;box-shadow:0 0 0 4px #165bd810}.twintitle{font-size:17px;font-weight:750}.values{display:flex;gap:12px;margin:12px 0}.value{flex:1;border-radius:9px;background:#f1f5fa;padding:10px}.value strong{font-size:24px;display:block}.candidates{display:flex;gap:7px;margin-top:12px}.candidate{flex:1;padding:9px 5px;border:1px solid #dce3ec;border-radius:10px;text-align:center;font-size:12px}.candidate strong{display:block;font-size:19px}.candidate.chosen{border:2px solid #21966b;background:#eaf8f2}.explanation{margin-top:16px;background:#edf4ff;border-radius:13px;padding:17px;min-height:112px}.explanation h3{margin:0 0 6px;font-size:19px}.explanation p{margin:0;font-size:15px}.footer{margin-top:12px;font-size:12px;color:#64748b}.badge{color:#20704f;font-weight:700;font-size:12px;margin-top:10px}
.traffic-story{margin-top:12px;padding:13px;background:#f2f7fd;border:1px solid #d9e5f3;border-radius:12px;font-size:13px}.traffic-story strong{display:block;margin-bottom:6px}.traffic-story p{margin:5px 0}.traffic-story ul{margin:8px 0 0;padding-left:18px;font-size:12px}.traffic-story li{margin:5px 0}.traffic-story[hidden]{display:none}.sync-notice{margin-top:9px;padding:10px;border-radius:9px;background:#eaf7ef;color:#28664b;font-size:12px;white-space:pre-line}.sync-notice[data-stale="true"]{background:#fff5df;color:#805f13}.sync-notice[hidden]{display:none}.case-feedback{margin-top:14px;padding:14px;border:1px solid #b9dfcb;background:#f0faf5;border-radius:12px}.case-feedback h4{margin:0 0 8px;color:#246347}.case-feedback table{width:100%;border-collapse:collapse;font-size:12px;text-align:right}.case-feedback th,.case-feedback td{padding:7px 4px;border-bottom:1px solid #dcece2}.case-feedback th:first-child,.case-feedback td:first-child{text-align:left}.case-feedback[hidden]{display:none}@media(max-width:650px){.scene{grid-template-columns:1fr}.roadbox{height:310px}.meta{grid-template-columns:1fr 1fr}.meta-card:last-child{grid-column:1/-1}.flow{grid-template-columns:repeat(3,1fr)}.title{font-size:20px}.shell{padding:12px}}
</style></head><body><div class="shell">
<div class="top"><div><div class="eyebrow">MỘT GIAO LỘ · MỘT VÒNG ĐIỀU KHIỂN</div><div class="title">Xe đang chờ. Twin sẽ chọn đèn thế nào?</div><div class="muted">Mỗi case bắt đầu từ một hàng đợi riêng. Xem chọn đèn, xe đi qua và phản hồi; demo dừng ở cuối case.</div></div><div class="actions"><button id="play">▶ Bắt đầu case</button><button id="reset" class="secondary" title="Khởi động lại case hiện tại">↺ Xem lại case</button><button id="next-case" class="secondary" disabled>Case tiếp theo →</button></div></div>
<div class="meta"><div class="meta-card"><small>KHUNG GIỜ CASE NÀY</small><strong id="window"></strong><br><span>Trích từ buổi mô phỏng 07:00–09:00</span></div><div class="meta-card"><small>THỜI ĐIỂM ĐANG XEM</small><strong id="now"></strong><br><span id="play-status">Sẵn sàng phát lại · tốc độ xe 2×</span></div><div class="meta-card"><small>CASE ĐANG XEM</small><strong id="round"></strong><br><span id="global-round"></span></div></div><div class="progress"><i id="progress"></i></div><div class="flow" id="flow"></div>
<div class="scene"><div><div class="road-heading"><strong>GIAO LỘ — SỐ XE ĐANG CHỜ HIỆN TẠI</strong><span><i class="legend-dot"></i>Bắc–Nam<i class="legend-dot ew"></i>Đông–Tây</span></div><div class="roadbox"><svg class="map" viewBox="0 0 600 400" preserveAspectRatio="none" aria-hidden="true"><defs><pattern id="grass" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M3 8l2-3m12 15l2-3" stroke="#c4d6bf" stroke-width="1" opacity=".6"/></pattern><pattern id="paving" width="14" height="14" patternUnits="userSpaceOnUse"><path d="M0 0h14v14H0z" fill="#e5e5de" stroke="#d4d6cf" stroke-width=".6"/></pattern><filter id="shadow"><feDropShadow dx="1" dy="3" stdDeviation="2" flood-opacity=".16"/></filter></defs><rect width="600" height="400" fill="url(#grass)"/><path d="M234 0h132v134h234v132H366v134H234V266H0V134h234z" fill="url(#paving)"/><path d="M252 0h96v152h252v96H348v152h-96V248H0v-96h252z" fill="#65737c"/><path d="M257 0h86v157h257v86H343v157h-86V243H0v-86h257z" fill="#3a4954"/><g stroke="#bdc6ca" stroke-width="2" stroke-dasharray="12 11" opacity=".7"><path d="M300 0v140m0 120v140M0 200h240m120 0h240"/></g><g stroke="#e4c96c" stroke-width="1.5" opacity=".75"><path d="M297 0v142m6-142v142m-6 116v142m6-142v142M0 197h240M0 203h240m120-6h240m-240 6h240"/></g><g fill="#edf0e9"><rect x="258" y="140" width="36" height="4"/><rect x="238" y="159" width="4" height="34"/><rect x="306" y="256" width="36" height="4"/><rect x="358" y="207" width="4" height="34"/></g><g fill="#e0e6df" opacity=".7"><path d="M273 70h5v17h5l-7.5 9-7.5-9h5z"/><path d="M140 174v5h17v5l9-7.5-9-7.5v5z"/><path d="M322 330h5v-17h5l-7.5-9-7.5 9h5z"/><path d="M460 222v5h-17v5l-9-7.5 9-7.5v5z"/></g><g filter="url(#shadow)"><g fill="#91af82"><circle cx="54" cy="86" r="21"/><circle cx="167" cy="46" r="17"/><circle cx="535" cy="62" r="24"/><circle cx="439" cy="107" r="14"/><circle cx="67" cy="326" r="23"/><circle cx="187" cy="303" r="17"/><circle cx="480" cy="325" r="22"/><circle cx="554" cy="290" r="15"/></g><g fill="#a9c49a"><circle cx="49" cy="80" r="13"/><circle cx="530" cy="55" r="15"/><circle cx="61" cy="319" r="14"/><circle cx="474" cy="320" r="13"/></g></g></svg><div id="cars"></div><div class="light ns" id="light-ns" role="img"><span class="bulb red"></span><span class="bulb yellow"></span><span class="bulb green"></span></div><div class="light ew" id="light-ew" role="img"><span class="bulb red"></span><span class="bulb yellow"></span><span class="bulb green"></span></div><div class="tag ns-tag" id="ns"></div><div class="tag ew-tag" id="ew"></div><div class="counter" id="clock"></div></div><div id="phase-status" class="phase-pill"></div><div class="muted" id="served-count" style="margin-top:7px"></div><div class="muted" id="road-note" style="margin-top:6px"></div><div id="traffic-story" class="traffic-story" hidden></div></div>
<div class="twin" id="twin"><div class="eyebrow">BẢN SAO SỐ CỦA GIAO LỘ</div><div class="twintitle">Digital Twin</div><div class="muted">Nhận số xe chờ, dự báo và thử phương án trước khi ra lệnh.</div><div class="values"><div class="value">Bắc–Nam (bản sao)<strong id="t-ns">—</strong></div><div class="value">Đông–Tây (bản sao)<strong id="t-ew">—</strong></div></div><div class="muted" id="sync"></div><div id="sync-notice" class="sync-notice" hidden></div><div id="forecast" class="badge" style="white-space:pre-line"></div><div id="forecast-help" class="muted" style="margin-top:6px"></div><div id="signal-plan" class="badge" style="margin-top:12px"></div><div class="candidates" id="candidates"></div><div id="signal-help" class="muted" style="margin-top:7px"></div><div class="muted" id="candidate-note" style="margin-top:8px"></div></div></div>
<div class="explanation" aria-live="polite"><h3 id="heading"></h3><p id="explain"></p></div>
<div id="case-feedback" class="case-feedback" hidden></div><div class="footer">Mỗi case là một đoạn log riêng: hàng đợi ban đầu → chọn đèn → áp dụng khoảng xanh → phản hồi rồi dừng. Case sau chỉ mở khi bấm nút. Mỗi hình xe tương ứng 1 xe trong mô phỏng. Vẽ đủ xe đang chờ; kích thước xe được điều chỉnh để hàng đợi vừa khung. Xe được phục vụ đi qua vạch rồi ra khỏi khung, đúng số lượt trong log. Hai đường đại diện hai nhóm hướng, không phải hình học giao lộ thật.</div>
</div><script>
const data=__DATA__;
const steps=['Xe đang chờ','Quan sát','Đồng bộ Twin','Dự báo & thử','Chọn đèn','Xe đi & phản hồi'];
const $=id=>document.getElementById(id);
let round=0, stage=0, frame=0, running=false, finished=false, timer=null;
const frames=new Map(data.frames.map(r=>[r.time,r]));
const num=n=>Math.round(n).toLocaleString('vi-VN');
function clock(t){return `${String(7+Math.floor(t/3600)).padStart(2,'0')}:${String(Math.floor(t%3600/60)).padStart(2,'0')}:${String(t%60).padStart(2,'0')}`;}
function endTime(){const d=data.decisions[round];return Math.min(d.time+d.chosen_green,data.end);}
const visualQueues={NS:[],EW:[]};
const replayServed={NS:0,EW:0};
const queueLayout={};
for(const g of ['NS','EW']){
 const maximum=Math.max(1,...data.frames.map(r=>r['queue_'+g]));
 const normal=g==='NS'?32:36,available=g==='NS'?112:208;
 const step=Math.min(normal,available/Math.max(1,maximum-1));
 queueLayout[g]={step,scale:step/normal};
}
let lastSceneTime=null;
function carScale(group){
 const box=$('cars').getBoundingClientRect();
 // Use the available pixels along this road, not both axes and queue density twice.
 const pixelsPerUnit=group==='NS'?(box.height||370)/400:(box.width||800)/600;
 return Math.min(1,queueLayout[group].step*pixelsPerUnit/38);
}
function queuePosition(group,index){
 return group==='NS'?{x:46.2,y:(124-index*queueLayout.NS.step)/4}
                    :{x:(224-index*queueLayout.EW.step)/6,y:44.2};
}
function putCar(group,x,y){
 const el=document.createElement('span');el.className='car '+group.toLowerCase();
 el.dataset.group=group;el.dataset.state='waiting';
 el.style.setProperty('--car-scale',carScale(group));
 const color=group==='NS'?'#328fdd':'#efbb36';
 el.innerHTML=`<svg viewBox="0 0 32 22" aria-hidden="true"><rect x="5" y="1" width="6" height="4" rx="1.2" fill="#111c29"/><rect x="21" y="1" width="6" height="4" rx="1.2" fill="#111c29"/><rect x="5" y="17" width="6" height="4" rx="1.2" fill="#111c29"/><rect x="21" y="17" width="6" height="4" rx="1.2" fill="#111c29"/><rect x="1" y="3" width="30" height="16" rx="5" fill="${color}" stroke="#24334a" stroke-width="1.1"/><rect x="11" y="4.5" width="10" height="13" rx="2" fill="#f4fbff" fill-opacity=".65"/><path d="M22 5l4 1v10l-4 1zM8 5H5v12h3z" fill="#294b67"/><path d="M12 6h8v10h-8z" fill="${color}"/><path d="M29 6v3m0 4v3" stroke="#fffbe3" stroke-width="2.3"/><path d="M2 6v3m0 4v3" stroke="#be3036" stroke-width="1.8"/></svg>`;
 $('cars').append(el);el.style.left=x+'%';el.style.top=y+'%';return {el,x,y};
}
function resizeCars(){
 $('cars').querySelectorAll('.car').forEach(el=>el.style.setProperty('--car-scale',carScale(el.dataset.group)));
}
if('ResizeObserver' in window)new ResizeObserver(resizeCars).observe($('cars'));
window.addEventListener('resize',resizeCars);
function moveCar(car,x,y,duration){
 if(car.x===x&&car.y===y)return;
 const parent=$('cars').getBoundingClientRect(),box=car.el.getBoundingClientRect();
 const fromX=(box.left+box.width/2-parent.left)/parent.width*100;
 const fromY=(box.top+box.height/2-parent.top)/parent.height*100;
 car.el.getAnimations().forEach(a=>a.cancel());
 car.el.style.left=x+'%';car.el.style.top=y+'%';car.x=x;car.y=y;
 if(duration)return car.el.animate([{left:fromX+'%',top:fromY+'%'},{left:x+'%',top:y+'%'}],{duration,easing:'cubic-bezier(.25,.1,.25,1)'});
}
function departCar(car,group){
 car.el.dataset.state='departing';
 replayServed[group]++;
 const animation=moveCar(car,group==='NS'?46.2:108,group==='NS'?108:44.2,1000);
 if(animation)animation.finished.then(()=>car.el.remove()).catch(()=>{});else car.el.remove();
}
function updateCars(row,moving){
 if(lastSceneTime===null){
  // Initial state is a recorded snapshot; each waiting vehicle gets one identity.
  for(const g of ['NS','EW']){
   for(let i=0;i<row['queue_'+g];i++){
    const p=queuePosition(g,i);visualQueues[g].push(putCar(g,p.x,p.y));
   }
  }
 }else if(moving&&row.time>lastSceneTime){
  for(let t=lastSceneTime+1;t<=row.time;t++){
   const observation=frames.get(t);
   if(!observation)throw new Error('Missing replay second '+t);
   for(const g of ['NS','EW']){
    const queue=visualQueues[g];
    // Apply exactly the simulator order: every arrival, then every departure.
    for(let n=0;n<observation['arrivals_'+g];n++){
     const p=queuePosition(g,queue.length);
     const car=putCar(g,p.x,p.y);queue.push(car);
     car.el.animate([{opacity:0},{opacity:1}],{duration:350});
    }
    for(let n=0;n<observation['served_'+g];n++){
     if(!queue.length)throw new Error('Departure without a vehicle: '+g+' at '+t);
     const car=queue.shift();
     // A newly arrived vehicle may be served in this same second.
     const front=queuePosition(g,0);moveCar(car,front.x,front.y,0);
     departCar(car,g);
    }
    if(queue.length!==observation['queue_'+g])throw new Error('Queue/log mismatch: '+g+' at '+t);
    queue.forEach((car,i)=>{const p=queuePosition(g,i);moveCar(car,p.x,p.y,450);});
   }
  }
 }
 lastSceneTime=row.time;
 $('served-count').textContent=`Đã đi qua trong case này: Bắc–Nam ${replayServed.NS} xe · Đông–Tây ${replayServed.EW} xe. Mỗi hình xe = 1 xe.`;
}
function explainTraffic(row,d){
 const active=stage===5;
 $('traffic-story').hidden=!active;
 if(!active)return;
 const records=data.frames.filter(r=>r.time>d.time&&r.time<=row.time);
 const names={NS:'Bắc–Nam',EW:'Đông–Tây'};
 const balances=['NS','EW'].map(g=>{
  const arrivals=records.reduce((sum,r)=>sum+r['arrivals_'+g],0);
  return `<p><b>${names[g]}:</b> ${d['queue_'+g]} xe ban đầu + ${arrivals} xe mới đến − ${replayServed[g]} xe đã đi = <b>${row['queue_'+g]} xe đang chờ</b>.</p>`;
 }).join('');
 const latest=records.at(-1),prior=latest?(frames.get(latest.time-1)||d):null;
 const now=latest?['NS','EW'].map(g=>{
  const arrivals=latest['arrivals_'+g],served=latest['served_'+g];
  if(!arrivals&&!served)return latest['queue_'+g]>0&&latest.phase!==g+'_GREEN'?`${names[g]} vẫn còn ${latest['queue_'+g]} xe chờ vì đèn đỏ.`:`${names[g]} không có xe đến hoặc đi trong giây này.`;
  return `${names[g]}: ${prior['queue_'+g]} xe chờ từ giây trước + ${arrivals} xe vừa đến − ${served} xe được đi → còn ${latest['queue_'+g]} xe chờ.${latest.phase!==g+'_GREEN'&&arrivals?' Xe mới đến phải chờ đèn đỏ.':''}`;
 }).join(' '):'Chuẩn bị áp dụng đèn xanh. Xe mới vẫn có thể đến trong suốt khoảng xanh, không chỉ có số xe ban đầu.';
 const milestones=[];
 for(const r of records){
  const p=frames.get(r.time-1)||d;
  for(const g of ['NS','EW']){
   const before=p['queue_'+g],after=r['queue_'+g],arrivals=r['arrivals_'+g],served=r['served_'+g];
   if(before===0&&after>0){
    milestones.push(`<li><b>${clock(r.time)} · ${names[g]}:</b> thêm ${arrivals} xe mới, ${served} xe đi qua → còn ${after} xe chờ${r.phase!==g+'_GREEN'?' vì đèn đỏ':' (tối đa 1 xe đi/giây)'}.</li>`);
   }else if(before>0&&after===0){
    milestones.push(`<li><b>${clock(r.time)} · ${names[g]}:</b> xe cuối hàng đã đi qua → hàng đợi về 0. Xe mới vẫn có thể đến sau đó.</li>`);
   }
  }
 }
 $('traffic-story').innerHTML=`<strong>Vì sao hết xe rồi lại có xe chờ?</strong><p>Xe mới vẫn đến trong lúc đèn xanh. Số xe ban đầu không phải toàn bộ xe của case.</p>${balances}<p><b>Giây ${clock(row.time)}:</b> ${now}</p>${milestones.length?'<strong style="margin-top:10px">Các mốc dễ theo dõi</strong><ul>'+milestones.slice(-8).join('')+'</ul>':''}`;
}
function scene(row,moving=false){
 $('ns').textContent=`Bắc–Nam: ${row.queue_NS} xe chờ`;$('ew').textContent=`Đông–Tây: ${row.queue_EW} xe chờ`;
 $('clock').textContent='Đường minh họa · số đếm từ log';
 $('window').textContent=`${clock(data.decisions[round].time)}–${clock(endTime())}`;
 $('now').textContent=clock(row.time);
 $('round').textContent=`Case ${round+1} / ${data.decisions.length}`;
 $('global-round').textContent=`Lượt ${data.first_decision_number+round} / ${data.total_decisions} của cả buổi 07:00–09:00`;
 $('progress').style.width=(row.time-data.decisions[round].time)/(endTime()-data.decisions[round].time)*100+'%';
 $('play-status').textContent=finished?'Case đã xong · chọn case tiếp theo để xem tiếp':!running?'Đang dừng · bấm nút để phát':stage===5?'Xe đang di chuyển · phát lại 2×':'Tạm dừng thời gian để giải thích flow';
 for(const g of ['NS','EW']){
  const state=row.phase===g+'_GREEN'?'green':row.phase===g+'_YELLOW'?'yellow':'red';
  const light=$('light-'+g.toLowerCase());light.dataset.state=state;
  light.setAttribute('aria-label',`${g==='NS'?'Bắc–Nam':'Đông–Tây'}: đèn ${{green:'xanh',yellow:'vàng',red:'đỏ'}[state]}`);
 }
 updateCars(row,moving);
 const d=data.decisions[round],elapsed=row.time-d.time;
 explainTraffic(row,d);
 const group=d.phase.startsWith('NS')?'Bắc–Nam':'Đông–Tây';
 let phaseText='Trước quyết định · quan sát trạng thái cuối giây vừa qua',tone='red';
 if(stage===5){
  if(row.phase.endsWith('_GREEN')){phaseText=`${group} đèn xanh · còn ${Math.max(0,d.chosen_green-elapsed)} giây`;tone='green';}
  else if(row.phase.endsWith('_YELLOW')){phaseText=`${group} đèn vàng · còn ${Math.max(0,d.chosen_green+3-elapsed)} giây`;tone='yellow';}
  else phaseText=`Hai hướng đèn đỏ · chờ chuyển hướng ${Math.max(0,d.chosen_green+5-elapsed)} giây`;
 }
 $('phase-status').textContent=phaseText;$('phase-status').dataset.tone=tone;
 $('road-note').textContent=stage===5?`Giây này: ${row.arrivals_NS+row.arrivals_EW} xe đến · đi qua: Bắc–Nam ${row.served_NS}, Đông–Tây ${row.served_EW}. Hàng đợi và đèn thay đổi theo log.`:'Vẽ đủ từng xe đang chờ trước vạch dừng. Xe đầu hàng đi qua thì các xe sau tiến lên.';
}
function render(){
 $('next-case').disabled=!finished||round===data.decisions.length-1;
 $('case-feedback').hidden=!finished;
 const d=data.decisions[round], before=frames.get(d.time)||data.frames[0];
 const row=stage===5?(frames.get(frame)||before):before;
 const group=d.phase.startsWith('NS')?'Bắc–Nam':'Đông–Tây';
 const opposite=d.phase.startsWith('NS')?'Đông–Tây':'Bắc–Nam';
 $('flow').innerHTML=steps.map((s,i)=>`<div class="step ${i===stage?'active':i<stage?'done':''}">${i+1}. ${s}${i<5?' →':''}</div>`).join('');
 scene(row,stage===5&&running);
 $('twin').classList.toggle('active',stage>=2&&stage<=4);
 const synchronized=stage>=2;
 $('t-ns').textContent=synchronized?(stage===5?row.twin_queue_NS:d.queue_NS):'—';
 $('t-ew').textContent=synchronized?(stage===5?row.twin_queue_EW:d.queue_EW):'—';
 const observedAt=stage===5?row.observation_time:d.time;
 const age=stage===5?row.time-observedAt:0;
 const twinNS=stage===5?row.twin_queue_NS:d.queue_NS,twinEW=stage===5?row.twin_queue_EW:d.queue_EW;
 const differs=row.queue_NS!==twinNS||row.queue_EW!==twinEW;
 $('sync').textContent=synchronized?`Bản sao ở lần đồng bộ gần nhất: ${clock(observedAt)} · cách hiện tại ${age} giây.`:'Chưa nhận quan sát. Các ô này sẽ hiện số xe của lần đồng bộ gần nhất, không phải hàng đợi trực tiếp.';
 $('sync-notice').hidden=!synchronized;
 $('sync-notice').dataset.stale=String(differs);
 $('sync-notice').textContent=differs
  ?`Twin CHƯA cập nhật kịp (đồng bộ mỗi 10 giây).
Giao lộ hiện tại: Bắc–Nam ${row.queue_NS}, Đông–Tây ${row.queue_EW} xe chờ.
Bản sao lúc ${clock(observedAt)}: Bắc–Nam ${twinNS}, Đông–Tây ${twinEW}. Vì vậy có thể thấy giao lộ đã về 0 nhưng Twin vẫn hiện 1; Twin đổi số khi nhận quan sát mới.`
  :`Số xe trong bản sao đang khớp giao lộ tại ${clock(row.time)}. Twin nhận quan sát mỗi 10 giây và tại điểm chọn đèn; giữa các lần cập nhật, hai bên có thể khác nhau.`;
 $('forecast').textContent=stage>=3?`ML dự báo XE MỚI SẼ ĐẾN
Bắc–Nam: ${(d.rate_NS*60).toFixed(1)} xe mới/phút
Đông–Tây: ${(d.rate_EW*60).toFixed(1)} xe mới/phút`:'';
 const zeroGroup=['NS','EW'].find(g=>d['queue_'+g]===0&&d['rate_'+g]>0);
 $('forecast-help').textContent=stage<3?'':zeroGroup
  ?`Dù ban đầu ${zeroGroup==='NS'?'Bắc–Nam':'Đông–Tây'} có 0 xe chờ, ML vẫn dự báo trung bình ${(d['rate_'+zeroGroup]*60).toFixed(1)} xe mới đến mỗi phút. Đây là lưu lượng sắp đến, không phải số xe đang chờ; xe không nhất thiết đến đúng mỗi phút.`
  :'Đây là số xe MỚI dự kiến đến trung bình mỗi phút, không phải số xe đang chờ trong lần quan sát phía trên. Xe đến thực tế có thể khác dự báo.';
 $('signal-plan').textContent=stage>=4?`Đã chọn: ${group} XANH ${d.chosen_green} giây · ${opposite} ĐỎ`:stage===3?`Thử 3 thời lượng ĐÈN XANH cho nhóm ${group}`:'';
 $('signal-help').textContent=stage>=3?`Trong khoảng xanh, xe ${group} được đi; xe ${opposite} phải chờ đèn đỏ. Đây là thời gian cho cả nhóm hướng, không phải cho từng xe. Tối đa 1 xe đi qua mỗi giây nếu có xe, nên xanh 45 giây không có nghĩa chắc chắn 45 xe đi qua.`:'';
 $('candidates').innerHTML=stage>=3?[15,30,45].map(g=>`<div class="candidate ${stage>=4&&g===d.chosen_green?'chosen':''}"><strong>${g} giây</strong>đèn xanh<br>Điểm chờ<br>${num(d['score_'+g])}${stage>=4&&g===d.chosen_green?'<br>✓ Được chọn':''}</div>`).join(''):'';
 $('candidate-note').textContent=stage>=3?'Điểm chờ = tổng hàng đợi dự báo trong 120 giây (xe·giây). Điểm thấp hơn được ưu tiên.':'';
 const startTotal=d.queue_NS+d.queue_EW, total=row.queue_NS+row.queue_EW;
 const headings=['1. Hàng đợi ban đầu của case','2. Quan sát: đang có bao nhiêu xe chờ?','3. Đồng bộ: cập nhật bản sao số','4. Dự báo: thử trước 3 cách bật đèn','5. Quyết định: gửi lệnh về giao lộ','6. Phản hồi: xe đi, hàng đợi thay đổi'];
 const descriptions=[
 `Case ${round+1} bắt đầu từ snapshot lúc ${clock(d.time)}: có ${d.queue_NS} xe Bắc–Nam và ${d.queue_EW} xe Đông–Tây đang chờ. Đây là số xe ban đầu riêng của case này. Bây giờ Twin sẽ quan sát và chọn đèn.`,
 `Cảm biến ảo đếm được ${startTotal} xe đang chờ và gửi số xe từng hướng, trạng thái đèn cùng các lượt xe đã đến cho Twin. Trong demo này, cảm biến lấy số liệu từ mô phỏng.`,
 `Twin là bản sao số của giao lộ. Nó cập nhật hàng đợi Bắc–Nam = ${d.queue_NS}, Đông–Tây = ${d.queue_EW}. Bản sao này dùng để tính thử phương án trước khi điều khiển giao lộ.`,
 `ML học từ những lượt xe đã đến để dự báo số xe MỚI sắp vào giao lộ mỗi phút, khác với số xe đang chờ. Dù hàng đợi hiện bằng 0, vẫn có thể có xe mới đến. Twin dùng cả hàng đợi đã quan sát và dự báo đó để thử cho hướng ${group} xanh 15, 30 hoặc 45 giây và tính tổng chờ trong cùng 120 giây. Việc thử diễn ra trong bản sao, chưa tác động đến giao lộ.`,
 `Phương án có điểm chờ dự báo thấp nhất: bật ĐÈN XANH cho cả nhóm ${group} trong ${d.chosen_green} giây; nhóm ${opposite} giữ ĐÈN ĐỎ và phải chờ. Twin gửi lựa chọn này cho bộ điều khiển đèn. Bây giờ hãy nhìn xe trên giao lộ bắt đầu di chuyển.`,
 `Đang áp dụng: đèn ${group} XANH trong ${d.chosen_green} giây, đèn ${opposite} ĐỎ. Xe ${group} lần lượt đi qua, tối đa 1 xe mỗi giây nếu có xe. Hết khoảng xanh sẽ hiện phản hồi và dừng. Hàng đợi hiện là ${total} xe; lúc chọn đèn là ${startTotal} xe. Xe mới tiếp tục đến sau khi xe ban đầu đã đi hết. Xem phép tính và các mốc thời gian ngay dưới giao lộ; bản sao bên phải chỉ đổi số khi đồng bộ nên có thể chậm hơn giao lộ.`
 ];
 $('heading').textContent=headings[stage];$('explain').textContent=descriptions[stage];
}
function finishCase(){
 running=false;finished=true;document.getAnimations().forEach(a=>a.finish());render();
 const d=data.decisions[round],after=frames.get(endTime());
 const records=data.frames.filter(r=>r.time>d.time&&r.time<=endTime());
 const rows=['NS','EW'].map(g=>{
  const arrivals=records.reduce((sum,r)=>sum+r['arrivals_'+g],0);
  return `<tr><td>${g==='NS'?'Bắc–Nam':'Đông–Tây'}</td><td>${d['queue_'+g]}</td><td>+${arrivals}</td><td>−${replayServed[g]}</td><td><strong>${after['queue_'+g]}</strong></td></tr>`;
 }).join('');
 $('case-feedback').innerHTML=`<h4>Phản hồi case ${round+1} · ${clock(d.time)} → ${clock(endTime())}</h4><table><thead><tr><th>Hướng</th><th>Chờ ban đầu</th><th>Xe đến thêm</th><th>Đã đi qua</th><th>Còn chờ</th></tr></thead><tbody>${rows}</tbody></table><div class="muted" style="margin-top:8px">Chờ ban đầu + xe đến thêm − xe đi qua = xe còn chờ. Đây là kết quả mô phỏng sau khoảng xanh đã chọn.</div>`;
 $('play').textContent='▶ Chạy lại case này';
 $('heading').textContent=`Case ${round+1} đã kết thúc — xem phản hồi bên dưới`;
 $('explain').textContent=`Twin đã bật đèn xanh cho nhóm ${d.phase.startsWith('NS')?'Bắc–Nam':'Đông–Tây'} trong ${d.chosen_green} giây; nhóm đối diện chờ đèn đỏ. Trong case này, ${replayServed.NS} xe Bắc–Nam và ${replayServed.EW} xe Đông–Tây đi qua; còn ${after.queue_NS} xe Bắc–Nam và ${after.queue_EW} xe Đông–Tây chờ. Demo đã dừng. ${round+1<data.decisions.length?'Bấm “Case tiếp theo” để bắt đầu từ hàng đợi riêng của case khác.':'Anh đã xem hết các case; có thể chạy lại case này.'}`;
 $('phase-status').textContent='Đã hết khoảng xanh · case dừng để xem phản hồi';
}
function tick(){
 if(!running)return;
 if(stage===5){
  if(frame<endTime()){frame++;render();timer=setTimeout(tick,500);return;}
  finishCase();return;
 }
 stage++;if(stage===5)frame=data.decisions[round].time;
 render();schedule();
}
function schedule(){timer=setTimeout(tick,stage===5?500:stage===3?6500:stage===0?3500:4500);}
function reset(){clearTimeout(timer);document.getAnimations().forEach(a=>a.cancel());$('cars').replaceChildren();visualQueues.NS=[];visualQueues.EW=[];replayServed.NS=0;replayServed.EW=0;lastSceneTime=null;stage=0;frame=0;running=false;finished=false;$('play').textContent='▶ Bắt đầu case';render();}
$('play').onclick=()=>{if(finished)reset();running=!running;clearTimeout(timer);$('play').textContent=running?'Ⅱ Tạm dừng':'▶ Tiếp tục';render();document.getAnimations().forEach(a=>running?a.play():a.pause());if(running)schedule();};
$('reset').onclick=reset;
$('next-case').onclick=()=>{if(!finished||round>=data.decisions.length-1)return;round++;reset();};
render();
</script></body></html>'''
