"use client";

export const dynamic = "force-dynamic";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Briefcase, ExternalLink, FileText, GraduationCap, HeartPulse, Landmark, Printer, Search, ShieldCheck, Sprout, UserRound, Users, X } from "lucide-react";
import policies from "@/lib/policies.json";
import { AuthNav } from "@/components/AuthNav";
import { SaveSchemeButton } from "@/components/SaveSchemeButton";
import { createClient, isSupabaseConfigured } from "@/lib/supabase/client";
import { fetchUserPreferredLanguage, persistUserPreferredLanguage } from "@/lib/supabase/profile";
import type { Language } from "@/lib/types";

type Policy = any;

export default function PoliciesPage() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [level, setLevel] = useState("all");
  const [language, setLanguage] = useState<Language>("en");
  const [textSize, setTextSize] = useState<"normal" | "large" | "xlarge">("normal");
  const [authUserId, setAuthUserId] = useState<string | null>(null);

  useEffect(() => {
    if (isSupabaseConfigured()) {
      const supabase = createClient();
      supabase.auth.getUser().then(async ({ data: { user } }) => {
        if (!user) {
          router.replace("/login?redirectTo=/policies");
          return;
        }
        setAuthUserId(user.id);
        const savedLang = await fetchUserPreferredLanguage(supabase, user.id);
        if (savedLang) {
          setLanguage(savedLang);
        }
      });
    }
  }, [router]);

  function handleLanguageChange(nextLang: Language) {
    setLanguage(nextLang);
    if (authUserId) {
      const supabase = createClient();
      void persistUserPreferredLanguage(supabase, authUserId, nextLang);
    }
  }

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  useEffect(() => {
    try {
      const savedSize = localStorage.getItem("sahayaka_text_size");
      if (savedSize === "normal" || savedSize === "large" || savedSize === "xlarge") {
        setTextSize(savedSize);
      }
    } catch {}
  }, []);

  function handleTextSizeChange(nextSize: "normal" | "large" | "xlarge") {
    setTextSize(nextSize);
    try {
      localStorage.setItem("sahayaka_text_size", nextSize);
    } catch {}
  }

  const copyMap = {
    en: {
      back: "Back to assistant",
      eyebrow: "COMPLETE SCHEME DIRECTORY",
      title: "Explore all 111 government schemes",
      sub: "Browse the official scheme catalogue available in Sahayaka across Central & South Indian state departments (Andhra Pradesh, Karnataka, Kerala, Tamil Nadu). Check rules, benefits, and required documents before applying.",
      search: "Search schemes, benefits, departments…",
      all: "All categories",
      central: "Central Government",
      state: "State Government",
      results: "schemes listed",
      review: "Needs verification",
      catalogue: "Verified Entry",
      department: "Department",
      benefit: "Benefits",
      criteria: "Eligibility criteria in catalogue",
      documents: "Documents to prepare",
      steps: "Application guidance",
      official: "Open official portal",
      disclaimer: "This directory is for public discovery and academic research. The official government portal is always the authoritative source.",
      noResults: "No schemes match those filters. Try another search or select 'All'.",
      textSize: "Text Size",
      clear: "Clear search",
      print: "Print Catalogue",
    },
    kn: {
      back: "ಸಹಾಯಕಕ್ಕೆ ಹಿಂತಿರುಗಿ",
      eyebrow: "ಸಂಪೂರ್ಣ ಯೋಜನೆಗಳ ಪಟ್ಟಿ",
      title: "ಎಲ್ಲಾ 111 ಸರ್ಕಾರಿ ಯೋಜನೆಗಳನ್ನು ಅನ್ವೇಷಿಸಿ",
      sub: "ಕೇಂದ್ರ, ಕರ್ನಾಟಕ, ಆಂಧ್ರಪ್ರದೇಶ, ಕೇರಳ ಮತ್ತು ತಮಿಳುನಾಡು ಸರ್ಕಾರಗಳ ಅಧಿಕೃತ ಯೋಜನೆಗಳ ಪಟ್ಟಿಯನ್ನು ನೋಡಿ. ಅರ್ಜಿ ಸಲ್ಲಿಸುವ ಮೊದಲು ನಿಯಮಗಳು, ಪ್ರಯೋಜನಗಳು ಮತ್ತು ದಾಖಲೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
      search: "ಯೋಜನೆ, ಪ್ರಯೋಜನ ಅಥವಾ ಇಲಾಖೆಯನ್ನು ಹುಡುಕಿ…",
      all: "ಎಲ್ಲಾ ವಿಭಾಗಗಳು",
      central: "ಕೇಂದ್ರ ಸರ್ಕಾರ",
      state: "ರಾಜ್ಯ ಸರ್ಕಾರ",
      results: "ಯೋಜನೆಗಳು",
      review: "ಪರಿಶೀಲನೆ ಅಗತ್ಯ",
      catalogue: "ದೃಢೀಕೃತ ದಾಖಲೆ",
      department: "ಇಲಾಖೆ",
      benefit: "ಪ್ರಯೋಜನಗಳು",
      criteria: "ಪಟ್ಟಿಯಲ್ಲಿರುವ ಅರ್ಹತಾ ಮಾನದಂಡಗಳು",
      documents: "ಸಿದ್ಧಪಡಿಸಬೇಕಾದ ದಾಖಲೆಗಳು",
      steps: "ಅರ್ಜಿ ಮಾರ್ಗದರ್ಶನ",
      official: "ಅಧಿಕೃತ ಪೋರ್ಟಲ್ ತೆರೆಯಿರಿ",
      disclaimer: "ಈ ಪಟ್ಟಿ ಸಾರ್ವಜನಿಕ ಮಾಹಿತಿ ಮತ್ತು ಶೈಕ್ಷಣಿಕ ಸಂಶೋಧನೆಗಾಗಿ. ಅಧಿಕೃತ ಸರ್ಕಾರಿ ಪೋರ್ಟಲ್ ಅಂತಿಮ ಮೂಲವಾಗಿದೆ.",
      noResults: "ಈ ಫಿಲ್ಟರ್‌ಗಳಿಗೆ ಹೊಂದುವ ಯೋಜನೆಗಳಿಲ್ಲ. ಬೇರೆ ಹುಡುಕಾಟ ಅಥವಾ 'ಎಲ್ಲಾ' ಆಯ್ಕೆಮಾಡಿ.",
      textSize: "ಅಕ್ಷರ ಗಾತ್ರ",
      clear: "ಹುಡುಕಾಟ ತೆರವುಗೊಳಿಸಿ",
      print: "ಪಟ್ಟಿ ಮುದ್ರಿಸಿ",
    },
    te: {
      back: "సహాయకుడికి తిరిగి వెళ్ళండి",
      eyebrow: "పూర్తి పథకాల డైరెక్టరీ",
      title: "మొత్తం 111 ప్రభుత్వ పథకాలను అన్వేషించండి",
      sub: "కేంద్ర, ఆంధ్రప్రదేశ్, కర్ణాటక, కేరళ, తమిళనాడు రాష్ట్రాల అధికారిక సంక్షేమ పథకాలను చూడండి. దరఖాస్తు చేయడానికి ముందు నిబంధనలు, ప్రయోజనాలు మరియు పత్రాలను తనిఖీ చేయండి.",
      search: "పథకాలు, ప్రయోజనాలు, శాఖలను వెతకండి…",
      all: "అన్ని వర్గాలు",
      central: "కేంద్ర ప్రభుత్వం",
      state: "రాష్ట్ర ప్రభుత్వం",
      results: "పథకాలు నమోదయ్యాయి",
      review: "పరిశీలన అవసరం",
      catalogue: "ధృవీకరించబడిన పథకం",
      department: "శాఖ",
      benefit: "ప్రయోజనాలు",
      criteria: "కేటలాగ్‌లోని అర్హత నిబంధనలు",
      documents: "సిద్ధం చేసుకోవాల్సిన పత్రాలు",
      steps: "దరఖాస్తు మార్గదర్శకత్వం",
      official: "అధికారిక పోర్టల్ తెరవండి",
      disclaimer: "ఈ డైరెక్టరీ సమాచార అవగాహన మరియు విద్యా పరిశోధన కోసం మాత్రమే. అధికారిక ప్రభుత్వ పోర్టల్ మాత్రమే ప్రామాణికమైనది.",
      noResults: "ఈ ఫిల్టర్‌లకు సరిపోలే పథకాలు లేవు. వేరొక శోధన ప్రయత్నించండి లేదా 'అన్ని' ఎంచుకోండి.",
      textSize: "అక్షర పరిమాణం",
      clear: "శోధనను క్లియర్ చేయండి",
      print: "కేటలాగ్ ప్రింట్ చేయండి",
    },
    ta: {
      back: "உதவியாளரிடம் திரும்பு",
      eyebrow: "முழு திட்டங்களின் பட்டியல்",
      title: "அனைத்து 111 அரசு திட்டங்களையும் காண்க",
      sub: "மத்திய, தமிழ்நாடு, கர்நாடகா, ஆந்திரா, கேரளா அரசுகளின் அதிகாரப்பூர்வ திட்டங்களின் அட்டவணையைப் பாருங்கள். விண்ணப்பிக்கும் முன் விதிமுறைகள், பயன்கள், ஆவணங்களைச் சரிபார்க்கவும்.",
      search: "திட்டங்கள், பயன்கள், துறைகளைத் தேடுங்கள்…",
      all: "அனைத்துப் பிரிவுகள்",
      central: "மத்திய அரசு",
      state: "மாநில அரசு",
      results: "திட்டங்கள் பட்டியலிடப்பட்டுள்ளன",
      review: "சரிபார்ப்பு தேவை",
      catalogue: "சான்றளிக்கப்பட்ட பதிவு",
      department: "துறை",
      benefit: "பயன்கள்",
      criteria: "பட்டியலில் உள்ள தகுதி வரம்புகள்",
      documents: "தயார் செய்ய வேண்டிய ஆவணங்கள்",
      steps: "விண்ணப்ப வழிகாட்டுதல்",
      official: "அதிகாரப்பூர்வ தளம் திறக்க",
      disclaimer: "இந்தத் தொகுப்பு தகவல் அறியும் கல்வி ஆய்வுக்காக மட்டுமே. அதிகாரப்பூர்வ அரசு போர்ட்டலே இறுதியானது.",
      noResults: "வடிகட்டிகளுக்குப் பொருத்தமான திட்டங்கள் இல்லை. வேறு தேடலை முயற்சிக்கவும் அல்லது 'அனைத்தும்' தேர்ந்தெடுக்கவும்.",
      textSize: "எழுத்து அளவு",
      clear: "தேடலை அழிக்கவும்",
      print: "பட்டியலை அச்சிடுக",
    },
    ml: {
      back: "സഹായിലേക്ക് മടങ്ങുക",
      eyebrow: "പൂർണ്ണ പദ്ധതി ഡയറക്ടറി",
      title: "എല്ലാ 111 സർക്കാർ പദ്ധതികളും അറിയുക",
      sub: "കേന്ദ്ര, കേരള, കർണാടക, ആന്ധ്രാപ്രദേശ്, തമിഴ്നാട് സർക്കാരുകളുടെ ഔദ്യോഗിക ക്ഷേമപദ്ധതികൾ പരിശോധിക്കുക. അപേക്ഷിക്കുന്നതിന് മുമ്പ് നിബന്ധനകളും രേഖകളും പരിശോധിക്കുക.",
      search: "പദ്ധതികൾ, ആനുകൂല്യങ്ങൾ, വകുപ്പുകൾ തിരയുക…",
      all: "എല്ലാ വിഭാഗങ്ങളും",
      central: "കേന്ദ്ര സർക്കാർ",
      state: "സംസ്ഥാന സർക്കാർ",
      results: "പദ്ധതികൾ ലിസ്റ്റ് ചെയ്തിട്ടുണ്ട്",
      review: "പരിശോധന ആവശ്യമാണ്",
      catalogue: "സ്ഥിരീകരിച്ച രേഖ",
      department: "വകുപ്പ്",
      benefit: "ആനുകൂല്യങ്ങൾ",
      criteria: "ലിസ്റ്റിലുള്ള യോഗ്യതാ മാനദണ്ഡങ്ങൾ",
      documents: "തയ്യാറാക്കേണ്ട രേഖകൾ",
      steps: "അപേക്ഷാ മാർഗ്ഗനിർദ്ദേശം",
      official: "ഔദ്യോഗിക പോർട്ടൽ തുറക്കുക",
      disclaimer: "ഈ ഡയറക്ടറി പൊതുജന വിവരങ്ങൾക്കും വിദ്യാഭ്യാസ ഗവേഷണത്തിനുമുള്ളതാണ്. ഔദ്യോഗിക സർക്കാർ പോർട്ടലാണ് അവസാന വാക്ക്.",
      noResults: "ഈ ഫിൽട്ടറുകളുമായി പൊരുത്തപ്പെടുന്ന പദ്ധതികളൊന്നുമില്ല. മറ്റൊരു തിരച്ചിൽ നടത്തുക അല്ലെങ്കിൽ 'എല്ലാം' തിരഞ്ഞെടുക്കുക.",
      textSize: "അക്ഷര വലുപ്പം",
      clear: "തിരച്ചിൽ മായ്‌ക്കുക",
      print: "ലിസ്റ്റ് പ്രിന്റ് ചെയ്യുക",
    },
  };
  const copy = copyMap[language];

  const categories = useMemo(
    () => Array.from(new Set(policies.map((p) => p.category).filter(Boolean))).sort(),
    []
  );

  const filtered = useMemo(() => {
    return policies.filter((p) => {
      const text = `${p.name} ${p.name_kannada ?? ""} ${p.short_description ?? ""} ${p.department ?? ""} ${p.category ?? ""} ${p.subcategory ?? ""}`.toLowerCase();
      const matchesQuery = text.includes(query.toLowerCase().trim());
      const matchesCategory = category === "all" || p.category === category;
      const matchesLevel = level === "all" || (level === "central" ? p.level === "central" : p.level !== "central");
      return matchesQuery && matchesCategory && matchesLevel;
    });
  }, [query, category, level]);

  const QUICK_PILLS = [
    {
      id: "all",
      icon: Landmark,
      label:
        language === "kn"
          ? "ಎಲ್ಲಾ (111)"
          : language === "te"
            ? "అన్ని (111)"
            : language === "ta"
              ? "அனைத்தும் (111)"
              : language === "ml"
                ? "എല്ലാം (111)"
                : "All (111)",
    },
    {
      id: "Agriculture",
      icon: Sprout,
      label:
        language === "kn"
          ? "ಕೃಷಿ & ರೈತರು"
          : language === "te"
            ? "వ్యవసాయం & రైతులు"
            : language === "ta"
              ? "வேளாண்மை & விவசாயிகள்"
              : language === "ml"
                ? "കൃഷി & കർഷകർ"
                : "Agriculture",
    },
    {
      id: "Education",
      icon: GraduationCap,
      label:
        language === "kn"
          ? "ಶಿಕ್ಷಣ & ವಿದ್ಯಾರ್ಥಿವೇತನ"
          : language === "te"
            ? "విద్య & స్కాలర్‌షిప్‌లు"
            : language === "ta"
              ? "கல்வி & உதவித்தொகை"
              : language === "ml"
                ? "വിദ്യാഭ്യാസം & സ്കോളർഷിപ്പ്"
                : "Education",
    },
    {
      id: "Social Welfare",
      icon: Users,
      label:
        language === "kn"
          ? "ಸಾಮಾಜಿಕ ಕಲ್ಯಾಣ & ಪಿಂಚಣಿ"
          : language === "te"
            ? "సాంఘిక సంక్షేమం & పింఛను"
            : language === "ta"
              ? "சமூக நலம் & ஓய்வூதியம்"
              : language === "ml"
                ? "സാമൂഹികക്ഷേമം & പെൻഷൻ"
                : "Social Welfare & Pension",
    },
    {
      id: "Employment",
      icon: Briefcase,
      label:
        language === "kn"
          ? "ಉದ್ಯೋಗ & ವ್ಯಾಪಾರ"
          : language === "te"
            ? "ఉపాధి & వ్యాపారం"
            : language === "ta"
              ? "வேலைவாய்ப்பு & தொழில்"
              : language === "ml"
                ? "തൊഴിൽ & സംരംഭം"
                : "Employment",
    },
    {
      id: "Healthcare",
      icon: HeartPulse,
      label:
        language === "kn"
          ? "ಆರೋಗ್ಯ & ವಿಮೆ"
          : language === "te"
            ? "ఆరోగ్యం & బీమా"
            : language === "ta"
              ? "மருத்துவம் & காப்பீடு"
              : language === "ml"
                ? "ആരോഗ്യം & ഇൻഷുറൻസ്"
                : "Healthcare",
    },
    {
      id: "Women and Child Welfare",
      icon: UserRound,
      label:
        language === "kn"
          ? "ಮಹಿಳಾ ಕಲ್ಯಾಣ"
          : language === "te"
            ? "మహిళా సంక్షేమం"
            : language === "ta"
              ? "மகளிர் நலம்"
              : language === "ml"
                ? "വനിതാക്ഷേമം"
                : "Women Welfare",
    },
  ];

  return (
    <main className={`policies-page text-size-${textSize}`}>
      <header className="topbar policies-topbar">
        <Link className="brand" href="/" aria-label="Sahayaka home">
          <span className="brand-mark">
            <Landmark size={21} strokeWidth={1.8} />
          </span>
          <span className="brand-word">
            sahayaka<span>.</span>
            <small>PUBLIC BENEFITS, MADE CLEAR</small>
          </span>
        </Link>
        <div className="topbar-right">
          <div className="font-size-switch" aria-label={copy.textSize} title={copy.textSize}>
            <span>{copy.textSize}:</span>
            <button type="button" className={textSize === "normal" ? "active" : ""} onClick={() => handleTextSizeChange("normal")}>
              A
            </button>
            <button type="button" className={textSize === "large" ? "active" : ""} onClick={() => handleTextSizeChange("large")}>
              A+
            </button>
            <button type="button" className={textSize === "xlarge" ? "active" : ""} onClick={() => handleTextSizeChange("xlarge")}>
              A++
            </button>
          </div>

          <button className="print-button" onClick={() => window.print()} title={copy.print}>
            <Printer size={13} /> {copy.print}
          </button>

          <div className="language-switch" aria-label="Language">
            <button className={language === "en" ? "active" : ""} onClick={() => handleLanguageChange("en")}>
              EN
            </button>
            <span>/</span>
            <button className={language === "kn" ? "active" : ""} onClick={() => handleLanguageChange("kn")}>
              ಕನ್ನಡ
            </button>
            <span>/</span>
            <button className={language === "te" ? "active" : ""} onClick={() => handleLanguageChange("te")}>
              తెలుగు
            </button>
            <span>/</span>
            <button className={language === "ta" ? "active" : ""} onClick={() => handleLanguageChange("ta")}>
              தமிழ்
            </button>
            <span>/</span>
            <button className={language === "ml" ? "active" : ""} onClick={() => handleLanguageChange("ml")}>
              മലയാളം
            </button>
          </div>

          <AuthNav lang={language} />
        </div>
      </header>

      <section className="policies-main">
        <Link href="/" className="policies-back">
          <ArrowLeft size={15} /> {copy.back}
        </Link>
        <div className="policies-hero">

          <h1>{copy.title}</h1>
          <p>{copy.sub}</p>
          <div className="policies-count">
            <Landmark size={17} />
            <strong>{filtered.length}</strong> {copy.results}
          </div>
        </div>

        {/* Quick Category Filter Pills for All Age Brackets */}
        <div className="category-pills">
          {QUICK_PILLS.map((pill) => {
            const Icon = pill.icon;
            return (
              <button
                key={pill.id}
                className={`category-pill ${category === pill.id ? "active" : ""}`}
                onClick={() => setCategory(pill.id)}
              >
                <Icon size={14} strokeWidth={1.8} />
                <span>{pill.label}</span>
              </button>
            );
          })}
        </div>

        <div className="policy-filters">
          <label className="policy-search">
            <Search size={17} />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={copy.search}
              aria-label={copy.search}
            />
            {query.length > 0 && (
              <button
                type="button"
                className="composer-clear"
                onClick={() => setQuery("")}
                title={copy.clear}
                aria-label={copy.clear}
              >
                <X size={15} />
              </button>
            )}
          </label>
          <select aria-label={copy.all} value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="all">{copy.all}</option>
            {categories.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
          <select aria-label="Scheme level" value={level} onChange={(e) => setLevel(e.target.value)}>
            <option value="all">All levels</option>
            <option value="central">{copy.central}</option>
            <option value="state">{copy.state}</option>
          </select>
        </div>

        {filtered.length === 0 ? (
          <div className="policies-empty">{copy.noResults}</div>
        ) : (
          <div className="policy-grid">
            {filtered.map((policy: Policy) => {
              const needsReview = policy.review_status === "needs_review" || policy.source_reliability === "low";
              return (
                <article className="policy-card" key={policy.scheme_id}>
                  <div className="policy-card-meta">
                    <span className="policy-category">{policy.category}</span>
                    <span className={`policy-review ${needsReview ? "needs-review" : "catalogue-status"}`}>
                      {needsReview ? copy.review : copy.catalogue}
                    </span>
                    <div style={{ marginLeft: "auto" }}>
                      <SaveSchemeButton
                        schemeId={policy.scheme_id}
                        schemeName={language === "kn" && policy.name_kannada ? policy.name_kannada : policy.name}
                        category={policy.category}
                        benefitsSummary={policy.benefits_summary}
                        officialPortalUrl={policy.official_portal_url || policy.url}
                        lang={language}
                      />
                    </div>
                  </div>
                  <h2>{language === "kn" && policy.name_kannada ? policy.name_kannada : policy.name}</h2>
                  {language === "kn" && policy.name_kannada && <p className="policy-english-name">{policy.name}</p>}
                  <p className="policy-description">
                    {language === "kn" && policy.detailed_description ? policy.detailed_description : policy.short_description}
                  </p>
                  <div className="policy-detail">
                    <strong>{copy.department}</strong>
                    <span>{policy.department || "Not specified in catalogue"}</span>
                  </div>
                  {policy.benefits_summary && (
                    <div className="policy-detail">
                      <strong>{copy.benefit}</strong>
                      <span>{policy.benefits_summary}</span>
                    </div>
                  )}
                  {Array.isArray(policy.rules) && policy.rules.length > 0 && (
                    <details className="policy-expand">
                      <summary>
                        <ShieldCheck size={14} />
                        {copy.criteria}
                      </summary>
                      <ul>
                        {policy.rules.map(
                          (
                            rule: {
                              name?: string;
                              field?: string;
                              operator?: string;
                              expected_value?: unknown;
                              is_mandatory?: boolean;
                              source_citation?: string;
                            },
                            i: number
                          ) => (
                            <li key={`${policy.scheme_id}-rule-${i}`}>
                              <strong>{rule.name || rule.field || "Eligibility criterion"}</strong>
                              {rule.expected_value !== undefined
                                ? ` — ${String(rule.operator || "requires").replaceAll("_", " ")} ${String(rule.expected_value)}`
                                : ""}
                              {rule.is_mandatory ? " (mandatory)" : ""}
                              {rule.source_citation ? ` · ${rule.source_citation}` : ""}
                            </li>
                          )
                        )}
                      </ul>
                    </details>
                  )}
                  {Array.isArray(policy.required_documents) && policy.required_documents.length > 0 && (
                    <details className="policy-expand">
                      <summary>
                        <FileText size={14} />
                        {copy.documents}
                      </summary>
                      <ul>
                        {policy.required_documents.map((doc: string, i: number) => (
                          <li key={`${policy.scheme_id}-doc-${i}`}>{doc}</li>
                        ))}
                      </ul>
                    </details>
                  )}
                  {Array.isArray(policy.application_process) && policy.application_process.length > 0 && (
                    <details className="policy-expand">
                      <summary>
                        <ShieldCheck size={14} />
                        {copy.steps}
                      </summary>
                      <ol>
                        {policy.application_process.map((step: string, i: number) => (
                          <li key={`${policy.scheme_id}-step-${i}`}>{step}</li>
                        ))}
                      </ol>
                    </details>
                  )}
                  <div className="policy-card-footer">
                    {policy.official_portal_url ? (
                      <a href={policy.official_portal_url} target="_blank" rel="noreferrer">
                        {copy.official}
                        <ExternalLink size={13} />
                      </a>
                    ) : (
                      <span>No official URL listed</span>
                    )}
                    <span>{policy.level === "central" ? copy.central : copy.state}</span>
                  </div>
                </article>
              );
            })}
          </div>
        )}
        <p className="policies-disclaimer">{copy.disclaimer}</p>
      </section>
    </main>
  );
}
