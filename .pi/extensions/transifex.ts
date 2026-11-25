// biome-ignore lint/style/noExcessiveLinesPerFile: extension is a cohesive single-file module
import fs from "node:fs";
import os from "node:os";
import process from "node:process";
// biome-ignore lint/correctness/noUndeclaredDependencies: pi built-in extension import, provided by the host
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";

// Transifex API v3 extension: lets the agent list untranslated strings and
// save translations via the public REST API. Requires TX_TOKEN (Bearer token
// from https://app.transifex.com/user/settings/) or a token stored in
// ~/.tx-token as a fallback.
//
// Preconfigured for the pyvista-js project: the org and project parameters
// default to tkoyama010/pyvista-js (https://app.transifex.com/tkoyama010/pyvista-js/)
// and can be overridden when calling the tools.

const API = "https://rest.api.transifex.com";
const DEFAULT_ORG = "tkoyama010";
const DEFAULT_PROJECT = "pyvista-js";

const DEFAULT_LIMIT = 50;

// Caller-controlled ids go into a URL path segment; validate them against the
// official Transifex resource-translation id format
// (o:org:p:project:r:resource:s:hash:l:language) so nothing that could escape
// the endpoint is accepted.
const TRANSLATION_ID_RE =
  /^o:[a-zA-Z0-9._-]+:p:[a-zA-Z0-9_-]+:r:[a-zA-Z0-9_-]+:s:[0-9a-fA-F]{32}:l:[a-zA-Z0-9@_-]+$/u;

interface JsonApiItem {
  id: string;
  attributes: Record<string, unknown>;
  relationships?: Record<string, { data?: { id: string } }>;
}

interface JsonApiResponse {
  data: JsonApiItem[];
  included?: JsonApiItem[];
  links?: { next?: string | null };
}

interface TranslationEntry {
  id: string;
  text?: string;
  form?: string;
}

interface SaveOutcome {
  error?: string;
}

function token(): string {
  let value = process.env.TX_TOKEN;
  if (!value) {
    // Fallback: read token from a file in the user's home directory so a
    // full pi restart is not required. os.homedir() is safe even when HOME
    // is unset.
    const tokenFile = `${os.homedir()}/.tx-token`;
    if (fs.existsSync(tokenFile)) {
      value = fs.readFileSync(tokenFile, "utf8").trim();
    }
  }
  if (!value) {
    throw new Error(
      "TX_TOKEN is not set. Generate an API token at https://app.transifex.com/user/settings/ and either export TX_TOKEN or store the token in ~/.tx-token.",
    );
  }
  return value;
}

async function txGet(path: string): Promise<JsonApiResponse> {
  let url = `${API}${path}`;
  if (path.startsWith("http")) {
    url = path;
  }
  const response = await fetch(url, {
    headers: {
      // biome-ignore lint/style/useNamingConvention: HTTP header names are protocol constants
      Accept: "application/vnd.api+json",
      // biome-ignore lint/style/useNamingConvention: HTTP header names are protocol constants
      Authorization: `Bearer ${token()}`,
    },
  });
  if (!response.ok) {
    throw new Error(`Transifex API ${response.status}: ${await response.text()}`);
  }
  return (await response.json()) as JsonApiResponse;
}

function resourceId(org: string, project: string, resource: string): string {
  return `o:${org}:p:${project}:r:${resource}`;
}

/** Narrow the unknown `strings` attribute into a plural-form map. */
function stringsOf(item: JsonApiItem | undefined): Record<string, string> {
  return (item?.attributes.strings as Record<string, string> | undefined) ?? {};
}

/** Only follow pagination links on the Transifex API origin, so the bearer token is never sent to another host. */
function nextPath(next: string | undefined | null): string | undefined {
  if (!next) {
    return undefined;
  }
  let url = `${API}${next}`;
  if (next.startsWith("http")) {
    url = next;
  }
  if (!url.startsWith(`${API}/`)) {
    return undefined;
  }
  return url;
}

