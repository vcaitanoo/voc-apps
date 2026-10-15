import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createRemoteJWKSet, jwtVerify } from "npm:jose@5";

const SUPABASE_URL = (Deno.env.get("SUPABASE_URL") ?? "").replace(/\/$/, "");
const SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
const ISSUER = "https://gitlab.com";
const AUDIENCE = "https://khinnoxpesnhtmmvrken.supabase.co/functions/v1/jarvis-vc37-build-oidc";
const PROJECT_ID = "85949230";
const NAMESPACE_ID = "140704148";
const PROJECT_PATH = "oliveira.caitano2023/voc-lab";
const ALLOWED_REF = "main";
const OBJECT = "jarvis/candidate/Jarvis-0.3.12-vc37.apk";
const JWKS = createRemoteJWKSet(new URL("https://gitlab.com/oauth/discovery/keys"));
const GITHUB_ISSUER = "https://token.actions.githubusercontent.com";
const GITHUB_REPOSITORY = "vcaitanoo/voc-apps";
const GITHUB_WORKFLOW_REF = "vcaitanoo/voc-apps/.github/workflows/jarvis-vc37-build.yml@refs/heads/main";
const GITHUB_JWKS = createRemoteJWKSet(new URL("https://token.actions.githubusercontent.com/.well-known/jwks"));

const headers = { "content-type": "application/json", "cache-control": "no-store" };
const reply = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers });

async function authorize(request: Request): Promise<boolean> {
  const authorization = request.headers.get("authorization") ?? "";
  if (!authorization.startsWith("Bearer ")) return false;
  const token = authorization.slice(7);

  // CI GitLab project VOC Lab: protected main only.
  try {
    const { payload } = await jwtVerify(token, JWKS, { issuer: ISSUER, audience: AUDIENCE });
    if (
      String(payload.project_id ?? "") === PROJECT_ID &&
      String(payload.namespace_id ?? "") === NAMESPACE_ID &&
      String(payload.project_path ?? "") === PROJECT_PATH &&
      String(payload.ref ?? "") === ALLOWED_REF &&
      String(payload.ref_type ?? "") === "branch" &&
      String(payload.ref_protected ?? "") === "true"
    ) return true;
  } catch {
    // Continue to the tightly scoped GitHub Actions identity below.
  }

  // Hosted GitHub runner: one repository, main branch, one exact workflow.
  try {
    const { payload } = await jwtVerify(token, GITHUB_JWKS, {
      issuer: GITHUB_ISSUER,
      audience: AUDIENCE,
    });
    return String(payload.repository ?? "") === GITHUB_REPOSITORY &&
      String(payload.repository_owner ?? "").toLowerCase() === "vcaitanoo" &&
      String(payload.ref ?? "") === "refs/heads/main" &&
      String(payload.sub ?? "") === "repo:vcaitanoo/voc-apps:ref:refs/heads/main" &&
      String(payload.workflow_ref ?? "") === GITHUB_WORKFLOW_REF &&
      ["push", "workflow_dispatch"].includes(String(payload.event_name ?? ""));
  } catch {
    console.error("Build OIDC authorization rejected");
    return false;
  }
}

async function signingMaterial(): Promise<Response> {
  if (!SUPABASE_URL || !SERVICE_ROLE_KEY) {
    return reply({ error: "signing_backend_unavailable" }, 503);
  }
  const response = await fetch(`${SUPABASE_URL}/rest/v1/rpc/jarvis_vc23_signing_material_temp`, {
    method: "POST",
    headers: {
      apikey: SERVICE_ROLE_KEY,
      authorization: `Bearer ${SERVICE_ROLE_KEY}`,
      "content-type": "application/json",
    },
    body: "{}",
  });
  if (!response.ok) {
    console.error("Signing material RPC failed", response.status);
    return reply({ error: "signing_unavailable" }, 503);
  }
  return new Response(await response.text(), { status: 200, headers });
}

async function sha256Hex(bytes: Uint8Array): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest))
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("");
}

async function uploadArtifact(request: Request): Promise<Response> {
  const object = request.headers.get("x-artifact-path") ?? "";
  if (object !== OBJECT) return reply({ error: "invalid_artifact_path" }, 400);
  if (!SUPABASE_URL || !SERVICE_ROLE_KEY) return reply({ error: "storage_backend_unavailable" }, 503);

  const expected = (request.headers.get("x-artifact-sha256") ?? "").toLowerCase();
  if (!/^[a-f0-9]{64}$/.test(expected)) return reply({ error: "invalid_sha256" }, 400);
  const bytes = new Uint8Array(await request.arrayBuffer());
  if (bytes.length < 1_000_000 || bytes.length > 100_000_000) {
    return reply({ error: "invalid_artifact_size" }, 400);
  }
  const actual = await sha256Hex(bytes);
  if (actual !== expected) return reply({ error: "artifact_digest_mismatch" }, 400);

  const response = await fetch(`${SUPABASE_URL}/storage/v1/object/voc-lab/${OBJECT}`, {
    method: "POST",
    headers: {
      apikey: SERVICE_ROLE_KEY,
      authorization: `Bearer ${SERVICE_ROLE_KEY}`,
      "content-type": "application/vnd.android.package-archive",
      "x-upsert": "true",
    },
    body: bytes,
  });
  if (!response.ok) {
    const detail = await response.text();
    console.error("APK upload failed", response.status);
    return reply({ error: "upload_failed", status: response.status, detail: detail.slice(0, 120) }, 502);
  }
  return reply({ ok: true, object: OBJECT, sha256: actual, size: bytes.length });
}

Deno.serve(async (request: Request) => {
  if (!(await authorize(request))) return reply({ error: "forbidden" }, 403);
  try {
    const action = request.headers.get("x-action") ?? (request.method === "GET" ? "signing" : "");
    if (action === "signing" && request.method === "GET") return await signingMaterial();
    if (action === "upload" && request.method === "POST") return await uploadArtifact(request);
    if (action === "status" && request.method === "GET") return reply({ ok: true });
    return reply({ error: "unsupported_action" }, 400);
  } catch {
    console.error("Jarvis VC37 build bridge failure");
    return reply({ error: "internal" }, 500);
  }
});
