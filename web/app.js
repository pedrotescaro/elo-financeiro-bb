"use strict";
let state;
let busy = false;
const $ = id => document.getElementById(id);
const money = cents => new Intl.NumberFormat("pt-BR", {style:"currency",currency:"BRL"}).format(cents / 100);
const day = value => value.slice(8,10) + "/" + value.slice(5,7);
const node = (tag, text, className) => { const e = document.createElement(tag); if(text !== undefined) e.textContent = text; if(className) e.className = className; return e; };

function syncControls(){
  document.querySelectorAll("button").forEach(b => b.disabled = busy);
  $("start").disabled = busy || !state;
  $("consent-toggle").disabled = busy || !state;
  const monitorDone = state?.monitor_done === true;
  $("monitor").disabled = busy || !state?.consent || monitorDone;
  $("monitor").textContent = monitorDone ? "Despesa já simulada" : "Simular nova despesa";
  $("monitor").setAttribute("aria-disabled", String($("monitor").disabled));
  $("main").setAttribute("aria-busy", String(busy));
}

async function request(path, body){
  if(busy) return;
  const focusId = document.activeElement?.id;
  busy = true;
  $("error").textContent = "";
  $("error").classList.add("sr-only");
  $("retry").hidden = true;
  $("status").textContent = state ? "Atualizando cenário…" : "Carregando demonstração…";
  syncControls();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);
  try {
    const options = body === undefined ? {} : {method:"POST",headers:{"Content-Type":"application/json","X-Demo-CSRF":state.csrf},body:JSON.stringify(body)};
    options.signal = controller.signal;
    const response = await fetch(path, options);
    const result = await response.json();
    if(!response.ok) throw new Error(result.error || "Não foi possível atualizar o cenário.");
    if(!Array.isArray(result.scenarios) || typeof result.csrf !== "string" || !result.report){
      throw new Error("A resposta está incompleta. Tente carregar o cenário novamente.");
    }
    state = result;
    render();
    $("status").textContent = "Cenário atualizado.";
  } catch(error){
    $("error").textContent = error.name === "AbortError"
      ? "O servidor demorou para responder. Tente carregar o cenário novamente."
      : error instanceof TypeError ? "Não foi possível conectar ao servidor. Confira a conexão e tente novamente." : error.message;
    $("error").classList.remove("sr-only");
    $("retry").hidden = false;
    $("status").textContent = "";
  }
  finally {
    clearTimeout(timeout); busy = false; syncControls();
    if(focusId){
      const previous = $(focusId);
      if(previous && !previous.disabled && !previous.hidden && previous.offsetParent !== null){
        previous.focus({preventScroll:true});
      } else if(state?.consent && !$("workspace").hidden){
        $("report-title").focus({preventScroll:true});
      } else if(state){
        $("start").focus({preventScroll:true});
      }
    }
  }
}

function renderAudit(){
  const records = state.audit || [];
  $("audit-panel").hidden = !records.length;
  $("audit").replaceChildren();
  records.forEach(record => {
    const entry = node("li");
    const time = node("time", new Intl.DateTimeFormat("pt-BR",{hour:"2-digit",minute:"2-digit",second:"2-digit"}).format(new Date(record.time)));
    time.dateTime = record.time;
    entry.append(time, node("span",record.label));
    $("audit").append(entry);
  });
}

function renderExplanations(report){
  $("explanations").replaceChildren();
  Object.values(report.explanations || {}).forEach(item => {
    const section = node("details",undefined,"explanation");
    section.append(node("summary",item.title),node("p",item.summary));
    const values = node("dl");
    item.numbers.forEach(number => values.append(node("dt",number.label),node("dd",money(number.value_cents))));
    section.append(values);
    [["Hipóteses usadas",item.assumptions],["O que ficou fora",item.not_considered]].forEach(([title,items]) => {
      if(!items.length) return;
      const list = node("ul");
      items.forEach(text => list.append(node("li",text)));
      section.append(node("h3",title),list);
    });
    $("explanations").append(section);
  });
}

