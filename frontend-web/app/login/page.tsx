"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  ArrowLeft,
  CheckCircle2,
  KeyRound,
  Landmark,
  Languages,
  LoaderCircle,
  Lock,
  Mail,
  ShieldAlert,
  ShieldCheck,
  User,
} from "lucide-react";
import { createClient, isSupabaseConfigured } from "@/lib/supabase/client";

type AuthMode = "signin" | "signup" | "forgot";
type Language = "en" | "kn" | "te" | "ta" | "ml";

const AUTH_COPY: Record<
  Language,
  {
    titleSignIn: string;
    titleSignUp: string;
    titleForgot: string;
    subSignIn: string;
    subSignUp: string;
    subForgot: string;
    fullName: string;
    fullNamePlaceholder: string;
    email: string;
    emailPlaceholder: string;
    password: string;
    passwordPlaceholder: string;
    confirmPassword: string;
    btnSignIn: string;
    btnSignUp: string;
    btnForgot: string;
    googleContinue: string;
    orDivider: string;
    forgotLink: string;
    noAccount: string;
    hasAccount: string;
    signUpLink: string;
    signInLink: string;
    backHome: string;
    passwordMismatch: string;
    checkEmail: string;
    checkEmailDesc: string;
    resetSent: string;
    resetSentDesc: string;
    unconfiguredAlert: string;
  }
