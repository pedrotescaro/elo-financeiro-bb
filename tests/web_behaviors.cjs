// Optional development check: node --test tests/web_behaviors.cjs
// Exercises requests and rendered states with a small DOM double; no packages.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const root = path.join(__dirname, "..");
const html = fs.readFileSync(path.join(root, "web/index.html"), "utf8");
const source = fs.readFileSync(path.join(root, "web/app.js"), "utf8");

class Element {
  constructor(tag = "div") {
    this.tag = tag;
    this.hidden = false;
    this.disabled = false;
    this.textContent = "";
    this.children = [];
    this.attrs = {};
    this.clientWidth = 300;
    const classes = new Set();
    this.classList = {
      add: value => classes.add(value),
      remove: value => classes.delete(value),
      contains: value => classes.has(value),
      toggle(value) {
        if (classes.has(value)) { classes.delete(value); return false; }
        classes.add(value); return true;
      },
    };
  }
  setAttribute(name, value) { this.attrs[name] = value; }
  append(...children) { this.children.push(...children); }
  replaceChildren() { this.children = []; }
}

const initial = {
  scenario: "month", scenario_title: "Demonstração", scenarios: [],
  csrf: "synthetic-test-token", consent: false, monitor_done: false,
  report: {status: "consent_required"}, history: [], audit: [],
};

const ready = {
  ...initial, consent: true, monitor_done: true,
  report: {
    title: "Projeção", horizon: "2026-10-15", actions: [], trace: [],
    results: {cashflow: {
      daily: [
        {date: "2026-10-07", balance_cents: 150000, events: []},
        {date: "2026-10-13", balance_cents: -10000, events: ["Despesa prevista"]},
        {date: "2026-10-15", balance_cents: 170000, events: ["Recebimento esperado"]},
      ],
      minimum_cents: -10000, minimum_date: "2026-10-13", buffer_cents: 20000,
      closing_cents: 170000,
    }},
    explanations: {cashflow: {
      title: "Projeção de caixa", summary: "Estimativa com dados sintéticos.",
      numbers: [{label: "Menor saldo", value_cents: -10000}],
      assumptions: ["Recebimento na data esperada"], not_considered: ["Novas despesas"],
    }},
  },
};

async function harness(first = initial) {
  const elements = {};
  const buttonIds = new Set(["start", "consent-toggle", "monitor", "retry", "text-size"]);
  for (const match of html.matchAll(/id="([^"]+)"/g)) {
    elements[match[1]] = new Element(buttonIds.has(match[1]) ? "button" : "div");
  }
  let response = first;
  const context = vm.createContext({
    document: {
      getElementById: id => elements[id],
      querySelectorAll: () => Object.values(elements).filter(e => e.tag === "button"),
      createElement: tag => new Element(tag),
      createElementNS: (_, tag) => new Element(tag),
      documentElement: new Element(),
    },
    fetch: async () => {
      if (response instanceof Error) throw response;
      return {ok: true, json: async () => response};
    },
    AbortController, TypeError, Intl, setTimeout, clearTimeout,
  });
  vm.runInContext(source, context);
  await new Promise(resolve => setImmediate(resolve));
  return {
    elements,
    evaluate: expression => vm.runInContext(expression, context),
    async load(next) {
      response = next;
      await vm.runInContext('request("/api/state")', context);
    },
  };
}

test("startup network error leaves a working retry and blocks consent until loaded", async () => {
  const app = await harness(new TypeError("fetch failed"));
  assert.equal(app.elements.start.disabled, true);
  assert.equal(app.elements.retry.hidden, false);
  assert.match(app.elements.error.textContent, /conectar ao servidor/);
  await app.load(initial);
  assert.equal(app.elements.start.disabled, false);
  assert.equal(app.elements.retry.hidden, true);
});

test("monitor stays disabled after request cleanup and subsequent refresh", async () => {
  const app = await harness(ready);
  assert.equal(app.elements.monitor.disabled, true);
  await app.load(ready);
  assert.equal(app.elements.monitor.disabled, true);
  assert.equal(app.elements.monitor.attrs["aria-disabled"], "true");
  assert.equal(app.elements.main.attrs["aria-busy"], "false");
});

