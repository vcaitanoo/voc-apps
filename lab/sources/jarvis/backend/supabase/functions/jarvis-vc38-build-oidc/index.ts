import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createRemoteJWKSet, jwtVerify } from "npm:jose@5";

const SUPABASE_URL = (Deno.env.get("SUPABASE_URL") ?? "").replace(/\/$/, "");
const SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
const ISSUER = "https://gitlab.com";
const AUDIENCE = "https://khinnoxpesnhtmmvrken.supabase.co/functions/v1/jarvis-vc38-build-oidc";
const PROJECT_ID = "85949230";
const NAMESPACE_ID = "140704148";
const PROJECT_PATH = "oliveira.caitano2023/voc-lab";
const ALLOWED_REF = "main";
const OBJECT = "jarvis/candidate/Jarvis-0.3.13-vc38.apk";
const JWKS = createRemoteJWKSet(new URL("https://gitlab.com/oauth/discovery/keys"));
const GITHUB_ISSUER = "https://token.actions.githubusercontent.com";
const GITHUB_REPOSITORY = "vcaitanoo/voc-apps";
const GITHUB_WORKFLOW_REF = "vcaitanoo/voc-apps/.github/workflows/jarvis-vc38-build.yml@refs/heads/main";
const GITHUB_SUBJECTS = new Set([
  "repo:vcaitanoo@162039938/voc-apps@1335849419:ref:refs/heads/main",
  "repo:vcaitanoo/voc-apps:ref:refs/heads/main",
]);
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
      GITHUB_SUBJECTS.has(String(payload.sub ?? "")) &&
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


async function publishCatalog(request: Request): Promise<Response> {
  const report = await request.json().catch(() => null) as Record<string, unknown> | null;
  const expectedSha = "7fc8e6f264c29d881a6bfcf064aa3801e3c352d31ed261a05fe49bd202256697";
  const expectedUrl = `${SUPABASE_URL}/storage/v1/object/public/voc-lab/${OBJECT}`;
  const expectedSignature = "f1193b9ea3123a4b1ca9938f1bf070c9ce97648f492c3f47b56a195a517138c2";

  if (!report ||
      report.apk !== "Jarvis-0.3.13-vc38.apk" ||
      report.versionCode !== 38 ||
      report.versionName !== "0.3.13" ||
      report.apkUrl !== expectedUrl ||
      String(report.sha256 ?? "").toLowerCase() !== expectedSha) {
    return reply({ error: "invalid_catalog_report" }, 400);
  }

  const restHeaders = {
    apikey: SERVICE_ROLE_KEY,
    authorization: `Bearer ${SERVICE_ROLE_KEY}`,
    accept: "application/json",
  };
  const read = await fetch(
    `${SUPABASE_URL}/rest/v1/voc_lab_catalog_store?id=eq.main&select=body&limit=1`,
    { headers: restHeaders },
  );
  if (!read.ok) return reply({ error: "catalog_read_failed", status: read.status }, 502);
  const rows = await read.json() as Array<{ body?: Record<string, unknown> }>;
  if (!rows.length || !rows[0]?.body) return reply({ error: "catalog_missing" }, 404);

  const catalog = rows[0].body;
  const apps = catalog.apps;
  if (!Array.isArray(apps)) return reply({ error: "catalog_apps_invalid" }, 502);
  const jarvis = apps.find((item: any) => item?.id === "jarvis") as Record<string, any> | undefined;
  if (!jarvis) return reply({ error: "jarvis_missing" }, 404);

  const currentCode = Number(jarvis.candidate?.versionCode ?? 0);
  if (currentCode > 38) return reply({ error: "newer_candidate_already_registered", currentCode }, 409);

  const candidate = {
    versionCode: 38,
    versionName: "0.3.13",
    apkUrl: expectedUrl,
    sha256: expectedSha,
    signatureSha256: expectedSignature,
    notes: "CANDIDATO VC38 / 0.3.13: correção da escuta silenciosa e voz masculina obrigatória em português. APK publicado no armazenamento permanente; SHA-256 do binário servido conferido e certificado histórico validado no build. Teste físico pendente; não é versão estável.",
  };
  const same = currentCode === 38 &&
    jarvis.candidate?.versionName === candidate.versionName &&
    jarvis.candidate?.apkUrl === candidate.apkUrl &&
    String(jarvis.candidate?.sha256 ?? "").toLowerCase() === candidate.sha256 &&
    jarvis.candidate?.signatureSha256 === candidate.signatureSha256;
  if (same) {
    return reply({ ok: true, changed: false, updatedAt: catalog.updatedAt, versionCode: 38, versionName: "0.3.13" });
  }

  jarvis.candidate = candidate;
  const now = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  catalog.updatedAt = now;
  const write = await fetch(`${SUPABASE_URL}/rest/v1/voc_lab_catalog_store?id=eq.main`, {
    method: "PATCH",
    headers: {
      ...restHeaders,
      "content-type": "application/json",
      prefer: "return=representation",
    },
    body: JSON.stringify({ body: catalog, updated_at: now }),
  });
  if (!write.ok) {
    console.error("Live VOC Lab catalog update failed", write.status);
    return reply({ error: "catalog_write_failed", status: write.status }, 502);
  }
  const saved = await write.json() as Array<{ body?: Record<string, any> }>;
  const savedJarvis = saved[0]?.body?.apps?.find((item: any) => item?.id === "jarvis");
  if (Number(savedJarvis?.candidate?.versionCode) !== 38 ||
      String(savedJarvis?.candidate?.sha256 ?? "").toLowerCase() !== expectedSha) {
    return reply({ error: "catalog_write_verification_failed" }, 502);
  }
  return reply({ ok: true, changed: true, updatedAt: now, versionCode: 38, versionName: "0.3.13", apkUrl: expectedUrl, sha256: expectedSha });
}


Deno.serve(async (request: Request) => {
  if (!(await authorize(request))) return reply({ error: "forbidden" }, 403);
  try {
    const action = request.headers.get("x-action") ?? (request.method === "GET" ? "signing" : "");
    if (action === "signing" && request.method === "GET") return await signingMaterial();
    if (action === "upload" && request.method === "POST") return await uploadArtifact(request);
    if (action === "publish-catalog" && request.method === "POST") return await publishCatalog(request);
    if (action === "status" && request.method === "GET") return reply({ ok: true });
    return reply({ error: "unsupported_action" }, 400);
  } catch {
    console.error("Jarvis VC38 build bridge failure");
    return reply({ error: "internal" }, 500);
  }
});
