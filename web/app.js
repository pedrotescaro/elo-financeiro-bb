"use strict";
let state;
let busy = false;
const $ = id => document.getElementById(id);
const money = cents => new Intl.NumberFormat("pt-BR", {style:"currency",currency:"BRL"}).format(cents / 100);
const day = value => value.slice(8,10) + "/" + value.slice(5,7);
const node = (tag, text, className) => { const e = document.createElement(tag); if(text !== undefined) e.textContent = text; if(className) e.className = className; return e; };

async function request(path, body){
  if(busy) return;
  busy = true;
  $("error").hidden = true;
  document.querySelectorAll("button").forEach(b => b.disabled = true);
  try {
    const options = body === undefined ? {} : {method:"POST",headers:{"Content-Type":"application/json","X-Demo-CSRF":state.csrf},body:JSON.stringify(body)};
    const response = await fetch(path, options);
    const result = await response.json();
    if(!response.ok) throw new Error(result.error || "Não foi possível atualizar o cenário.");
    state = result;
    render();
  } catch(error){ $("error").textContent = error.message; $("error").hidden = false; }
  finally {busy = false; document.querySelectorAll("button").forEach(b => b.disabled = false);}
}

function render(){
  $("scenarios").replaceChildren();
  state.scenarios.forEach(s => {
    const b = node("button", s.title, s.id === state.scenario ? "active" : "");
    if(s.id === state.scenario) b.setAttribute("aria-current","true");
    b.onclick = () => request("/api/scenario",{name:s.id});
    $("scenarios").append(b);
  });
  $("scenario-title").textContent = state.scenario_title;
  $("consent-toggle").textContent = state.consent ? "Desativar leitura e limpar planos" : "Autorizar leitura";
  $("consent-panel").hidden = state.consent;
  $("workspace").hidden = !state.consent;
  $("notice").hidden = true;
  if(!state.consent) return;
  const report = state.report, flow = report.results.cashflow;
  $("report-title").textContent = report.title;
  $("report-description").textContent = flow.first_negative_date
    ? `Mesmo com um recebimento esperado, o saldo pode chegar a ${money(flow.minimum_cents)} em ${day(flow.minimum_date)}. O calendário dos compromissos faz diferença.`
    : `O menor saldo previsto até ${day(report.horizon)} é ${money(flow.minimum_cents)}. Compare esse valor com sua margem desejada de ${money(flow.buffer_cents)} antes de decidir.`;
  $("mode").textContent = report.mode === "watsonx" ? "Planejamento de ferramentas: IBM watsonx.ai · Cálculos: ferramentas determinísticas" : "Demonstração por regras · Planejamento por IA generativa ainda não validado";
  if(report.warning){$("notice").textContent=report.warning;$("notice").hidden=false;}
  $("minimum").textContent = money(flow.minimum_cents);
  $("minimum").className = flow.minimum_cents < 0 ? "negative" : "";
  $("minimum-date").textContent = `Previsto para ${day(flow.minimum_date)}`;
  $("buffer").textContent = money(flow.buffer_cents);
  $("closing").textContent = money(flow.closing_cents);
  $("horizon").textContent = `Em ${day(report.horizon)}`;
  $("daily").replaceChildren();
  flow.daily.forEach(r => {
    const tr = node("tr");
    tr.append(node("td",day(r.date)),node("td",r.events.join(" + ") || "Saldo inicial"),node("td",money(r.balance_cents),r.balance_cents < 0 ? "negative" : ""));
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
  $("sources").replaceChildren();
  (report.results.guidance?.documents || []).forEach(s=>{const p=node("p",s.text);if(s.url){const a=node("a",s.title);a.href=s.url;a.target="_blank";a.rel="noopener noreferrer";p.append(node("br"),a);}$("sources").append(p);});
  $("history-panel").hidden=!state.history.length;$("history").replaceChildren();
  state.history.forEach(h=>$("history").append(node("li",h.label)));
}

$("start").onclick=()=>request("/api/consent",{enabled:true});
$("consent-toggle").onclick=()=>request("/api/consent",{enabled:!state.consent});
$("monitor").onclick=()=>request("/api/monitor",{});
request("/api/state");
