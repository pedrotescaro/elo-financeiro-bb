"use strict";
let state;
let busy = false;
let presentationOpen = false;
let presentationIndex = 0;
const $ = id => document.getElementById(id);
const integerFormat = new Intl.NumberFormat("pt-BR", {maximumFractionDigits:0});
const money = cents => {
  if(!Number.isSafeInteger(cents)) return "Valor indisponível";
  const value = BigInt(cents), absolute = value < 0n ? -value : value;
  return `${value < 0n ? "−" : ""}R$\u00a0${integerFormat.format(absolute / 100n)},${String(absolute % 100n).padStart(2,"0")}`;
};
const day = value => value.slice(8,10) + "/" + value.slice(5,7);
const node = (tag, text, className) => { const e = document.createElement(tag); if(text !== undefined) e.textContent = text; if(className) e.className = className; return e; };

// Converte string de reais (ex.: "150,00" ou "150.00") para centavos inteiros.
// Retorna null se o valor for inválido.
const parseCents = raw => {
  if (typeof raw !== "string") return null;
  const trimmed = raw.trim().replace(/\s/g, "");
  if (!trimmed) return null;
  // Aceita vírgula ou ponto como separador decimal, mas não ambos.
  const normalized = trimmed.replace(",", ".");
  // Deve ser um número com no máximo 2 casas decimais.
  if (!/^\d+(\.\d{1,2})?$/.test(normalized)) return null;
  const float = parseFloat(normalized);
  if (!isFinite(float) || float < 0) return null;
  // Converte para centavos sem ponto flutuante intermediário.
  const [intPart, fracPart = ""] = normalized.split(".");
  const cents = parseInt(intPart, 10) * 100 + parseInt((fracPart + "0").slice(0, 2), 10);
  if (!Number.isSafeInteger(cents) || cents <= 0) return null;
  return cents;
};

function syncControls(){
  document.querySelectorAll("button").forEach(b => b.disabled = busy);
  $("start").disabled = busy || !state;
  $("consent-toggle").disabled = busy || !state;
  $("demo-reset").disabled = busy || !state;
  const monitorDone = state?.monitor_done === true;
  $("monitor").disabled = busy || !state?.consent || monitorDone;
  $("monitor").textContent = monitorDone ? "Despesa já simulada" : "Simular nova despesa";
  $("monitor").setAttribute("aria-disabled", String($("monitor").disabled));
  $("main").setAttribute("aria-busy", String(busy));
  syncPresentationControls();
  // Controles do painel de redução são gerenciados apenas quando ele está visível.
  if($("reduction-panel") && !$("reduction-panel").hidden){
    const hasPreview = state?.pending_adjustment != null;
    $("reduction-approve").disabled = busy || !hasPreview;
    $("reduction-discard").disabled = busy || !hasPreview;
    $("reduction-preview").disabled = busy;
  }
}

function syncPresentationControls(){
  $("pitch-previous").disabled = busy || presentationIndex === 0;
  $("pitch-next").disabled = busy || presentationIndex === 3;
}

function showPresentationSlide(index){
  presentationIndex = Math.max(0,Math.min(3,index));
  for(let i=0;i<4;i++){
    $("pitch-slide-"+i).hidden = i !== presentationIndex;
    $("pitch-tab-"+i).setAttribute("aria-current",i === presentationIndex ? "step" : "false");
  }
  $("pitch-position").textContent = `${presentationIndex+1} de 4`;
  syncPresentationControls();
}

function setPresentation(enabled){
  presentationOpen = enabled;
  $("presentation-panel").hidden = !enabled;
  $("dashboard-view").hidden = enabled;
  $("presenter-launch").setAttribute("aria-expanded",String(enabled));
  document.documentElement.classList[enabled ? "add" : "remove"]("presentation-mode");
  showPresentationSlide(enabled ? 0 : presentationIndex);
  const focusTarget = enabled ? $("pitch-title-0") : $("presenter-launch");
  if(typeof focusTarget.focus === "function") focusTarget.focus({preventScroll:true});
}

