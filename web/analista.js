"use strict";
// Visão do analista: conversa com a carteira sintética da agência.
// Os números vêm sempre do servidor; o modelo, quando ativo, só interpreta a pergunta.
let csrf = "";
let busy = false;
let currentRows = [];
let contacts = [];
const history = [];
const $ = id => document.getElementById(id);
const integerFormat = new Intl.NumberFormat("pt-BR", {maximumFractionDigits:0});
const money = cents => {
  if(!Number.isSafeInteger(cents)) return "Valor indisponível";
  const value = BigInt(cents), absolute = value < 0n ? -value : value;
  return `${value < 0n ? "−" : ""}R$ ${integerFormat.format(absolute / 100n)},${String(absolute % 100n).padStart(2,"0")}`;
};
const day = value => value ? value.slice(8,10) + "/" + value.slice(5,7) : "";
const node = (tag, text, className) => { const e = document.createElement(tag); if(text !== undefined) e.textContent = text; if(className) e.className = className; return e; };
const RISK = {negativo: "Negativo", abaixo_da_margem: "Abaixo da margem", ok: "Sem risco no período"};
const INTERPRETER = {
  watsonx: "Interpretação da pergunta: IBM watsonx.ai · números calculados no código",
  regras_contingencia: "Interpretação da pergunta: contingência por regras · o IBM watsonx.ai não devolveu uma consulta válida",
  regras: "Interpretação da pergunta: regras locais · IBM watsonx.ai desligado nesta execução",
};
const BY = {watsonx:"IBM watsonx.ai", regras:"regras locais", regras_contingencia:"regras (contingência)"};

// Aviso curto no canto da tela, com o "check" em Lottie quando o player carregou.
let toastTimer = null;
function showToast(text){
  const box = $("toast");
  if(!box) return;
  $("toast-text").textContent = text;
  box.hidden = false;
  if(globalThis.EloAnim) globalThis.EloAnim.play($("toast-anim"), "check");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { box.hidden = true; }, 3600);
}

// Régua fina do indicador: largura proporcional e tom pelo significado.
function setMeter(id, fraction, tone){
  const meter = $(id);
  if(!meter) return;
  const bar = meter.firstElementChild;
  const pct = Math.round(Math.max(0, Math.min(1, fraction)) * 100);
  if(bar && bar.style) bar.style.width = pct + "%";
  if(tone) meter.setAttribute("data-tone", tone); else if(meter.removeAttribute) meter.removeAttribute("data-tone");
  meter.setAttribute("data-value", String(pct));
}

function setBusy(value){
  busy = value;
  document.querySelectorAll("button").forEach(b => b.disabled = value);
  $("main").setAttribute("aria-busy", String(value));
  if(!value) syncAddAll();
}

function showError(message){
  $("error").textContent = message;
  $("error").classList.remove("sr-only");
  $("status").textContent = "";
}

function clearError(){
  $("error").textContent = "";
  $("error").classList.add("sr-only");
}

const errorText = error => error.name === "AbortError" ? "O servidor demorou para responder."
  : error instanceof TypeError ? "Não foi possível conectar ao servidor." : error.message;

async function call(path, body){
  const options = body === undefined ? {} : {method:"POST", headers:{"Content-Type":"application/json","X-Demo-CSRF":csrf}, body:JSON.stringify(body)};
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);
  options.signal = controller.signal;
  try {
    const response = await fetch(path, options);
    const result = await response.json();
    if(!response.ok) throw new Error(result.error || "Não foi possível consultar a carteira.");
    return result;
  } finally { clearTimeout(timeout); }
}

const inList = id => contacts.some(c => c.id === id);

function syncAddAll(){
  const pending = currentRows.filter(r => r.risco !== "ok" && !inList(r.id));
  $("add-all").disabled = busy || pending.length === 0;
  $("add-all").textContent = pending.length ? `Adicionar ${pending.length} à lista` : "Todos já estão na lista";
}

