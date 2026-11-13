/* MIRROR_SMART_TOOLS_V4 */
(() => {
  'use strict';
  const root = document.getElementById('mc-smart-page');
  if (!root) return;
  const LANG = root.dataset.lang === 'zh' ? 'zh' : 'ru';
  const ZH = LANG === 'zh';
  const I = {
    ru: {
      choose:'Нажми, чтобы выбрать программу',search:'Поиск по коду, названию или профилю…',
      selected:'Выбрано',listCount:'В списке',nothing:'Совпадений нет. Уточни запрос.',
      more:'Прокрути ниже для следующих вариантов',
      no:'Нет подтверждённых данных', unknown:'Требует отдельной проверки',
      noCompare:'Выбери две программы в выпадающих списках — сравнение заполнится автоматически.',
      print:'Распечатать',saved:'Отметки сохранены в этом браузере',
      results:'Ваш персональный план',next:'Что делать дальше',
      evidence:'Проверить на сайте РУТ',resultsReady:'Рекомендации построены по выбранным ответам',
      all:'Все уровни',basic:'Базовое высшее / специалитет',master:'Магистратура',asp:'Аспирантура',
      selectorA:'Программа А',selectorB:'Программа Б',
      fields:{discipline:'Область',name:'Направление',code:'Код',profile:'Профиль / программа',degree:'Уровень образования',mode:'Форма обучения',year:'Год учебного плана',curriculum_url:'Официальное описание',tuition:'Стоимость',language:'Язык преподавания',admission:'Набор иностранцев'},
      contract:'Платное обучение',general:'Общий конкурс',quota:'Государственная квота',
      basicShort:'Базовое высшее / специалитет',masterShort:'Магистратура',aspShort:'Аспирантура',
      russianYes:'Готов учиться / проходить испытания на русском',russianNo:'Нужна языковая подготовка',russianUnknown:'Не знаю требований',
      secondary:'Школа',college:'Колледж / СПО',degree:'Диплом о высшем образовании',other:'Другой документ',
      planIntro:'Это ориентировочный маршрут подготовки, а не решение о допуске или зачислении.',
      generalWarning:'Важно: возможность иностранного гражданина участвовать в конкурсе на бюджет требует проверки правил и оснований. Наличие бюджетных мест в плане приёма не гарантирует право на них.',
      quotaWarning:'Важно: квота Правительства РФ имеет отдельную процедуру отбора. Отметка «квота» здесь не подтверждает, что она вам предоставлена.',
      contractWarning:'Важно: договорная форма не означает зачисления без вступительных испытаний. Стоимость и места проверяются по выбранной программе.',
      levelWarning:'Проверь соответствие своего предыдущего образования уровню выбранной программы.',
      languageWarning:'Проверь язык обучения и вступительных испытаний именно на этой программе. Подготовительное обучение может потребоваться.',
      qualificationWarning:'Выбранный уровень может требовать диплом о предыдущем высшем образовании. Сверь правила до подачи заявления.',
      noProgramWarning:'Программа пока не выбрана. Следующий шаг — найти её в официальном каталоге и проверить приём.',
      steps:[
        'Открыть правила приёма иностранных граждан на соответствующий учебный год.',
        'Проверить, что выбранная программа участвует в нужном виде конкурса и доступна вашему статусу.',
        'Подготовить документ об образовании, паспорт и требуемые переводы/подтверждения.',
        'Уточнить вступительные испытания, язык и сроки подачи документов.',
        'Подать заявление выбранным официальным способом и отслеживать статус.',
        'После решения университета выполнить требования для зачисления и въезда.'
      ],
      routeStep:{contract:'Отдельно проверить актуальную цену, условия оплаты и договор.',general:'Отдельно подтвердить право на бюджетный конкурс и доступные места.',quota:'Уточнить порядок отбора по государственной квоте и результаты отбора.'},
      summaryPrefix:'Вариант',sourceText:'Источник: официальный реестр учебных планов РУТ за 2026 год.',
      costText:'В официальном реестре образовательных программ нет надёжной цены для каждого варианта — не рассчитываем её автоматически.',
      rawName:'Названия программ сохранены на русском — так, как они опубликованы университетом.'
    },
    zh: {
      choose:'点击选择专业项目',search:'按代码、专业名称或方向搜索…',
      selected:'已选择',listCount:'目录记录',nothing:'没有找到结果，请更换关键词。',
      more:'继续向下滚动可加载更多项目',
      no:'无已核实数据',unknown:'需向大学进一步确认',
      noCompare:'在下拉列表中选择两个专业，系统会自动填写对比表。',
      print:'打印',saved:'选择仅保存在本浏览器中',
      results:'你的个性化申请准备计划',next:'下一步需要做什么',
      evidence:'在俄交大官网核实',resultsReady:'根据所选项目和回答生成',
      all:'所有层次',basic:'基础高等教育 / 专家学位',master:'硕士层次',asp:'研究生（博士方向）',
      selectorA:'项目 A',selectorB:'项目 B',
      fields:{discipline:'领域',name:'专业方向',code:'专业代码',profile:'具体专业方向',degree:'培养层次',mode:'学习形式',year:'课程计划年份',curriculum_url:'官方课程说明',tuition:'学费',language:'授课语言',admission:'外国申请者招生'},
      contract:'合同制（自费）',general:'一般竞争录取',quota:'俄罗斯政府配额',
      basicShort:'基础高等教育 / 专家学位',masterShort:'硕士',aspShort:'博士研究生',
      russianYes:'具备俄语学习 / 考试能力',russianNo:'需要进一步学习俄语',russianUnknown:'尚不清楚语言要求',
      secondary:'高中',college:'专科 / 职业教育',degree:'已有高等教育文凭',other:'其他学历',
      planIntro:'仅提供申请准备指引，不判断资格，也不保证被录取。',
      generalWarning:'注意：外国公民能否参加预算制一般竞争录取，需要依据适用规定及个人身份核实。专业存在预算名额并不代表你自动有资格。',
      quotaWarning:'注意：俄罗斯政府配额有单独的申请和选拔程序。选择此项不代表已经获得配额。',
      contractWarning:'注意：自费合同制通常也需要满足招生与考试要求，不能理解为免试或保证录取。',
      levelWarning:'需要核实已有学历是否满足所选培养层次的申请条件。',
      languageWarning:'请核实该项目的授课语言、入学考试语言以及是否需要预科或语言准备。',
      qualificationWarning:'当前培养层次可能要求此前取得高等教育文凭。申请前请核实。',
      noProgramWarning:'尚未选定具体专业。下一步请使用官方目录选择项目并查看招生条件。',
      steps:[
        '打开适用学年的俄交大外国公民招生规定。',
        '核实所选专业是否提供你计划申请的录取方式，以及该方式是否适用于你的身份。',
        '准备教育证明、护照以及学校要求的翻译和认证材料。',
        '确认入学考试科目、考试语言和材料提交时间。',
        '通过大学认可的渠道申请，并跟进申请状态。',
        '收到大学正式决定后按要求办理入学和入境手续。'
      ],
      routeStep:{contract:'另外确认该项目的学费、付款规定和合同条件。',general:'另外核实自己是否可以参加预算名额竞争。',quota:'另外查看俄罗斯政府配额的独立选拔及结果确认流程。'},
      summaryPrefix:'已选',sourceText:'来源：俄交大公布的2026年教育方案目录。',
      costText:'教育方案目录不提供每一项专业的准确费用，不自动填入未证实的学费。',
      rawName:'专业名称保持大学正式公布的俄语原文，以免错误翻译。'
    }
  }[LANG];
  let payload = {programs:[],count:0};
  try { payload = JSON.parse(document.getElementById('mc-rut-program-data').textContent); } catch(e) {console.warn('Catalog unavailable',e);}
  const catalog = Array.isArray(payload.programs) ? payload.programs : [];
  const byId = new Map(catalog.map(p=>[p.id,p]));
  const one = (q,base=root) => base.querySelector(q);
  const all = (q,base=root) => [...base.querySelectorAll(q)];
  const h = (tag,cls,text) => { const x=document.createElement(tag); if(cls)x.className=cls;if(text!==undefined)x.textContent=text;return x; };
  const sourceLinks = [
    ['https://rut-miit.ru/page/120705',ZH?'外国公民招生':'Иностранные абитуриенты'],
    ['https://rut-miit.ru/admissions/degrees?year=2026',ZH?'2026招生计划':'План приёма 2026'],
    ['https://rut-miit.ru/sveden/education/programs',ZH?'教育项目正式目录':'Реестр программ'],
    ['https://rut-miit.ru/sveden/paid_edu',ZH?'官方收费资料':'Стоимость обучения']
  ];
  function validOfficial(url) {
    try {const u=new URL(url);return u.protocol==='https:' && (u.hostname==='rut-miit.ru'||u.hostname==='miit.ru'||u.hostname.endsWith('.rut-miit.ru')||u.hostname.endsWith('.miit.ru'));}
    catch(_) {return false;}
  }
  function link(href,label){const a=h('a','',label);a.href=validOfficial(href)?href:'https://rut-miit.ru/sveden/education/programs';a.target='_blank';a.rel='noopener noreferrer';return a;}
  function label(p){return p.code+' · '+(p.profile||p.name);}
  function subtitle(p){return [ZH?p.discipline_zh:p.discipline,p.name,p.degree,p.mode].filter(Boolean).join(' · ');}
  function matches(p,text,group){
    if(group!=='all' && p.group!==group)return false;
    if(!text)return true;
    const input=text.toLocaleLowerCase();const words=input.split(/\s+/).filter(Boolean);
    const bag=[p.code,p.name,p.profile,p.degree,p.mode,p.discipline,p.discipline_zh].join(' ').toLocaleLowerCase();
    return words.every(w=>bag.includes(w));
  }
  const pickers=[];
  function setupPicker(node,groupGetter,onChoose) {
    if(!node) return;
    const btn=one('.ms-pick-button',node), span=one('.ms-pick-label',node), pop=one('.ms-popover',node);
    const input=one('.ms-search',node), list=one('.ms-options',node), count=one('.ms-pop-count',node);
    let filtered=[],shown=0,focusIndex=-1,selected=null;
    function setLabel(p){span.textContent=p?label(p):I.choose;selected=p?p.id:null;btn.setAttribute('aria-label',span.textContent);}
    function close(){pop.hidden=true;btn.setAttribute('aria-expanded','false');}
    function update(){
      filtered=catalog.filter(p=>matches(p,input.value.trim(),groupGetter()));
      shown=0; focusIndex=-1;list.replaceChildren();append();
      count.textContent=I.listCount+': '+filtered.length+(filtered.length>shown?' · '+I.more:'');
      if(filtered.length===0)list.appendChild(h('p','ms-empty',I.nothing));
    }
    function append(){
      const next=filtered.slice(shown,shown+80);
      for(const p of next){
        const opt=h('button','ms-option');opt.type='button';opt.setAttribute('role','option');opt.dataset.value=p.id;
        opt.appendChild(h('strong','',label(p)));
        opt.appendChild(h('small','',subtitle(p)));
        opt.addEventListener('click',()=>{setLabel(p);close();onChoose(p);btn.focus();});
        list.appendChild(opt);
      }
      shown+=next.length;
      count.textContent=I.listCount+': '+filtered.length+(shown<filtered.length?' · '+I.more:'');
    }
    btn.addEventListener('click',()=>{
      for(const pick of pickers){if(pick.node!==node)pick.close();}
      pop.hidden=!pop.hidden;btn.setAttribute('aria-expanded',String(!pop.hidden));
      if(!pop.hidden){input.value='';update();input.focus();}
    });
    input.addEventListener('input',update);
    list.addEventListener('scroll',()=>{if(list.scrollTop+list.clientHeight>=list.scrollHeight-70 && shown<filtered.length)append();},{passive:true});
    input.addEventListener('keydown',ev=>{
      if(ev.key==='Escape'){ev.preventDefault();close();btn.focus();return;}
      if(ev.key==='ArrowDown'||ev.key==='ArrowUp'){
        ev.preventDefault();const items=all('.ms-option',list);
        if(ev.key==='ArrowDown'&&focusIndex>=items.length-2&&shown<filtered.length)append();
        const updated=all('.ms-option',list);
        focusIndex=Math.max(0,Math.min(updated.length-1,focusIndex+(ev.key==='ArrowDown'?1:-1)));
        updated.forEach((it,i)=>it.classList.toggle('active',i===focusIndex));
        if(updated[focusIndex])updated[focusIndex].scrollIntoView({block:'nearest'});
      }
      if(ev.key==='Enter'){
        const items=all('.ms-option',list);const el=items[focusIndex]||items[0];
        if(el){ev.preventDefault();el.click();}
      }
    });
    document.addEventListener('pointerdown',ev=>{if(!node.contains(ev.target))close();});
    const pick={node,close,setLabel,refresh:()=>{if(!pop.hidden)update();}};
    pickers.push(pick);
    setLabel(null);
    return pick;
  }
  const storageKey='mirror-smart-v4-'+root.dataset.mode;
  function safeGet(){try{return JSON.parse(localStorage.getItem(storageKey)||'{}')||{};}catch(_){return {};}}
  function safeSet(obj){try{localStorage.setItem(storageKey,JSON.stringify(obj));}catch(_){}}
  function safeClear(){try{localStorage.removeItem(storageKey);}catch(_){}}
  function fillSourceLinks(container){
    if(!container)return;
    container.replaceChildren();
    for(const [url,name] of sourceLinks) container.appendChild(link(url,name));
  }
  function downloaded(name,text){
    const blob=new Blob([text],{type:'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);
  }
  function wizard(){
    const saved=safeGet();
    const state={finance:saved.finance||null,level:saved.level||null,education:saved.education||null,russian:saved.russian||null,program:saved.program||null};
    const selections=['finance','level','education','russian'];
    const nodes=Object.fromEntries(['finance','level','education','russian','program','result'].map(k=>[k,one('[data-ms-step="'+k+'"]')]));
    const out=one('#ms-wizard-result');
    const picker=setupPicker(one('[data-ms-picker="wizard"]'),()=>state.level||'all',(p)=>{state.program=p.id;render();});
    const buttons=all('input[data-ms-field]');
    buttons.forEach(input=>input.addEventListener('change',()=>{
      const field=input.dataset.msField;
      const idx=selections.indexOf(field);
      if(idx>=0){state[field]=input.value;
        for(const later of selections.slice(idx+1))state[later]=null;
        state.program=null;
      }
      render();
    }));
    const skip=one('[data-ms-skip]');
    skip.addEventListener('click',()=>{state.program='unsure';render();});
    one('[data-ms-reset]').addEventListener('click',()=>{
      for(const key of [...selections,'program'])state[key]=null;
      safeClear();render();
      window.scrollTo({top:Math.max(0,root.getBoundingClientRect().top+window.scrollY-20),behavior:'smooth'});
    });
    one('[data-ms-download]').addEventListener('click',()=>downloaded('rut-miit-personal-plan-'+LANG+'.txt',out.innerText+'\n\n'+sourceLinks.map(v=>v.join(': ')).join('\n')));
    one('[data-ms-print]').addEventListener('click',()=>window.print());
    fillSourceLinks(one('.ms-source-links',out));
    function render(){
      let ready=true;
      for(const field of selections){
        if(nodes[field])nodes[field].hidden=!ready;
        const value=state[field];
        all('input[data-ms-field="'+field+'"]').forEach(x=>x.checked=x.value===value);
        if(!value)ready=false;
      }
      nodes.program.hidden=!ready;
      const chosen=byId.get(state.program);
      if(state.program && !chosen && state.program!=='unsure')state.program=null;
      picker.setLabel(chosen||null);
      nodes.result.hidden=!ready || !state.program;
      const complete=[...selections.map(k=>!!state[k]),!!state.program].filter(Boolean).length;
      all('.ms-step-bar span').forEach((e,i)=>e.classList.toggle('done',i<complete));
      one('[data-ms-progress]').textContent=complete+'/5';
      let warning=one('[data-ms-financing-note]');
      warning.hidden=!state.finance;
      warning.textContent=state.finance==='contract'?I.contractWarning:state.finance==='quota'?I.quotaWarning:I.generalWarning;
      let qualifier=one('[data-ms-education-note]');
      const mismatch=['master','asp'].includes(state.level) && ['secondary','college'].includes(state.education);
      qualifier.hidden=!mismatch;qualifier.textContent=I.qualificationWarning;
      if(state.program){
        const resultLines=[];
        resultLines.push(I.steps[0]);
        resultLines.push(I.routeStep[state.finance]);
        resultLines.push(I.steps[1]);
        resultLines.push(I.steps[2]);
        if(state.russian!=='yes')resultLines.push(I.languageWarning);
        resultLines.push(I.steps[3]);
        resultLines.push(I.steps[4]);
        resultLines.push(I.steps[5]);
        const title=one('[data-ms-summary-title]',out);
        title.textContent=I.results;
        const context=one('[data-ms-summary-context]',out);
        context.textContent=[I.summaryPrefix+': '+(state.finance==='contract'?I.contract:state.finance==='quota'?I.quota:I.general),
          state.level==='basic'?I.basicShort:state.level==='master'?I.masterShort:I.aspShort,
          chosen?label(chosen):I.noProgramWarning].join(' · ');
        const warn=one('[data-ms-summary-warnings]',out);warn.replaceChildren();
        if(mismatch)warn.appendChild(h('p','ms-warning',I.qualificationWarning));
        if(state.russian!=='yes')warn.appendChild(h('p','ms-warning',I.languageWarning));
        if(!chosen)warn.appendChild(h('p','ms-warning',I.noProgramWarning));
        if(chosen){
          const p=h('p','ms-info',subtitle(chosen));warn.appendChild(p);
          warn.appendChild(link(chosen.curriculum_url||chosen.registry_url,I.evidence));
        }
        const list=one('[data-ms-summary-list]',out);list.replaceChildren();
        for(const line of resultLines)list.appendChild(h('li','',line));
      }
      safeSet(state);
    }
    render();
  }
  function comparison(){
    const saved=safeGet(),state={a:saved.a||null,b:saved.b||null,filter:saved.filter||'all'};
    const filter=one('[data-ms-level-filter]');filter.value=state.filter;
    const holder=one('[data-ms-compare-result]');
    const pa=setupPicker(one('[data-ms-picker="a"]'),()=>state.filter,(p)=>{state.a=p.id;render();});
    const pb=setupPicker(one('[data-ms-picker="b"]'),()=>state.filter,(p)=>{state.b=p.id;render();});
    filter.addEventListener('change',()=>{state.filter=filter.value;pa.refresh();pb.refresh();render();});
    one('[data-ms-reset]').addEventListener('click',()=>{state.a=null;state.b=null;state.filter='all';filter.value='all';safeClear();render();});
    one('[data-ms-print]').addEventListener('click',()=>window.print());
    fillSourceLinks(one('.ms-source-links'));
    function cellValue(p,key){
      if(!p)return '—';
      if(key==='tuition'||key==='language'||key==='admission')return I.unknown;
      if(key==='year')return String(p.year);
      if(key==='discipline')return ZH?(p.discipline_zh||I.unknown):(p.discipline||I.unknown);
      return p[key]||'—';
    }
    function render(){
      const a=byId.get(state.a),b=byId.get(state.b);
      if(state.a&&!a)state.a=null;if(state.b&&!b)state.b=null;
      pa.setLabel(a||null);pb.setLabel(b||null);
      const empty=one('[data-ms-compare-empty]');empty.hidden=!!(a&&b);
      holder.hidden=!(a&&b);
      if(a&&b){
        const table=one('.ms-compare-table tbody',holder);table.replaceChildren();
        for(const key of ['discipline','code','name','profile','degree','mode','year','tuition','language','admission','curriculum_url']){
          const tr=h('tr','');const th=h('th','',I.fields[key]);th.scope='row';tr.appendChild(th);
          for(const p of [a,b]){
            const td=h('td','');
            if(key==='curriculum_url'){td.appendChild(link(p.curriculum_url||p.registry_url,I.evidence));}
            else td.textContent=cellValue(p,key);
            tr.appendChild(td);
          }
          if(key!=='curriculum_url'&&cellValue(a,key)!==cellValue(b,key))tr.classList.add('ms-diff');
          table.appendChild(tr);
        }
      }
      safeSet(state);
    }
    render();
  }
  if(root.dataset.mode==='wizard')wizard();
  if(root.dataset.mode==='compare')comparison();
})();
