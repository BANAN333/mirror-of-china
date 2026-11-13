/* MIRROR_UNIFIED_APPLICATION_V5: bilingual, offline-capable, no network requests. */
(() => {
  'use strict';
  const root = document.getElementById('v5-root');
  if (!root) return;
  const host = document.getElementById('v5-application');
  const zh = root.dataset.lang === 'zh';
  const lang = zh ? 'zh' : 'ru';
  const mode = root.dataset.mode;
  const STORE = 'mirror-application-route-v5';
  const CHECK_STORE = 'mirror-action-items-v5';
  const COST_STORE = 'mirror-estimated-budget-v5';
  const links = {
    admission:'https://rut-miit.ru/page/120705',
    programs:'https://rut-miit.ru/sveden/education/programs',
    fees:'https://rut-miit.ru/sveden/paid_edu',
    campaign:'https://miit.ru/admissions/degrees?year=2026',
    university:'https://www.rut-miit.ru/'
  };
  const L = zh ? {
    flow:['学习形式','申请途径 / 学费','申请层次','已有学历','俄语水平','专业选择'],
    form:['全日制','非全日制（全日制与函授结合）','函授制','尚不确定'],
    formdesc:'先选择希望采用的学习形式。目录中的形式不代表该年度开放招生。',
    finance:['合同制 / 自费','一般竞争 / 预算名额','俄罗斯政府配额'],
    financedesc:'选择计划采用的途径，系统会提醒你核查对应资格与要求。',
    level:['基础高等教育 / 专家学位','硕士','博士研究生'],
    leveldesc:'以大学公布的培养层次为准；不是全部专业都会向外国学生招生。',
    edu:['高中学历','职业 / 专科学历','已获大学学历','其他 / 尚不确定'],
    edudesc:'此处仅用于提醒可能的前置学历要求，不判断你的学历是否被认可。',
    russian:['可以使用俄语学习','需要语言准备','尚不清楚'],
    rudesc:'课程与入学考试语言应以具体项目和当年规则为准。',
    program:'选择第一个专业',program2:'可选：选择第二个专业作比较',
    programdesc:'从俄交大公布的课程计划目录选择。名称使用官方俄文，搜索支持专业代码。',
    search:'按专业代码、名称、方向搜索…',choose:'点击，展开专业目录',count:'找到的项目',
    noMatches:'当前筛选条件没有找到项目。可以修改学习形式或培养层次，或选择稍后再决定。',
    skip:'还没选好专业，先生成准备计划',remove:'取消第二个专业',
    progress:'已经回答', of:' / 6 个问题', editable:'可以随时修改之前的选择',
    wait:'继续填写下一个问题，即可生成你的行动计划。',
    summary:'你的个性化申请路线', resultsDesc:'依据你选择的条件生成准备步骤。此结果不构成资格审查。',
    plan:'打开我的详细行动清单',download:'下载准备计划',reset:'重新填写',
    warnings:'需要重点核实', comparison:'两个专业的实际比较',
    fields:['专业代码','专业名称','方向 / 概况','培养层次','学习形式','课程计划年份','正式来源'],
    unknown:'需单独核实', official:'查看大学官方来源',
    budget:'可选：估算学习和生活预算',budgetText:'先从大学正式材料核实学费，再输入自己的估计。数字由你输入，不是俄交大的官方报价。',
    cost:['每学期学费（₽）','学期数','每月住宿预算（₽）','每月其他费用（₽）','月数'],total:'个人估算合计',
    costCaution:'不自动包含机票、签证、保险等额外支出。',
    financeWarnings:{contract:'自费不等于免试，也不保证录取。需确认学费、招生名额和合同条件。',general:'外国公民申请一般预算名额需确认具体资格。专业有预算名额不代表你自动有资格。',quota:'政府配额采用独立的申请及选拔流程；本工具不能确认你已获得名额。'},
    qualification:'硕士或博士通常有相关前置学历要求；你所选学历可能不足，请先核实。',
    language:'需要核实具体专业的授课语言、考试语言，以及是否提供语言准备。',
    noProgram:'尚未选定专业。请从大学正式公布的目录中核实，并确认本年度招生。',
    formWarning:'注意：课程计划存在此学习形式，不等于该年为外国申请者开放这一形式。',
    steps:['查阅适用年份的外国公民招生规定','核查所选申请途径的资格、名额与费用','核实专业、学习形式与授课语言','准备学历文件、翻译和必要证明','核实考试、时间并使用官方途径报名','按照正式录取结果办理后续手续'],
    routeAction:{contract:'核实合同制实际招生、最新学费以及合同条款。',general:'核实本人是否有资格参加预算制一般竞争录取。',quota:'核查政府配额的独立申请、评选及结果确认步骤。'},
    programAction:'核实实际招生及学习形式：',
    checklist:'详细行动清单', resume:'我的申请路线',emptyRoute:'尚未生成个性化路线。可以从一个通用行动清单开始，也可以先填写申请助手。',
    startWizard:'填写申请助手', editWizard:'修改申请信息',
    checkStats:'已完成操作', taskProgress:'本阶段已完成', nextTask:'接下来要做的事', goTo:'跳转到该操作', allDone:'当前清单的所有操作已标记完成。', stagesStatus:['未开始','进行中','已完成'],
    filterNote:'根据已选专业与申请方式整理。只有你实际完成并核对过的事项才应该勾选。',
    resetTasks:'清空已完成的操作',resetConfirm:'确定清空所有已完成的操作吗？',
    exportTasks:'下载我的操作清单',details:'官方资料',
    stages:['确认申请条件','核实招生途径与专业','准备申请文件','语言与入学考试','提交申请并跟踪','录取决定与合同','入境、住宿与报到'],
    taskDone:'你已完成当前适用任务。仍需按正式要求核实。',
    catalogYear:'2026年课程计划目录',curricula:'官方培养方案',change:'修改选择',
    changeNote:'修改申请路线后，清单将按新路线更新；已完成的通用任务会保留。',
    compareNotice:'比较的是大学公开的课程计划信息，不代表实际招生、奖学金、语言或费用已确认。',
    generic:'未填写信息：这里显示通用任务。',
    noData:'无法加载专业目录。可以先生成不指定专业的准备路线。'
  } : {
    flow:['Форма обучения','Способ поступления','Уровень образования','Предыдущее образование','Знание русского','Выбор программы'],
    form:['Очная','Очно-заочная','Заочная','Пока не определился'],
    formdesc:'Сначала укажи желаемую форму обучения. Наличие формы в каталоге не означает открытый набор.',
    finance:['Платное обучение','Общий бюджетный конкурс','Государственная квота'],
    financedesc:'Выбери предполагаемый способ поступления: для каждого действуют свои требования.',
    level:['Базовое высшее / специалитет','Магистратура','Аспирантура'],
    leveldesc:'Отфильтруем официальный перечень по уровню. Наличие учебного плана — не гарантия набора.',
    edu:['Школа / аттестат','Колледж / СПО','Уже есть высшее образование','Другое / не уверен'],
    edudesc:'Это помогает предупредить о требованиях к предыдущему диплому, а не проверить его признание.',
    russian:['Могу учиться на русском','Нужна языковая подготовка','Пока не знаю'],
    rudesc:'Язык обучения и вступительных испытаний нужно отдельно подтвердить для программы.',
    program:'Выбери первую программу',program2:'Необязательно: вторую программу для сравнения',
    programdesc:'Выбирай из официального реестра учебных планов РУТ. Прокручивай список или ищи по названию и коду.',
    search:'Найти код, программу или профиль…',choose:'Нажми для выбора программы',count:'Вариантов',
    noMatches:'По этим фильтрам программ не нашлось. Измени форму или уровень либо продолжи без выбора.',
    skip:'Пока не выбрал программу — получить план',remove:'Очистить сравнение',
    progress:'Заполнено',of:' из 6 шагов',editable:'Любой предыдущий ответ можно изменить',
    wait:'Ответь на следующий вопрос — персональный план появится после выбора программы.',
    summary:'Твой персональный маршрут',resultsDesc:'План составлен из твоих ответов, но не определяет право на поступление.',
    plan:'Перейти к подробному плану действий',download:'Скачать план .txt',reset:'Начать заново',
    warnings:'На что обратить внимание',comparison:'Сравнение двух реальных программ',
    fields:['Код','Направление','Профиль / название','Уровень','Форма обучения','Год учебного плана','Официальный источник'],
    unknown:'Проверить отдельно',official:'Официальные источники',
    budget:'Дополнительно: рассчитать ориентировочный бюджет',budgetText:'Стоимость обучения сначала сверь с документом РУТ. Все суммы вводишь сам — калькулятор не выдаёт официальный прайс.',
    cost:['Стоимость за семестр (₽)','Число семестров','Жильё в месяц (₽)','Другие расходы в месяц (₽)','Число месяцев'],total:'Твоя ориентировочная сумма',
    costCaution:'Автоматически не включены билеты, виза, страховка и другие возможные расходы.',
    financeWarnings:{contract:'Платное обучение не означает приём без экзаменов и не гарантирует зачисление. Уточни стоимость, договор и наличие набора.',general:'Участие иностранного гражданина в бюджетном конкурсе зависит от его оснований и правил. Наличие бюджетных мест не даёт автоматического права.',quota:'Для государственной квоты действует отдельный отбор. Выбор этого варианта не подтверждает получение квоты.'},
    qualification:'Для магистратуры или аспирантуры обычно нужно предшествующее высшее образование. Проверь требования к своему диплому.',
    language:'Нужно уточнить язык программы и вступительных испытаний; может потребоваться языковая подготовка.',
    noProgram:'Программа пока не выбрана. Найди её в официальном реестре и проверь приём в текущем году.',
    formWarning:'Наличие этой формы в учебных планах не подтверждает доступность приёма для иностранцев.',
    steps:['Открыть правила поступления иностранцев на нужный год','Уточнить доступность выбранного способа приёма и финансирования','Проверить программу, форму обучения и язык преподавания','Подготовить образовательные документы и необходимые переводы','Уточнить экзамены, сроки и подать заявление официальным способом','Следовать решению университета при зачислении и подготовке к въезду'],
    routeAction:{contract:'Уточнить договорный набор, актуальную стоимость и условия договора.',general:'Подтвердить основания участия в бюджетном конкурсе иностранных граждан.',quota:'Выяснить отдельный порядок подачи, отбора и подтверждения государственной квоты.'},
    programAction:'Проверить набор и форму обучения по программе:',
    checklist:'Подробный чек-лист',resume:'Маршрут поступления',emptyRoute:'Ты ещё не сформировал персональный маршрут. Можно пройти общий чек-лист или сначала заполнить анкету.',
    startWizard:'Открыть помощник',editWizard:'Изменить ответы',
    checkStats:'Выполнено действий', taskProgress:'В этом этапе выполнено', nextTask:'Следующее действие',goTo:'Перейти к действию', allDone:'Все действия в текущем списке отмечены выполненными.',stagesStatus:['Не начато','В работе','Готово'],
    filterNote:'План подстраивается под программу и способ поступления. Отмечай только действительно сделанные и проверенные действия.',
    resetTasks:'Сбросить выполнение',resetConfirm:'Сбросить все выполненные действия?',
    exportTasks:'Скачать список действий',details:'Официальные материалы',
    stages:['Проверка условий','Программа и способ поступления','Подготовка документов','Язык и экзамены','Подача заявления','Зачисление и договор','Въезд, общежитие, начало учёбы'],
    taskDone:'Действия отмечены выполненными. Сверь их с актуальными требованиями вуза.',
    catalogYear:'Реестр учебных планов 2026',curricula:'Официальный учебный план',change:'Изменить',
    changeNote:'Если изменить условия в анкете, персональные пункты обновятся; универсальные отметки останутся.',
    compareNotice:'Сравниваются опубликованные сведения об учебных планах, а не фактический набор, бюджетные места, язык или цена.',
    generic:'Маршрут не заполнен: показаны общие действия.',
    noData:'Каталог не загрузился. Можно получить план и без выбранной программы.'
  };

  const $ = (q,p=root) => p.querySelector(q);
  const $$ = (q,p=root) => [...p.querySelectorAll(q)];
  const node = (tag, cls, text) => {const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
  const add = (parent, tag, cls, text) => {const n=node(tag,cls,text);parent.appendChild(n);return n;};
  const mklink = (url,text) => {const a=node('a','v5-link',text);a.href=url;a.target='_blank';a.rel='noopener noreferrer';return a;};
  const save = (key,val) => {try{localStorage.setItem(key,JSON.stringify(val));}catch(_){}};
  const read = (key,fallback) => {try{const v=JSON.parse(localStorage.getItem(key)||'null');return v&&typeof v==='object'?v:fallback;}catch(_){return fallback;}};
  const getPlanFromURL = () => {
    try {const value=new URLSearchParams(location.search).get('plan');if(!value||value.length>5000)return null;
      const p=JSON.parse(value);return p && typeof p==='object' && !Array.isArray(p)?p:null;
    }catch(_){return null;}
  };
  const allowed={form:['full','hybrid','remote','undecided'],finance:['contract','general','quota'],level:['basic','master','asp'],education:['secondary','college','degree','other'],russian:['yes','no','unknown']};
  const tidy = (v) => {
    const out={};
    for(const key of Object.keys(allowed))out[key]=allowed[key].includes(v?.[key])?v[key]:null;
    out.primary=typeof v?.primary==='string'&&v.primary.length<120?v.primary:null;
    out.secondary=typeof v?.secondary==='string'&&v.secondary.length<120?v.secondary:null;
    out.primaryLabel=typeof v?.primaryLabel==='string'&&v.primaryLabel.length<240?v.primaryLabel:null;
    out.secondaryLabel=typeof v?.secondaryLabel==='string'&&v.secondaryLabel.length<240?v.secondaryLabel:null;
    return out;
  };
  const encodePlan = (route) => '?plan='+encodeURIComponent(JSON.stringify(tidy(route)));
  const routeLabels={form:['full','hybrid','remote','undecided'],finance:['contract','general','quota'],level:['basic','master','asp'],education:['secondary','college','degree','other'],russian:['yes','no','unknown']};
  const labelByValue=(field,value)=>{const i=(routeLabels[field]||[]).indexOf(value);const data={form:L.form,finance:L.finance,level:L.level,education:L.edu,russian:L.russian}[field];return i>=0?data[i]:L.unknown;};
  const programSafeUrl=(raw)=>{try{const u=new URL(raw);if(u.protocol==='https:'&&(['rut-miit.ru','miit.ru'].some(d=>u.hostname===d||u.hostname.endsWith('.'+d))))return u.href;}catch(_){}return links.programs;};
  const sourceRow=(container,items)=>{for(const [url,text] of items)container.appendChild(mklink(programSafeUrl(url),text));};
  const download=(name,content)=>{const blob=new Blob([content],{type:'text/plain;charset=utf-8'});const u=URL.createObjectURL(blob);const a=node('a');a.href=u;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),1500);};
  function setSwitcher(plan){
    const a=$('.v5-switch',document);if(a)a.href=a.href.split('?')[0]+encodePlan(plan);
    if(mode==='wizard'){const b=$('.v5-nav-links a[href*="/checklist/"]',document);if(b)b.href=b.href.split('?')[0]+encodePlan(plan);}
  }
  let catalog=[];const byId=new Map();
  if(mode==='wizard'){
    try{const raw=JSON.parse(document.getElementById('v5-catalog').textContent);catalog=raw.programs||[];}
    catch(e){console.error('Catalog parse error',e);}
    for(const p of catalog)if(p&&p.id)byId.set(p.id,p);
  }
  // Handle duplicated route across language pages and file:// origins with URL query.
  const initial=tidy(getPlanFromURL()||read(STORE,{}));
  save(STORE,initial);
  if(mode==='wizard')wizard(initial); else checklist(initial);

  function wizard(state){
    const steps=['form','finance','level','education','russian','program'];
    host.replaceChildren();
    const prog=add(host,'section','v5-progress');
    const progressRow=add(prog,'div','v5-progress-row');const progressText=add(progressRow,'strong','');add(progressRow,'span','v5-muted',L.editable);
    const track=add(prog,'div','v5-track');const fill=add(track,'div','v5-track-fill');
    const panels={};
    const options={form:routeLabels.form,finance:routeLabels.finance,level:routeLabels.level,education:routeLabels.education,russian:routeLabels.russian};
    const labels={form:L.form,finance:L.finance,level:L.level,education:L.edu,russian:L.russian};
    const desc={form:L.formdesc,finance:L.financedesc,level:L.leveldesc,education:L.edudesc,russian:L.rudesc,program:L.programdesc};
    for(let i=0;i<steps.length;i++){
      const name=steps[i];const section=add(host,'section','v5-stage');panels[name]=section;section.dataset.step=name;
      const header=add(section,'div','v5-stage-head');add(header,'span','v5-num',String(i+1).padStart(2,'0'));const box=add(header,'div');add(box,'h2','',L.flow[i]);add(box,'p','v5-muted',desc[name]);
      if(name!=='program'){
        const container=add(section,'div','v5-options');
        options[name].forEach((key,j)=>{
          const label=add(container,'label','v5-option');const radio=add(label,'input');radio.type='radio';radio.name='v5-'+name;radio.value=key;
          radio.addEventListener('change',()=>{
            if(!radio.checked)return;
            state[name]=key;
            if(name==='form'||name==='level'){state.primary=null;state.secondary=null;}
            save(STORE,state);render();
          });
          add(label,'span','',labels[name][j]);
        });
      }else{
        const first=add(section,'div','v5-choose');add(first,'h3','',L.program);const fieldA=makePicker(first,'a',(p)=>{state.primary=p.id;state.secondary=null;render();});
        const second=add(section,'div','v5-choose v5-optional');add(second,'h3','',L.program2);
        const fieldB=makePicker(second,'b',(p)=>{state.secondary=p.id;render();});
        const clear=add(second,'button','v5-mini',L.remove);clear.type='button';clear.addEventListener('click',()=>{state.secondary=null;render();});
        const skip=add(section,'button','v5-button secondary',L.skip);skip.type='button';skip.addEventListener('click',()=>{state.primary='unsure';state.secondary=null;render();});
        section._pickers=[fieldA,fieldB];
        section._note=add(section,'p','v5-hint','');
      }
      section.hidden=i>0;
    }
    const result=add(host,'section','v5-result');result.hidden=true;
    const title=add(result,'div','v5-result-head');add(title,'span','v5-kicker',L.summary);add(title,'h2','',L.summary);add(title,'p','v5-muted',L.resultsDesc);
    const badges=add(result,'div','v5-pills');const cautions=add(result,'div','v5-alerts');
    const list=add(result,'ol','v5-result-steps');
    const compare=add(result,'section','v5-comparison');
    const sources=add(result,'div','v5-sources');sourceRow(sources,[[links.admission,zh?'外国公民招生规定':'Поступление иностранцев'],[links.campaign,zh?'2026招生计划':'План приёма 2026'],[links.programs,L.catalogYear]]);
    const budget=add(result,'details','v5-budget');add(budget,'summary','',L.budget);add(budget,'p','v5-muted',L.budgetText);
    const costValues=read(COST_STORE,{semester:0,semesters:2,housing:0,other:0,months:10});
    const costs=add(budget,'div','v5-budget-fields');const fields=['semester','semesters','housing','other','months'];const costInputs={};
    fields.forEach((key,i)=>{const label=add(costs,'label','v5-cost-field');add(label,'span','',L.cost[i]);const inp=add(label,'input');inp.type='number';inp.min='0';inp.max='100000000';inp.step='1';inp.value=Number(costValues[key])>=0?Number(costValues[key]):0;costInputs[key]=inp;
      inp.addEventListener('input',calculate);});
    const total=add(budget,'strong','v5-money');add(budget,'p','v5-muted',L.costCaution);
    function calculate(){const o={};fields.forEach(k=>o[k]=Math.max(0,Math.min(1e8,Number(costInputs[k].value)||0)));save(COST_STORE,o);
      const amount=o.semester*o.semesters+(o.housing+o.other)*o.months;
      total.textContent=L.total+': '+new Intl.NumberFormat(zh?'zh-CN':'ru-RU',{maximumFractionDigits:0}).format(amount)+' ₽';return amount;}
    calculate();
    const actions=add(result,'div','v5-actions');
    const next=add(actions,'a','v5-button',L.plan);next.href='../checklist/index.html';
    const dl=add(actions,'button','v5-button secondary',L.download);dl.type='button';
    function personalizedSteps(){const a=byId.get(state.primary);const arr=[...L.steps];
      if(state.finance&&L.routeAction[state.finance])arr[1]=L.routeAction[state.finance];
      if(a)arr[2]=L.programAction+' '+a.code+' · '+(a.profile||a.name)+' ('+labelByValue('form',state.form)+').';
      if(state.russian!=='yes')arr[4]+=zh?'（另需确认语言及考试要求）':' (проверь языковые требования)';
      return arr;
    }
    dl.addEventListener('click',()=>{
      const lines=[L.summary, ...Object.keys(options).map(k=>L.flow[steps.indexOf(k)]+': '+labelByValue(k,state[k])),
      L.program+': '+(byId.get(state.primary)?.profile||byId.get(state.primary)?.name||L.noProgram),
      ...personalizedSteps(), ...getWarnings(state),L.budget+': '+calculate()+' ₽',links.admission,links.programs];
      download('rut-miit-plan-'+lang+'.txt',lines.join('\n'));
    });
    const reset=add(host,'button','v5-reset',L.reset);reset.type='button';reset.addEventListener('click',()=>{
      for(const key of Object.keys(state))state[key]=null;
      save(STORE,state);render();window.scrollTo({top:0,behavior:'smooth'});
    });
    function getWarnings(s){let r=[L.financeWarnings[s.finance],L.formWarning];
      if((s.level==='master'||s.level==='asp')&&['secondary','college'].includes(s.education))r.push(L.qualification);
      if(s.russian!=='yes')r.push(L.language);
      if(!byId.has(s.primary))r.push(L.noProgram);
      return r.filter(Boolean);
    }
    function render(){
      let completed=0;
      for(let i=0;i<steps.length;i++){
        const key=steps[i];const available=steps.slice(0,i).every(k=>k==='program'?!!state.primary:!!state[k]);
        panels[key].hidden=!available;
        if(key!=='program'){
          $$('input',panels[key]).forEach(input=>input.checked=state[key]===input.value);
          if(state[key])completed++;
        }
      }
      const allowProgram=['form','finance','level','education','russian'].every(k=>!!state[k]);
      const a=byId.get(state.primary),b=byId.get(state.secondary);
      if(state.primary!=='unsure'&&!a)state.primary=null;
      if(state.secondary&&!b)state.secondary=null;
      if(state.primary&&state.secondary&&state.primary===state.secondary)state.secondary=null;
      const programPane=panels.program;
      if(allowProgram){
        for(const p of programPane._pickers)p.refresh();
        programPane._pickers[0].setValue(a);
        programPane._pickers[1].setValue(b);
        programPane._note.textContent=(!catalog.length?L.noData:
          catalog.filter(p=>eligible(p,state)).length===0?L.noMatches:L.catalogYear+': '+catalog.filter(p=>eligible(p,state)).length+' '+L.count.toLowerCase());
      }
      const finished=allowProgram&&!!state.primary;
      if(finished)completed++;
      progressText.textContent=L.progress+' '+completed+L.of;
      fill.style.width=(100*completed/6)+'%';
      result.hidden=!finished;
      if(finished){
        badges.replaceChildren();
        for(const field of ['form','finance','level','russian'])add(badges,'span','v5-pill',labelByValue(field,state[field]));
        if(a)add(badges,'span','v5-pill prominent',(a.code||'')+' · '+(a.profile||a.name));
        cautions.replaceChildren();
        if(getWarnings(state).length){add(cautions,'h3','',L.warnings);getWarnings(state).forEach(msg=>add(cautions,'p','v5-warning',msg));}
        list.replaceChildren();personalizedSteps().forEach(s=>add(list,'li','',s));
        compare.replaceChildren();
        if(a&&b){add(compare,'h3','',L.comparison);add(compare,'p','v5-muted',L.compareNotice);const table=add(compare,'table','v5-compare');
          const keys=['code','name','profile','degree','mode','year','source'];
          keys.forEach((key,i)=>{const tr=add(table,'tr');add(tr,'th','',L.fields[i]);
            for(const p of [a,b]){const td=add(tr,'td');if(key==='source')td.appendChild(mklink(programSafeUrl(p.curriculum_url||p.registry_url),L.curricula));
              else td.textContent=String(p[key]||L.unknown);}
            if(key!=='source'&&String(a[key])!==String(b[key]))tr.classList.add('v5-different');
          });
        }
      }
      state.primaryLabel=a?((a.code||'')+' · '+(a.profile||a.name||'')).slice(0,235):null;
      state.secondaryLabel=b?((b.code||'')+' · '+(b.profile||b.name||'')).slice(0,235):null;
      next.href='../checklist/index.html'+encodePlan(state);
      setSwitcher(state);
      save(STORE,state);
    }
    function eligible(p,s){
      if(s.level&&p.group!==s.level)return false;
      if(s.form&&s.form!=='undecided'){
        const mode=String(p.mode||'').toLowerCase().replace(/ё/g,'е');
        if(s.form==='full'&&(mode.includes('заоч')||!mode.includes('очн')))return false;
        if(s.form==='hybrid'&&!mode.includes('очно-заоч'))return false;
        if(s.form==='remote'&&(!mode.includes('заоч')||mode.includes('очно-заоч')))return false;
      }
      return true;
    }
    function makePicker(parent,key,onPick){
      const wrap=add(parent,'div','v5-picker');const btn=add(wrap,'button','v5-picker-button',L.choose+' ▾');btn.type='button';btn.setAttribute('aria-haspopup','listbox');btn.setAttribute('aria-expanded','false');
      const pop=add(wrap,'div','v5-popover');pop.hidden=true;
      const query=add(pop,'input','v5-search');query.type='search';query.placeholder=L.search;query.autocomplete='off';
      const count=add(pop,'p','v5-count');const viewport=add(pop,'div','v5-list');viewport.setAttribute('role','listbox');
      let filtered=[],shown=0,current=null;let offset=0;
      function update(){const q=query.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
        filtered=catalog.filter(p=>eligible(p,state)&&(key!=='b'||p.id!==state.primary)&&q.every(w=>[p.code,p.name,p.profile,p.discipline,p.mode].join(' ').toLocaleLowerCase().includes(w)));
        shown=0;offset=0;viewport.replaceChildren();append();
        if(filtered.length===0)add(viewport,'p','v5-muted',L.noMatches);
      }
      function append(){for(const p of filtered.slice(shown,shown+60)){
        const option=add(viewport,'button','v5-item');option.type='button';option.setAttribute('role','option');
        add(option,'strong','',(p.code||'')+' · '+(p.profile||p.name));
        add(option,'small','',[(p.name||''),(p.mode||''),(p.degree||'')].filter(Boolean).join(' · '));
        option.addEventListener('click',()=>{current=p;close();onPick(p);btn.focus();});
      }shown=Math.min(shown+60,filtered.length);count.textContent=L.count+': '+filtered.length+(filtered.length>shown?' ↓':'');}
      function close(){pop.hidden=true;btn.setAttribute('aria-expanded','false');}
      btn.addEventListener('click',()=>{pop.hidden=!pop.hidden;btn.setAttribute('aria-expanded',String(!pop.hidden));if(!pop.hidden){query.value='';update();query.focus();}});
      query.addEventListener('input',update);
      viewport.addEventListener('scroll',()=>{if(viewport.scrollTop+viewport.clientHeight>viewport.scrollHeight-80&&shown<filtered.length)append();},{passive:true});
      query.addEventListener('keydown',e=>{if(e.key==='Escape'){close();btn.focus();}if(e.key==='Enter'){const first=$('.v5-item',viewport);if(first){e.preventDefault();first.click();}}});
      document.addEventListener('pointerdown',e=>{if(!wrap.contains(e.target))close();});
      return {refresh:()=>{if(!pop.hidden)update();},setValue:(p)=>{current=p;btn.textContent=p?(p.code+' · '+(p.profile||p.name)+' ▾'):L.choose+' ▾';}};
    }
    render();
  }

  function checklist(initialRoute){
    const route=tidy(getPlanFromURL()||initialRoute);save(STORE,route);setSwitcher(route);
    host.replaceChildren();
    const head=add(host,'section','v5-progress');
    if(!route.form){add(head,'p','v5-warning',L.emptyRoute);}
    else{
      const row=add(head,'div','v5-pills');for(const field of ['form','finance','level'])if(route[field])add(row,'span','v5-pill',labelByValue(field,route[field]));
      if(route.primaryLabel)add(row,'span','v5-pill prominent',route.primaryLabel);
      if(route.secondaryLabel)add(row,'span','v5-pill',route.secondaryLabel);
      if(['master','asp'].includes(route.level)&&['secondary','college'].includes(route.education))add(head,'p','v5-warning',L.qualification);
      if(route.russian&&route.russian!=='yes')add(head,'p','v5-warning',L.language);
    }
    const actions=add(head,'div','v5-actions');const edit=add(actions,'a','v5-button secondary',route.form?L.editWizard:L.startWizard);
    edit.href='../guides/index.html'+(route.form?encodePlan(route):'');
    const exportButton=add(actions,'button','v5-button secondary',L.exportTasks);exportButton.type='button';
    const bar=add(head,'div','v5-progress-block');const stats=add(bar,'strong','');const track=add(bar,'div','v5-track');const fill=add(track,'div','v5-track-fill');
    const nextArea=add(head,'div','v5-next-card');const nextCopy=add(nextArea,'div');add(nextCopy,'strong','',L.nextTask);const nextText=add(nextCopy,'p','',L.filterNote);
    const jump=add(nextArea,'button','v5-button secondary',L.goTo);jump.type='button';
    jump.addEventListener('click',()=>{const item=entries.find(e=>!e.input.checked);if(item){item.input.scrollIntoView({block:'center',behavior:'smooth'});item.input.focus({preventScroll:true});}});
    const tasks=read(CHECK_STORE,{});
    const cards=add(host,'div','v5-checklist');
    const stages=taskData(route);
    const entries=[];
    stages.forEach((stage,i)=>{
      const card=add(cards,'article','v5-task');
      const title=add(card,'div','v5-task-title');add(title,'span','v5-num',String(i+1).padStart(2,'0'));add(title,'h2','',L.stages[i]);const stageBadge=add(title,'span','v5-stage-badge',L.stagesStatus[0]);
      const completion=add(card,'div','v5-task-count');
      const sub=add(card,'div','v5-task-items');
      for(const [key,body] of stage.items){
        const label=add(sub,'label','v5-subtask');const c=add(label,'input');c.type='checkbox';c.checked=tasks[key]===true;c.dataset.task=key;
        add(label,'span','',body);
        const item={input:c,key,card,completion,stage,stageBadge,stageIndex:i,description:body};entries.push(item);
        c.addEventListener('change',()=>{tasks[key]=c.checked;save(CHECK_STORE,tasks);update();});
      }
      const details=add(card,'details','v5-task-sources');add(details,'summary','',L.details);
      const linksBlock=add(details,'div','v5-sources');stage.refs.forEach(ref=>linksBlock.appendChild(mklink(programSafeUrl(ref[0]),ref[1])));
    });
    const bottom=add(host,'div','v5-check-actions');const reset=add(bottom,'button','v5-reset',L.resetTasks);reset.type='button';
    reset.addEventListener('click',()=>{if(!confirm(L.resetConfirm))return;entries.forEach(i=>{delete tasks[i.key];i.input.checked=false;});save(CHECK_STORE,tasks);update();});
    exportButton.addEventListener('click',()=>{
      const lines=[L.checklist,route.form?'':L.generic,route.form?Object.keys(routeLabels).map(k=>labelByValue(k,route[k])).join(' · '):'',route.primaryLabel||'',
      ...stages.flatMap((s,i)=>['',L.stages[i],...s.items.map(([k,v])=>(tasks[k]?'[x] ':'[ ] ')+v)]),links.admission,links.programs];
      download('rut-miit-checklist-'+lang+'.txt',lines.join('\n'));
    });
    function update(){const done=entries.filter(o=>o.input.checked).length;
      stats.textContent=L.checkStats+': '+done+' / '+entries.length;
      fill.style.width=(entries.length?100*done/entries.length:0)+'%';
      const upcoming=entries.find(o=>!o.input.checked);
      nextText.textContent=upcoming?L.stages[upcoming.stageIndex]+': '+upcoming.description:L.allDone;
      jump.hidden=!upcoming;
      stages.forEach((stage,i)=>{const items=entries.filter(o=>o.stage===stage);const ready=items.filter(o=>o.input.checked).length;
        const card=items[0]?.card;if(!card)return;
        card.classList.toggle('v5-task-done',ready===items.length);
        items[0].stageBadge.textContent=L.stagesStatus[ready===0?0:ready===items.length?2:1];
        items[0].stageBadge.dataset.status=ready===0?'new':ready===items.length?'done':'progress';
        items[0].completion.textContent=L.taskProgress+': '+ready+'/'+items.length;
      });
    }
    update();
  }
  function routeProgramTask(s,p){
    return s.primaryLabel
      ? p('Проверить актуальный набор на выбранную программу: '+s.primaryLabel,'核实所选专业是否正在招生：'+s.primaryLabel)
      : p('Проверить код, профиль и актуальный набор выбранной программы.','核对所选专业代码、方向及当前是否招生。');
  }
  function taskData(s){
    const finance=s.finance;
    const chosen=byId.get(s.primary); // usually unavailable on checklist page; task refers to code from route only
    const isZH=zh;
    const p=(ru,cn)=>isZH?cn:ru;
    const conditionalFinance=finance==='contract'
      ?p('Проверить актуальную стоимость, места по договору и порядок оплаты.','核实最新学费、合同名额和付款要求。')
      :finance==='general'
      ?p('Проверить свои основания для участия в бюджетном конкурсе.','核实本人是否符合一般预算制竞争录取条件。')
      :finance==='quota'
      ?p('Проверить правила и результат отдельного отбора по государственной квоте.','核实俄罗斯政府配额的独立申请、评选及结果。')
      :p('Выбрать подходящий способ приёма: договор, общий конкурс или квота.','确认申请途径：自费、一般竞争或政府配额。');
    const modeDetail=s.form&&s.form!=='undecided'?labelByValue('form',s.form):p('подходящая форма','相应学习形式');
    const levelDetail=s.level?labelByValue('level',s.level):p('подходящий уровень','合适的培养层次');
    const languageTask=s.russian==='yes'
      ?p('Сверить язык обучения и вступительных испытаний с требованиями программы.','核实具体专业授课与入学考试语言。')
      :p('Проверить необходимость русского языка и возможной подготовительной программы.','核实俄语要求及是否需要预科/语言准备。');
    const financeTaskKey='finance-'+(finance||'generic');
    return [
      {items:[
        ['rules',p('Открыть актуальные правила приёма иностранных граждан на нужный учебный год.','查阅适用学年的外国公民正式招生规定。')],
        ['level',p('Проверить требования к уровню '+levelDetail+' и признанию предыдущего образования.','核对'+levelDetail+'的前置学历与学历认证要求。')],
        ['deadlines',p('Зафиксировать официальные сроки подачи и испытаний.','记录官方申请与考试截止日期。')]],refs:[[links.admission,p('Приём иностранных граждан','外国公民招生')],[links.campaign,p('План приёма 2026','2026招生计划')]]},
      {items:[
        [financeTaskKey,conditionalFinance],
        ['mode-'+(s.form||'generic'),p('Уточнить, открыт ли приём по форме обучения «'+modeDetail+'» для интересующей программы.','确认所选专业是否按'+modeDetail+'招生。')],
        ['program-choice',routeProgramTask(s,p)],
        ...(s.secondaryLabel?[['compare-choice',p('Сравнить две выбранные программы и окончательно определиться с направлением.','比较两个专业后确定最终申请方向。')]]:[])] ,refs:[[links.programs,p('Официальный реестр программ','官方教育专业目录')],[links.campaign,p('План приёма','招生计划')]]},
      {items:[
        ['passport',p('Проверить требования к загранпаспорту и сроку его действия.','核对护照及有效期要求。')],
        ['education-doc',p('Подготовить диплом или аттестат и приложения.','准备毕业证、成绩单及附件。')],
        ['translations',p('Уточнить требования к переводу, заверению и признанию документа об образовании.','核实翻译、公证及学历认可要求。')],
        ['other-docs',p('Сверить полный список дополнительных документов для своего статуса.','核对本人身份适用的其他材料清单。')]],refs:[[links.admission,p('Список и порядок подачи документов','申请材料与提交说明')]]},
      {items:[
        ['language-'+(s.russian||'generic'),languageTask],
        ['exams',p('Уточнить предметы, формат и расписание вступительных испытаний.','核实入学考试科目、形式和日期。')],
        ['preparation',p('Подготовиться к указанным испытаниям или дополнительному отбору.','准备相应考试或专项选拔。')]],refs:[[links.admission,p('Вступительные требования','入学要求')]]},
      {items:[
        ['application',p('Подать заявление только через разрешённый университетом канал.','通过学校认可的渠道提交申请。')],
        ['submitted',p('Сохранить подтверждение подачи и список приложенных документов.','保存提交凭证及申请材料清单。')],
        ['status',p('Проверять статус заявления и сообщения приёмной комиссии.','持续查看申请状态与招生办公室通知。')]],refs:[[links.admission,p('Подача заявления','提交申请')]]},
      {items:[
        ['decision',p('Дождаться официального решения о зачислении.','等待大学正式录取决定。')],
        [finance==='contract'?'contract':'contract-conditional',finance==='contract'
          ?p('Ознакомиться с договором и выполнить официальные условия оплаты.','核对合同并按学校要求付款。')
          :p('Проверить обязательные действия для своего вида поступления после отбора.','核实适用申请途径在选拔结果后的手续。')],
        ['confirmation',p('Получить официальные инструкции по дальнейшему оформлению.','取得学校关于后续手续的正式通知。')]],refs:[[links.admission,p('Зачисление','录取手续')],[links.fees,p('Официальные сведения об оплате','官方收费说明')]]},
      {items:[
        ['arrival',p('Сверить визовые и въездные документы по гражданству и условиям зачисления.','按国籍与录取情况核对签证和入境材料。')],
        ['housing',p('Узнать, предоставлено ли место в общежитии; не считать его гарантированным.','确认是否实际获得宿舍名额，不应默认有宿舍。')],
        ['registration',p('Выяснить порядок регистрации, медицинских документов и заселения после прибытия.','了解抵达后的登记、医疗文件及宿舍入住安排。')],
        ['schedule',p('Получить сведения о начале занятий, личном кабинете и расписании.','查询开学时间、个人账户和课表。')]],refs:[[links.university,p('Официальный сайт РУТ','俄交大官网')]]}
    ];
  }
})();
