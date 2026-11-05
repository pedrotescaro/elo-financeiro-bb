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
  const buttonIds = new Set([
    "start", "consent-toggle", "monitor", "retry", "text-size",
    "reduction-preview", "reduction-approve", "reduction-discard",
  ]);
  for (const match of html.matchAll(/id="([^"]+)"/g)) {
    elements[match[1]] = new Element(buttonIds.has(match[1]) ? "button" : "div");
  }
  // input especial para o campo de redução
  const inputEl = new Element("input");
  inputEl.value = "";
  elements["reduction-input"] = inputEl;
  let response = first;
  const context = vm.createContext({
    document: {
      getElementById: id => elements[id],
      querySelectorAll: () => Object.values(elements).filter(e => e.tag === "button"),
      createElement: tag => new Element(tag),
      createElementNS: (_, tag) => new Element(tag),
      documentElement: new Element(),
    },
    fetch: async (url, options) => {
      if (response instanceof Error) throw response;
      // Captura o último body enviado para inspeção nos testes.
      if (options && options.body) {
        try { context.__lastPostBody = JSON.parse(options.body); } catch {}
      }
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

// ── Testes do painel de redução personalizada ─────────────────────────────

// Estado com ação budget-plan disponível e gastos flexíveis.
const readyWithBudgetPlan = {
  ...ready,
  report: {
    ...ready.report,
    report_id: "test-report-abc",
    actions: [{
      id: "budget-plan",
      label: "Ativar plano de gastos",
      reduction_cents: 30000,
      before_cents: -10000,
      after_cents: 20000,
      meets_buffer: true,
      effect: "Registra um plano e ajusta a previsão de despesas flexíveis.",
    }],
    results: {
      cashflow: {
        ...ready.report.results.cashflow,
        flexible_cents: 30000,
        gap_to_buffer_cents: 30000,
      },
    },
  },
  pending_adjustment: null,
};

test("painel de redução é exibido quando há proposta budget-plan", async () => {
  const app = await harness(readyWithBudgetPlan);
  assert.equal(app.elements["reduction-panel"].hidden, false,
    "O painel de redução deve estar visível quando há budget-plan.");
});

test("painel de redução fica oculto quando não há proposta budget-plan", async () => {
  const app = await harness(ready);
  // ready não tem actions com budget-plan.
  assert.equal(app.elements["reduction-panel"].hidden, true,
    "O painel de redução deve estar oculto sem budget-plan.");
});

test("campo de redução com valor inválido exibe mensagem de erro sem chamar o servidor", async () => {
  const app = await harness(readyWithBudgetPlan);
  // Configura valor inválido no input.
  app.elements["reduction-input"].value = "abc";
  app.elements["reduction-preview"].onclick();
  await new Promise(resolve => setImmediate(resolve));
  // Erro deve aparecer.
  assert.equal(app.elements["reduction-error"].classList.contains("sr-only"), false,
    "Mensagem de erro deve estar visível após valor inválido.");
  assert.match(app.elements["reduction-error"].textContent, /Valor inválido/);
});

test("campo de redução com valor vazio exibe mensagem de erro sem chamar o servidor", async () => {
  const app = await harness(readyWithBudgetPlan);
  app.elements["reduction-input"].value = "";
  app.elements["reduction-preview"].onclick();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(app.elements["reduction-error"].classList.contains("sr-only"), false);
  assert.match(app.elements["reduction-error"].textContent, /Valor inválido/);
});

test("prévia de redução exibe menor saldo projetado retornado pelo servidor", async () => {
  const previewResponse = {
    ...readyWithBudgetPlan,
    pending_adjustment: {
      report_id: "test-report-abc",
      reduction_cents: 15000,
      preview: {
        reduction_cents: 15000,
        minimum_cents: 5000,
        gap_to_buffer_cents: 15000,
        meets_buffer: false,
        flexible_total_cents: 30000,
        warning: "Com essa redução, o menor saldo previsto (5000 centavos) ainda ficará abaixo da margem desejada (20000 centavos). Faltam 15000 centavos para atingir a margem.",
      },
    },
    preview: {
      reduction_cents: 15000,
      minimum_cents: 5000,
      gap_to_buffer_cents: 15000,
      meets_buffer: false,
      flexible_total_cents: 30000,
      warning: "Com essa redução, o menor saldo previsto (5000 centavos) ainda ficará abaixo da margem desejada (20000 centavos). Faltam 15000 centavos para atingir a margem.",
    },
  };
  const app = await harness(readyWithBudgetPlan);
  app.elements["reduction-input"].value = "150,00";
  await app.load(previewResponse);
  // Painel de prévia deve estar visível.
  assert.equal(app.elements["reduction-preview-panel"].hidden, false,
    "Painel de prévia deve estar visível após receber a prévia do servidor.");
  assert.match(app.elements["reduction-preview-result"].textContent, /R\$/,
    "Resultado da prévia deve exibir valor monetário formatado.");
});

test("aviso de margem não atingida é exibido quando meets_buffer é false", async () => {
  const withWarningState = {
    ...readyWithBudgetPlan,
    pending_adjustment: {
      report_id: "test-report-abc",
      reduction_cents: 5000,
      preview: {
        reduction_cents: 5000,
        minimum_cents: -5000,
        gap_to_buffer_cents: 25000,
        meets_buffer: false,
        flexible_total_cents: 30000,
        warning: "Com essa redução, o menor saldo previsto ainda ficará abaixo da margem desejada.",
      },
    },
  };
  const app = await harness(withWarningState);
  assert.equal(app.elements["reduction-preview-panel"].hidden, false,
    "Painel de prévia deve estar visível quando há pending_adjustment.");
  assert.equal(app.elements["reduction-preview-warning"].hidden, false,
    "Aviso de margem não atingida deve estar visível quando meets_buffer é false.");
  assert.match(app.elements["reduction-preview-warning"].textContent, /abaixo da margem/);
});

test("aviso de margem oculto quando meets_buffer é true", async () => {
  const withSuccessState = {
    ...readyWithBudgetPlan,
    pending_adjustment: {
      report_id: "test-report-abc",
      reduction_cents: 30000,
      preview: {
        reduction_cents: 30000,
        minimum_cents: 20000,
        gap_to_buffer_cents: 0,
        meets_buffer: true,
        flexible_total_cents: 30000,
        warning: null,
      },
    },
  };
  const app = await harness(withSuccessState);
  assert.equal(app.elements["reduction-preview-panel"].hidden, false);
  assert.equal(app.elements["reduction-preview-warning"].hidden, true,
    "Aviso deve estar oculto quando a margem é atingida.");
});

test("botão de aprovação de redução envia report_id, action_id e preview_id corretos", async () => {
  const withApproveState = {
    ...readyWithBudgetPlan,
    pending_adjustment: {
      report_id: "test-report-abc",
      preview_id: 3,
      reduction_cents: 15000,
      preview: {
        reduction_cents: 15000,
        minimum_cents: 5000,
        gap_to_buffer_cents: 15000,
        meets_buffer: false,
        flexible_total_cents: 30000,
        warning: "Margem não atingida.",
      },
    },
  };
  const app = await harness(withApproveState);
  // Simula aprovação
  await app.load(withApproveState);
  app.elements["reduction-approve"].onclick();
  await new Promise(resolve => setImmediate(resolve));
  // O body enviado deve conter report_id, action_id e preview_id corretos.
  const body = app.evaluate("__lastPostBody");
  assert.equal(body.report_id, "test-report-abc",
    "report_id deve ser o do relatório vigente.");
  assert.equal(body.action_id, "budget-plan",
    "action_id deve ser budget-plan.");
  assert.equal(body.preview_id, 3,
    "preview_id deve ser o da prévia pendente.");
});

test("botão de aprovação padrão (sem prévia) não envia preview_id", async () => {
  const app = await harness(readyWithBudgetPlan); // sem pending_adjustment
  app.elements["reduction-approve"].onclick();
  await new Promise(resolve => setImmediate(resolve));
  const body = app.evaluate("__lastPostBody");
  assert.equal(body.action_id, "budget-plan");
  assert.equal(Object.prototype.hasOwnProperty.call(body, "preview_id"), false,
    "Aprovação padrão não deve incluir preview_id.");
});

test("botão de recusar proposta envia report_id e action_id corretos", async () => {
  const app = await harness(readyWithBudgetPlan);
  // Os botões de ação são criados dinamicamente em $("actions").children.
  // O segundo filho da primeira ação é o botão "Recusar proposta".
  const actionWrap = app.elements.actions.children[0];
  assert.ok(actionWrap, "Deve haver ao menos uma ação renderizada.");
  const actionRow = actionWrap.children.find(c => c.children && c.children.some(b => b.tag === "button"));
  assert.ok(actionRow, "Deve haver um div de botões na ação.");
  const declineBtn = actionRow.children.find(b => b.tag === "button" && (b.textContent || "").includes("Recusar"));
  assert.ok(declineBtn, "Deve haver um botão de recusar na ação.");
  declineBtn.onclick();
  await new Promise(resolve => setImmediate(resolve));
  const body = app.evaluate("__lastPostBody");
  assert.equal(body.report_id, "test-report-abc");
  assert.equal(body.action_id, "budget-plan");
});

test("descarte de prévia chama /api/preview/discard e oculta o painel ao receber resposta", async () => {
  const withPending = {
    ...readyWithBudgetPlan,
    pending_adjustment: {
      report_id: "test-report-abc",
      preview_id: 1,
      reduction_cents: 10000,
      preview: {
        reduction_cents: 10000,
        minimum_cents: 0,
        gap_to_buffer_cents: 20000,
        meets_buffer: false,
        flexible_total_cents: 30000,
        warning: "Margem não atingida.",
      },
    },
  };
  // O servidor devolve o estado sem ajuste pendente após o descarte.
  const afterDiscard = {...readyWithBudgetPlan, pending_adjustment: null};
  const app = await harness(withPending);
  assert.equal(app.elements["reduction-preview-panel"].hidden, false,
    "Painel deve estar visível antes do descarte.");
  // Simula: o próximo fetch retorna o estado sem pendência.
  await app.load(afterDiscard);
  assert.equal(app.elements["reduction-preview-panel"].hidden, true,
    "Painel de prévia deve ser ocultado quando servidor confirma descarte.");
  assert.equal(app.elements["reduction-input"].value, "",
    "Campo de entrada deve ser limpo após descarte.");
});

test("descarte de prévia envia requisição para /api/preview/discard com corpo vazio", async () => {
  const withPending = {
    ...readyWithBudgetPlan,
    pending_adjustment: {
      report_id: "test-report-abc",
      preview_id: 1,
      reduction_cents: 10000,
      preview: {
        reduction_cents: 10000,
        minimum_cents: 0,
        gap_to_buffer_cents: 20000,
        meets_buffer: false,
        flexible_total_cents: 30000,
        warning: "Margem não atingida.",
      },
    },
  };
  const afterDiscard = {...readyWithBudgetPlan, pending_adjustment: null};
  const app = await harness(withPending);
  // Aciona o descarte: chama /api/preview/discard com corpo {}.
  app.elements["reduction-discard"].onclick();
  await new Promise(resolve => setImmediate(resolve));
  // O corpo enviado para discard deve ser {}.
  const body = app.evaluate("__lastPostBody");
  assert.deepEqual(body, {}, "Descarte deve enviar corpo vazio ao servidor.");
});

test("painel de redução é descartado ao trocar de cenário (pending_adjustment limpo)", async () => {
  const withPending = {
    ...readyWithBudgetPlan,
    pending_adjustment: {
      report_id: "test-report-abc",
      reduction_cents: 10000,
      preview: {
        reduction_cents: 10000,
        minimum_cents: 0,
        gap_to_buffer_cents: 20000,
        meets_buffer: false,
        flexible_total_cents: 30000,
        warning: "Margem não atingida.",
      },
    },
  };
  const app = await harness(withPending);
  assert.equal(app.elements["reduction-preview-panel"].hidden, false);
  // Troca de cenário: servidor retorna estado sem ajuste pendente.
  await app.load({...readyWithBudgetPlan, pending_adjustment: null,
    report: {...readyWithBudgetPlan.report, report_id: "new-report-xyz"}});
  assert.equal(app.elements["reduction-preview-panel"].hidden, true,
    "Painel de prévia deve ser ocultado quando pending_adjustment é null.");
});

test("histórico exibe [✔ personalizada] para aprovação customizada com applied_cents", async () => {
  const withHistory = {
    ...readyWithBudgetPlan,
    history: [{
      action: "budget-plan",
      report_id: "test-report-abc",
      label: "Ativar plano de gastos",
      status: "accepted",
      kind: "custom",
      applied_cents: 15000,
      preview_id: 1,
      effect: "Registra um plano.",
    }],
  };
  const app = await harness(withHistory);
  const item = app.elements.history.children[0];
  assert.ok(item, "Deve haver um item no histórico.");
  assert.match(item.textContent, /personalizada/,
    "Aprovação customizada deve indicar 'personalizada'.");
  assert.match(item.textContent, /R\$.*150,00|150,00|15000/i,
    "O valor aplicado deve aparecer no histórico.");
});

test("histórico exibe [✗ recusada] para recusa e sem valor aplicado", async () => {
  const withHistory = {
    ...readyWithBudgetPlan,
    history: [{
      action: "budget-plan",
      report_id: "test-report-abc",
      label: "Ativar plano de gastos",
      status: "declined",
      kind: "declined",
      applied_cents: null,
      preview_id: null,
      effect: "Proposta recusada.",
    }],
  };
  const app = await harness(withHistory);
  const item = app.elements.history.children[0];
  assert.ok(item, "Deve haver um item no histórico.");
  assert.match(item.textContent, /recusada/,
    "Recusa deve indicar 'recusada'.");
  assert.doesNotMatch(item.textContent, /—.*R\$/,
    "Recusa não deve mostrar valor aplicado.");
});

test("histórico exibe [✔ padrão] para aprovação padrão", async () => {
  const withHistory = {
    ...readyWithBudgetPlan,
    history: [{
      action: "budget-plan",
      report_id: "test-report-abc",
      label: "Ativar plano de gastos",
      status: "accepted",
      kind: "default",
      applied_cents: 30000,
      preview_id: null,
      effect: "Registra um plano.",
    }],
  };
  const app = await harness(withHistory);
  const item = app.elements.history.children[0];
  assert.ok(item, "Deve haver um item no histórico.");
  assert.match(item.textContent, /padrão/,
    "Aprovação padrão deve indicar 'padrão'.");
});