test("revoking consent keeps the audit visible while hiding financial results", async () => {
  const app = await harness(ready);
  await app.load({...initial, audit: [{
    sequence: 1, event: "consent_revoked", time: "2026-10-21T12:00:00+00:00",
    label: "Leitura revogada e planos apagados.",
  }]});
  assert.equal(app.elements.workspace.hidden, true);
  assert.equal(app.elements["audit-panel"].hidden, false);
  assert.equal(app.elements.audit.children.length, 1);
  assert.match(app.elements.audit.children[0].children[1].textContent, /revogada/);
});

test("incomplete consented report offers recovery instead of an unhandled crash", async () => {
  const app = await harness(ready);
  await app.load({...ready, report: {status: "ready"}});
  assert.equal(app.elements.workspace.hidden, true);
  assert.equal(app.elements.retry.hidden, false);
  assert.match(app.elements.error.textContent, /análise ainda não está disponível/);
});

test("chart identifies the lowest balance in text and retains the daily table", async () => {
  const app = await harness(ready);
  const svg = app.elements["balance-chart"].children[0];
  assert.equal(svg.attrs.role, "img");
  assert.equal(svg.children.filter(e => e.attrs.class === "chart-low-dot").length, 1);
  assert.match(app.elements["chart-caption"].textContent, /13\/10 \(abaixo de zero\)/);
  assert.equal(app.elements.daily.children.length, 3);
  assert.equal(app.elements.explanations.children.length, 1);
  assert.equal(svg.children.some(e => String(e.attrs.points).includes("NaN")), false);
});

test("currency formatting is exact for integer cents and rejects unsafe values", async () => {
  const app = await harness();
  assert.equal(app.evaluate("money(0)"), "R$\u00a00,00");
  assert.equal(app.evaluate("money(-1)"), "−R$\u00a00,01");
  assert.equal(app.evaluate("money(9007199254740991)"), "R$\u00a090.071.992.547.409,91");
  assert.equal(app.evaluate("money(1.5)"), "Valor indisponível");
  assert.equal(app.evaluate("money(Number.MAX_SAFE_INTEGER + 1)"), "Valor indisponível");
  app.elements["text-size"].onclick();
  assert.equal(app.elements["text-size"].attrs["aria-pressed"], "true");
});

test("goals panel is hidden when state has no goals", async () => {
  const app = await harness(ready);
  assert.equal(app.elements["goals-panel"].hidden, true);
  assert.equal(app.elements["goals"].children.length, 0);
});

test("goals panel shows label and formatted amount after approval", async () => {
  const withGoal = {...ready, goals: [{label: "Celular", target_cents: 120000}]};
  const app = await harness(withGoal);
  assert.equal(app.elements["goals-panel"].hidden, false);
  assert.equal(app.elements["goals"].children.length, 1);
  const li = app.elements["goals"].children[0];
  assert.equal(li.children[0].textContent, "Celular");
  assert.match(li.children[1].textContent, /1\.200,00/);
});

test("goals panel persists on reload and clears after consent revoked", async () => {
  const withGoal = {...ready, goals: [{label: "Celular", target_cents: 120000}]};
  const app = await harness(withGoal);
  assert.equal(app.elements["goals-panel"].hidden, false);
  // Reload while session valid: goal remains visible
  await app.load(withGoal);
  assert.equal(app.elements["goals-panel"].hidden, false);
  assert.equal(app.elements["goals"].children.length, 1);
  // Revoke consent: server clears goals; panel must hide
  await app.load({...initial, goals: []});
  assert.equal(app.elements["goals-panel"].hidden, true);
  assert.equal(app.elements["goals"].children.length, 0);
});

test("goals panel is hidden without consent even if stale goals are present", async () => {
  // Server should never send goals without consent, but the UI must be defensive
  const stale = {...initial, goals: [{label: "Celular", target_cents: 120000}]};
  const app = await harness(stale);
  assert.equal(app.elements["goals-panel"].hidden, true);
  assert.equal(app.elements["goals"].children.length, 0);
});

