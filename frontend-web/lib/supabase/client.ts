import { createBrowserClient } from "@supabase/ssr";
import { getSupabaseConfig, isSupabaseConfigured } from "./config";

export { isSupabaseConfigured };

export function createClient() {
  const { url, key } = getSupabaseConfig();
  return createBrowserClient(url, key);
}

