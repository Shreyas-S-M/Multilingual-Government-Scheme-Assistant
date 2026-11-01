"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ArrowLeft, ExternalLink, FileText, Landmark, Printer, Search, ShieldCheck, X } from "lucide-react";
import policies from "@/lib/policies.json";

type Policy = any;

export default function PoliciesPage() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [level, setLevel] = useState("all");
  const [language, setLanguage] = useState<"en" | "kn">("en");
  const [textSize, setTextSize] = useState<"normal" | "large" | "xlarge">("normal");

  const copy = language === "en" ? {
    back: "Back to assistant",
    eyebrow: "COMPLETE SCHEME DIRECTORY",
    title: "Explore all 57 government schemes",
    sub: "Browse the official scheme catalogue available in Sahayaka across Central & Karnataka state departments. Check rules, benefits, and required documents before applying.",
    search: "Search schemes, benefits, departments…",
    all: "All categories",
    central: "Central Government",
    state: "Karnataka State",
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
  } : {
    back: "ಸಹಾಯಕಕ್ಕೆ ಹಿಂತಿರುಗಿ",
    eyebrow: "ಸಂಪೂರ್ಣ ಯೋಜನೆಗಳ ಪಟ್ಟಿ",
    title: "ಎಲ್ಲಾ 57 ಸರ್ಕಾರಿ ಯೋಜನೆಗಳನ್ನು ಅನ್ವೇಷಿಸಿ",
    sub: "ಕೇಂದ್ರ ಮತ್ತು ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಎಲ್ಲಾ ಇಲಾಖೆಗಳ ಅಧಿಕೃತ ಯೋಜನೆಗಳ ಪಟ್ಟಿಯನ್ನು ನೋಡಿ. ಅರ್ಜಿ ಸಲ್ಲಿಸುವ ಮೊದಲು ನಿಯಮಗಳು, ಪ್ರಯೋಜನಗಳು ಮತ್ತು ದಾಖಲೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
    search: "ಯೋಜನೆ, ಪ್ರಯೋಜನ ಅಥವಾ ಇಲಾಖೆಯನ್ನು ಹುಡುಕಿ…",
    all: "ಎಲ್ಲಾ ವಿಭಾಗಗಳು",
    central: "ಕೇಂದ್ರ ಸರ್ಕಾರ",
    state: "ಕರ್ನಾಟಕ ರಾಜ್ಯ",
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
  };

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
    { id: "all", label: language === "kn" ? "ಎಲ್ಲಾ (57)" : "All (57)" },
    { id: "Agriculture", label: language === "kn" ? "🌾 ಕೃಷಿ & ರೈತರು" : "🌾 Agriculture" },
    { id: "Education", label: language === "kn" ? "🎓 ಶಿಕ್ಷಣ & ವಿದ್ಯಾರ್ಥಿವೇತನ" : "🎓 Education" },
    { id: "Social Welfare", label: language === "kn" ? "👵 ಸಾಮಾಜಿಕ ಕಲ್ಯಾಣ & ಪಿಂಚಣಿ" : "👵 Social Welfare & Pension" },
    { id: "Employment", label: language === "kn" ? "💼 ಉದ್ಯೋಗ & ವ್ಯಾಪಾರ" : "💼 Employment" },
    { id: "Healthcare", label: language === "kn" ? "🏥 ಆರೋಗ್ಯ & ವಿಮೆ" : "🏥 Healthcare" },
    { id: "Women and Child Welfare", label: language === "kn" ? "👩 ಮಹಿಳಾ ಕಲ್ಯಾಣ" : "👩 Women Welfare" },
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
            <button className={textSize === "normal" ? "active" : ""} onClick={() => setTextSize("normal")}>
              A
            </button>
            <button className={textSize === "large" ? "active" : ""} onClick={() => setTextSize("large")}>
              A+
            </button>
            <button className={textSize === "xlarge" ? "active" : ""} onClick={() => setTextSize("xlarge")}>
              A++
            </button>
          </div>

          <button className="print-button" onClick={() => window.print()} title={copy.print}>
            <Printer size={13} /> {copy.print}
          </button>

          <div className="language-switch" aria-label="Language">
            <button className={language === "en" ? "active" : ""} onClick={() => setLanguage("en")}>
              EN
            </button>
            <span>/</span>
            <button className={language === "kn" ? "active" : ""} onClick={() => setLanguage("kn")}>
              ಕನ್ನಡ
            </button>
          </div>
        </div>
      </header>

      <section className="policies-main">
        <Link href="/" className="policies-back">
          <ArrowLeft size={15} /> {copy.back}
        </Link>
        <div className="policies-hero">
          <div className="eyebrow">
            <span className="eyebrow-line" />
            {copy.eyebrow}
          </div>
          <h1>{copy.title}</h1>
          <p>{copy.sub}</p>
          <div className="policies-count">
            <Landmark size={17} />
            <strong>{filtered.length}</strong> {copy.results}
          </div>
        </div>

        {/* Quick Category Filter Pills for All Age Brackets */}
        <div className="category-pills">
          {QUICK_PILLS.map((pill) => (
            <button
              key={pill.id}
              className={`category-pill ${category === pill.id ? "active" : ""}`}
              onClick={() => setCategory(pill.id)}
            >
              {pill.label}
            </button>
          ))}
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
