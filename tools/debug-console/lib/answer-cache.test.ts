import assert from "node:assert/strict";
import test from "node:test";

import {
  cacheQuestionsAreCompatible,
  normalizeQuestion,
  questionSimilarity,
} from "./answer-cache.ts";

test("normalizes punctuation and spacing", () => {
  assert.equal(normalizeQuestion(" 固定资产出售，计入什么科目？ "), "固定资产出售计入什么科目");
});

test("accepts a close paraphrase above 80 percent", () => {
  const score = questionSimilarity("固定资产出售计入什么科目？", "固定资产出售应计入什么科目");
  assert.ok(score >= 0.8, String(score));
  assert.equal(
    cacheQuestionsAreCompatible("固定资产出售计入什么科目？", "固定资产出售应计入什么科目"),
    true,
  );
});

test("rejects accounting contrasts even when wording is close", () => {
  assert.equal(cacheQuestionsAreCompatible("固定资产出售如何列报", "固定资产报废如何列报"), false);
  assert.equal(cacheQuestionsAreCompatible("应确认收入吗", "不应确认收入吗"), false);
  assert.equal(cacheQuestionsAreCompatible("金额为100万元如何处理", "金额为200万元如何处理"), false);
});