/** Return the (slot id, key, source) triples of untranslated strings from a resource_translations response. */
function pickUntranslated(
  response: JsonApiResponse,
): Array<{ id: string; key: string; source: string }> {
  const includedById = new Map<string, JsonApiItem>(
    (response.included ?? []).map((item) => [item.id, item]),
  );
  const result: Array<{ id: string; key: string; source: string }> = [];
  for (const item of response.data) {
    // Untranslated slots have strings null or all forms empty. Any populated
    // plural form counts as translated.
    const resourceString = includedById.get(item.relationships?.resource_string?.data?.id ?? "");
    if (!Object.values(stringsOf(item)).some(Boolean) && resourceString) {
      result.push({
        id: item.id,
        key: String(resourceString.attributes.key ?? ""),
        source: String(stringsOf(resourceString).other ?? ""),
      });
    }
  }
  return result;
}

/**
 * Read the current slot, merge the new plural form(s), and PATCH it back.
 * Returns an error message on failure, or an empty object on success.
 */
// biome-ignore lint/complexity/noExcessiveLinesPerFunction: read-merge-PATCH is one cohesive HTTP sequence
async function saveTranslation(entry: TranslationEntry): Promise<SaveOutcome> {
  const { id, text, form } = entry;
  if (!TRANSLATION_ID_RE.test(id)) {
    return { error: "invalid resource translation id" };
  }
  let json: JsonApiResponse;
  let strings: Record<string, string>;
  try {
    // PATCH replaces the whole plural-form map, so fetch the current slot
    // first and merge into it (json.data is the target slot; included holds
    // the source resource_string).
    // ponytail: read-merge-PATCH has a small lost-update window; the
    // Transifex API v3 does not support ETag/If-Match conditional updates,
    // so conflicts cannot be rejected server-side. Retry failed-looking
    // saves if another translator edited the slot concurrently.
    json = await txGet(`/resource_translations/${id}?include=resource_string`);
    let slots: JsonApiItem[];
    if (Array.isArray(json.data)) {
      slots = json.data;
    } else {
      slots = [json.data];
    }
    strings = stringsOf(slots[0]);
  } catch (error) {
    return { error: String(error) };
  }
  if (text === undefined) {
    // Copy source: take every plural form from the source string.
    const source = stringsOf(json.included?.[0]);
    // Fail closed: never PATCH an empty source (it would wipe the
    // translation slot).
    if (!Object.values(source).some(Boolean)) {
      return { error: "source string is missing or empty; not overwritten" };
    }
    Object.assign(strings, source);
  } else {
    // Fail closed: never PATCH an empty translation either; a blank
    // model result would erase the slot.
    if (!text) {
      return { error: "empty translation text; not saved" };
    }
    strings = { ...strings, [form ?? "other"]: text };
  }
  try {
    const response = await fetch(`${API}/resource_translations/${id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/vnd.api+json",
        // biome-ignore lint/style/useNamingConvention: HTTP header names are protocol constants
        Accept: "application/vnd.api+json",
        // biome-ignore lint/style/useNamingConvention: HTTP header names are protocol constants
        Authorization: `Bearer ${token()}`,
      },
      body: JSON.stringify({
        data: {
          id,
          type: "resource_translations",
          attributes: { strings },
        },
      }),
    });
    if (response.ok) {
      return {};
    }
    return { error: `${response.status}: ${await response.text()}` };
  } catch (error) {
    // Network/auth failures must not reject the whole batch; keep earlier
    // partial results reportable.
    return { error: String(error) };
  }
}

// biome-ignore lint/style/noDefaultExport: pi loads extensions via the default export
// biome-ignore lint/complexity/noExcessiveLinesPerFunction: one registration block per tool keeps the API surface in one place
export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "transifex_list_resources",
    label: "Transifex: List Resources",
    description:
      "List resources (slug, name, categories) in a Transifex project. Uses TX_TOKEN env var or ~/.tx-token file.",
    parameters: Type.Object({
      org: Type.Optional(
        Type.String({ description: `Organization slug (default: ${DEFAULT_ORG})` }),
      ),
      project: Type.Optional(
        Type.String({ description: `Project slug (default: ${DEFAULT_PROJECT})` }),
      ),
    }),
    async execute(_toolCallId, params) {
      const org = params.org ?? DEFAULT_ORG;
      const project = params.project ?? DEFAULT_PROJECT;
      const query = new URLSearchParams({
        "filter[project]": `o:${org}:p:${project}`,
      });
      const resources: JsonApiItem[] = [];
      let path: string | undefined = `/resources?${query}`;
      while (path) {
        // biome-ignore lint/performance/noAwaitInLoops: cursor pagination must be sequential
        const json = await txGet(path);
        resources.push(...json.data);
        path = nextPath(json.links?.next);
      }
      const text = JSON.stringify(
        resources.map((r) => ({
          slug: r.attributes.slug,
          name: r.attributes.name,
          categories: r.attributes.categories,
        })),
        null,
        2,
      );
      return { content: [{ type: "text", text }], details: {} };
    },
  });

  pi.registerTool({
    name: "transifex_get_untranslated",
    label: "Transifex: Get Untranslated",
    description:
      "Fetch untranslated strings (slot id, source text) for one resource and language. Translate them with transifex_translate.",
    parameters: Type.Object({
      org: Type.Optional(
        Type.String({ description: `Organization slug (default: ${DEFAULT_ORG})` }),
      ),
      project: Type.Optional(
        Type.String({ description: `Project slug (default: ${DEFAULT_PROJECT})` }),
      ),
      resource: Type.String({ description: "Resource slug" }),
      lang: Type.String({ description: "Target language code, e.g. ja" }),
      limit: Type.Optional(Type.Number({ description: "Max strings to return (default 50)" })),
    }),
    async execute(_toolCallId, params) {
      // Normalize: reject negative/fractional values so slice(0, limit)
      // cannot violate the stated maximum.
      const limit = Math.max(1, Math.floor(params.limit ?? DEFAULT_LIMIT));
      const query = new URLSearchParams({
        "filter[resource]": resourceId(
          params.org ?? DEFAULT_ORG,
          params.project ?? DEFAULT_PROJECT,
          params.resource,
        ),
        "filter[language]": `l:${params.lang}`,
        include: "resource_string",
        // resource_translations rejects page[limit]/page[number]; it uses
        // cursor pagination, which the links.next loop below follows.
      });
      const untranslated: Array<{ id: string; key: string; source: string }> = [];
      let path: string | undefined = `/resource_translations?${query}`;
      while (path && untranslated.length < limit) {
        // biome-ignore lint/performance/noAwaitInLoops: cursor pagination must be sequential
        const json = await txGet(path);
        untranslated.push(...pickUntranslated(json));
        path = nextPath(json.links?.next);
      }
      const text = JSON.stringify(untranslated.slice(0, limit), null, 2);
      return { content: [{ type: "text", text }], details: {} };
    },
  });

  pi.registerTool({
    name: "transifex_translate",
    label: "Transifex: Save Translation",
    description:
      "Save translations for untranslated strings. Pass one entry per string: the slot id and translated text from transifex_get_untranslated. Omit text to copy the source string unchanged (for markup/identifier strings that must not be translated).",
    parameters: Type.Object({
      translations: Type.Array(
        Type.Object({
          id: Type.String({ description: "Resource translation slot id" }),
          text: Type.Optional(
            Type.String({
              description: "Translated text; omit to copy the source string",
            }),
          ),
          form: Type.Optional(
            Type.String({
              description: 'Plural form key to set when text is given (default: "other")',
            }),
          ),
        }),
      ),
    }),
    async execute(_toolCallId, params) {
      const saved: string[] = [];
      const failed: Array<{ id: string; error: string }> = [];
      for (const entry of params.translations) {
        // biome-ignore lint/performance/noAwaitInLoops: save sequentially to preserve caller order and respect API rate limits
        const outcome = await saveTranslation(entry);
        if (outcome.error) {
          failed.push({ id: entry.id, error: outcome.error });
        } else {
          saved.push(entry.id);
        }
      }
      const text = JSON.stringify({ saved, failed }, null, 2);
      return { content: [{ type: "text", text }], details: {} };
    },
  });
}

export { pickUntranslated };
