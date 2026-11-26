"use client";

import { useCallback, useEffect, useState } from "react";
import { Bookmark, LoaderCircle } from "lucide-react";
import { createClient } from "@/lib/supabase/client";

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

  const checkSaved = useCallback(async () => {
    try {
      const supabase = createClient();
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) {
        setSaved(false);
        return;
      }

      const { data, error } = await supabase
        .from("saved_schemes")
        .select("id")
        .eq("user_id", user.id)
        .eq("scheme_id", schemeId)
        .maybeSingle();

      if (!error) {
        setSaved(Boolean(data));
      }
    } catch {
      setSaved(false);
    }
  }, [schemeId]);

  useEffect(() => {
    void checkSaved();

    const handleSavedChange = () => {
      void checkSaved();
    };

    window.addEventListener("sahayaka_saved_schemes_changed", handleSavedChange);
    return () => {
      window.removeEventListener("sahayaka_saved_schemes_changed", handleSavedChange);
    };
  }, [checkSaved]);

  async function handleToggle(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    if (loading) return;

    setLoading(true);
    const previousSaved = saved;
    const newSaved = !saved;
    setSaved(newSaved);

    try {
      const supabase = createClient();
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) {
        setSaved(false);
        return;
      }

      if (newSaved) {
        const { error } = await supabase.from("saved_schemes").upsert(
          {
            user_id: user.id,
            scheme_id: schemeId,
            scheme_name: schemeName,
            category: category ?? "General Welfare",
            benefits_summary: benefitsSummary ?? null,
            official_portal_url: officialPortalUrl ?? null,
          },
          { onConflict: "user_id,scheme_id" }
        );
        if (error) throw error;
      } else {
        const { error } = await supabase
          .from("saved_schemes")
          .delete()
          .eq("user_id", user.id)
          .eq("scheme_id", schemeId);
        if (error) throw error;
      }

      window.dispatchEvent(new Event("sahayaka_saved_schemes_changed"));
    } catch (err) {
      setSaved(previousSaved);
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
