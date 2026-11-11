"use strict";
// Visão do analista: conversa com a carteira sintética da agência.
// Os números vêm sempre do servidor; o modelo, quando ativo, só interpreta a pergunta.
let csrf = "";
let busy = false;
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

function setBusy(value){
  busy = value;
  document.querySelectorAll("button").forEach(b => b.disabled = value);
  $("main").setAttribute("aria-busy", String(value));
}

function showError(message){
  $("error").textContent = message;
  $("error").classList.remove("sr-only");
  $("status").textContent = "";
}

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

function renderClients(rows){
  $("clients").replaceChildren();
  if(!rows.length){
    const tr = node("tr"); const td = node("td","Nenhum cliente para esta consulta."); td.colSpan = 5; tr.append(td);
    $("clients").append(tr);
    return;
  }
  rows.forEach(r => {
    const tr = node("tr");
    const who = node("td"); who.append(node("strong", r.nome), node("small", " · " + r.segmento_rotulo));
    const when = r.primeiro_negativo ? ` em ${day(r.primeiro_negativo)}` : "";
    const risk = node("td"); risk.append(node("span", RISK[r.risco] + when, "risk-tag"));
    risk.lastChild.setAttribute("data-risk", r.risco);
    const minimum = node("td", money(r.menor_saldo_cents), r.menor_saldo_cents < 0 ? "negative" : "");
    const gap = node("td", money(r.falta_para_margem_cents));
    const next = node("td");
    next.append(node("span", r.acao_sugerida));
    if(r.risco !== "ok"){
      const open = node("button", "Abrir no atendimento", "secondary open-client");
      open.type = "button";
      open.id = "open-" + r.id;
      open.setAttribute("aria-label", "Abrir " + r.nome + " no atendimento");
      open.onclick = () => openClient(r.id);
      next.append(open);
    }
    tr.append(who, risk, minimum, gap, next);
    $("clients").append(tr);
  });
}

function renderSummary(data){
  $("agency-title").textContent = `${data.agencia}: ${data.negativos + data.abaixo_da_margem} clientes precisam de atenção nos próximos 14 dias`;
  $("agency-description").textContent = `Base de ${day(data.data_base)}. ${data.analisados} clientes analisados; ${data.sem_consentimento} sem consentimento de compartilhamento ficaram de fora. Falta total para a margem: ${money(data.falta_total_cents)}.`;
  $("m-negative").textContent = String(data.negativos);
  $("m-analyzed").textContent = `de ${data.analisados} clientes analisados`;
  $("m-margin").textContent = String(data.abaixo_da_margem);
  $("m-resolve").textContent = String(data.resolvem_com_flexivel);
  $("m-time").textContent = `Análise da carteira em ${String(data.tempo_analise_ms).replace(".", ",")} ms`;
  $("interpreter").textContent = data.interpretador === "watsonx"
    ? "Interpretação da pergunta: IBM watsonx.ai disponível · números calculados no código"
    : INTERPRETER.regras;
  $("interpreter").setAttribute("data-mode", data.interpretador === "watsonx" ? "watsonx" : "demo_rules");
  renderClients(data.clientes.filter(r => r.risco !== "ok"));
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
    showError(error.name === "AbortError" ? "O servidor demorou para responder." : error instanceof TypeError ? "Não foi possível conectar ao servidor." : error.message);
  } finally { setBusy(false); }
}

async function ask(question){
  const text = (question || "").trim();
  if(!text){ showError("Escreva uma pergunta sobre a carteira."); return; }
  if(busy) return;
  setBusy(true);
  $("error").textContent = ""; $("error").classList.add("sr-only");
  $("status").textContent = "Consultando a carteira…";
  try {
    const result = await call("/api/analista", {pergunta: text});
    $("answer").hidden = false;
    $("answer-text").textContent = result.resposta;
    const by = {watsonx:"IBM watsonx.ai", regras:"regras locais", regras_contingencia:"regras (contingência)"}[result.interpretado_por] || result.interpretado_por;
    $("answer-how").textContent = `Como respondi: pergunta interpretada por ${by} como "${result.consulta.intencao}"`
      + (result.consulta.segmento ? `, segmento ${result.consulta.segmento}` : "")
      + (result.consulta.dias ? `, até ${result.consulta.dias} dias` : "")
      + `; ${result.analisados} clientes analisados em ${String(result.tempo_resposta_ms).replace(".", ",")} ms. ${result.aviso || ""}`.trim();
    $("interpreter").textContent = INTERPRETER[result.interpretado_por] || INTERPRETER.regras;
    $("interpreter").setAttribute("data-mode", result.interpretado_por === "watsonx" ? "watsonx" : result.interpretado_por === "regras_contingencia" ? "demo_fallback" : "demo_rules");
    $("list-title").textContent = "Resultado da pergunta";
    renderClients(result.clientes);
    $("status").textContent = "Resposta pronta.";
  } catch(error){
    showError(error.name === "AbortError" ? "O servidor demorou para responder." : error instanceof TypeError ? "Não foi possível conectar ao servidor." : error.message);
  } finally { setBusy(false); }
}

async function openClient(id){
  if(busy) return;
  setBusy(true);
  try {
    await call("/api/scenario", {name: "cliente-" + id});
    window.location.href = "/";
  } catch(error){
    showError(error.message);
    setBusy(false);
  }
}

$("ask-form").onsubmit = event => { event.preventDefault(); ask($("question").value); };
document.querySelectorAll(".chip").forEach(chip => {
  chip.onclick = () => { $("question").value = chip.dataset.q; ask(chip.dataset.q); };
});
load();
