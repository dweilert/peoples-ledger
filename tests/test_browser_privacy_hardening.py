from __future__ import annotations

import subprocess
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class BrowserPrivacyHardeningTests(unittest.TestCase):
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
              if (initialCallCount !== 5) {
                throw new Error(`expected five initial allowlisted fetches, got ${initialCallCount}`);
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