function render(){
  renderAudit();
  $("scenarios").replaceChildren();
  state.scenarios.forEach(s => {
    const b = node("button", s.title, s.id === state.scenario ? "active" : "");
    b.id = "scenario-" + s.id;
    b.setAttribute("aria-label", "Selecionar cenário: " + s.title);
    if(s.id === state.scenario) b.setAttribute("aria-current","true");
    b.onclick = () => request("/api/scenario",{name:s.id});
    $("scenarios").append(b);
  });
  $("scenario-title").textContent = state.scenario_title;
  $("consent-toggle").textContent = state.consent ? "Desativar leitura e limpar planos" : "Autorizar leitura";
  $("consent-panel").hidden = state.consent;
  $("workspace").hidden = !state.consent;
  $("notice").textContent = "";
  $("notice").hidden = true;
  if(!state.consent) return;
  const report = state.report, flow = report.results?.cashflow;
  if(!flow){
    $("workspace").hidden = true;
    throw new Error("A análise ainda não está disponível. Tente carregar o cenário novamente.");
  }
  $("report-title").textContent = report.title;
  $("report-description").textContent = flow.first_negative_date
    ? `Mesmo com um recebimento esperado, o saldo pode chegar a ${money(flow.minimum_cents)} em ${day(flow.minimum_date)}. O calendário dos compromissos faz diferença.`
    : `O menor saldo previsto até ${day(report.horizon)} é ${money(flow.minimum_cents)}. Compare esse valor com sua margem desejada de ${money(flow.buffer_cents)} antes de decidir.`;
  $("mode").textContent = report.mode === "watsonx" ? "Planejamento de ferramentas: IBM watsonx.ai · Cálculos: ferramentas determinísticas" : "Demonstração por regras · Planejamento por IA generativa ainda não validado";
  if(report.warning){$("notice").textContent=report.warning;$("notice").hidden=false;}
  $("minimum").textContent = money(flow.minimum_cents);
  $("minimum").className = flow.minimum_cents < 0 ? "negative" : "";
  $("minimum-date").textContent = `${flow.minimum_cents < 0 ? "Saldo abaixo de zero · " : ""}Previsto para ${day(flow.minimum_date)}`;
  $("buffer").textContent = money(flow.buffer_cents);
  $("closing").textContent = money(flow.closing_cents);
  $("horizon").textContent = `Em ${day(report.horizon)}`;
  $("daily").replaceChildren();
  flow.daily.forEach((r,index) => {
    const tr = node("tr");
    const balance = node("td",money(r.balance_cents),r.balance_cents < 0 ? "negative" : "");
    if(r.balance_cents < 0) balance.append(node("span"," (abaixo de zero)","sr-only"));
    tr.append(node("td",day(r.date)),node("td",r.events.join(" + ") || (index === 0 ? "Início do período" : "Sem eventos previstos")),balance);
    $("daily").append(tr);
  });
  $("actions").replaceChildren();
  if(!report.actions.length){
    const p = flow.gap_to_buffer_cents > 0 ? "Não há redução flexível suficiente para recompor a margem neste cenário. Revise o calendário e as alternativas com atendimento humano." : "Sua projeção já preserva a margem desejada. Continue acompanhando antes de assumir novos compromissos.";
    $("actions").append(node("p",p));
  }
  report.actions.forEach(a => {
    const wrap=node("div",undefined,"action");
    if(a.id === "budget-plan"){
      wrap.append(node("p",`Proposta: reduzir ${money(a.reduction_cents)} dos gastos flexíveis previstos. As despesas essenciais permanecem na projeção.`));
      wrap.append(node("p",`Menor saldo: ${money(a.before_cents)} → ${money(a.after_cents)}.${a.meets_buffer ? " Margem desejada preservada." : " A margem desejada ainda não é atingida."}`,"impact"));
    } else wrap.append(node("p",`Registre a meta de ${money(a.target_cents)} e preserve sua margem antes da compra. Nenhuma aplicação automática será feita.`));
    const button=node("button",a.label,"primary");
    button.onclick=()=>request("/api/approve",{report_id:report.report_id,action_id:a.id});
    wrap.append(button);$("actions").append(wrap);
  });
  $("special").replaceChildren();
  const purchase=report.results.purchase, safety=report.results.safety;
  $("special").hidden=!(purchase?.available || safety?.available);
  if(purchase?.available){
    $("special").append(node("h2",`${purchase.label}: o preço não conta toda a história.`));
    const compare=node("div",undefined,"compare");
    [["À vista",money(purchase.price_cents),`Menor saldo previsto: ${money(purchase.cash_minimum_cents)}`],[`${purchase.installments} parcelas`,money(purchase.first_installment_cents),`Menor saldo com a primeira parcela: ${money(purchase.installment_minimum_cents)}`],["Adiar","Criar uma meta","Preservar a margem enquanto você planeja."]].forEach(([label,value,text])=>{const c=node("article");c.append(node("p",label),node("strong",value),node("p",text));compare.append(c);});
    $("special").append(compare,node("p",purchase.assumption,"footnote"));
  }
  if(safety?.available){
    $("special").append(node("h2",`PIX de ${money(safety.amount_cents)}: ${safety.signal_level}`));
    const list=node("ul");safety.reasons.forEach(r=>list.append(node("li",r)));
    $("special").append(list,node("p",safety.recommendation),node("p",safety.limitation,"footnote"));
  }
  $("trace-description").textContent="Veja as ferramentas consultadas e os dados usados. Estes registros mostram ações observáveis, sem expor raciocínio interno do modelo.";
  $("trace").replaceChildren();report.trace.forEach(t=>$("trace").append(node("li",`${t.role} · ${t.tool} · consulta concluída`)));
  renderExplanations(report);
  $("sources").replaceChildren();
  (report.results.guidance?.documents || []).forEach(s=>{const p=node("p",s.text);if(s.url){const a=node("a",s.title);a.href=s.url;a.target="_blank";a.rel="noopener noreferrer";p.append(node("br"),a);}$("sources").append(p);});
  if(report.results.guidance){
    const guide = report.results.guidance;
    $("sources").append(node("p",guide.retrieval_mode === "local_concepts" ? "Orientações relacionadas por conceitos locais." : "Orientações selecionadas pelo tópico do cenário."),node("p",guide.limitation,"footnote"));
  }
  $("history-panel").hidden=!state.history.length;$("history").replaceChildren();
  state.history.forEach(h=>$("history").append(node("li",h.label)));
}

$("start").onclick=()=>request("/api/consent",{enabled:true});
$("consent-toggle").onclick=()=>request("/api/consent",{enabled:!state.consent});
$("monitor").onclick=()=>request("/api/monitor",{});
$("retry").onclick=()=>request("/api/state");
$("text-size").onclick=()=>{
  const enabled = document.documentElement.classList.toggle("large-text");
  $("text-size").setAttribute("aria-pressed",String(enabled));
  $("text-size").textContent = enabled ? "Texto padrão" : "Aumentar texto";
};
request("/api/state");
