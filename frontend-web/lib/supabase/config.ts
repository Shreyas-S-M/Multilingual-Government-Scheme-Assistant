export const CENTRALIZED_SUPABASE_URL = "https://thgmyraggpllimqhbxul.supabase.co";
export const CENTRALIZED_SUPABASE_PUBLISHABLE_KEY = "sb_publishable_QSKZUV_1-qU4AxyuHR8WTA_alGlZACH";

const PLACEHOLDER_FRAGMENTS = [
  "your-project-id",
  "your-anon-key",
  "placeholder-project",
  "placeholder-anon-key",
];

function resolveEnvValue(value: string | undefined): string | null {
  const trimmed = value?.trim();
  if (!trimmed) return null;
  if (PLACEHOLDER_FRAGMENTS.some((fragment) => trimmed.includes(fragment))) {
    return null;
  }
  return trimmed;
}

export function getSupabaseConfig(): { url: string; key: string } {
  const url = resolveEnvValue(process.env.NEXT_PUBLIC_SUPABASE_URL) ?? CENTRALIZED_SUPABASE_URL;
  const key =
    resolveEnvValue(process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY) ??
    resolveEnvValue(process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) ??
    CENTRALIZED_SUPABASE_PUBLISHABLE_KEY;

  return { url, key };
}

export function isSupabaseConfigured(): boolean {
  const { url, key } = getSupabaseConfig();
  return Boolean(url && key);
}

export function sanitizeRedirectPath(target: string | null | undefined, fallback = "/"): string {
  if (!target) return fallback;
  const trimmed = target.trim();
  if (!trimmed.startsWith("/") || trimmed.startsWith("//")) {
    return fallback;
  }
  return trimmed;
}