function renderClients(rows){
  currentRows = rows;
  $("clients").replaceChildren();
  if(!rows.length){
    const tr = node("tr"); const td = node("td","Nenhum cliente para esta consulta."); td.colSpan = 5; tr.append(td);
    $("clients").append(tr);
    syncAddAll();
    return;
  }
  rows.forEach(r => {
    const tr = node("tr");
    const who = node("td"); who.append(node("strong", r.nome), node("small", " · " + r.segmento_rotulo + " · " + r.gerente));
    const when = r.primeiro_negativo ? ` em ${day(r.primeiro_negativo)}` : "";
    const risk = node("td"); const tag = node("span", RISK[r.risco] + when, "risk-tag");
    tag.setAttribute("data-risk", r.risco); risk.append(tag);
    const minimum = node("td", money(r.menor_saldo_cents), r.menor_saldo_cents < 0 ? "negative" : "");
    const gap = node("td", money(r.falta_para_margem_cents));
    const next = node("td");
    next.append(node("span", r.acao_sugerida));
    if(r.risco !== "ok"){
      const actions = node("div", undefined, "row-actions");
      const add = node("button", inList(r.id) ? "Na lista" : "Adicionar à lista", "secondary row-button");
      add.type = "button"; add.id = "add-" + r.id;
      add.disabled = busy || inList(r.id);
      add.setAttribute("aria-label", (inList(r.id) ? "Já está na lista: " : "Adicionar à lista de contatos: ") + r.nome);
      add.onclick = () => updateContacts("adicionar", [r.id]);
      const open = node("button", "Abrir no atendimento", "secondary row-button open-client");
      open.type = "button"; open.id = "open-" + r.id;
      open.setAttribute("aria-label", "Abrir " + r.nome + " no atendimento");
      open.onclick = () => openClient(r.id);
      actions.append(add, open);
      next.append(actions);
    }
    tr.append(who, risk, minimum, gap, next);
    $("clients").append(tr);
  });
  syncAddAll();
}

function renderContacts(list){
  contacts = list;
  $("contacts").replaceChildren();
  $("contacts-wrap").hidden = list.length === 0;
  $("contacts-csv").hidden = list.length === 0;
  if(!list.length){
    $("contacts-summary").textContent = 'Nenhum cliente na lista. Use "Adicionar à lista" nos resultados para montar a semana dos gerentes.';
  } else {
    const count = status => list.filter(c => c.status === status).length;
    const perManager = [...new Set(list.map(c => c.gerente))].sort()
      .map(g => `${g}: ${list.filter(c => c.gerente === g).length}`).join(" · ");
    $("contacts-summary").textContent = `${list.length} na lista · ${count("pendente")} pendentes · ${count("contatado")} contatados · `
      + `${count("plano_aprovado")} com plano aprovado · ${count("proposta_recusada")} com proposta recusada. ${perManager}.`;
  }
  list.forEach(c => {
    const tr = node("tr");
    const who = node("td"); who.append(node("strong", c.nome));
    const when = c.primeiro_negativo ? ` em ${day(c.primeiro_negativo)}` : "";
    const risk = node("td"); const tag = node("span", RISK[c.risco] + when, "risk-tag");
    tag.setAttribute("data-risk", c.risco); risk.append(tag);
    const status = node("td"); const st = node("span", c.status_rotulo, "status-tag"); st.setAttribute("data-status", c.status); status.append(st);
    const actions = node("td"); const box = node("div", undefined, "row-actions");
    if(c.status === "pendente" || c.status === "contatado"){
      const toggle = node("button", c.status === "pendente" ? "Marcar como contatado" : "Voltar a pendente", "secondary row-button");
      toggle.type = "button"; toggle.id = "toggle-" + c.id;
      toggle.onclick = () => updateContacts(c.status === "pendente" ? "contatado" : "pendente", [c.id]);
      box.append(toggle);
    }
    const open = node("button", "Abrir no atendimento", "secondary row-button");
    open.type = "button"; open.id = "contact-open-" + c.id;
    open.onclick = () => openClient(c.id);
    const remove = node("button", "Remover", "text-button row-button");
    remove.type = "button"; remove.id = "remove-" + c.id;
    remove.setAttribute("aria-label", "Remover da lista: " + c.nome);
    remove.onclick = () => updateContacts("remover", [c.id]);
    box.append(open, remove); actions.append(box);
    tr.append(who, node("td", c.gerente), risk, status, actions);
    $("contacts").append(tr);
  });
  renderClients(currentRows);
}

function renderSummary(data){
  $("agency-title").textContent = `${data.agencia}: ${data.negativos + data.abaixo_da_margem} clientes precisam de atenção nos próximos 14 dias`;
  const managers = (data.por_gerente || []).map(g => `${g.gerente}: ${g.em_risco}`).join(" · ");
  $("agency-description").textContent = `Base de ${day(data.data_base)}. ${data.analisados} clientes analisados; ${data.sem_consentimento} sem consentimento de compartilhamento ficaram de fora. Falta total para a margem: ${money(data.falta_total_cents)}.`
    + (managers ? ` Em atenção por gerente: ${managers}.` : "");
  $("m-negative").textContent = String(data.negativos);
  $("m-analyzed").textContent = `de ${data.analisados} clientes analisados`;
  $("m-margin").textContent = String(data.abaixo_da_margem);
  $("m-resolve").textContent = String(data.resolvem_com_flexivel);
  const atRisk = data.negativos + data.abaixo_da_margem;
  setMeter("m-negative-meter", data.analisados ? data.negativos / data.analisados : 0, "negative");
  setMeter("m-margin-meter", data.analisados ? data.abaixo_da_margem / data.analisados : 0, "warn");
  setMeter("m-resolve-meter", atRisk ? data.resolvem_com_flexivel / atRisk : 0, null);
  $("m-margin-note").textContent = `Sem ficar negativo · ${data.analisados ? Math.round(data.abaixo_da_margem / data.analisados * 100) : 0}% da carteira`;
  $("m-time").textContent = `Análise da carteira em ${String(data.tempo_analise_ms).replace(".", ",")} ms`;
  $("interpreter").textContent = data.interpretador === "watsonx"
    ? "Interpretação da pergunta: IBM watsonx.ai disponível · números calculados no código"
    : INTERPRETER.regras;
  $("interpreter").setAttribute("data-mode", data.interpretador === "watsonx" ? "watsonx" : "demo_rules");
  currentRows = data.clientes.filter(r => r.risco !== "ok");
  renderContacts(data.contatos || []);
}

