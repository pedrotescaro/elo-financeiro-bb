// node --test tests/analyst_behaviors.cjs
// Exercita a visão do analista com um DOM mínimo; sem pacotes.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const root = path.join(__dirname, "..");
const html = fs.readFileSync(path.join(root, "web/analista.html"), "utf8");
const source = fs.readFileSync(path.join(root, "web/analista.js"), "utf8");

class Element {
  constructor(tag = "div") {
    this.tag = tag; this.hidden = false; this.disabled = false; this.textContent = "";
    this.children = []; this.attrs = {}; this.dataset = {}; this.value = "";
    this.classList = {add() {}, remove() {}};
  }
  setAttribute(name, value) { this.attrs[name] = value; }
  append(...children) { this.children.push(...children); }
  replaceChildren() { this.children = []; }
  get lastChild() { return this.children[this.children.length - 1]; }
}

const row = (id, risco, extra = {}) => ({
  id, nome: "Cliente " + id.slice(1), segmento: "mei", segmento_rotulo: "Microempreendedor", gerente: "Gerente 1",
  risco, menor_saldo_cents: risco === "negativo" ? -17000 : 9000, primeiro_negativo: risco === "negativo" ? "2026-10-19" : null,
  falta_para_margem_cents: 49000, acao_sugerida: "Contato proativo.", resolve_com_flexivel: true, ...extra,
});

const portfolio = {
  agencia: "Agência fictícia 0001", data_base: "2026-10-07", analisados: 37, sem_consentimento: 3,
  negativos: 11, abaixo_da_margem: 4, resolvem_com_flexivel: 6, falta_total_cents: 635000,
  tempo_analise_ms: 2.5, interpretador: "regras", csrf: "token-sintetico", contatos: [],
  por_gerente: [{gerente: "Gerente 1", em_risco: 2, analisados: 3}],
  clientes: [row("C30", "negativo"), row("C07", "abaixo_da_margem"), row("C13", "ok")],
};

async function harness(responses) {
  const elements = {};
  for (const match of html.matchAll(/id="([^"]+)"/g)) elements[match[1]] = new Element();
  const findById = (root, id) => {
    if (root.id === id) return root;
    for (const child of root.children || []) { const found = findById(child, id); if (found) return found; }
    return null;
  };
  const chips = [...html.matchAll(/class="chip" data-q="([^"]+)"/g)].map(m => {
    const chip = new Element("button"); chip.dataset.q = m[1]; return chip;
  });
  const calls = [];
  const context = vm.createContext({
    document: {
      getElementById: id => elements[id],
      querySelectorAll: selector => selector === ".chip" ? chips : [],
      createElement: tag => new Element(tag),
    },
    window: {location: {href: "/analista"}},
    fetch: async (url, options) => {
      calls.push({url, options});
      const next = responses.shift();
      return {ok: !next.error, json: async () => next};
    },
    AbortController, Intl, setTimeout, clearTimeout, TypeError, BigInt, Number, String,
  });
  vm.runInContext(source, context);
  await new Promise(resolve => setImmediate(resolve));
  const button = id => Object.values(elements).map(e => findById(e, id)).find(Boolean);
  return {elements, chips, calls, context, button};
}

test("summary shows measured analysis time and lists only clients needing contact", async () => {
  const app = await harness([portfolio]);
  assert.equal(app.elements["m-negative"].textContent, "11");
  assert.match(app.elements["m-time"].textContent, /2,5 ms/);
  assert.equal(app.elements.clients.children.length, 2);
  assert.match(app.elements.interpreter.textContent, /regras locais/);
});

