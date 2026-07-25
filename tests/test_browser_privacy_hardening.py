from __future__ import annotations

import subprocess
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class BrowserPrivacyHardeningTests(unittest.TestCase):
    def test_phase3_evaluator_panel_renders_blocked_status_and_no_mutation_flags(self) -> None:
        script = textwrap.dedent(
            """
            const fs = require("node:fs");
            const vm = require("node:vm");
            const appJs = fs.readFileSync("frontend/app.js", "utf8");

            class Element {
              constructor(selector) {
                this.selector = selector;
                this.value = selector === "#dependents" ? "0" : "single";
                this.checked = false;
                this.textContent = "";
                this.innerHTML = "";
                this.listeners = {};
              }
              addEventListener(name, fn) {
                this.listeners[name] = fn;
              }
            }

            const elements = {};
            for (const selector of [
              "#analysis",
              "#sources",
              "#candidate-status",
              "#promotion-audit",
              "#promotion-evaluator",
              "#ledger",
              "#refresh",
              "#summarize",
              "#filing-unit",
              "#dependents",
              "#itemizes",
              "#clear-local",
              "#local-result"
            ]) {
              elements[selector] = new Element(selector);
            }

            const context = {
              console,
              setTimeout,
              Promise,
              document: {
                querySelector(selector) {
                  if (!elements[selector]) {
                    elements[selector] = new Element(selector);
                  }
                  return elements[selector];
                },
                querySelectorAll(selector) {
                  if (selector === "[data-local-only='true']") {
                    return [elements["#filing-unit"], elements["#dependents"], elements["#itemizes"]];
                  }
                  return [];
                }
              },
              fetch: async (url) => ({
                ok: true,
                status: 200,
                json: async () => {
                  if (url.endsWith("/analysis-units/tcja-2017-representative-provisions")) {
                    return { claims: [], expected_outputs: { plain_language_summary: "summary" }, title: "title" };
                  }
                  if (url.endsWith("/sources")) {
                    return { sources: [] };
                  }
                  if (url.endsWith("/ai-decision-ledger")) {
                    return { entries: [] };
                  }
                  if (url.endsWith("/reports/tcja-2017-representative-provisions")) {
                    return { report_id: "report" };
                  }
                  if (url.endsWith("/candidates/status")) {
                    return { candidates: [] };
                  }
                  if (url.endsWith("/candidates/promotion-audit")) {
                    return { candidate_summaries: [] };
                  }
                  if (url.endsWith("/candidates/promotion-evaluator")) {
                    return {
                      status: "blocked",
                      fixture_id: "phase3_promotion_evaluator_contract_examples_v1",
                      evaluation_count: 1,
                      first_failing_gates: ["schema", "promotion_disabled"],
                      promotion_execution_allowed: false,
                      ledger_appended: false,
                      public_report_changed: false,
                      live_provider_called: false,
                      household_financial_data_storage_allowed: false,
                      evaluations: [
                        {
                          request_id: "invalid_request_missing_candidate_ref",
                          status: "blocked",
                          first_failing_gate: "schema",
                          candidate_analysis_unit_id: null,
                          blockers: [
                            { code: "schema.invalid_request" },
                            { code: "promotion_disabled.phase3_hard_stop" }
                          ]
                        }
                      ]
                    };
                  }
                  return {};
                }
              })
            };

            async function main() {
              vm.createContext(context);
              vm.runInContext(appJs, context);
              await new Promise((resolve) => setImmediate(resolve));

              const panel = elements["#promotion-evaluator"].innerHTML;
              for (const expected of [
                "Status</dt><dd>blocked",
                "First failing gates</dt><dd>schema, promotion_disabled",
                "Promotion execution allowed</dt><dd>no",
                "Ledger appended</dt><dd>no",
                "Public report changed</dt><dd>no",
                "Live provider called</dt><dd>no",
                "Household financial data storage allowed</dt><dd>no",
                "schema.invalid_request",
                "promotion_disabled.phase3_hard_stop"
              ]) {
                if (!panel.includes(expected)) {
                  throw new Error(`missing evaluator panel text: ${expected}`);
                }
              }
            }

            main().catch((error) => {
              console.error(error);
              process.exit(1);
            });
            """
        )
        result = subprocess.run(
            ["node", "-e", script],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_local_privacy_controls_do_not_trigger_network_egress(self) -> None:
        script = textwrap.dedent(
            """
            const fs = require("node:fs");
            const vm = require("node:vm");
            const appJs = fs.readFileSync("frontend/app.js", "utf8");

            class Element {
              constructor(selector) {
                this.selector = selector;
                this.value = selector === "#dependents" ? "0" : "single";
                this.checked = false;
                this.textContent = "";
                this.innerHTML = "";
                this.listeners = {};
              }
              addEventListener(name, fn) {
                this.listeners[name] = fn;
              }
              trigger(name) {
                if (this.listeners[name]) {
                  this.listeners[name]({ target: this });
                }
              }
            }

            const elements = {};
            for (const selector of [
              "#analysis",
              "#sources",
              "#candidate-status",
              "#promotion-audit",
              "#promotion-evaluator",
              "#ledger",
              "#refresh",
              "#summarize",
              "#filing-unit",
              "#dependents",
              "#itemizes",
              "#clear-local",
              "#local-result"
            ]) {
              elements[selector] = new Element(selector);
            }

            const calls = [];
            const context = {
              console,
              setTimeout,
              Promise,
              document: {
                querySelector(selector) {
                  if (!elements[selector]) {
                    elements[selector] = new Element(selector);
                  }
                  return elements[selector];
                },
                querySelectorAll(selector) {
                  if (selector === "[data-local-only='true']") {
                    return [elements["#filing-unit"], elements["#dependents"], elements["#itemizes"]];
                  }
                  return [];
                }
              },
              fetch: async (url, options = {}) => {
                calls.push({ url, options });
                return {
                  ok: true,
                  status: 200,
                  json: async () => {
                    if (url.endsWith("/analysis-units/tcja-2017-representative-provisions")) {
                      return { claims: [], expected_outputs: { plain_language_summary: "summary" }, title: "title" };
                    }
                    if (url.endsWith("/sources")) {
                      return { sources: [] };
                    }
                    if (url.endsWith("/ai-decision-ledger")) {
                      return { entries: [] };
                    }
                    if (url.endsWith("/reports/tcja-2017-representative-provisions")) {
                      return { report_id: "report" };
                    }
                    if (url.endsWith("/candidates/status")) {
                      return {
                        candidates: [
                          {
                            title: "candidate",
                            publication_state: "draft",
                            promotable: false,
                            source_record_ids: ["source"],
                            candidate_provision_ids: ["candidate_provision"],
                            promotion_blockers: [{ gate: "promotion_disabled", reason: "disabled" }],
                            review_status: "review_required",
                            review_findings: [{ severity: "blocking", message: "review required" }],
                            review_promotion_recommendation: "blocked"
                          }
                        ]
                      };
                    }
                    if (url.endsWith("/candidates/promotion-audit")) {
                      return {
                        candidate_ids_match: true,
                        public_report_includes_candidates: false,
                        source_promotion_state: "blocked",
                        source_registry_update_allowed: false,
                        candidate_summaries: [
                          {
                            candidate_analysis_unit_id: "candidate",
                            publication_state: "draft",
                            promotion_decision: "blocked",
                            blocker_gates: ["promotion_disabled"],
                            blockers_match: true,
                            source_refs_match: true,
                            public_report_includes_candidate: false
                          }
                        ]
                      };
                    }
                    if (url.endsWith("/candidates/promotion-evaluator")) {
                      return {
                        status: "blocked",
                        fixture_id: "fixture",
                        evaluation_count: 1,
                        first_failing_gates: ["promotion_disabled"],
                        promotion_execution_allowed: false,
                        ledger_appended: false,
                        public_report_changed: false,
                        live_provider_called: false,
                        household_financial_data_storage_allowed: false,
                        evaluations: [
                          {
                            request_id: "request",
                            status: "blocked",
                            first_failing_gate: "promotion_disabled",
                            candidate_analysis_unit_id: "candidate",
                            blockers: [{ code: "promotion_disabled.phase3_hard_stop" }]
                          }
                        ]
                      };
                    }
                    return {};
                  }
                };
              }
            };

            async function main() {
              vm.createContext(context);
              vm.runInContext(appJs, context);
              await new Promise((resolve) => setImmediate(resolve));
              const initialCallCount = calls.length;
              if (initialCallCount !== 7) {
                throw new Error(`expected seven initial allowlisted fetches, got ${initialCallCount}`);
              }

              calls.length = 0;
              elements["#filing-unit"].value = "sentinel-local-only";
              elements["#dependents"].value = "9";
              elements["#itemizes"].checked = true;
              elements["#filing-unit"].trigger("change");
              elements["#dependents"].trigger("input");
              elements["#itemizes"].trigger("change");
              elements["#clear-local"].trigger("click");
              await new Promise((resolve) => setImmediate(resolve));

              if (calls.length !== 0) {
                throw new Error(`local-only controls triggered network calls: ${JSON.stringify(calls)}`);
              }
              if (!elements["#local-result"].textContent.includes("No household financial values are collected or sent")) {
                throw new Error("local privacy result did not preserve no-transmission message");
              }
            }

            main().catch((error) => {
              console.error(error);
              process.exit(1);
            });
            """
        )
        result = subprocess.run(
            ["node", "-e", script],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
