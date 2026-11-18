import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
// biome-ignore lint/correctness/noUndeclaredDependencies: pi built-in extension import, provided by the host
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

// Capture extension: runs `pyvista-js capture-api-example` so the agent can
// capture a pyvista-js API documentation page after running its embedded
// "Try it with JupyterLite" example, and read the detected problems. Requires
// the playwright browsers (`uv run playwright install chromium`); issue
// reporting additionally needs the gh CLI and GH_TOKEN.

interface CaptureRun {
  ok: boolean;
  stdout: string;
  stderr: string;
  problems: string[];
}

/** Run the capture CLI and return its output plus the parsed problem report. */
function runCapture(cwd: string, url: string, output: string, openIssue: boolean): CaptureRun {
  const args = ["run", "pyvista-js", "capture-api-example", url, "--output", output];
  if (openIssue) {
    args.push("--open-issue");
  }
  const result = spawnSync("uv", args, { cwd, encoding: "utf8" });
  const problemsFile = path.join(cwd, output, "problems.json");
  let problems: string[] = [];
  if (fs.existsSync(problemsFile)) {
    const parsed = JSON.parse(fs.readFileSync(problemsFile, "utf8")) as {
      problems: string[];
    };
    ({ problems } = parsed);
  }
  return {
    ok: result.status === 0,
    stdout: result.stdout ?? "",
    stderr: result.stderr ?? "",
    problems,
  };
}

// biome-ignore lint/style/noDefaultExport: pi extensions are loaded through a default export
export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "capture_api_example",
    label: "pyvista-js: Capture API Example",
    description:
      "Capture a pyvista-js API documentation page after running its embedded 'Try it with JupyterLite' example. Writes a full-page screenshot and a problems.json report; with open_issue, files a [Bug]: issue via the gh CLI when problems are detected.",
    parameters: Type.Object({
      url: Type.String({
        description: "API documentation page URL to capture",
      }),
      output: Type.Optional(
        Type.String({
          description: "Directory for capture.png and problems.json (default: capture-artifacts)",
        }),
      ),
      openIssue: Type.Optional(
        Type.Boolean({
          description:
            "Open a bug-report issue with the gh CLI when problems are detected (default: false)",
        }),
      ),
    }),
    // biome-ignore lint/suspicious/useAwait: the tool interface is asynchronous; the capture itself is a synchronous CLI call
    async execute(_toolCallId, params) {
      const cwd = process.cwd();
      const output = params.output ?? "capture-artifacts";
      const run = runCapture(cwd, params.url, output, params.openIssue ?? false);
      let summary: string;
      if (run.ok) {
        summary = "Capture finished cleanly.";
      } else {
        summary = "Capture detected problems.";
      }
      const text = [
        summary,
        `Problems: ${JSON.stringify(run.problems)}`,
        `Screenshot: ${path.join(cwd, output, "capture.png")}`,
      ]
        .filter(Boolean)
        .join("\n");
      return { content: [{ type: "text", text }], details: {} };
    },
  });
}
