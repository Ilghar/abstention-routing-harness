// Port of policy.decide, costpolicy.decide_cost/calibrate and metrics.evaluate
// from Ilghar/abstention-routing-harness@62eb8ff. Verified against the Python in verify/.
(function (g) {
  var ROUTES = ["conversation", "spreadsheet"]; // sorted, as Python min(sorted(ROUTES))
  var PERMITTED = { synthetic: 1, "approved-existing-text": 1 };
  var ID_RX = /^[A-Z0-9_-]{1,32}$/;
  var COSTS = { error_cost: { spreadsheet: 1.0, conversation: 1.0 }, abstain_cost: 0.3 };
  var GRID = []; for (var i = 0; i <= 20; i++) GRID.push(Math.round(i / 20 * 100) / 100);
  function visible(t) { return /[^\p{Z}\p{C}]/u.test(t); }
  function h(c, code) { return { case_id: c.id, route: "human", abstained: true, reason_code: code }; }
  function decide(c) {
    if (!c || typeof c !== "object") return h({}, "TEXT_INVALID");
    if (typeof c.id !== "string" || !ID_RX.test(c.id)) return h(c, "CASE_INVALID");
    var t = c.text;
    if (typeof t !== "string" || t.length > 2000 || !visible(t)) return h(c, "TEXT_INVALID");
    if (c.scope_verified !== true) return h(c, "SCOPE_UNVERIFIED");
    if (!PERMITTED[c.fixture_kind]) return h(c, "INPUT_NOT_PERMITTED");
    var u = c.requests_used;
    if (typeof u !== "number" || !Number.isInteger(u) || u < 0) return h(c, "BUDGET_INVALID");
    if (u > 1) return h(c, "BUDGET_EXCEEDED");
    var p = c.proposals;
    if (!Array.isArray(p) || !p.length) return h(c, "NO_PROPOSAL");
    if (p.length > 8) return h(c, "PROPOSAL_MALFORMED");
    var rs = {};
    for (var i = 0; i < p.length; i++) {
      var r = p[i] && p[i].route;
      if (r === "unknown") return h(c, "PROPOSAL_ABSTAINED");
      if (ROUTES.indexOf(r) < 0) return h(c, "PROPOSAL_MALFORMED");
      rs[r] = 1;
    }
    if (Object.keys(rs).length > 1) return h(c, "PROPOSALS_CONFLICT");
    return { case_id: c.id, route: Object.keys(rs)[0], abstained: false, reason_code: "ADMITTED_ADVISORY" };
  }
  function support(p) {
    var tot = 0, per = { spreadsheet: 0, conversation: 0 };
    for (var i = 0; i < p.length; i++) {
      var c = p[i].confidence === undefined ? 1.0 : p[i].confidence;
      if (typeof c !== "number" || !isFinite(c) || c < 0 || c > 1) return null;
      per[p[i].route] += c; tot += 1;
    }
    var s = {}; ROUTES.forEach(function (r) { s[r] = tot ? per[r] / tot : 0; }); return s;
  }
  function decideCost(c, t) {
    var base = decide(c);
    if (base.route === "human" && base.reason_code !== "PROPOSALS_CONFLICT") return Object.assign(base, { support: null, expected_cost: COSTS.abstain_cost });
    var s = support(c.proposals);
    if (!s) return Object.assign(base, { route: "human", abstained: true, reason_code: "CONFIDENCE_INVALID", support: null });
    var exp = {}; ROUTES.forEach(function (r) { exp[r] = (1 - s[r]) * COSTS.error_cost[r]; });
    var best = ROUTES.reduce(function (a, r) { return exp[r] < exp[a] ? r : a; });
    var code, route;
    if (s[best] < t) { code = "SUPPORT_BELOW_THRESHOLD"; route = "human"; }
    else if (exp[best] >= COSTS.abstain_cost) { code = "RISK_ABOVE_ABSTAIN_COST"; route = "human"; }
    else { code = "ADMITTED_COST"; route = best; }
    return { case_id: c.id, route: route, abstained: route === "human", reason_code: code, best: best, support: s, expected_cost: exp[best] };
  }
  function r6(x) { return Math.round(x * 1e6) / 1e6; }
  function frac(n, d) { return d === 0 ? null : r6(n / d); }
  function evaluate(cases, decs) {
    var exp = {}; cases.forEach(function (c) { exp[c.id] = c.expected_route; });
    var adm = decs.filter(function (d) { return !d.abstained; });
    var correct = adm.filter(function (d) { return exp[d.case_id] === d.route; }).length;
    var hum = cases.filter(function (c) { return c.expected_route === "human"; }).length;
    var fa = adm.filter(function (d) { return exp[d.case_id] === "human"; }).length;
    return { coverage: { admitted: adm.length, denominator: cases.length, value: frac(adm.length, cases.length) },
      selective_accuracy: { correct: correct, denominator: adm.length, value: frac(correct, adm.length) },
      false_acceptance: { count: fa, denominator: hum, value: frac(fa, hum) } };
  }
  function realised(route, er) { if (route === "human") return er === "human" ? 0 : COSTS.abstain_cost; return route === er ? 0 : COSTS.error_cost[route]; }
  function calibrate(cases) {
    var rows = GRID.map(function (t) { return { min_support: t, total_cost: r6(cases.reduce(function (a, c) { return a + realised(decideCost(c, t).route, c.expected_route); }, 0)) }; });
    var best = rows.reduce(function (a, r) { return (r.total_cost < a.total_cost || (r.total_cost === a.total_cost && r.min_support > a.min_support)) ? r : a; });
    return { best_min_support: best.min_support, best_total_cost: best.total_cost, sweep: rows };
  }
  g.Engine = { decide: decide, decideCost: decideCost, evaluate: evaluate, calibrate: calibrate, GRID: GRID, COSTS: COSTS };
  if (typeof module !== "undefined") module.exports = g.Engine;
})(typeof window !== "undefined" ? window : globalThis);
