import { execFile } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { promisify } from "node:util";

import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const execFileAsync = promisify(execFile);

export async function GET() {
  const root = path.resolve(process.cwd(), "..", "..");
  const script = path.join(root, "tools", "wecom-bot", "history_report.py");
  const dataDir = path.join(root, "tools", "wecom-bot", "data");
  const bundledPython =
    process.platform === "win32"
      ? path.join(root, ".venv", "Scripts", "python.exe")
      : path.join(root, ".venv", "bin", "python");
  const python = fs.existsSync(bundledPython) ? bundledPython : process.env.PYTHON_BIN || "python";

  try {
    const { stdout } = await execFileAsync(
      python,
      [script, "--data-dir", dataDir, "--limit", "500"],
      { cwd: root, encoding: "utf8", timeout: 15_000, maxBuffer: 10 * 1024 * 1024 },
    );
    return NextResponse.json(JSON.parse(stdout));
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : String(error), records: [] },
      { status: 500 },
    );
  }
}