function renderHistory(){
  $("history-panel").hidden = history.length < 2;
  $("history").replaceChildren();
  history.slice(1).forEach(item => {
    const li = node("li");
    li.append(node("strong", item.pergunta), node("span", " · " + item.resposta));
    $("history").append(li);
  });
}

async function load(){
  setBusy(true);
  $("status").textContent = "Carregando a carteira…";
  try {
    const data = await call("/api/carteira");
    csrf = data.csrf;
    renderSummary(data);
    $("status").textContent = "Carteira analisada.";
  } catch(error){
    showError(errorText(error));
  } finally { setBusy(false); }
}

async function ask(question){
  const text = (question || "").trim();
  if(!text){ showError("Escreva uma pergunta sobre a carteira."); return; }
  if(busy) return;
  setBusy(true);
  clearError();
  $("status").textContent = "Consultando a carteira…";
  $("thinking").hidden = false;
  if(globalThis.EloAnim) globalThis.EloAnim.play($("thinking-anim"), "dots", true);
  try {
    const result = await call("/api/analista", {pergunta: text});
    $("answer").hidden = false;
    $("answer-text").textContent = result.resposta;
    const q = result.consulta;
    $("answer-how").textContent = (`Como respondi: pergunta interpretada por ${BY[result.interpretado_por] || result.interpretado_por} como "${q.intencao}"`
      + (q.segmento ? `, segmento ${q.segmento}` : "")
      + (q.gerente ? `, ${q.gerente}` : "")
      + (q.dias ? `, até ${q.dias} dias` : "")
      + `; ${result.analisados} clientes analisados em ${String(result.tempo_resposta_ms).replace(".", ",")} ms. ${result.aviso || ""}`).trim();
    $("interpreter").textContent = INTERPRETER[result.interpretado_por] || INTERPRETER.regras;
    $("interpreter").setAttribute("data-mode", result.interpretado_por === "watsonx" ? "watsonx" : result.interpretado_por === "regras_contingencia" ? "demo_fallback" : "demo_rules");
    $("list-title").textContent = "Resultado da pergunta";
    history.unshift({pergunta: result.pergunta, resposta: result.resposta});
    history.splice(6);
    renderHistory();
    renderClients(result.clientes);
    $("status").textContent = "Resposta pronta.";
  } catch(error){
    showError(errorText(error));
  } finally {
    $("thinking").hidden = true;
    if(globalThis.EloAnim) globalThis.EloAnim.stop($("thinking-anim"));
    setBusy(false);
  }
}

async function updateContacts(acao, clientes){
  if(busy || !clientes.length) return;
  setBusy(true);
  clearError();
  try {
    const before = contacts.length;
    const result = await call("/api/contatos", {acao, clientes});
    renderContacts(result.contatos);
    if(acao === "adicionar" && result.contatos.length > before){
      const added = result.contatos.length - before;
      showToast(added === 1 ? "1 cliente entrou na lista da semana." : `${added} clientes entraram na lista da semana.`);
    }
    $("status").textContent = "Lista de contatos atualizada.";
  } catch(error){
    showError(errorText(error));
  } finally { setBusy(false); }
}

async function openClient(id){
  if(busy) return;
  setBusy(true);
  try {
    await call("/api/scenario", {name: "cliente-" + id});
    window.location.href = "/";
  } catch(error){
    showError(errorText(error));
    setBusy(false);
  }
}

$("ask-form").onsubmit = event => { event.preventDefault(); ask($("question").value); };
$("add-all").onclick = () => updateContacts("adicionar", currentRows.filter(r => r.risco !== "ok" && !inList(r.id)).map(r => r.id));
document.querySelectorAll(".chip").forEach(chip => {
  chip.onclick = () => { $("question").value = chip.dataset.q; ask(chip.dataset.q); };
});
load();
