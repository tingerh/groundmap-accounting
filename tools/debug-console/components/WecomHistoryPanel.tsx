"use client";

import { useEffect, useMemo, useState } from "react";

import { useT } from "@/lib/i18n-client";

interface HistoryRecord {
  id: number;
  database: string;
  user_key: string;
  question: string;
  answer: string;
  references: string[];
  provider: string;
  workspace: string;
  input_tokens: number | null;
  output_tokens: number | null;
  status: string;
  error: string | null;
  duration_ms: number;
  created_at: string;
}

export function WecomHistoryPanel({ onClose }: { onClose: () => void }) {
  const t = useT();
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [database, setDatabase] = useState("all");
  const [status, setStatus] = useState("all");
  const [user, setUser] = useState("all");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<HistoryRecord | null>(null);

  const load = () => {
    setLoading(true);
    setError("");
    fetch("/api/wecom-history", { cache: "no-store" })
      .then(async (response) => {
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
        setRecords(Array.isArray(data.records) ? data.records : []);
      })
      .catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const databases = useMemo(() => [...new Set(records.map((item) => item.database))], [records]);
  const users = useMemo(() => [...new Set(records.map((item) => item.user_key))], [records]);
  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return records.filter(
      (item) =>
        (database === "all" || item.database === database) &&
        (status === "all" || item.status === status) &&
        (user === "all" || item.user_key === user) &&
        (!needle || item.question.toLowerCase().includes(needle) || item.answer.toLowerCase().includes(needle)),
    );
  }, [records, database, status, user, query]);

  const successful = filtered.filter((item) => item.status === "success").length;
  const avgSeconds = filtered.length
    ? filtered.reduce((sum, item) => sum + item.duration_ms, 0) / filtered.length / 1000
    : 0;

  return (
    <section className="flex h-full min-h-0 flex-col bg-[var(--ink)]">
      <div className="flex flex-wrap items-center gap-3 border-b border-[var(--line)] px-6 py-4">
        <div>
          <div className="k-eyebrow text-[var(--amber)]">{t("wecom.eyebrow")}</div>
          <h2 className="k-display mt-1 text-2xl text-[var(--paper)]">{t("wecom.title")}</h2>
        </div>
        <div className="ml-auto flex gap-2">
          <button className="k-btn" onClick={load}>{t("wecom.refresh")}</button>
          <button className="k-btn" onClick={onClose}>{t("wecom.close")}</button>
        </div>
      </div>

      <div className="grid grid-cols-2 border-b border-[var(--line)] md:grid-cols-4">
        {[
          [t("wecom.total"), filtered.length],
          [t("wecom.success"), successful],
          [t("wecom.failed"), filtered.length - successful],
          [t("wecom.avg"), `${avgSeconds.toFixed(1)}s`],
        ].map(([label, value]) => (
          <div key={String(label)} className="border-r border-[var(--line)] px-5 py-3 last:border-r-0">
            <div className="k-eyebrow">{label}</div>
            <div className="mt-1 font-mono text-xl text-[var(--paper)]">{value}</div>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-3 border-b border-[var(--line)] px-6 py-3">
        <select className="k-input" value={database} onChange={(event) => setDatabase(event.target.value)}>
          <option value="all">{t("wecom.all_enterprises")}</option>
          {databases.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
        <select className="k-input" value={user} onChange={(event) => setUser(event.target.value)}>
          <option value="all">{t("wecom.all_users")}</option>
          {users.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
        <select className="k-input" value={status} onChange={(event) => setStatus(event.target.value)}>
          <option value="all">{t("wecom.all_statuses")}</option>
          <option value="success">{t("wecom.success")}</option>
          <option value="error">{t("wecom.failed")}</option>
        </select>
        <input
          className="k-input min-w-64 flex-1"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={t("wecom.search")}
        />
      </div>

      <div className="flex min-h-0 flex-1">
        <div className="min-w-0 flex-1 overflow-auto">
          {loading && <div className="p-6 text-[var(--paper-dim)]">{t("wecom.loading")}</div>}
          {error && <div className="p-6 text-[var(--vermilion)]">{error}</div>}
          {!loading && !error && filtered.length === 0 && (
            <div className="p-6 text-[var(--paper-mute)]">{t("wecom.empty")}</div>
          )}
          {filtered.map((item) => (
            <button
              key={`${item.database}-${item.id}`}
              onClick={() => setSelected(item)}
              className="grid w-full grid-cols-[9rem_6rem_1fr_5rem] gap-3 border-b border-[var(--line)] px-5 py-3 text-left text-[11.5px] hover:bg-[var(--ink-2)]"
            >
              <span className="font-mono text-[var(--paper-mute)]">{new Date(item.created_at).toLocaleString()}</span>
              <span className="font-mono text-[var(--amber)]">{item.user_key}</span>
              <span className="truncate text-[var(--paper)]">{item.question}</span>
              <span className={item.status === "success" ? "text-emerald-400" : "text-[var(--vermilion)]"}>
                {item.status === "success" ? t("wecom.success") : t("wecom.failed")}
              </span>
            </button>
          ))}
        </div>

        {selected && (
          <aside className="hidden w-[42%] shrink-0 overflow-y-auto border-l border-[var(--line)] p-5 lg:block">
            <div className="flex items-start justify-between gap-3">
              <div className="k-eyebrow text-[var(--amber)]">{selected.database} · {selected.user_key}</div>
              <button className="text-[var(--paper-mute)] hover:text-[var(--paper)]" onClick={() => setSelected(null)}>×</button>
            </div>
            <h3 className="mt-4 text-base leading-relaxed text-[var(--paper)]">{selected.question}</h3>
            <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 font-mono text-[10.5px] text-[var(--paper-mute)]">
              <span>{selected.provider}</span><span>{selected.workspace}</span>
              <span>{(selected.duration_ms / 1000).toFixed(1)}s</span>
              <span>tokens {selected.input_tokens ?? 0}/{selected.output_tokens ?? 0}</span>
            </div>
            {selected.error && <pre className="mt-4 whitespace-pre-wrap text-[11px] text-[var(--vermilion)]">{selected.error}</pre>}
            {selected.answer && <div className="mt-5 whitespace-pre-wrap text-[12.5px] leading-6 text-[var(--paper-dim)]">{selected.answer}</div>}
            {selected.references.length > 0 && (
              <div className="mt-5 border-t border-[var(--line)] pt-4">
                <div className="k-eyebrow">{t("wecom.references")}</div>
                {selected.references.map((reference) => <div key={reference} className="mt-2 font-mono text-[10.5px] text-[var(--paper-mute)]">{reference}</div>)}
              </div>
            )}
          </aside>
        )}
      </div>

      <div className="border-t border-[var(--line)] px-6 py-2 text-[10.5px] text-[var(--paper-mute)]">
        {t("wecom.privacy")}
      </div>
    </section>
  );
}

