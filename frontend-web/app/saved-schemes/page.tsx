"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  Bookmark,
  ExternalLink,
  FileText,
  Landmark,
  LoaderCircle,
  Printer,
  ShieldCheck,
  Trash2,
  UserRound,
} from "lucide-react";
import { createClient, isSupabaseConfigured } from "@/lib/supabase/client";

interface SavedScheme {
  id: string;
  scheme_id: string;
  scheme_name: string;
  category: string;
  benefits_summary?: string;
  official_portal_url?: string;
  notes?: string;
  created_at: string;
}

export default function SavedSchemesPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [schemes, setSchemes] = useState<SavedScheme[]>([]);
  const [loading, setLoading] = useState(true);
  const [removingId, setRemovingId] = useState<string | null>(null);

  useEffect(() => {
    async function loadSaved() {
      const supabase = createClient();
      const {
        data: { user: currentUser },
      } = await supabase.auth.getUser();

      if (!currentUser) {
        router.push("/login?redirectTo=/saved-schemes");
        return;
      }

      setUser(currentUser);

      if (isSupabaseConfigured()) {
        const { data, error } = await supabase
          .from("saved_schemes")
          .select("*")
          .order("created_at", { ascending: false });

        if (!error && data) {
          setSchemes(data as SavedScheme[]);
        }
      } else {
        // Fallback for local demo if credentials are being configured
        const local = localStorage.getItem("sahayaka_saved_schemes");
        if (local) {
          try {
            setSchemes(JSON.parse(local));
          } catch {}
        }
      }
      setLoading(false);
    }

    loadSaved();
  }, [router]);

  async function handleRemoveScheme(id: string, scheme_id: string) {
    setRemovingId(id);
    const supabase = createClient();

    if (isSupabaseConfigured()) {
      await supabase.from("saved_schemes").delete().eq("id", id);
    }

    setSchemes((prev) => prev.filter((s) => s.id !== id));

    // Also update local fallback
    try {
      const local = localStorage.getItem("sahayaka_saved_schemes");
      if (local) {
        const list = JSON.parse(local).filter((s: SavedScheme) => s.scheme_id !== scheme_id);
        localStorage.setItem("sahayaka_saved_schemes", JSON.stringify(list));
      }
    } catch {}

    setRemovingId(null);
  }

  return (
    <div className="policies-page">
      <header className="topbar policies-topbar">
        <Link className="brand" href="/" aria-label="Sahayaka Home">
          <span className="brand-mark">
            <Landmark size={21} strokeWidth={1.8} />
          </span>
          <span className="brand-word">
            sahayaka<span>.</span>
            <small>SAVED WELFARE PORTFOLIO</small>
          </span>
        </Link>

        <div className="topbar-right">
          <button className="print-button" onClick={() => window.print()} title="Print saved schemes">
            <Printer size={13} /> Print Portfolio
          </button>
          <Link href="/" className="auth-back-link">
            <ArrowLeft size={14} /> Back to Assistant
          </Link>
        </div>
      </header>

      <main className="policies-main">
        <Link href="/" className="policies-back">
          <ArrowLeft size={15} /> Back to Assistant
        </Link>

        <div className="policies-hero">
          <div className="eyebrow">
            <span className="eyebrow-line" />
            CITIZEN BENEFIT PORTFOLIO
          </div>
          <h1>Your Saved Welfare Schemes</h1>
          <p>
            Schemes you have shortlisted for application. Review statutory benefits, official links, and prepare
            mandatory documents before visiting the department counter.
          </p>

          <div className="policies-count">
            <Bookmark size={15} />
            <strong>{schemes.length}</strong> schemes shortlisted
          </div>
        </div>

        {loading ? (
          <div className="policies-empty">
            <LoaderCircle size={24} className="spin" style={{ margin: "0 auto 12px" }} />
            <p>Loading your saved portfolio…</p>
          </div>
        ) : schemes.length === 0 ? (
          <div className="policies-empty">
            <Bookmark size={32} style={{ margin: "0 auto 12px", opacity: 0.5 }} />
            <h2>No schemes saved yet</h2>
            <p style={{ maxWidth: 460, margin: "8px auto 18px", fontSize: 13 }}>
              When you explore schemes with the assistant or in the scheme directory, click the bookmark icon to save
              them to your personal citizen portfolio.
            </p>
            <div style={{ display: "flex", gap: 10, justifyContent: "center" }}>
              <Link href="/" className="auth-submit-btn" style={{ textDecoration: "none", display: "inline-flex" }}>
                Chat with Assistant
              </Link>
              <Link
                href="/policies"
                className="auth-link-btn"
                style={{ padding: "8px 14px", border: "1px solid var(--border)", borderRadius: "var(--radius-md)" }}
              >
                Browse All 111 Schemes
              </Link>
            </div>
          </div>
        ) : (
          <div className="policy-grid">
            {schemes.map((scheme) => (
              <article className="policy-card" key={scheme.id}>
                <div className="policy-card-meta">
                  <span className="policy-category">{scheme.category || "General Welfare"}</span>
                  <button
                    className="auth-link-btn"
                    style={{ color: "var(--error)", display: "flex", alignItems: "center", gap: 4 }}
                    onClick={() => handleRemoveScheme(scheme.id, scheme.scheme_id)}
                    disabled={removingId === scheme.id}
                    title="Remove from saved portfolio"
                  >
                    <Trash2 size={13} />
                    <span>{removingId === scheme.id ? "Removing…" : "Remove"}</span>
                  </button>
                </div>

                <h2>{scheme.scheme_name}</h2>

                {scheme.benefits_summary && (
                  <p className="policy-description" style={{ marginTop: 4 }}>
                    <strong>Benefit: </strong>
                    {scheme.benefits_summary}
                  </p>
                )}

                <div className="policy-card-footer" style={{ marginTop: "auto" }}>
                  {scheme.official_portal_url ? (
                    <a href={scheme.official_portal_url} target="_blank" rel="noreferrer">
                      <Landmark size={13} /> Official Portal <ExternalLink size={12} />
                    </a>
                  ) : (
                    <span>Check local department</span>
                  )}
                  <span style={{ fontSize: 10, color: "var(--muted-foreground)" }}>
                    Saved on {new Date(scheme.created_at).toLocaleDateString()}
                  </span>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

