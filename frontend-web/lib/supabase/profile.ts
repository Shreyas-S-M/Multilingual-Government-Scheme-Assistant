import type { SupabaseClient } from "@supabase/supabase-js";
import type { Language } from "@/lib/types";

const SUPPORTED_LANGUAGES: readonly Language[] = ["en", "kn", "te", "ta", "ml"];

export function isSupportedLanguage(value: unknown): value is Language {
  return typeof value === "string" && (SUPPORTED_LANGUAGES as readonly string[]).includes(value);
}

export async function fetchUserPreferredLanguage(
  supabase: SupabaseClient,
  userId: string
): Promise<Language | null> {
  try {
    const { data, error } = await supabase
      .from("profiles")
      .select("preferred_language")
      .eq("id", userId)
      .maybeSingle();

    if (error || !data) return null;
    return isSupportedLanguage(data.preferred_language) ? data.preferred_language : null;
  } catch {
    return null;
  }
}

export async function persistUserPreferredLanguage(
  supabase: SupabaseClient,
  userId: string,
  language: Language
): Promise<void> {
  try {
    await supabase.from("profiles").upsert(
      {
        id: userId,
        preferred_language: language,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "id" }
    );
  } catch {
    // Non-blocking preference sync
  }
}