> = {
  en: {
    titleSignIn: "Sign in to Sahayaka",
    titleSignUp: "Create your citizen account",
    titleForgot: "Reset your password",
    subSignIn: "Save eligible schemes, track document checklists, and resume assessments anytime.",
    subSignUp: "Join Sahayaka to bookmark public benefits and track application readiness.",
    subForgot: "Enter your registered email address and we'll send a secure password recovery link.",
    fullName: "Full Name",
    fullNamePlaceholder: "e.g. Ramesh Kumar",
    email: "Email Address",
    emailPlaceholder: "name@example.com",
    password: "Password",
    passwordPlaceholder: "At least 6 characters",
    confirmPassword: "Confirm Password",
    btnSignIn: "Sign In",
    btnSignUp: "Create Account",
    btnForgot: "Send Reset Link",
    googleContinue: "Continue with Google",
    orDivider: "or continue with email",
    forgotLink: "Forgot password?",
    noAccount: "Don't have an account?",
    hasAccount: "Already have an account?",
    signUpLink: "Sign up",
    signInLink: "Sign in",
    backHome: "Back to Assistant",
    passwordMismatch: "Passwords do not match.",
    checkEmail: "Verification email sent!",
    checkEmailDesc: "Please check your inbox and click the confirmation link to activate your account.",
    resetSent: "Password reset link sent!",
    resetSentDesc: "If an account exists with this email, you will receive a secure password reset link shortly.",
    unconfiguredAlert: "Supabase connection is not configured yet. Add NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY to your .env.local file.",
  },
  kn: {
    titleSignIn: "ಸಹಾಯಕಕ್ಕೆ ಲಾಗಿನ್ ಆಗಿ",
    titleSignUp: "ನಿಮ್ಮ ನಾಗರಿಕ ಖಾತೆ ತೆರೆಯಿರಿ",
    titleForgot: "ಪಾಸ್‌ವರ್ಡ್ ಮರುಹೊಂದಿಸಿ",
    subSignIn: "ಅರ್ಹ ಯೋಜನೆಗಳನ್ನು ಉಳಿಸಿ, ದಾಖಲೆಗಳ ಪಟ್ಟಿಯನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಸಂಭಾಷಣೆ ಮುಂದುವರಿಸಿ.",
    subSignUp: "ಸರ್ಕಾರಿ ಸೌಲಭ್ಯಗಳನ್ನು ಉಳಿಸಿಕೊಳ್ಳಲು ಮತ್ತು ಅರ್ಜಿಗೆ ಸಿದ್ಧರಾಗಲು ಸಹಾಯಕಕ್ಕೆ ಸೇರಿ.",
    subForgot: "ನಿಮ್ಮ ನೋಂದಾಯಿತ ಇಮೇಲ್ ವಿಳಾಸವನ್ನು ನಮೂದಿಸಿ, ನಾವು ಲಿಂಕ್ ಕಳುಹಿಸುತ್ತೇವೆ.",
    fullName: "ಪೂರ್ಣ ಹೆಸರು",
    fullNamePlaceholder: "ಉದಾ: ರಮೇಶ್ ಕುಮಾರ್",
    email: "ಇಮೇಲ್ ವಿಳಾಸ",
    emailPlaceholder: "name@example.com",
    password: "ಪಾಸ್‌ವರ್ಡ್",
    passwordPlaceholder: "ಕನಿಷ್ಠ 6 ಅಕ್ಷರಗಳು",
    confirmPassword: "ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ",
    btnSignIn: "ಲಾಗಿನ್ ಆಗಿ",
    btnSignUp: "ಖಾತೆ ರಚಿಸಿ",
    btnForgot: "ಲಿಂಕ್ ಕಳುಹಿಸಿ",
    googleContinue: "Google ಮೂಲಕ ಮುಂದುವರಿಯಿರಿ",
    orDivider: "ಅಥವಾ ಇಮೇಲ್ ಮೂಲಕ",
    forgotLink: "ಪಾಸ್‌ವರ್ಡ್ ಮರೆತಿರಾ?",
    noAccount: "ಖಾತೆ ಇಲ್ಲವೇ?",
    hasAccount: "ಈಗಾಗಲೇ ಖಾತೆ ಹೊಂದಿದ್ದೀರಾ?",
    signUpLink: "ನೋಂದಾಯಿಸಿ",
    signInLink: "ಲಾಗಿನ್ ಆಗಿ",
    backHome: "ಸಹಾಯಕಕ್ಕೆ ಹಿಂತಿರುಗಿ",
    passwordMismatch: "ಪಾಸ್‌ವರ್ಡ್‌ಗಳು ಹೊಂದಿಕೆಯಾಗುತ್ತಿಲ್ಲ.",
    checkEmail: "ದೃಢೀಕರಣ ಇಮೇಲ್ ಕಳುಹಿಸಲಾಗಿದೆ!",
    checkEmailDesc: "ನಿಮ್ಮ ಖಾತೆಯನ್ನು ಸಕ್ರಿಯಗೊಳಿಸಲು ನಿಮ್ಮ ಇನ್‌ಬಾಕ್ಸ್ ಪರಿಶೀಲಿಸಿ ಲಿಂಕ್ ಕ್ಲಿಕ್ ಮಾಡಿ.",
    resetSent: "ಮರುಹೊಂದಿಸುವ ಲಿಂಕ್ ಕಳುಹಿಸಲಾಗಿದೆ!",
    resetSentDesc: "ಖಾತೆ ಲಭ್ಯವಿದ್ದರೆ ಮರುಹೊಂದಿಸುವ ಲಿಂಕ್ ನಿಮ್ಮ ಇಮೇಲ್‌ಗೆ ತಲುಪುತ್ತದೆ.",
    unconfiguredAlert: "Supabase ಸಂಪರ್ಕ ಇನ್ನೂ ಕಾನ್ಫಿಗರ್ ಆಗಿಲ್ಲ. .env.local ನಲ್ಲಿ ವಿವರಗಳನ್ನು ಸೇರಿಸಿ.",
  },
  te: {
    titleSignIn: "సహాయకకు లాగిన్ అవ్వండి",
    titleSignUp: "మీ పౌర ఖాతాను సృష్టించండి",
    titleForgot: "పాస్‌వర్డ్‌ను రీసెట్ చేయండి",
    subSignIn: "మీకు వర్తించే పథకాలను సేవ్ చేయండి మరియు పత్రాల జాబితాను ట్రాక్ చేయండి.",
    subSignUp: "ప్రభుత్వ సంక్షేమ పథకాలను భద్రపరచుకోవడానికి సహాయకలో చేరండి.",
    subForgot: "మీ నమోదిత ఇమెయిల్ చిరునామాను నమోదు చేయండి, మేము లింక్ పంపుతాము.",
    fullName: "పూర్తి పేరు",
    fullNamePlaceholder: "ఉదా: రమేష్ కుమార్",
    email: "ఇమెయిల్ చిరునామా",
    emailPlaceholder: "name@example.com",
    password: "పాస్‌వర్డ్",
    passwordPlaceholder: "కనీసం 6 అక్షరాలు",
    confirmPassword: "పాస్‌వర్డ్ నిర్ధారించండి",
    btnSignIn: "లాగిన్ అవ్వండి",
    btnSignUp: "ఖాతా సృష్టించండి",
    btnForgot: "రీసెట్ లింక్ పంపండి",
    googleContinue: "Google తో కొనసాగండి",
    orDivider: "లేదా ఇమెయిల్ ద్వారా",
    forgotLink: "పాస్‌వర్డ్ మర్చిపోయారా?",
    noAccount: "ఖాతా లేదా?",
    hasAccount: "ఇప్పటికే ఖాతా ఉందా?",
    signUpLink: "నమోదు చేసుకోండి",
    signInLink: "లాగిన్ అవ్వండి",
    backHome: "సహాయకుడికి తిరిగి వెళ్ళండి",
    passwordMismatch: "పాస్‌వర్డ్‌లు సరిపోలడం లేదు.",
    checkEmail: "ధృవీకరణ ఇమెయిల్ పంపబడింది!",
    checkEmailDesc: "మీ ఖాతాను సక్రియం చేయడానికి మీ ఇన్‌బాక్స్‌లోని లింక్‌ను క్లిక్ చేయండి.",
    resetSent: "రీసెట్ లింక్ పంపబడింది!",
    resetSentDesc: "ఈ ఇమెయిల్‌తో ఖాతా ఉంటే రీసెట్ లింక్ వస్తుంది.",
    unconfiguredAlert: "Supabase కాన్ఫిగరేషన్ ఇంకా పూర్తి కాలేదు. .env.local ఫైల్ చూడండి.",
  },
  ta: {
    titleSignIn: "சஹாயகாவில் உள்நுழையவும்",
    titleSignUp: "உங்கள் கணக்கை உருவாக்கவும்",
    titleForgot: "கடவுச்சொல்லை மீட்டமைக்கவும்",
    subSignIn: "பொருத்தமான திட்டங்களைச் சேமிக்கவும், ஆவணங்களின் நிலையை அறியவும்.",
    subSignUp: "அரசு நலத்திட்டங்களை புக்மார்க் செய்ய சஹாயகாவில் இணையுங்கள்.",
    subForgot: "பதிவுசெய்த மின்னஞ்சல் முகவரியை உள்ளிடவும், மீட்பு இணைப்பை அனுப்புகிறோம்.",
    fullName: "முழு பெயர்",
    fullNamePlaceholder: "எ.கா: ரமேஷ் குமார்",
    email: "மின்னஞ்சல் முகவரி",
    emailPlaceholder: "name@example.com",
    password: "கடவுச்சொல்",
    passwordPlaceholder: "குறைந்தது 6 எழுத்துகள்",
    confirmPassword: "கடவுச்சொல்லை உறுதிப்படுத்தவும்",
    btnSignIn: "உள்நுழைக",
    btnSignUp: "கணக்கை உருவாக்கு",
    btnForgot: "இணைப்பை அனுப்பு",
    googleContinue: "Google மூலம் தொடரவும்",
    orDivider: "அல்லது மின்னஞ்சல் மூலம்",
    forgotLink: "கடவுச்சொல் மறந்துவிட்டதா?",
    noAccount: "கணக்கு இல்லையா?",
    hasAccount: "ஏற்கனவே கணக்கு உள்ளதா?",
    signUpLink: "பதிவு செய்யவும்",
    signInLink: "உள்நுழைக",
    backHome: "உதவியாளரிடம் திரும்பு",
    passwordMismatch: "கடவுச்சொற்கள் பொருந்தவில்லை.",
    checkEmail: "சரிபார்ப்பு மின்னஞ்சல் அனுப்பப்பட்டது!",
    checkEmailDesc: "உங்கள் கணக்கைச் செயல்படுத்த உங்கள் மின்னஞ்சல் இணைப்பைக் கிளிக் செய்யவும்.",
    resetSent: "மீட்டமைப்பு இணைப்பு அனுப்பப்பட்டது!",
    resetSentDesc: "கணக்கு இருந்தால் உங்கள் மின்னஞ்சலுக்கு இணைப்பு வரும்.",
    unconfiguredAlert: "Supabase உள்ளமைவு இன்னும் முடிக்கப்படவில்லை. .env.local ஐப் பார்க்கவும்.",
  },
  ml: {
    titleSignIn: "സഹായകയിലേക്ക് ലോഗിൻ ചെയ്യുക",
    titleSignUp: "നിങ്ങളുടെ അക്കൗണ്ട് സൃഷ്ടിക്കുക",
    titleForgot: "പാസ്‌വേഡ് പുനഃക്രമീകരിക്കുക",
    subSignIn: "അർഹമായ പദ്ധതികൾ സംരക്ഷിക്കുകയും രേഖകളുടെ പട്ടിക പരിശോധിക്കുകയും ചെയ്യുക.",
    subSignUp: "ക്ഷേമപദ്ധതികൾ സൂക്ഷിച്ചുവെക്കാൻ സഹായകയിൽ അംഗമാവുക.",
    subForgot: "രജിസ്റ്റർ ചെയ്ത ഇമെയിൽ നൽകുക, ഞങ്ങൾ റീസെറ്റ് ലിങ്ക് അയയ്ക്കാം.",
    fullName: "മുഴുവൻ പേര്",
    fullNamePlaceholder: "ഉദാ: രമേഷ് കുമാർ",
    email: "ഇമെയിൽ വിലാസം",
    emailPlaceholder: "name@example.com",
    password: "പാസ്‌വേഡ്",
    passwordPlaceholder: "കുറഞ്ഞത് 6 അക്ഷരങ്ങൾ",
    confirmPassword: "പാസ്‌വേഡ് സ്ഥിരീകരിക്കുക",
    btnSignIn: "ലോഗിൻ ചെയ്യുക",
    btnSignUp: "അക്കൗണ്ട് ഉണ്ടാക്കുക",
    btnForgot: "റീസെറ്റ് ലിങ്ക് അയക്കുക",
    googleContinue: "Google വഴി തുടരുക",
    orDivider: "അല്ലെങ്കിൽ ഇമെയിൽ വഴി",
    forgotLink: "പാസ്‌വേഡ് മറന്നോ?",
    noAccount: "അക്കൗണ്ട് ഇല്ലേ?",
    hasAccount: "ഇതിനകം അക്കൗണ്ട് ഉണ്ടോ?",
    signUpLink: "രജിസ്റ്റർ ചെയ്യുക",
    signInLink: "ലോഗിൻ ചെയ്യുക",
    backHome: "സഹായിലേക്ക് മടങ്ങുക",
    passwordMismatch: "പാസ്‌വേഡുകൾ പൊരുത്തപ്പെടുന്നില്ല.",
    checkEmail: "സ്ഥിരീകരണ ഇമെയിൽ അയച്ചു!",
    checkEmailDesc: "അക്കൗണ്ട് പ്രവർത്തനക്ഷമമാക്കാൻ ഇമെയിലിലെ ലിങ്കിൽ ക്ലിക്ക് ചെയ്യുക.",
    resetSent: "റീസെറ്റ് ലിങ്ക് അയച്ചു!",
    resetSentDesc: "അക്കൗണ്ട് ഉണ്ടെങ്കിൽ ഇമെയിലിലേക്ക് ലിങ്ക് ലഭിക്കും.",
    unconfiguredAlert: "Supabase കോൺഫിഗറേഷൻ ഇതുവരെ ചെയ്തിട്ടില്ല. .env.local പരിശോധിക്കുക.",
  },
};

function AuthContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [lang, setLang] = useState<Language>("en");
  const [mode, setMode] = useState<AuthMode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const t = AUTH_COPY[lang];
  const configured = isSupabaseConfigured();
  const redirectTo = searchParams.get("redirectTo") || "/";
  const urlError = searchParams.get("error");

  useEffect(() => {
    if (urlError) {
      setErrorMsg(urlError);
    }
  }, [urlError]);

  async function handleGoogleSignIn() {
    setErrorMsg(null);
    setSuccessMsg(null);

    if (!configured) {
      setErrorMsg(t.unconfiguredAlert);
      return;
    }

    setLoading(true);
    try {
      const supabase = createClient();
      const origin = typeof window !== "undefined" ? window.location.origin : "";
      const callbackUrl = `${origin}/auth/callback?redirectTo=${encodeURIComponent(redirectTo)}`;

      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: callbackUrl,
        },
      });

      if (error) throw error;
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to initialize Google authentication.");
      setLoading(false);
    }
  }

  async function handleEmailAuth(e: React.FormEvent) {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    if (!configured) {
      setErrorMsg(t.unconfiguredAlert);
      return;
    }

    if (mode === "signup" && password !== confirmPassword) {
      setErrorMsg(t.passwordMismatch);
      return;
    }

    setLoading(true);
    const supabase = createClient();
    const origin = typeof window !== "undefined" ? window.location.origin : "";

    try {
      if (mode === "signin") {
        const { error } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password,
        });
        if (error) throw error;
        router.push(redirectTo);
        router.refresh();
      } else if (mode === "signup") {
        const { data, error } = await supabase.auth.signUp({
          email: email.trim(),
          password,
          options: {
            data: {
              full_name: fullName.trim(),
              preferred_language: lang,
            },
            emailRedirectTo: `${origin}/auth/callback?redirectTo=${encodeURIComponent(redirectTo)}`,
          },
        });
        if (error) throw error;

        // If auto-confirmed or existing session
        if (data.session) {
          router.push(redirectTo);
          router.refresh();
        } else {
          setSuccessMsg(`${t.checkEmail} ${t.checkEmailDesc}`);
        }
      } else if (mode === "forgot") {
        const { error } = await supabase.auth.resetPasswordForEmail(email.trim(), {
          redirectTo: `${origin}/reset-password`,
        });
        if (error) throw error;
        setSuccessMsg(`${t.resetSent} ${t.resetSentDesc}`);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Authentication request failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-shell">
      {/* Top Header */}
      <header className="auth-header">
        <Link href="/login" className="auth-brand" aria-label="Sahayaka">
          <span className="brand-mark">
            <Landmark size={20} strokeWidth={1.8} />
          </span>
          <span className="brand-word">
            sahayaka<span>.</span>
          </span>
        </Link>

        <div className="auth-header-right">
          <div className="language-switch" aria-label="Language selection">
            <Languages size={14} />
            <button className={lang === "en" ? "active" : ""} onClick={() => setLang("en")}>
              EN
            </button>
            <span>/</span>
            <button className={lang === "kn" ? "active" : ""} onClick={() => setLang("kn")}>
              ಕನ್ನಡ
            </button>
            <span>/</span>
            <button className={lang === "te" ? "active" : ""} onClick={() => setLang("te")}>
              తెలుగు
            </button>
            <span>/</span>
            <button className={lang === "ta" ? "active" : ""} onClick={() => setLang("ta")}>
              தமிழ்
            </button>
            <span>/</span>
            <button className={lang === "ml" ? "active" : ""} onClick={() => setLang("ml")}>
              മലയാളം
            </button>
          </div>

          <div className="auth-portal-tag">
            <ShieldCheck size={14} />
            <span>{lang === "kn" ? "ಲಾಗಿನ್ ಅಗತ್ಯವಿದೆ" : lang === "te" ? "లాగిన్ అవసరం" : lang === "ta" ? "உள்நுழைவு தேவை" : lang === "ml" ? "ലോഗിൻ ആവശ്യമാണ്" : "Sign In Required"}</span>
          </div>
        </div>
      </header>

      {/* Main Form Container */}
      <main className="auth-main">
        <div className="auth-card">
          <div className="auth-card-head">
            <div className="auth-icon-badge">
              {mode === "forgot" ? <KeyRound size={20} /> : <Lock size={20} />}
            </div>
            <h1>
              {mode === "signin"
                ? t.titleSignIn
                : mode === "signup"
                ? t.titleSignUp
                : t.titleForgot}
            </h1>
            <p>
              {mode === "signin"
                ? t.subSignIn
                : mode === "signup"
                ? t.subSignUp
                : t.subForgot}
            </p>
          </div>

          {/* Mode Switch Tabs */}
          {mode !== "forgot" && (
            <div className="auth-tabs" role="tablist">
              <button
                type="button"
                role="tab"
                aria-selected={mode === "signin"}
                className={`auth-tab ${mode === "signin" ? "active" : ""}`}
                onClick={() => {
                  setMode("signin");
                  setErrorMsg(null);
                  setSuccessMsg(null);
                }}
              >
                {t.btnSignIn}
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={mode === "signup"}
                className={`auth-tab ${mode === "signup" ? "active" : ""}`}
                onClick={() => {
                  setMode("signup");
                  setErrorMsg(null);
                  setSuccessMsg(null);
                }}
              >
                {t.btnSignUp}
              </button>
            </div>
          )}

          {/* Google OAuth Button */}
          {mode !== "forgot" && (
            <>
              <button
                type="button"
                className="google-auth-button"
                onClick={handleGoogleSignIn}
                disabled={loading}
              >
                <svg className="google-icon" viewBox="0 0 24 24" width="18" height="18">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                  />
                </svg>
                <span>{t.googleContinue}</span>
              </button>

              <div className="auth-divider">
                <span className="auth-divider-line" />
                <span className="auth-divider-text">{t.orDivider}</span>
                <span className="auth-divider-line" />
              </div>
            </>
          )}

          {/* Feedback Banners */}
          {errorMsg && (
            <div className="auth-alert error" role="alert">
              <ShieldAlert size={16} />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="auth-alert success" role="status">
              <CheckCircle2 size={16} />
              <span>{successMsg}</span>
            </div>
          )}

          {/* Email / Password Form */}
          <form className="auth-form" onSubmit={handleEmailAuth}>
            {mode === "signup" && (
              <div className="auth-field">
                <label htmlFor="full-name">{t.fullName}</label>
                <div className="auth-input-wrap">
                  <User size={16} className="auth-input-icon" />
                  <input
                    id="full-name"
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder={t.fullNamePlaceholder}
                    disabled={loading}
                  />
                </div>
              </div>
            )}

            <div className="auth-field">
              <label htmlFor="email">{t.email}</label>
              <div className="auth-input-wrap">
                <Mail size={16} className="auth-input-icon" />
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={t.emailPlaceholder}
                  disabled={loading}
                />
              </div>
            </div>

            {mode !== "forgot" && (
              <div className="auth-field">
                <div className="auth-field-row">
                  <label htmlFor="password">{t.password}</label>
                  {mode === "signin" && (
                    <button
                      type="button"
                      className="auth-text-link"
                      onClick={() => {
                        setMode("forgot");
                        setErrorMsg(null);
                        setSuccessMsg(null);
                      }}
                    >
                      {t.forgotLink}
                    </button>
                  )}
                </div>
                <div className="auth-input-wrap">
                  <Lock size={16} className="auth-input-icon" />
                  <input
                    id="password"
                    type="password"
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder={t.passwordPlaceholder}
                    disabled={loading}
                  />
                </div>
              </div>
            )}

            {mode === "signup" && (
              <div className="auth-field">
                <label htmlFor="confirm-password">{t.confirmPassword}</label>
                <div className="auth-input-wrap">
                  <Lock size={16} className="auth-input-icon" />
                  <input
                    id="confirm-password"
                    type="password"
                    required
                    minLength={6}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder={t.passwordPlaceholder}
                    disabled={loading}
                  />
                </div>
              </div>
            )}

            <button type="submit" className="auth-submit-btn" disabled={loading}>
              {loading ? (
                <span className="auth-btn-loading">
                  <LoaderCircle size={16} className="spin" />
                  <span>Processing…</span>
                </span>
              ) : mode === "signin" ? (
                t.btnSignIn
              ) : mode === "signup" ? (
                t.btnSignUp
              ) : (
                t.btnForgot
              )}
            </button>
          </form>

          {/* Card Footer Switcher */}
          <div className="auth-card-footer">
            {mode === "signin" && (
              <p>
                {t.noAccount}{" "}
                <button
                  type="button"
                  className="auth-link-btn"
                  onClick={() => {
                    setMode("signup");
                    setErrorMsg(null);
                    setSuccessMsg(null);
                  }}
                >
                  {t.signUpLink}
                </button>
              </p>
            )}

            {mode === "signup" && (
              <p>
                {t.hasAccount}{" "}
                <button
                  type="button"
                  className="auth-link-btn"
                  onClick={() => {
                    setMode("signin");
                    setErrorMsg(null);
                    setSuccessMsg(null);
                  }}
                >
                  {t.signInLink}
                </button>
              </p>
            )}

            {mode === "forgot" && (
              <p>
                <button
                  type="button"
                  className="auth-link-btn"
                  onClick={() => {
                    setMode("signin");
                    setErrorMsg(null);
                    setSuccessMsg(null);
                  }}
                >
                  ← {t.signInLink}
                </button>
              </p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="auth-shell" />}>
      <AuthContent />
    </Suspense>
  );
}