test("goals panel clears when scenario changes", async () => {
  const withGoal = {...ready, goals: [{label: "Celular", target_cents: 120000}]};
  const app = await harness(withGoal);
  assert.equal(app.elements["goals-panel"].hidden, false);
  // Scenario switch resets goals to empty (server behaviour)
  await app.load({...ready, goals: []});
  assert.equal(app.elements["goals-panel"].hidden, true);
  assert.equal(app.elements["goals"].children.length, 0);
});

test("purchase section renders installment schedule table and out-of-horizon warning", async () => {
  const withPurchase = {
    ...ready,
    report: {
      ...ready.report,
      horizon: "2026-12-15",
      results: {
        ...ready.report.results,
        purchase: {
          available: true,
          label: "Celular",
          price_cents: 350000,
          installments: 3,
          first_installment_cents: 116667,
          cash_minimum_cents: -200000,
          cash_closing_cents: -200000,
          installment_minimum_cents: 33333,
          installment_projected_minimum_cents: -83334,
          installment_projected_closing_cents: -83334,
          out_of_horizon: 0,
          schedule: [
            {number: 1, date: "2026-10-07", amount_cents: 116667},
            {number: 2, date: "2026-11-07", amount_cents: 116667},
            {number: 3, date: "2026-12-07", amount_cents: 116666},
          ],
          assumption: "Primeira parcela em 2026-10-07; sem juros no exemplo. Todas as parcelas estão dentro do horizonte analisado.",
          recommendation: "Adiar e criar uma meta",
        },
      },
    },
  };
  const app = await harness(withPurchase);
  assert.equal(app.elements.special.hidden, false);
  // schedule table wrapper is appended
  const schedWrap = app.elements.special.children.find(c => c.attrs["role"] === "region" && c.attrs["aria-label"] === "Cronograma de parcelas projetadas");
  assert.ok(schedWrap, "Deve haver um wrapper de tabela com role=region para o cronograma");
  // table has 3 data rows
  const table = schedWrap.children[0];
  const tbody = table.children.find(c => c.tag === "tbody" || c.children);
  // Each of the 3 schedule entries becomes a <tr> inside tbody
  const allRows = (function collectRows(el) {
    const rows = [];
    if (el.tag === "tr") rows.push(el);
    (el.children || []).forEach(c => rows.push(...collectRows(c)));
    return rows;
  })(schedWrap);
  // 1 header row + 3 data rows = 4
  assert.equal(allRows.length, 4);
  // No out-of-horizon warning paragraph when out_of_horizon === 0
  const warnNode = app.elements.special.children.find(c => c.tag === "p" && c.textContent.includes("fora do horizonte"));
  assert.equal(warnNode, undefined);
});

test("purchase section shows out-of-horizon warning when installments exceed horizon", async () => {
  const withPartialPurchase = {
    ...ready,
    report: {
      ...ready.report,
      horizon: "2026-10-15",
      results: {
        ...ready.report.results,
        purchase: {
          available: true,
          label: "Celular",
          price_cents: 350000,
          installments: 5,
          first_installment_cents: 70000,
          cash_minimum_cents: -200000,
          cash_closing_cents: -200000,
          installment_minimum_cents: 80000,
          installment_projected_minimum_cents: 80000,
          installment_projected_closing_cents: 80000,
          out_of_horizon: 4,
          schedule: [
            {number: 1, date: "2026-10-07", amount_cents: 70000},
          ],
          assumption: "Primeira parcela em 2026-10-07; sem juros no exemplo. 4 parcela(s) fora do horizonte não foram incluídas no cálculo do menor saldo.",
          recommendation: "Comparar antes de decidir",
        },
      },
    },
  };
  const app = await harness(withPartialPurchase);
  assert.equal(app.elements.special.hidden, false);
  // Out-of-horizon warning paragraph exists
  const warnNode = app.elements.special.children.find(c => c.tag === "p" && c.textContent.includes("fora do horizonte"));
  assert.ok(warnNode, "Deve haver aviso sobre parcelas fora do horizonte");
  assert.match(warnNode.textContent, /4 parcela\(s\)/);
});
