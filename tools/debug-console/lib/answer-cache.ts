import fs from "node:fs";
import path from "node:path";

export interface AnswerCacheContext {
  provider: string;
  model: string;
  mode: string;
  workspace: string;
}

interface AnswerCacheEntry extends AnswerCacheContext {
  question: string;
  normalized_question: string;
  answer: string;
  knowledge_version: string;
  created_at: string;
}

export interface AnswerCacheHit {
  answer: string;
  question: string;
  similarity: number;
  createdAt: string;
}

const CACHE_DIR = path.resolve(process.cwd(), "data");
const CACHE_FILE = path.join(CACHE_DIR, "answer-cache.json");
const MAX_ENTRIES = 500;
const MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000;
const SIMILARITY_THRESHOLD = 0.8;

const CONTRAST_TERMS = [
  "出售",
  "报废",
  "毁损",
  "持有待售",
  "营业外收入",
  "营业外支出",
  "资产处置收益",
  "总额法",
  "净额法",
  "主要责任人",
  "代理人",
  "确认",
  "终止确认",
];
const NEGATION_TERMS = ["不", "非", "无", "未", "否", "不得", "不能", "无需", "不应"];

export function normalizeQuestion(value: string): string {
  return value
    .normalize("NFKC")
    .toLowerCase()
    .replace(/[\s，。？！、；：,.?!;:'"“”‘’（）()【】\[\]{}<>《》-]/g, "");
}

function levenshtein(left: string, right: string): number {
  if (left === right) return 0;
  if (!left.length) return right.length;
  if (!right.length) return left.length;
  let previous = Array.from({ length: right.length + 1 }, (_, index) => index);
  for (let i = 1; i <= left.length; i += 1) {
    const current = [i];
    for (let j = 1; j <= right.length; j += 1) {
      current[j] = Math.min(
        current[j - 1] + 1,
        previous[j] + 1,
        previous[j - 1] + (left[i - 1] === right[j - 1] ? 0 : 1),
      );
    }
    previous = current;
  }
  return previous[right.length];
}

export function questionSimilarity(left: string, right: string): number {
  const a = normalizeQuestion(left).slice(0, 500);
  const b = normalizeQuestion(right).slice(0, 500);
  const longest = Math.max(a.length, b.length);
  if (!longest) return 1;
  return 1 - levenshtein(a, b) / longest;
}

function signature(question: string): string {
  const normalized = normalizeQuestion(question);
  const numbers = normalized.match(/\d+(?:\.\d+)?%?/g) ?? [];
  const contrasts = CONTRAST_TERMS.filter((term) => normalized.includes(term));
  const negations = NEGATION_TERMS.filter((term) => normalized.includes(term));
  return JSON.stringify({ numbers: [...new Set(numbers)].sort(), contrasts, negations });
}

export function cacheQuestionsAreCompatible(left: string, right: string): boolean {
  return signature(left) === signature(right);
}

function gitVersion(): string {
  try {
    const root = path.resolve(process.cwd(), "..", "..");
    const gitDir = path.join(root, ".git");
    const head = fs.readFileSync(path.join(gitDir, "HEAD"), "utf8").trim();
    if (!head.startsWith("ref: ")) return head;
    return fs.readFileSync(path.join(gitDir, head.slice(5)), "utf8").trim();
  } catch {
    return "unknown";
  }
}

function readEntries(): AnswerCacheEntry[] {
  try {
    const parsed = JSON.parse(fs.readFileSync(CACHE_FILE, "utf8"));
    return Array.isArray(parsed) ? (parsed as AnswerCacheEntry[]) : [];
  } catch {
    return [];
  }
}

function sameContext(entry: AnswerCacheEntry, context: AnswerCacheContext): boolean {
  return (
    entry.provider === context.provider &&
    entry.model === context.model &&
    entry.mode === context.mode &&
    entry.workspace === context.workspace
  );
}

export function findCachedAnswer(
  question: string,
  context: AnswerCacheContext,
): AnswerCacheHit | null {
  const now = Date.now();
  const version = gitVersion();
  let best: AnswerCacheHit | null = null;
  for (const entry of readEntries()) {
    if (!sameContext(entry, context) || entry.knowledge_version !== version) continue;
    if (now - Date.parse(entry.created_at) > MAX_AGE_MS) continue;
    if (!cacheQuestionsAreCompatible(question, entry.question)) continue;
    const similarity = questionSimilarity(question, entry.question);
    if (similarity < SIMILARITY_THRESHOLD || (best && similarity <= best.similarity)) continue;
    best = {
      answer: entry.answer,
      question: entry.question,
      similarity,
      createdAt: entry.created_at,
    };
  }
  return best;
}

export function saveCachedAnswer(
  question: string,
  answer: string,
  context: AnswerCacheContext,
): void {
  if (!answer.includes("【ANSWER】")) return;
  fs.mkdirSync(CACHE_DIR, { recursive: true });
  const version = gitVersion();
  const entries = readEntries().filter(
    (entry) =>
      !(
        sameContext(entry, context) &&
        entry.knowledge_version === version &&
        entry.normalized_question === normalizeQuestion(question)
      ),
  );
  entries.push({
    ...context,
    question,
    normalized_question: normalizeQuestion(question),
    answer,
    knowledge_version: version,
    created_at: new Date().toISOString(),
  });
  const recent = entries.slice(-MAX_ENTRIES);
  const temporary = `${CACHE_FILE}.tmp`;
  fs.writeFileSync(temporary, JSON.stringify(recent, null, 2), "utf8");
  fs.renameSync(temporary, CACHE_FILE);
}

