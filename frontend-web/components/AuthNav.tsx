"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Bookmark, ChevronDown, FileText, LoaderCircle, LogOut, User, UserRound } from "lucide-react";
import { createClient, isSupabaseConfigured } from "@/lib/supabase/client";

interface AuthNavProps {
  lang?: "en" | "kn" | "te" | "ta" | "ml";
}

const LABELS = {
  en: {
    signIn: "Sign In",
    savedSchemes: "Saved Schemes",
    allSchemes: "All 111 Schemes",
    signOut: "Sign Out",
    account: "Citizen Account",
  },
  kn: {
    signIn: "ಲಾಗಿನ್",
    savedSchemes: "ಉಳಿಸಿದ ಯೋಜನೆಗಳು",
    allSchemes: "ಎಲ್ಲಾ 111 ಯೋಜನೆಗಳು",
    signOut: "ಲಾಗ್ ಔಟ್",
    account: "ನಾಗರಿಕ ಖಾತೆ",
  },
  te: {
    signIn: "లాగిన్",
    savedSchemes: "సేవ్ చేసిన పథకాలు",
    allSchemes: "అన్ని 111 పథకాలు",
    signOut: "లాగ్ అవుట్",
    account: "పౌర ఖాతా",
  },
  ta: {
    signIn: "உள்நுழைக",
    savedSchemes: "சேமிக்கப்பட்ட திட்டங்கள்",
    allSchemes: "அனைத்து 111 திட்டங்கள்",
    signOut: "வெளியேறு",
    account: "குடிமக்கள் கணக்கு",
  },
  ml: {
    signIn: "ലോഗിൻ",
    savedSchemes: "സംരക്ഷിച്ച പദ്ധതികൾ",
    allSchemes: "എല്ലാ 111 പദ്ധതികളും",
    signOut: "ലോഗ് ഔട്ട്",
    account: "പൗര അക്കൗണ്ട്",
  },
};

export function AuthNav({ lang = "en" }: AuthNavProps) {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);
  const [savedCount, setSavedCount] = useState<number>(0);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const t = LABELS[lang] || LABELS.en;

  // Sync saved count
  const updateCount = () => {
    try {
      const local = localStorage.getItem("sahayaka_saved_schemes");
      if (local) {
        const arr = JSON.parse(local);
        setSavedCount(Array.isArray(arr) ? arr.length : 0);
      } else {
        setSavedCount(0);
      }
    } catch {
      setSavedCount(0);
    }
  };

  useEffect(() => {
    updateCount();
    window.addEventListener("sahayaka_saved_schemes_changed", updateCount);
    window.addEventListener("storage", updateCount);
    return () => {
      window.removeEventListener("sahayaka_saved_schemes_changed", updateCount);
      window.removeEventListener("storage", updateCount);
    };
  }, []);

  useEffect(() => {
    const supabase = createClient();

    async function checkUser() {
      try {
        const {
          data: { user: currentUser },
        } = await supabase.auth.getUser();
        setUser(currentUser);

        if (currentUser && isSupabaseConfigured()) {
          const { count } = await supabase
            .from("saved_schemes")
            .select("*", { count: "exact", head: true });
          if (count !== null && count !== undefined) {
            setSavedCount(count);
          }
        }
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    checkUser();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      setUser(session?.user ?? null);
      if (session?.user && isSupabaseConfigured()) {
        const { count } = await supabase
          .from("saved_schemes")
          .select("*", { count: "exact", head: true });
        if (count !== null && count !== undefined) {
          setSavedCount(count);
        }
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [menuOpen]);

  async function handleSignOut() {
    setMenuOpen(false);
    const supabase = createClient();
    await supabase.auth.signOut();
    setUser(null);
    router.refresh();
  }

  if (loading) {
    return (
      <div className="auth-nav-loading" aria-label="Checking account status">
        <LoaderCircle size={14} className="spin" />
      </div>
    );
  }

  if (!user) {
    return (
      <Link href="/login" className="auth-nav-signin" title={t.signIn}>
        <UserRound size={14} strokeWidth={1.8} />
        <span>{t.signIn}</span>
      </Link>
    );
  }

  // User is logged in
  const displayName =
    user.user_metadata?.full_name ||
    user.user_metadata?.name ||
    user.email?.split("@")[0] ||
    "Citizen";
  const initials = displayName
    .split(" ")
    .map((part: string) => part[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase() || "U";

  return (
    <div className="auth-nav-container" ref={dropdownRef}>
      <button
        type="button"
        className={`auth-user-button ${menuOpen ? "open" : ""}`}
        onClick={() => setMenuOpen(!menuOpen)}
        aria-expanded={menuOpen}
        aria-label="User profile menu"
      >
        <span className="auth-user-avatar">{initials}</span>
        <span className="auth-user-name">{displayName}</span>
        {savedCount > 0 && <span className="auth-saved-badge">{savedCount}</span>}
        <ChevronDown size={13} className={`chevron-arrow ${menuOpen ? "rotated" : ""}`} />
      </button>

      {menuOpen && (
        <div className="auth-user-dropdown" role="menu">
          <div className="dropdown-user-header">
            <span className="dropdown-user-name">{displayName}</span>
            <span className="dropdown-user-email">{user.email}</span>
          </div>

          <div className="dropdown-divider" />

          <Link
            href="/saved-schemes"
            className="dropdown-item"
            role="menuitem"
            onClick={() => setMenuOpen(false)}
          >
            <Bookmark size={14} />
            <span>{t.savedSchemes}</span>
            {savedCount > 0 && <span className="dropdown-item-badge">{savedCount}</span>}
          </Link>

          <Link
            href="/policies"
            className="dropdown-item"
            role="menuitem"
            onClick={() => setMenuOpen(false)}
          >
            <FileText size={14} />
            <span>{t.allSchemes}</span>
          </Link>

          <div className="dropdown-divider" />

          <button
            type="button"
            className="dropdown-item signout"
            role="menuitem"
            onClick={handleSignOut}
          >
            <LogOut size={14} />
            <span>{t.signOut}</span>
          </button>
        </div>
      )}
    </div>
  );
}