test("question goes to the server with CSRF and shows how it was interpreted", async () => {
  const answer = {resposta: "6 clientes com risco que se resolve.", interpretado_por: "watsonx",
    consulta: {intencao: "resolvem", segmento: null, dias: null}, analisados: 37, tempo_resposta_ms: 4.2,
    aviso: null, clientes: [row("C30", "negativo")]};
  const app = await harness([portfolio, answer]);
  app.chips[2].onclick();
  await new Promise(resolve => setImmediate(resolve));
  const sent = app.calls[1];
  assert.equal(sent.url, "/api/analista");
  assert.equal(sent.options.headers["X-Demo-CSRF"], "token-sintetico");
  assert.equal(JSON.parse(sent.options.body).pergunta, app.chips[2].dataset.q);
  assert.equal(app.elements.answer.hidden, false);
  assert.match(app.elements["answer-how"].textContent, /IBM watsonx\.ai como "resolvem"/);
  assert.equal(app.elements.interpreter.attrs["data-mode"], "watsonx");
});

test("rules fallback is labelled as contingency, never as watsonx", async () => {
  const answer = {resposta: "ok", interpretado_por: "regras_contingencia", consulta: {intencao: "resumo"},
    analisados: 37, tempo_resposta_ms: 3, aviso: "O IBM watsonx.ai não devolveu uma consulta válida.", clientes: []};
  const app = await harness([portfolio, answer]);
  app.elements["ask-form"].onsubmit({preventDefault() {}});  // pergunta vazia: não chama o servidor
  assert.equal(app.calls.length, 1);
  app.elements.question.value = "Como está a carteira?";
  app.elements["ask-form"].onsubmit({preventDefault() {}});
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(app.elements.interpreter.attrs["data-mode"], "demo_fallback");
  assert.match(app.elements.interpreter.textContent, /contingência por regras/);
  assert.doesNotMatch(app.elements.interpreter.textContent, /^Interpretação da pergunta: IBM/);
});

test("opening a client switches the attendance scenario before navigating", async () => {
  const app = await harness([portfolio, {scenario: "cliente-C30"}]);
  const open = app.button("open-C30");
  assert.ok(open);
  await open.onclick();
  assert.deepEqual(JSON.parse(app.calls[1].options.body), {name: "cliente-C30"});
  assert.equal(app.calls[1].url, "/api/scenario");
  assert.equal(vm.runInContext("window.location.href", app.context), "/");
});

test("adding a client to the contact list renders status, summary and CSV link", async () => {
  const listed = {contatos: [{...row("C30", "negativo"), status: "pendente", status_rotulo: "Contato pendente"}]};
  const app = await harness([portfolio, listed]);
  assert.equal(app.elements["contacts-wrap"].hidden, true);
  assert.equal(app.elements["contacts-csv"].hidden, true);
  await app.button("add-C30").onclick();
  assert.equal(app.calls[1].url, "/api/contatos");
  assert.deepEqual(JSON.parse(app.calls[1].options.body), {acao: "adicionar", clientes: ["C30"]});
  assert.equal(app.elements.contacts.children.length, 1);
  assert.equal(app.elements["contacts-wrap"].hidden, false);
  assert.equal(app.elements["contacts-csv"].hidden, false);
  assert.match(app.elements["contacts-summary"].textContent, /1 na lista · 1 pendentes/);
  assert.equal(app.button("add-C30").textContent, "Na lista");
  assert.equal(app.button("add-C30").disabled, true);
});

test("add all sends only at-risk clients that are not yet listed", async () => {
  const already = {...portfolio, contatos: [{...row("C30", "negativo"), status: "contatado", status_rotulo: "Cliente contatado"}]};
  const app = await harness([already, {contatos: []}]);
  assert.match(app.elements["add-all"].textContent, /Adicionar 1 à lista/);
  await app.elements["add-all"].onclick();
  assert.deepEqual(JSON.parse(app.calls[1].options.body), {acao: "adicionar", clientes: ["C07"]});
});

test("contacted clients can go back to pending and be removed", async () => {
  const listed = {...portfolio, contatos: [{...row("C30", "negativo"), status: "contatado", status_rotulo: "Cliente contatado"}]};
  const app = await harness([listed, {contatos: []}]);
  assert.equal(app.button("toggle-C30").textContent, "Voltar a pendente");
  await app.button("remove-C30").onclick();
  assert.deepEqual(JSON.parse(app.calls[1].options.body), {acao: "remover", clientes: ["C30"]});
  assert.equal(app.elements.contacts.children.length, 0);
});
