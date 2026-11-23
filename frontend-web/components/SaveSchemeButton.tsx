"use client";

import { useEffect, useState } from "react";
import { Bookmark, LoaderCircle } from "lucide-react";
import { createClient, isSupabaseConfigured } from "@/lib/supabase/client";

interface SaveSchemeButtonProps {
  schemeId: string;
  schemeName: string;
  category?: string | null;
  benefitsSummary?: string | null;
  officialPortalUrl?: string | null;
  lang?: "en" | "kn" | "te" | "ta" | "ml";
  className?: string;
  showText?: boolean;
}

const LABELS = {
  en: { save: "Save", saved: "Saved" },
  kn: { save: "ಉಳಿಸಿ", saved: "ಉಳಿಸಲಾಗಿದೆ" },
  te: { save: "సేవ్", saved: "సేవ్ అయింది" },
  ta: { save: "சேமி", saved: "சேமிக்கப்பட்டது" },
  ml: { save: "സേവ്", saved: "സേവ് ചെയ്തു" },
};

export function SaveSchemeButton({
  schemeId,
  schemeName,
  category = "General Welfare",
  benefitsSummary,
  officialPortalUrl,
  lang = "en",
  className = "",
  showText = true,
}: SaveSchemeButtonProps) {
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(false);
  const t = LABELS[lang] || LABELS.en;

  // Check initial saved status
  useEffect(() => {
    let isMounted = true;

    async function checkSaved() {
      // First check local storage for instant feedback
      try {
        const local = localStorage.getItem("sahayaka_saved_schemes");
        if (local) {
          const list = JSON.parse(local);
          if (Array.isArray(list) && list.some((item) => item.scheme_id === schemeId)) {
            if (isMounted) setSaved(true);
            return;
          }
        }
      } catch {}

      // If Supabase configured, check remote
      if (isSupabaseConfigured()) {
        try {
          const supabase = createClient();
          const {
            data: { user },
          } = await supabase.auth.getUser();
          if (user) {
            const { data } = await supabase
              .from("saved_schemes")
              .select("id")
              .eq("scheme_id", schemeId)
              .maybeSingle();

            if (isMounted && data) {
              setSaved(true);
            }
          }
        } catch {}
      }
    }

    checkSaved();

    const handleSavedChange = () => {
      try {
        const local = localStorage.getItem("sahayaka_saved_schemes");
        if (local) {
          const list = JSON.parse(local);
          setSaved(Array.isArray(list) && list.some((item) => item.scheme_id === schemeId));
        } else {
          setSaved(false);
        }
      } catch {}
    };

    window.addEventListener("sahayaka_saved_schemes_changed", handleSavedChange);
    return () => {
      isMounted = false;
      window.removeEventListener("sahayaka_saved_schemes_changed", handleSavedChange);
    };
  }, [schemeId]);

  async function handleToggle(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    if (loading) return;

    setLoading(true);
    const newSaved = !saved;
    setSaved(newSaved);

    try {
      // 1. Sync LocalStorage
      let list: any[] = [];
      try {
        const local = localStorage.getItem("sahayaka_saved_schemes");
        if (local) list = JSON.parse(local);
        if (!Array.isArray(list)) list = [];
      } catch {
        list = [];
      }

      if (newSaved) {
        if (!list.some((item) => item.scheme_id === schemeId)) {
          list.push({
            id: `local-${Date.now()}`,
            scheme_id: schemeId,
            scheme_name: schemeName,
            category,
            benefits_summary: benefitsSummary,
            official_portal_url: officialPortalUrl,
            created_at: new Date().toISOString(),
          });
        }
      } else {
        list = list.filter((item) => item.scheme_id !== schemeId);
      }
      localStorage.setItem("sahayaka_saved_schemes", JSON.stringify(list));

      // 2. Sync Supabase if configured & logged in
      if (isSupabaseConfigured()) {
        const supabase = createClient();
        const {
          data: { user },
        } = await supabase.auth.getUser();

        if (user) {
          if (newSaved) {
            await supabase.from("saved_schemes").insert({
              user_id: user.id,
              scheme_id: schemeId,
              scheme_name: schemeName,
              category: category ?? "General Welfare",
              benefits_summary: benefitsSummary ?? null,
              official_portal_url: officialPortalUrl ?? null,
            });
          } else {
            await supabase
              .from("saved_schemes")
              .delete()
              .eq("user_id", user.id)
              .eq("scheme_id", schemeId);
          }
        }
      }

      // Notify other components
      window.dispatchEvent(new Event("sahayaka_saved_schemes_changed"));
    } catch (err) {
      console.warn("Failed to persist saved scheme state:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      type="button"
      className={`scheme-save-btn ${saved ? "saved" : ""} ${className}`}
      onClick={handleToggle}
      title={saved ? t.saved : t.save}
      aria-label={saved ? t.saved : t.save}
      disabled={loading}
    >
      {loading ? (
        <LoaderCircle size={13} className="spin" />
      ) : (
        <Bookmark size={13} fill={saved ? "currentColor" : "none"} strokeWidth={1.8} />
      )}
      {showText && <span>{saved ? t.saved : t.save}</span>}
    </button>
  );
}