async function demonstrateScenario(name){
  setPresentation(false);
  if(state) await request("/api/scenario",{name});
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

function renderChart(flow){
  const target = $("balance-chart");
  target.replaceChildren();
  if(!flow.daily.length){
    target.append(node("p","Ainda não há dias suficientes para desenhar a projeção."));
    return;
  }
  const width = Math.max(240,target.clientWidth || 600), height = 240;
  const left = 18, right = width - 18, top = 24, bottom = height - 38;
  const values = flow.daily.map(row => row.balance_cents);
  const low = Math.min(0,...values), high = Math.max(flow.buffer_cents,0,...values);
  // A divisão é apenas da geometria; os valores monetários permanecem centavos inteiros.
  const y = value => top + (high - value) / Math.max(1,high - low) * (bottom - top);
  const x = index => left + index / Math.max(1,values.length - 1) * (right - left);
  const svgNode = (tag,attributes={},text) => {
    const element = document.createElementNS("http://www.w3.org/2000/svg",tag);
    Object.entries(attributes).forEach(([name,value])=>element.setAttribute(name,String(value)));
    if(text !== undefined) element.textContent = text;
    return element;
  };
  const svg = svgNode("svg",{viewBox:`0 0 ${width} ${height}`,role:"img","aria-labelledby":"chart-title chart-description"});
  svg.append(svgNode("title",{id:"chart-title"},"Saldo previsto por fechamento diário"),
    svgNode("desc",{id:"chart-description"},`Menor saldo: ${money(flow.minimum_cents)} em ${day(flow.minimum_date)}. Margem desejada: ${money(flow.buffer_cents)}. Consulte todos os valores na tabela abaixo.`));
  const line = (value,className) => svgNode("line",{x1:left,x2:right,y1:y(value),y2:y(value),class:className});
  const points = values.map((value,index)=>`${x(index)},${y(value)}`).join(" ");
  svg.append(svgNode("polygon",{points:`${left},${bottom} ${points} ${right},${bottom}`,class:"chart-area"}));
  [0.25,0.5,0.75].forEach(fraction => svg.append(line(low + (high-low) * fraction,"chart-grid")));
  svg.append(line(0,"chart-zero"),line(flow.buffer_cents,"chart-buffer"));
  svg.append(svgNode("text",{x:right,y:y(0)-7,"text-anchor":"end",class:"chart-label"},"zero"));
  svg.append(svgNode("polyline",{points,class:"chart-line"}));
  flow.daily.forEach((row,index)=>{
    const isLowest = row.date === flow.minimum_date;
    const dot = svgNode("circle",{cx:x(index),cy:y(row.balance_cents),r:isLowest ? 6 : 3,
      class:isLowest ? "chart-low-dot" : "chart-dot"});
    dot.append(svgNode("title",{},`${day(row.date)}: ${money(row.balance_cents)}${isLowest ? ", menor saldo" : ""}`));
    svg.append(dot);
  });
  svg.append(svgNode("text",{x:left,y:height-10,class:"chart-label"},day(flow.daily[0].date)),
    svgNode("text",{x:right,y:height-10,"text-anchor":"end",class:"chart-label"},day(flow.daily.at(-1).date)));
  target.append(svg);
  $("chart-caption").textContent = `Menor saldo: ${money(flow.minimum_cents)} em ${day(flow.minimum_date)}${flow.minimum_cents < 0 ? " (abaixo de zero)" : ""}. Margem desejada: ${money(flow.buffer_cents)}.`;
}

function renderDemoProgress(){
  const isPix = state.scenario === "pix";
  const hasDecision = state.history.some(entry => entry.status === "accepted" || entry.status === "declined");
  const active = !state.consent ? 0 : !isPix && hasDecision ? 2 : 1;
  const completed = [state.consent, state.consent && hasDecision, state.consent && state.monitor_done];
  $("step-plan-label").textContent = isPix ? "Confira os sinais" : state.scenario === "purchase" ? "Compare as opções" : "Escolha um plano";
  $("step-monitor").hidden = isPix;
  ["step-consent", "step-plan", "step-monitor"].forEach((id, index) => {
    const done = completed[index];
    $(id).setAttribute("data-state", done ? "done" : index === active ? "current" : "upcoming");
    $(id).setAttribute("aria-current", !done && index === active ? "step" : "false");
  });
}

function scenarioIcon(id){
  const paths = {
    month: "M3 20h18M5 16v-5m7 5V4m7 12V8",
    purchase: "M5 7h14l1 14H4L5 7Zm3 0V6a4 4 0 0 1 8 0v1",
    pix: "m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Zm-4 9 3 3 5-6",
  };
  const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  Object.entries({viewBox:"0 0 24 24",fill:"none",stroke:"currentColor","stroke-width":"1.6","stroke-linecap":"round","stroke-linejoin":"round","aria-hidden":"true",class:"scenario-icon"}).forEach(([key,value]) => icon.setAttribute(key,value));
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", paths[id] || paths.month);
  icon.append(path);
  return icon;
}

function render(){
  renderAudit();
  renderDemoProgress();
  $("scenarios").replaceChildren();
  state.scenarios.forEach(s => {
    const b = node("button", undefined, s.id === state.scenario ? "active" : "");
    const label = node("span",s.title,"scenario-label");
    const descriptions = {month:"Previsão de caixa",purchase:"Planejar a compra",pix:"Conferir um PIX"};
    label.append(node("span",descriptions[s.id] || "Cenário demonstrativo","scenario-description"));
    b.append(scenarioIcon(s.id),label);
    b.id = "scenario-" + s.id;
    b.setAttribute("aria-label", "Selecionar cenário: " + s.title);
    if(s.id === state.scenario) b.setAttribute("aria-current","true");
    b.onclick = () => request("/api/scenario",{name:s.id});
    $("scenarios").append(b);
  });
  $("scenario-title").textContent = state.scenario_title;
  $("scenario-period").textContent = "Cenário fictício · você controla as escolhas";
  $("consent-toggle").textContent = state.consent ? "Desativar leitura" : "Autorizar leitura";
  $("consent-toggle").setAttribute("aria-label",state.consent ? "Desativar leitura e limpar planos" : "Autorizar leitura");
  $("consent-toggle").title = state.consent ? "Desativar a leitura e limpar os planos desta sessão" : "Autorizar a leitura dos dados fictícios";
  $("consent-panel").hidden = state.consent;
  $("workspace").hidden = !state.consent;
  $("notice").textContent = "";
  $("notice").hidden = true;
  const showGoals = state.consent && state.goals && state.goals.length > 0;
  $("goals-panel").hidden=!showGoals;$("goals").replaceChildren();
  if(showGoals)(state.goals).forEach(g=>{const li=node("li");li.append(node("strong",g.label),node("span"," · "+money(g.target_cents)));$("goals").append(li);});
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
  const planner = {
    watsonx: "Planejador: IBM watsonx.ai escolheu as ferramentas · cálculos feitos no código, não pelo modelo",
    demo_fallback: "Planejador: contingência por regras · o IBM watsonx.ai não respondeu com um plano válido",
  }[report.mode] || "Planejador: regras locais · IBM watsonx.ai desligado nesta execução";
  $("mode").textContent = planner;
  $("mode").setAttribute("data-mode", report.mode || "demo_rules");
  if(report.warning){$("notice").textContent=report.warning;$("notice").hidden=false;}
  $("minimum").textContent = money(flow.minimum_cents);
  $("minimum").className = flow.minimum_cents < 0 ? "negative" : "";
  $("minimum-date").textContent = `${flow.minimum_cents < 0 ? "Saldo abaixo de zero · " : ""}Previsto para ${day(flow.minimum_date)}`;
  $("buffer").textContent = money(flow.buffer_cents);
  $("closing").textContent = money(flow.closing_cents);
  $("horizon").textContent = `Em ${day(report.horizon)}`;
  const firstDate = flow.daily[0]?.date;
  $("scenario-period").textContent = firstDate ? `${day(firstDate)} a ${day(report.horizon)} · calendário fictício` : "Calendário fictício";
  const preservesBuffer = flow.minimum_cents >= flow.buffer_cents;
  $("projection-state").textContent = flow.minimum_cents < 0 ? "Atenção ao saldo" : preservesBuffer ? "Margem preservada" : "Margem reduzida";
  $("projection-state").setAttribute("data-state", preservesBuffer ? "positive" : "attention");
  $("monitor-copy").textContent = state.monitor_done
    ? "Nova despesa de R$ 150,00 incluída. Confira o impacto na projeção e no histórico."
    : "Simule uma nova despesa de R$ 150,00 e veja a recomendação ser atualizada.";
  renderChart(flow);
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
  const hasBudgetPlan = report.actions.some(a => a.id === "budget-plan");
  report.actions.forEach(a => {
    const wrap=node("div",undefined,"action");
    if(a.id === "budget-plan"){
      wrap.append(node("p",`Proposta: reduzir ${money(a.reduction_cents)} dos gastos flexíveis previstos. As despesas essenciais permanecem na projeção.`));
      const impact = node("div",undefined,"impact");
      const comparison = node("div",undefined,"impact-comparison");
      const before = node("div"), after = node("div");
      before.append(node("span","Sem este plano"),node("strong",money(a.before_cents),a.before_cents < 0 ? "negative" : ""));
      after.append(node("span","Com este plano"),node("strong",money(a.after_cents)));
      comparison.append(before,node("span","→","impact-arrow"),after);
      impact.append(comparison,node("small",a.meets_buffer ? "Margem desejada preservada." : "A margem desejada ainda não é atingida."));
      wrap.append(impact);
    } else wrap.append(node("p",`Registre a meta de ${money(a.target_cents)} e preserve sua margem antes da compra. Nenhuma aplicação automática será feita.`));
    const actionRow=node("div",undefined,"action-buttons");
    const approveBtn=node("button",a.label,"primary");
    approveBtn.id = "approve-" + a.id;
    approveBtn.setAttribute("aria-label", "Aprovar: " + a.label);
    approveBtn.onclick=()=>request("/api/approve",{report_id:report.report_id,action_id:a.id});
    const declineBtn=node("button","Recusar proposta","secondary");
    declineBtn.id = "decline-" + a.id;
    declineBtn.setAttribute("aria-label", "Recusar proposta: " + a.label);
    declineBtn.onclick=()=>request("/api/decline",{report_id:report.report_id,action_id:a.id});
    actionRow.append(approveBtn,declineBtn);
    wrap.append(actionRow);$("actions").append(wrap);
  });
  // Painel de redução personalizada — exibido somente quando há proposta budget-plan ativa.
  const reductionPanel = $("reduction-panel");
  if(reductionPanel){
    reductionPanel.hidden = !hasBudgetPlan;
    if(hasBudgetPlan){
      // Restaura prévia pendente do servidor, se houver.
      const pending = state.pending_adjustment;
      const previewPanel = $("reduction-preview-panel");
      if(pending && pending.report_id === report.report_id){
        $("reduction-options").open = true;
        previewPanel.hidden = false;
        const p = pending.preview;
        $("reduction-preview-result").textContent =
          `Com redução de ${money(pending.reduction_cents)}: menor saldo previsto ${money(p.minimum_cents)}.`;
        const warnEl = $("reduction-preview-warning");
        if(p.warning){
          warnEl.textContent = Number.isSafeInteger(p.gap_to_buffer_cents)
            ? `O menor saldo de ${money(p.minimum_cents)} ainda fica abaixo da margem desejada de ${money(flow.buffer_cents)}. Faltam ${money(p.gap_to_buffer_cents)} para atingir a margem.`
            : p.warning;
          warnEl.hidden = false;
        } else {
          warnEl.textContent = "";
          warnEl.hidden = true;
        }
      } else {
        previewPanel.hidden = true;
        $("reduction-preview-result").textContent = "";
        $("reduction-preview-warning").textContent = "";
        $("reduction-preview-warning").hidden = true;
        // Limpa o campo de entrada sempre que não há prévia pendente (descarte ou estado novo).
        $("reduction-input").value = "";
        $("reduction-error").textContent = "";
        $("reduction-error").classList.add("sr-only");
      }
    }
  }
  $("special").replaceChildren();
  const purchase=report.results.purchase, safety=report.results.safety;
  $("special").hidden=!(purchase?.available || safety?.available);
  if(purchase?.available){
    $("special").append(node("h2",`${purchase.label}: o preço não conta toda a história.`));
    const compare=node("div",undefined,"compare");
    // À vista
    const cVista=node("article");
    cVista.append(node("p","À vista"),node("strong",money(purchase.price_cents)),node("p",`Menor saldo previsto: ${money(purchase.cash_minimum_cents)}`));
    compare.append(cVista);
    // Parcelado – usa o menor saldo projetado com todas as parcelas do horizonte quando disponível
    const hasProjected = typeof purchase.installment_projected_minimum_cents === "number";
    const installLabel = hasProjected && purchase.schedule && purchase.schedule.length > 1
      ? `${purchase.schedule.length} parcela(s) no horizonte`
      : `${purchase.installments}x – primeira parcela`;
    const installMinimum = hasProjected && purchase.schedule && purchase.schedule.length > 1
      ? purchase.installment_projected_minimum_cents
      : purchase.installment_minimum_cents;
    const cParc=node("article");
    cParc.append(node("p",installLabel),node("strong",money(purchase.first_installment_cents)),node("p",`Menor saldo projetado: ${money(installMinimum)}`));
    compare.append(cParc);
    // Adiar
    const cAdiar=node("article");
    cAdiar.append(node("p","Adiar"),node("strong","Criar uma meta"),node("p","Preservar a margem enquanto você planeja."));
    compare.append(cAdiar);
    $("special").append(compare);
    // Cronograma de parcelas
    if(purchase.schedule && purchase.schedule.length){
      const schedHead=node("h3","Parcelas projetadas neste horizonte");
      schedHead.className="installment-schedule-title";
      $("special").append(schedHead);
      const wrap=node("div",undefined,"table-wrap");
      wrap.setAttribute("tabindex","0");
      wrap.setAttribute("role","region");
      wrap.setAttribute("aria-label","Cronograma de parcelas projetadas");
      const table=node("table");
      const caption=node("caption","Cronograma de parcelas projetadas no horizonte");
      caption.className="sr-only";
      const thead=node("thead");
      const headerRow=node("tr");
      headerRow.append(node("th","Parcela"),node("th","Data"),node("th","Valor"));
      ["th","th","th"].forEach((t,i)=>headerRow.children[i].setAttribute("scope","col"));
      thead.append(headerRow);
      const tbody=node("tbody");
      purchase.schedule.forEach(entry=>{
        const tr=node("tr");
        tr.append(node("td",`${entry.number}/${purchase.installments}`),node("td",day(entry.date)),node("td",money(entry.amount_cents)));
        tbody.append(tr);
      });
      table.append(caption,thead,tbody);
      wrap.append(table);
      $("special").append(wrap);
    }
    // Aviso sobre parcelas fora do horizonte
    if(purchase.out_of_horizon > 0){
      const warn=node("p",`⚠ Atenção: ${purchase.out_of_horizon} parcela(s) com vencimento após ${day(report.horizon)} não foram incluídas na projeção acima.`,"footnote");
      $("special").append(warn);
    }
    $("special").append(node("p",purchase.assumption,"footnote"));
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
  state.history.forEach(h=>{
    const li=node("li");
    const status = h.status === "accepted"
      ? (h.kind === "custom" ? "✔ personalizada" : h.kind === "goal" ? "✔ meta" : "✔ padrão")
      : h.status === "declined" ? "✗ recusada" : "● observada";
    const detail = h.applied_cents != null ? ` — ${money(h.applied_cents)} aplicados` : "";
    li.textContent = `${h.label} [${status}${detail}]`;
    $("history").append(li);
  });
}

$("start").onclick=()=>request("/api/consent",{enabled:true});
$("consent-toggle").onclick=()=>request("/api/consent",{enabled:!state.consent});
$("monitor").onclick=()=>request("/api/monitor",{});
$("retry").onclick=()=>request("/api/state");
$("demo-reset").onclick=()=>request("/api/scenario",{name:state.scenario});
$("presenter-launch").onclick=()=>setPresentation(true);
$("presentation-close").onclick=()=>setPresentation(false);
$("pitch-previous").onclick=()=>showPresentationSlide(presentationIndex-1);
$("pitch-next").onclick=()=>showPresentationSlide(presentationIndex+1);
for(let i=0;i<4;i++) $("pitch-tab-"+i).onclick=()=>showPresentationSlide(i);
$("pitch-demo-month").onclick=()=>demonstrateScenario("month");
$("pitch-demo-purchase").onclick=()=>demonstrateScenario("purchase");
$("pitch-demo-pix").onclick=()=>demonstrateScenario("pix");
if(typeof document.addEventListener === "function"){
  document.addEventListener("keydown",event=>{
    if(!presentationOpen || /^(INPUT|TEXTAREA|SELECT)$/.test(event.target.tagName)) return;
    if(event.key === "Escape") {event.preventDefault();setPresentation(false);}
    else if(event.key === "ArrowRight") {event.preventDefault();showPresentationSlide(presentationIndex+1);}
    else if(event.key === "ArrowLeft") {event.preventDefault();showPresentationSlide(presentationIndex-1);}
  });
}
$("reduction-preview").onclick=()=>{
  const raw = $("reduction-input").value;
  const cents = parseCents(raw);
  const errorEl = $("reduction-error");
  if(cents === null){
    errorEl.textContent = "Valor inválido. Digite um valor positivo em reais. Exemplo: 150,00.";
    errorEl.classList.remove("sr-only");
    return;
  }
  // Validação de limite (gastos flexíveis) é feita no servidor; aqui apenas limpamos o erro visual.
  errorEl.textContent = "";
  errorEl.classList.add("sr-only");
  const rid = state?.report?.report_id;
  if(!rid) return;
  request("/api/preview",{report_id:rid,reduction_cents:cents});
};
$("reduction-approve").onclick=()=>{
  const rid = state?.report?.report_id;
  if(!rid) return;
  // Envia preview_id para detectar sobreposição por outra aba; null se aprovação padrão.
  const previewId = state?.pending_adjustment?.preview_id ?? null;
  request("/api/approve",{report_id:rid,action_id:"budget-plan",...(previewId !== null ? {preview_id:previewId} : {})});
};
$("reduction-discard").onclick=()=>{
  // Cancela a prévia no servidor para que persista após recarregar a página.
  request("/api/preview/discard",{});
};
$("text-size").onclick=()=>{
  const enabled = document.documentElement.classList.toggle("large-text");
  $("text-size").setAttribute("aria-pressed",String(enabled));
  $("text-size").textContent = enabled ? "Texto padrão" : "Aumentar texto";
};
if(typeof ResizeObserver !== "undefined"){
  new ResizeObserver(()=>{
    const flow = state?.consent && state.report?.results?.cashflow;
    if(flow) renderChart(flow);
  }).observe($("balance-chart"));
}
request("/api/state");
