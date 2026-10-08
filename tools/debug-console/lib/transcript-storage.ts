import type { UIMessage } from "@/components/MessageBubble";

const PREFIX = "groundmap:console:transcript:v1:";
const MAX_MESSAGES = 100;

export interface QuestionGroup {
  id: string;
  title: string;
  userMessageIds: string[];
}

export function transcriptKey(workspace: string | null): string {
  return `${PREFIX}${workspace ?? "__default__"}`;
}

export function directoryKey(transcriptStorageKey: string): string {
  return `${transcriptStorageKey}:directory`;
}

function textOnly(messages: UIMessage[]): UIMessage[] {
  return messages
    .filter((message) => !message.streaming)
    .filter((message) => message.role === "user" || message.role === "assistant")
    .slice(-MAX_MESSAGES)
    .map((message) => ({
      id: message.id,
      role: message.role,
      parts: message.parts
        .filter((part) => part.kind === "text")
        .map((part) => ({ kind: "text" as const, text: part.text })),
      ...(message.refValidation ? { refValidation: message.refValidation } : {}),
    }));
}

export function loadTranscript(storage: Storage, key: string): UIMessage[] {
  try {
    const raw = storage.getItem(key);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return textOnly(
      parsed.filter((message): message is UIMessage =>
        !!message &&
        typeof message === "object" &&
        typeof message.id === "string" &&
        (message.role === "user" || message.role === "assistant") &&
        Array.isArray(message.parts) &&
        message.parts.every(
          (part: unknown) =>
            !!part &&
            typeof part === "object" &&
            "kind" in part &&
            part.kind === "text" &&
            "text" in part &&
            typeof part.text === "string",
        ),
      ),
    ).map((message) => ({
      ...message,
      refValidation:
        message.refValidation &&
        Array.isArray(message.refValidation.broken) &&
        Array.isArray(message.refValidation.unread) &&
        (!message.refValidation.downgraded || Array.isArray(message.refValidation.downgraded))
          ? message.refValidation
          : undefined,
    }));
  } catch {
    return [];
  }
}

export function saveTranscript(storage: Storage, key: string, messages: UIMessage[]): boolean {
  try {
    storage.setItem(key, JSON.stringify(textOnly(messages)));
    return true;
  } catch {
    return false;
  }
}

function questionText(messages: UIMessage[], id: string): string {
  const message = messages.find((item) => item.id === id && item.role === "user");
  return (
    message?.parts
      .filter((part) => part.kind === "text")
      .map((part) => (part.kind === "text" ? part.text : ""))
      .join("")
      .trim() || "未命名问答"
  );
}

export function normalizeQuestionGroups(
  groups: QuestionGroup[],
  messages: UIMessage[],
): QuestionGroup[] {
  const userIds = messages.filter((message) => message.role === "user").map((message) => message.id);
  const validIds = new Set(userIds);
  const claimed = new Set<string>();
  const normalized: QuestionGroup[] = [];

  for (const group of groups) {
    const ids = group.userMessageIds.filter((id) => validIds.has(id) && !claimed.has(id));
    if (!ids.length) continue;
    ids.forEach((id) => claimed.add(id));
    normalized.push({
      id: group.id || `g-${ids[0]}`,
      title: group.title.trim() || questionText(messages, ids[0]),
      userMessageIds: ids,
    });
  }

  for (const id of userIds) {
    if (!claimed.has(id)) {
      normalized.push({ id: `g-${id}`, title: questionText(messages, id), userMessageIds: [id] });
    }
  }

  const order = new Map(userIds.map((id, index) => [id, index]));
  return normalized.sort(
    (a, b) => (order.get(a.userMessageIds[0]) ?? 0) - (order.get(b.userMessageIds[0]) ?? 0),
  );
}

export function loadQuestionGroups(storage: Storage, key: string): QuestionGroup[] {
  try {
    const parsed: unknown = JSON.parse(storage.getItem(key) || "[]");
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(
      (group): group is QuestionGroup =>
        !!group &&
        typeof group === "object" &&
        typeof group.id === "string" &&
        typeof group.title === "string" &&
        Array.isArray(group.userMessageIds) &&
        group.userMessageIds.every((id: unknown) => typeof id === "string"),
    );
  } catch {
    return [];
  }
}

export function saveQuestionGroups(
  storage: Storage,
  key: string,
  groups: QuestionGroup[],
): boolean {
  try {
    storage.setItem(key, JSON.stringify(groups));
    return true;
  } catch {
    return false;
  }
}

export function exportTranscript(messages: UIMessage[]): string {
  return textOnly(messages)
    .map((message) => {
      const text = message.parts.map((part) => (part.kind === "text" ? part.text : "")).join("");
      return `## ${message.role === "user" ? "提问" : "回答"}\n\n${text}`;
    })
    .join("\n\n");
}
