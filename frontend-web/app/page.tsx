"use client";

import { FormEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import {
  ArrowDown,
  ArrowRight,
  Check,
  CheckCheck,
  ChevronDown,
  CircleHelp,
  ExternalLink,
  FileText,
  GraduationCap,
  HeartHandshake,
  Landmark,
  Languages,
  LoaderCircle,
  Plus,
  Printer,
  RotateCcw,
  Send,
  ShieldCheck,
  Sparkles,
  Sprout,
  UserRound,
  Users,
  X,
} from "lucide-react";
import type { ChatMessage, ChatResponse, Language, Profile, SchemeResult } from "@/lib/types";

const COPY = {
  en: {
    gov: "GOVERNMENT SCHEME ASSISTANT",
    title: "Public welfare benefits, made clear for everyone.",
    subtitle: "Simple, transparent guidance for seniors, farmers, students, and families across Central & Karnataka government programs.",
    placeholder: "Type in English or ಕನ್ನಡ, e.g. 'I am 65 years old seeking pension in Karnataka'…",
    send: "Send message",
    start: "Start a conversation",
    examples: "SELECT YOUR CITIZEN CATEGORY TO START QUICKLY",
    privacy: "Your details are used solely in this session to evaluate scheme rules under the DPDP Act 2023.",
    profile: "YOUR PROFILE",
    profileSub: "Attributes recorded from your answers",
    emptyProfile: "Your details will appear here as you chat.",
    age: "Age",
    income: "Annual family income",
    state: "State",
    work: "Occupation",
    education: "Education",
    category: "Social category",
    status: "Assessment status",
    discovered: "MATCHED SCHEMES",
    noMatches: "Matched schemes will appear here once you share your basic profile details.",
    pass: "Appears eligible",
    unknown: "More details needed",
    fail: "Criteria not met",
    source: "Official source",
    benefit: "Benefit",
    missing: "Still needed",
    reset: "New conversation",
    online: "Assistant service",
    connected: "API connected",
    offline: "API unavailable",
    greeting: "Namaskara! Welcome!",
    greetingText: "I can help you explore Central and Karnataka government schemes. Select a category below or tell me your age, where you live, your occupation, or what support you need.",
    clear: "Clear conversation",
    typing: "Checking official scheme criteria…",
    results: "Based on details shared",
    notGuarantee: "Preliminary guidance only. Final eligibility is determined by the relevant government department.",
    evidence: "WHY THIS MATCH",
    verified: "Official portal",
    language: "Language",
    sources: "Sources",
    details: "View criteria rules",
    hide: "Hide criteria",
    profileNote: "Only details you provide are used. Sensitive attributes are never guessed or inferred.",
    startOver: "Start over",
    intro: "A simpler path to public welfare schemes",
    apiError: "I couldn't connect to the assistant service. Please check that the FastAPI backend is running and try again.",
    disclaimer: "Sahayaka is an academic public service project and does not represent a government department. Always confirm details on the official portal.",
    textSize: "Text Size",
    howItWorks: "HOW SAHAYAKA HELPS YOU",
    step1Title: "1. Share Details",
    step1Sub: "Tell your age, occupation & state in your own words.",
    step2Title: "2. Rule Check",
    step2Sub: "We check statutory criteria without guessing.",
    step3Title: "3. Get Benefits",
    step3Sub: "Official application links & document checklists.",
    printSlip: "Print / Save Document Slip",
    docChecklistTitle: "Required Documents Checklist",
    docsReady: "ready to apply",
  },
  kn: {
    gov: "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಸಹಾಯಕ",
    title: "ಎಲ್ಲರಿಗೂ ಸುಲಭವಾಗಿ ಅರ್ಥವಾಗುವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು.",
    subtitle: "ಕೇಂದ್ರ ಮತ್ತು ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಯೋಜನೆಗಳ ಬಗ್ಗೆ ಹಿರಿಯ ನಾಗರಿಕರು, ರೈತರು, ವಿದ್ಯಾರ್ಥಿಗಳು ಮತ್ತು ಕುಟುಂಬಗಳಿಗೆ ನೇರ ಮಾರ್ಗದರ್ಶನ.",
    placeholder: "ಕನ್ನಡ ಅಥವಾ English ನಲ್ಲಿ ಬರೆಯಿರಿ, ಉದಾ: 'ನನಗೆ 65 ವರ್ಷ, ಪಿಂಚಣಿ ಯೋಜನೆಗಳು ಬೇಕು'…",
    send: "ಸಂದೇಶ ಕಳುಹಿಸಿ",
    start: "ಸಂಭಾಷಣೆ ಪ್ರಾರಂಭಿಸಿ",
    examples: "ಸುಲಭವಾಗಿ ಪ್ರಾರಂಭಿಸಲು ನಿಮ್ಮ ವರ್ಗವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    privacy: "DPDP ಕಾಯ್ದೆ 2023 ರ ಅಡಿಯಲ್ಲಿ ನಿಮ್ಮ ವಿವರಗಳನ್ನು ಕೇವಲ ಈ ಅಧಿವೇಶನದಲ್ಲಿ ಯೋಜನೆಗಳ ಮಾನದಂಡ ಪರಿಶೀಲಿಸಲು ಬಳಸಲಾಗುತ್ತದೆ.",
    profile: "ನಿಮ್ಮ ವಿವರಗಳು",
    profileSub: "ಸಂಭಾಷಣೆಯ ಮೂಲಕ ಸಂಗ್ರಹಿಸಲಾದ ಮಾಹಿತಿ",
    emptyProfile: "ನೀವು ವಿವರಗಳನ್ನು ಹಂಚಿಕೊಂಡಾಗ ಇಲ್ಲಿ ಕಾಣಿಸುತ್ತವೆ.",
    age: "ವಯಸ್ಸು",
    income: "ವಾರ್ಷಿಕ ಕುಟುಂಬ ಆದಾಯ",
    state: "ರಾಜ್ಯ",
    work: "ವೃತ್ತಿ",
    education: "ಶಿಕ್ಷಣ",
    category: "ಸಾಮಾಜಿಕ ವರ್ಗ",
    status: "ಅರ್ಹತಾ ಸ್ಥಿತಿ",
    discovered: "ಹೊಂದುವ ಯೋಜನೆಗಳು",
    noMatches: "ಕೆಲವು ವಿವರಗಳನ್ನು ನೀಡಿದ ನಂತರ ನಿಮಗೆ ಹೊಂದುವ ಯೋಜನೆಗಳು ಇಲ್ಲಿ ಕಾಣಿಸುತ್ತವೆ.",
    pass: "ಅರ್ಹರಾಗಿರುವ ಸಾಧ್ಯತೆ ಇದೆ",
    unknown: "ಹೆಚ್ಚಿನ ವಿವರಗಳು ಬೇಕು",
    fail: "ಕೆಲವು ಮಾನದಂಡಗಳು ಹೊಂದಿಲ್ಲ",
    source: "ಅಧಿಕೃತ ಮೂಲ",
    benefit: "ಪ್ರಯೋಜನ",
    missing: "ಇನ್ನೂ ಬೇಕಾದ ವಿವರಗಳು",
    reset: "ಹೊಸ ಸಂಭಾಷಣೆ",
    online: "ಸಹಾಯಕ ಸೇವೆ",
    connected: "API ಸಂಪರ್ಕಗೊಂಡಿದೆ",
    offline: "API ಲಭ್ಯವಿಲ್ಲ",
    greeting: "ನಮಸ್ಕಾರ! ಸುಸ್ವಾಗತ!",
    greetingText: "ಕೇಂದ್ರ ಮತ್ತು ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಯೋಜನೆಗಳನ್ನು ಹುಡುಕಲು ನಾನು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ. ಕೆಳಗಿನ ವರ್ಗವನ್ನು ಆಯ್ಕೆಮಾಡಿ ಅಥವಾ ನಿಮ್ಮ ವಯಸ್ಸು, ವಾಸಿಸುವ ಸ್ಥಳ, ವೃತ್ತಿ ಅಥವಾ ಬೇಕಾದ ಸಹಾಯದ ಬಗ್ಗೆ ತಿಳಿಸಿ.",
    clear: "ಸಂಭಾಷಣೆ ತೆರವುಗೊಳಿಸಿ",
    typing: "ಅಧಿಕೃತ ಮಾನದಂಡಗಳನ್ನು ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ…",
    results: "ನೀವು ಹಂಚಿಕೊಂಡ ವಿವರಗಳ ಆಧಾರದಲ್ಲಿ",
    notGuarantee: "ಇದು ಪ್ರಾಥಮಿಕ ಮಾಹಿತಿ ಮಾತ್ರ. ಅಂತಿಮ ಅರ್ಹತೆಯನ್ನು ಸಂಬಂಧಿತ ಸರ್ಕಾರಿ ಇಲಾಖೆ ನಿರ್ಧರಿಸುತ್ತದೆ.",
    evidence: "ಈ ಯೋಜನೆ ಏಕೆ ಹೊಂದಬಹುದು",
    verified: "ಅಧಿಕೃತ ಪೋರ್ಟಲ್",
    language: "ಭಾಷೆ",
    sources: "ಮೂಲಗಳು",
    details: "ಮಾನದಂಡಗಳ ನಿಯಮಗಳನ್ನು ನೋಡಿ",
    hide: "ಮಾನದಂಡಗಳನ್ನು ಮರೆಮಾಡಿ",
    profileNote: "ನೀವು ನೀಡಿದ ವಿವರಗಳನ್ನಷ್ಟೇ ಬಳಸಲಾಗುತ್ತದೆ. ಸೂಕ್ಷ್ಮ ವಿವರಗಳನ್ನು ಊಹಿಸಲಾಗುವುದಿಲ್ಲ.",
    startOver: "ಮತ್ತೆ ಪ್ರಾರಂಭಿಸಿ",
    intro: "ಸರ್ಕಾರಿ ಸೌಲಭ್ಯಗಳಿಗೆ ನೇರ ದಾರಿ",
    apiError: "ಸಹಾಯಕ ಸೇವೆಗೆ ಸಂಪರ್ಕಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. FastAPI backend ಚಾಲನೆಯಲ್ಲಿದೆಯೇ ಎಂದು ಪರಿಶೀಲಿಸಿ.",
    disclaimer: "ಸಹಾಯಕ ಒಂದು ಶೈಕ್ಷಣಿಕ NLP ಯೋಜನೆ; ಇದು ಸರ್ಕಾರಿ ಇಲಾಖೆಯಲ್ಲ. ಅಧಿಕೃತ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ವಿವರಗಳನ್ನು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.",
    textSize: "ಅಕ್ಷರ ಗಾತ್ರ",
    howItWorks: "ಸಹಾಯಕ ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ",
    step1Title: "1. ವಿವರಗಳನ್ನು ಹಂಚಿಕೊಳ್ಳಿ",
    step1Sub: "ನಿಮ್ಮ ವಯಸ್ಸು, ವೃತ್ತಿ ಮತ್ತು ರಾಜ್ಯವನ್ನು ತಿಳಿಸಿ.",
    step2Title: "2. ನಿಯಮಗಳ ಪರಿಶೀಲನೆ",
    step2Sub: "ಸರ್ಕಾರಿ ನಿಯಮಗಳನ್ನು ನಿಖರವಾಗಿ ಪರಿಶೀಲಿಸುತ್ತೇವೆ.",
    step3Title: "3. ಯೋಜನೆಗಳ ಮಾಹಿತಿ ಪಡೆಯಿರಿ",
    step3Sub: "ಅಧಿಕೃತ ಅರ್ಜಿ ಲಿಂಕ್ ಮತ್ತು ದಾಖಲೆಗಳ ಪಟ್ಟಿ.",
    printSlip: "ದಾಖಲೆಗಳ ಚೀಟಿ ಮುದ್ರಿಸಿ / ಉಳಿಸಿ",
    docChecklistTitle: "ಸಿದ್ಧಪಡಿಸಬೇಕಾದ ದಾಖಲೆಗಳ ಪಟ್ಟಿ",
    docsReady: "ಅರ್ಜಿಗೆ ಸಿದ್ಧವಾಗಿದೆ",
  },
} as const;

const FIELD_LABELS: Record<string, { en: string; kn: string }> = {
  age: { en: "Age", kn: "ವಯಸ್ಸು" },
  annual_income: { en: "Annual income", kn: "ವಾರ್ಷಿಕ ಆದಾಯ" },
  state: { en: "State", kn: "ರಾಜ್ಯ" },
  occupation: { en: "Occupation", kn: "ವೃತ್ತಿ" },
  education_level: { en: "Education", kn: "ಶಿಕ್ಷಣ" },
  is_student: { en: "Student", kn: "ವಿದ್ಯಾರ್ಥಿ" },
  gender: { en: "Gender", kn: "ಲಿಂಗ" },
  social_category: { en: "Social category", kn: "ಸಾಮಾಜಿಕ ವರ್ಗ" },
  has_bpl_card: { en: "BPL card", kn: "ಬಿಪಿಎಲ್ ಕಾರ್ಡ್" },
  land_ownership_ha: { en: "Land owned", kn: "ಭೂಮಿ" },
  residence_type: { en: "Residence", kn: "ವಾಸಸ್ಥಳ" },
  is_disabled: { en: "Disability status", kn: "ಅಂಗವಿಕಲತೆ" },
  unemployed_duration_months: { en: "Unemployment duration", kn: "ನಿರುದ್ಯೋಗ ಅವಧಿ" },
};

const PROFILE_KEYS = [
  "age",
  "state",
  "occupation",
  "annual_income",
  "residence_type",
  "education_level",
  "gender",
  "social_category",
  "has_bpl_card",
  "land_ownership_ha",
] as const;

const INTAKE_QUESTIONS: Record<(typeof PROFILE_KEYS)[number], { en: string; kn: string }> = {
  age: { en: "How old are you?", kn: "ನಿಮ್ಮ ವಯಸ್ಸು ಎಷ್ಟು?" },
  state: { en: "Which state do you currently live in?", kn: "ನೀವು ಪ್ರಸ್ತುತ ಯಾವ ರಾಜ್ಯದಲ್ಲಿ ವಾಸಿಸುತ್ತಿದ್ದೀರಿ?" },
  occupation: {
    en: "What best describes your current status: farmer, student, senior citizen/retired, salaried, self-employed, homemaker, daily wager, or unemployed?",
    kn: "ನಿಮ್ಮ ಪ್ರಸ್ತುತ ಸ್ಥಿತಿ ಯಾವುದು: ರೈತ, ವಿದ್ಯಾರ್ಥಿ, ಹಿರಿಯ ನಾಗರಿಕ/ನಿವೃತ್ತ, ಸಂಬಳದ ಉದ್ಯೋಗಿ, ಸ್ವಯಂ ಉದ್ಯೋಗಿ, ಗೃಹಿಣಿ, ದಿನಗೂಲಿ ಅಥವಾ ನಿರುದ್ಯೋಗಿ?",
  },
  annual_income: { en: "What is your approximate total annual family income in rupees?", kn: "ನಿಮ್ಮ ಕುಟುಂಬದ ಅಂದಾಜು ವಾರ್ಷಿಕ ಆದಾಯ ಎಷ್ಟು?" },
  residence_type: { en: "Do you live in a rural, urban, or semi-urban area?", kn: "ನೀವು ಗ್ರಾಮೀಣ, ನಗರ ಅಥವಾ ಅರೆ-ನಗರ ಪ್ರದೇಶದಲ್ಲಿ ವಾಸಿಸುತ್ತೀರಾ?" },
  education_level: { en: "What is your current or highest education level (10th/SSLC, 12th/PUC, Graduate, Postgraduate, or other)?", kn: "ನಿಮ್ಮ ಪ್ರಸ್ತುತ ಅಥವಾ ಗರಿಷ್ಠ ಶಿಕ್ಷಣದ ಮಟ್ಟ ಯಾವುದು (10ನೇ/SSLC, 12ನೇ/PUC, ಪದವಿ, ಸ್ನಾತಕೋತ್ತರ ಅಥವಾ ಇತರೆ)?" },
  gender: { en: "What is your gender? You may reply 'skip' if you prefer not to share it.", kn: "ನಿಮ್ಮ ಲಿಂಗ ಯಾವುದು? ಹಂಚಿಕೊಳ್ಳಲು ಇಷ್ಟವಿಲ್ಲದಿದ್ದರೆ 'skip' ಎಂದು ಬರೆಯಬಹುದು." },
  social_category: { en: "If relevant, what is your social category (General, OBC, SC, ST, EWS, or minority)? You may reply 'skip'.", kn: "ಅನ್ವಯಿಸಿದರೆ ನಿಮ್ಮ ಸಾಮಾಜಿಕ ವರ್ಗ ಯಾವುದು (General, OBC, SC, ST, EWS ಅಥವಾ ಅಲ್ಪಸಂಖ್ಯಾತ)? 'skip' ಎಂದು ಹೇಳಬಹುದು." },
  has_bpl_card: { en: "Does your household have a BPL or Antyodaya ration card? Reply yes, no, or skip.", kn: "ನಿಮ್ಮ ಕುಟುಂಬದ ಬಳಿ BPL ಅಥವಾ ಅಂತ್ಯೋದಯ ಪಡಿತರ ಚೀಟಿ ಇದೆಯೇ? ಹೌದು, ಇಲ್ಲ ಅಥವಾ skip ಎಂದು ಹೇಳಿ." },
  land_ownership_ha: { en: "Do you own agricultural land? If yes, approximately how many acres or hectares? You may reply '0' or 'skip'.", kn: "ನಿಮ್ಮ ಬಳಿ ಕೃಷಿ ಭೂಮಿ ಇದೆಯೇ? ಇದ್ದರೆ ಅಂದಾಜು ಎಷ್ಟು ಎಕರೆ ಅಥವಾ ಹೆಕ್ಟೇರ್? '0' ಅಥವಾ 'skip' ಎಂದು ಹೇಳಬಹುದು." },
};

const COMMON_SCHEME_DOCS: Record<string, string[]> = {
  "pm-kisan": ["Aadhaar Card", "Land Record (Pahani / RTC)", "Active Bank Account Passbook"],
  "ayushman-bharat-pmjay": ["Aadhaar Card", "Ration Card (BPL/Antyodaya)", "Family Photo"],
  "gruha-lakshmi-karnataka": ["Woman Head Aadhaar Card", "Husband Aadhaar Card", "Bank Passbook linked to Aadhaar", "Electricity Account ID"],
  "yuva-nidhi-karnataka": ["Graduation / Diploma Certificate", "Aadhaar Card", "Karnataka Domicile Proof", "Bank Account Passbook"],
  "shakti-scheme-karnataka": ["Aadhaar Card / Voter ID with Karnataka address"],
  "anna-bhagya-karnataka": ["BPL or Antyodaya Ration Card", "Aadhaar Card linked to Bank Account"],
  "atal-pension-yojana": ["Aadhaar Card", "Active Savings Bank Account", "Mobile Number linked to Bank"],
  "pm-svanidhi": ["Vending Certificate / Identity Card", "Aadhaar Card", "Bank Account Details"],
  "raitha-siri-karnataka": ["Farmer Land Record (RTC / Pahani)", "Aadhaar Card", "Bank Passbook (Direct Benefit Transfer)"],
  "vidyasiri-karnataka": ["Student College Admission Receipt", "Caste and Income Certificate", "Aadhaar Card", "Bank Passbook"],
};

function getIntakeCount(profile: Profile): number {
  return PROFILE_KEYS.filter(
    (key) => (profile[key] !== null && profile[key] !== undefined) || profile.field_status?.[key] === "skipped"
  ).length;
}

function getNextIntakeQuestion(profile: Profile, lang: Language): string | null {
  const key = PROFILE_KEYS.find(
    (field) => (profile[field] === null || profile[field] === undefined) && profile.field_status?.[field] !== "skipped"
  );
  return key ? INTAKE_QUESTIONS[key][lang] : null;
}

function formatValue(key: string, value: unknown, lang: Language) {
  if (typeof value === "boolean") return value ? (lang === "kn" ? "ಹೌದು" : "Yes") : lang === "kn" ? "ಇಲ್ಲ" : "No";
  if (key === "annual_income" && typeof value === "number") return `₹${value.toLocaleString("en-IN")}`;
  if (key === "land_ownership_ha" && typeof value === "number") return `${value} ha (~${Math.round(value * 2.471 * 10) / 10} acres)`;
  if (key === "unemployed_duration_months" && typeof value === "number") return `${value} ${lang === "kn" ? "ತಿಂಗಳು" : "months"}`;
  if (typeof value === "string") return value.replaceAll("_", " ").replace(/\b\w/g, (m) => m.toUpperCase());
  return String(value ?? "");
}

function SchemeCard({ scheme, lang, provisional = false }: { scheme: SchemeResult; lang: Language; provisional?: boolean }) {
  const t = COPY[lang];
  const [expanded, setExpanded] = useState(false);
  const [docsChecked, setDocsChecked] = useState<Record<string, boolean>>({});
  const status = scheme.overall_status;
  const statusText = provisional
    ? lang === "kn"
      ? "ಸಂಭಾವ್ಯ ಹೊಂದಿಕೆ"
      : "Potential match"
    : status === "PASS"
    ? t.pass
    : status === "FAIL"
    ? t.fail
    : t.unknown;
  const criteria = scheme.criteria_results ?? scheme.failed_criteria ?? [];

  const requiredDocs = useMemo(() => {
    return (
      COMMON_SCHEME_DOCS[scheme.scheme_id] ?? [
        "Aadhaar Card",
        "Bank Account Passbook",
        "Income / Domicile Certificate (if applicable)",
      ]
    );
  }, [scheme.scheme_id]);

  const checkedCount = requiredDocs.filter((d) => docsChecked[d]).length;

  function toggleDoc(doc: string) {
    setDocsChecked((prev) => ({ ...prev, [doc]: !prev[doc] }));
  }

  return (
    <article className="scheme-card">
      <div className="scheme-card-top">
        <span className={`status-pill ${provisional ? "status-unknown" : `status-${status.toLowerCase()}`}`}>
          <span className="status-dot" />
          {statusText}
        </span>
        {scheme.is_near_miss && <span className="near-miss">Alternative Option</span>}
      </div>
      <h3>{scheme.scheme_name}</h3>
      {scheme.benefits_summary && (
        <div className="benefit-line">
          <span>{t.benefit}</span>
          <strong>{scheme.benefits_summary}</strong>
        </div>
      )}
      {!provisional && <p className="scheme-reason">{scheme.summary_explanation}</p>}
      {!provisional && scheme.missing_attributes && scheme.missing_attributes.length > 0 && (
        <div className="missing-box">
          <strong>{t.missing}</strong>
          <div>{scheme.missing_attributes.map((field) => FIELD_LABELS[field]?.[lang] ?? field.replaceAll("_", " ")).join(" · ")}</div>
        </div>
      )}
      {!provisional && scheme.near_miss_reason && <p className="scheme-reason">{scheme.near_miss_reason}</p>}
      {!provisional && criteria.length > 0 && (
        <button className="criteria-toggle" onClick={() => setExpanded(!expanded)} aria-expanded={expanded}>
          {expanded ? t.hide : t.details}
          <ChevronDown size={15} className={expanded ? "rotate" : ""} />
        </button>
      )}
      {expanded && (
        <div className="criteria-list">
          {criteria.map((c, i) => (
            <div className="criterion" key={`${c.criterion_id}-${i}`}>
              <span className={`mini-status status-${c.status.toLowerCase()}`}>{c.status}</span>
              <div>
                <strong>{c.name}</strong>
                <p>{c.reason}</p>
                {c.source_citation && <small>{c.source_citation}</small>}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Interactive Document Checklist for Elderly & Citizens */}
      <div className="doc-checklist">
        <strong>{t.docChecklistTitle}</strong>
        {requiredDocs.map((doc) => (
          <label className={`doc-item ${docsChecked[doc] ? "checked" : ""}`} key={doc}>
            <input type="checkbox" checked={!!docsChecked[doc]} onChange={() => toggleDoc(doc)} />
            <span>{doc}</span>
          </label>
        ))}
        <span className="doc-progress">
          ✓ {checkedCount} / {requiredDocs.length} {t.docsReady}
        </span>
      </div>

      <div className="scheme-card-footer">
        {scheme.official_portal_url ? (
          <a className="official-link" href={scheme.official_portal_url} target="_blank" rel="noreferrer">
            <Landmark size={14} />
            {t.verified}
            <ExternalLink size={12} />
          </a>
        ) : (
          <span style={{ fontSize: 10, color: "var(--muted)" }}>Check local department portal</span>
        )}
        <button className="print-button" onClick={() => window.print()} title="Print this scheme summary">
          <Printer size={13} /> {lang === "kn" ? "ಮುದ್ರಿಸಿ" : "Print"}
        </button>
      </div>
    </article>
  );
}

export default function Home() {
  const [lang, setLang] = useState<Language>("en");
  const [textSize, setTextSize] = useState<"normal" | "large" | "xlarge">("normal");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [profile, setProfile] = useState<Profile>({});
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [apiState, setApiState] = useState<"checking" | "connected" | "offline">("checking");
  const [mobileProfileOpen, setMobileProfileOpen] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const t = COPY[lang];

  const knownProfile = useMemo(
    () => PROFILE_KEYS.filter((key) => profile[key] !== null && profile[key] !== undefined),
    [profile]
  );
  const completedProfileCount = useMemo(
    () =>
      PROFILE_KEYS.filter(
        (key) => (profile[key] !== null && profile[key] !== undefined) || profile.field_status?.[key] === "skipped"
      ).length,
    [profile]
  );
  const latestResponse = [...messages].reverse().find((message) => message.response)?.response;
  const schemes = latestResponse ? [...(latestResponse.recommended_schemes ?? []), ...(latestResponse.near_miss_schemes ?? [])] : [];

  useEffect(() => {
    fetch("/api/health")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((data) => setApiState(data.status === "healthy" ? "connected" : "offline"))
      .catch(() => setApiState("offline"));
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, busy]);

  async function sendMessage(text: string) {
    const value = text.trim();
    if (!value || busy) return;
    setInput("");
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: "user", text: value };
    setMessages((old) => [...old, userMessage]);
    setBusy(true);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: value,
          conversation_id: conversationId,
          language: lang,
          current_profile: profile,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : t.apiError);
      const result = data as ChatResponse;
      const updatedProfile = result.updated_profile ?? profile;
      const completed = getIntakeCount(updatedProfile);

      if (completed < PROFILE_KEYS.length) {
        const nextQuestion = getNextIntakeQuestion(updatedProfile, lang);
        result.is_final_assessment = false;
        result.intake_completed = completed;
        result.intake_total = PROFILE_KEYS.length;
        result.follow_up_question = nextQuestion;
        result.follow_up_target_attribute =
          PROFILE_KEYS.find(
            (field) => (updatedProfile[field] === null || updatedProfile[field] === undefined) && updatedProfile.field_status?.[field] !== "skipped"
          ) ?? null;
        result.sources = [];
        result.near_miss_schemes = [];
        result.reply = nextQuestion
          ? `${lang === "kn" ? "ಧನ್ಯವಾದಗಳು. ನಿಮ್ಮ ವಿವರಗಳನ್ನು ದಾಖಲಿಸಿದ್ದೇನೆ." : "Thanks, I've recorded your details."}\n\n${nextQuestion}`
          : lang === "kn"
          ? "ನಿಮ್ಮ ವಿವರಗಳನ್ನು ಪರಿಶೀಲಿಸುತ್ತಿದ್ದೇನೆ."
          : "I'm checking your details.";
      } else {
        result.is_final_assessment = true;
        result.intake_completed = PROFILE_KEYS.length;
        result.intake_total = PROFILE_KEYS.length;
      }
      setConversationId(result.conversation_id);
      setProfile(updatedProfile);
      setMessages((old) => [...old, { id: crypto.randomUUID(), role: "assistant", text: result.reply, response: result }]);
    } catch (error) {
      const message = error instanceof Error ? error.message : t.apiError;
      setMessages((old) => [...old, { id: crypto.randomUUID(), role: "assistant", text: `${t.apiError}\n\n${message}` }]);
      setApiState("offline");
    } finally {
      setBusy(false);
      inputRef.current?.focus();
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    void sendMessage(input);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void sendMessage(input);
    }
  }

  function resetConversation() {
    if (conversationId) {
      fetch("/api/chat/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conversation_id: conversationId }),
      }).catch(() => {});
    }
    setMessages([]);
    setProfile({});
    setConversationId(null);
    setInput("");
    setMobileProfileOpen(false);
    inputRef.current?.focus();
  }

  const PERSONA_CARDS = [
    {
      id: "senior",
      icon: "👵",
      title: lang === "kn" ? "ಹಿರಿಯ ನಾಗರಿಕರು & ಪಿಂಚಣಿ (60+)" : "Senior Citizens & Pension (60+)",
      badge: lang === "kn" ? "ಪಿಂಚಣಿ / ಆರೋಗ್ಯ" : "Pension / Health",
      sub: lang === "kn" ? "ವೃದ್ಧಾಪ್ಯ ಪಿಂಚಣಿ, ಆಯುಷ್ಮಾನ್ ಭಾರತ್ ಮತ್ತು ಸಂಧ್ಯಾ ಸುರಕ್ಷಾ" : "Old age pension, health cover & Sandhya Suraksha",
      prompt:
        lang === "kn"
          ? "ನಾನು ಕರ್ನಾಟಕದ 65 ವರ್ಷದ ಹಿರಿಯ ನಾಗರಿಕ, ವೃದ್ಧಾಪ್ಯ ಪಿಂಚಣಿ ಮತ್ತು ಆರೋಗ್ಯ ಯೋಜನೆಗಳು ಬೇಕು"
          : "I am a 65 year old senior citizen in Karnataka looking for old age pension and health support",
    },
    {
      id: "farmer",
      icon: "🌾",
      title: lang === "kn" ? "ರೈತರು & ಕೃಷಿ ಕುಟುಂಬಗಳು" : "Farmers & Agriculture",
      badge: lang === "kn" ? "ಕೃಷಿ ಸಬ್ಸಿಡಿ" : "DBT / Irrigation",
      sub: lang === "kn" ? "ಪಿಎಂ-ಕಿಸಾನ್, ರೈತ ಸಿರಿ, ಬೆಳೆ ವಿಮೆ ಮತ್ತು ಗಂಗಾ ಕಲ್ಯಾಣ" : "PM-KISAN, Raitha Siri, crop insurance & Ganga Kalyana",
      prompt:
        lang === "kn"
          ? "ನಾನು ಕರ್ನಾಟಕದ 40 ವರ್ಷದ ರೈತ, 2 ಎಕರೆ ಭೂಮಿ ಇದೆ, ವಾರ್ಷಿಕ ಆದಾಯ 1.5 ಲಕ್ಷ"
          : "I am a 40 year old farmer in Karnataka with 2 acres of land and annual income of 1.5 lakh",
    },
    {
      id: "student",
      icon: "🎓",
      title: lang === "kn" ? "ವಿದ್ಯಾರ್ಥಿಗಳು & ಯುವಜನರು" : "Students & Job Seekers",
      badge: lang === "kn" ? "ವಿದ್ಯಾರ್ಥಿವೇತನ" : "Scholarships / Aid",
      sub: lang === "kn" ? "ಯುವನಿಧಿ, ವಿದ್ಯಾಸಿರಿ, ಮೆರಿಟ್ ಸ್ಕಾಲರ್‌ಶಿಪ್ ಮತ್ತು ಮುದ್ರಾ" : "Yuva Nidhi, Vidyasiri, scholarships & Mudra loan",
      prompt:
        lang === "kn"
          ? "ನಾನು 21 ವರ್ಷದ ನಿರುದ್ಯೋಗಿ ಪದವೀಧರ, ಕರ್ನಾಟಕದಲ್ಲಿ ವಾಸಿಸುತ್ತಿದ್ದೇನೆ, ವಿದ್ಯಾರ್ಥಿವೇತನ ಮತ್ತು ಉದ್ಯೋಗ ನೆರವು ಬೇಕು"
          : "I am a 21 year old student looking for college fee scholarships and job training in Karnataka",
    },
    {
      id: "women",
      icon: "👩",
      title: lang === "kn" ? "ಮಹಿಳೆಯರು & ಕುಟುಂಬ ಕಲ್ಯಾಣ" : "Women & Family Welfare",
      badge: lang === "kn" ? "ಗೃಹ ಲಕ್ಷ್ಮಿ / ಶಕ್ತಿ" : "Gruha Lakshmi / Shakti",
      sub: lang === "kn" ? "ಗೃಹ ಲಕ್ಷ್ಮಿ ಮಾಸಿಕ ₹2000, ಉಚಿತ ಬಸ್ ಪ್ರಯಾಣ ಮತ್ತು ಸುಕನ್ಯಾ ಸಮೃದ್ಧಿ" : "Gruha Lakshmi ₹2,000/mo, free RTC bus travel & Sukanya Samriddhi",
      prompt:
        lang === "kn"
          ? "ಕರ್ನಾಟಕದಲ್ಲಿ ಮಹಿಳೆಯರು ಮತ್ತು ಹೆಣ್ಣು ಮಕ್ಕಳ ಕಲ್ಯಾಣಕ್ಕಾಗಿ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳಿವೆ?"
          : "What government welfare, monthly grant and education schemes are available for women in Karnataka?",
    },
  ];

  return (
    <main className={`app-shell text-size-${textSize}`}>
      <header className="topbar">
        <a className="brand" href="#home" aria-label="Sahayaka home">
          <span className="brand-mark">
            <Landmark size={21} strokeWidth={1.8} />
          </span>
          <span className="brand-word">
            sahayaka<span>.</span>
            <small>PUBLIC BENEFITS, MADE CLEAR</small>
          </span>
        </a>

        <div className="topbar-right">
          {/* Text Size Scaling for Elderly Citizens */}
          <div className="font-size-switch" aria-label={t.textSize} title={t.textSize}>
            <span>{t.textSize}:</span>
            <button
              className={textSize === "normal" ? "active" : ""}
              onClick={() => setTextSize("normal")}
              aria-label="Normal text size"
            >
              A
            </button>
            <button
              className={textSize === "large" ? "active" : ""}
              onClick={() => setTextSize("large")}
              aria-label="Large text size"
            >
              A+
            </button>
            <button
              className={textSize === "xlarge" ? "active" : ""}
              onClick={() => setTextSize("xlarge")}
              aria-label="Extra large text size"
            >
              A++
            </button>
          </div>

          <Link className="all-policies-link" href="/policies">
            <FileText size={14} />
            {lang === "kn" ? "ಎಲ್ಲಾ 57 ಯೋಜನೆಗಳು" : "All 57 policies"}
          </Link>

          <div className={`connection ${apiState}`}>
            <span />
            {apiState === "connected" ? t.connected : apiState === "checking" ? "Checking…" : t.offline}
          </div>

          <div className="language-switch" aria-label={t.language}>
            <Languages size={15} />
            <button className={lang === "en" ? "active" : ""} onClick={() => setLang("en")}>
              EN
            </button>
            <span>/</span>
            <button className={lang === "kn" ? "active" : ""} onClick={() => setLang("kn")}>
              ಕನ್ನಡ
            </button>
          </div>
        </div>
      </header>

      <div className="workspace" id="home">
        <section className="conversation-column">
          <div className="conversation-heading">
            <div>
              <div className="eyebrow">
                <span className="eyebrow-line" />
                {t.gov}
              </div>
              <h1>{messages.length ? (lang === "kn" ? "ನಿಮ್ಮ ಯೋಜನೆಗಳನ್ನು ಹುಡುಕೋಣ." : "Let's find what you qualify for.") : t.title}</h1>
              <p>
                {messages.length
                  ? lang === "kn"
                    ? "ನಿಮ್ಮ ವಿವರಗಳನ್ನು ಹಂಚಿಕೊಳ್ಳಿ. ನಾನು ಹಂತ ಹಂತವಾಗಿ ಸಹಾಯ ಮಾಡುತ್ತೇನೆ."
                    : "Share your details in your own words. I'll guide you one step at a time."
                  : t.subtitle}
              </p>
            </div>
            <div className="hero-seal">
              <Landmark size={29} strokeWidth={1.25} />
              <span>भारत · ಕರ್ನಾಟಕ</span>
            </div>
          </div>

          {messages.length === 0 ? (
            <div className="welcome-panel">
              <div className="welcome-top">
                <div className="assistant-avatar">
                  <Sparkles size={19} />
                </div>
                <div>
                  <strong>{t.greeting}</strong>
                  <span>{t.intro}</span>
                </div>
                <span className="welcome-check">
                  <ShieldCheck size={18} />
                </span>
              </div>
              <p className="welcome-copy">{t.greetingText}</p>

              {/* 3-Step Simple Guide for All Age Brackets */}
              <div className="how-it-works-strip">
                <div className="how-step">
                  <span className="how-step-num">1</span>
                  <div className="how-step-text">
                    <strong>{t.step1Title}</strong>
                    <span>{t.step1Sub}</span>
                  </div>
                </div>
                <div className="how-step">
                  <span className="how-step-num">2</span>
                  <div className="how-step-text">
                    <strong>{t.step2Title}</strong>
                    <span>{t.step2Sub}</span>
                  </div>
                </div>
                <div className="how-step">
                  <span className="how-step-num">3</span>
                  <div className="how-step-text">
                    <strong>{t.step3Title}</strong>
                    <span>{t.step3Sub}</span>
                  </div>
                </div>
              </div>

              {/* Four Age Bracket & Citizen Persona Cards */}
              <div className="suggestion-heading">{t.examples}</div>
              <div className="persona-grid">
                {PERSONA_CARDS.map((p) => (
                  <button className="persona-card" key={p.id} onClick={() => void sendMessage(p.prompt)}>
                    <div className="persona-top">
                      <span className="persona-icon">{p.icon}</span>
                      <strong className="persona-title">{p.title}</strong>
                      <span className="persona-badge">{p.badge}</span>
                    </div>
                    <p className="persona-sub">{p.sub}</p>
                  </button>
                ))}
              </div>

              <div className="privacy-note">
                <ShieldCheck size={16} />
                <span>{t.profileNote}</span>
              </div>
            </div>
          ) : (
            <div className="message-list" aria-live="polite">
              {messages.map((message) => (
                <div className={`message-row ${message.role}`} key={message.id}>
                  {message.role === "assistant" && (
                    <div className="message-avatar">
                      <Sparkles size={15} />
                    </div>
                  )}
                  <div className="message-content">
                    <div className="message-author">
                      {message.role === "assistant" ? "Sahayaka" : lang === "kn" ? "ನೀವು" : "You"}
                      <span>{message.role === "assistant" ? <CheckCheck size={13} /> : null}</span>
                    </div>
                    {message.role === "assistant" ? (
                      <div className="assistant-bubble">
                        <div className="markdown-reply">
                          {message.text.split("\n").map((line, i) => (
                            <p key={i}>
                              {line
                                .replace(/^#{1,4}\s*/, "")
                                .replace(/\*\*/g, "")
                                .replace(/^[-*]\s/, "• ")
                                .replace(/`/g, "") || " "}
                            </p>
                          ))}
                        </div>
                        {message.response && (
                          <div className="response-foot">
                            <span>
                              <ShieldCheck size={14} />
                              {t.results}
                            </span>
                            <span>
                              {message.response.is_final_assessment === false
                                ? `${message.response.intake_completed ?? 0}/${message.response.intake_total ?? 10} ${
                                    lang === "kn" ? "ವಿವರಗಳು" : "details"
                                  }`
                                : `${message.response.sources?.length ?? 0} ${t.sources.toLowerCase()}`}
                            </span>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="user-bubble">{message.text}</div>
                    )}
                    {message.response && message.response.sources?.length > 0 && (
                      <div className="source-strip">
                        {message.response.sources.slice(0, 3).map((source) => (
                          <a key={source.scheme_id} href={source.official_portal_url} target="_blank" rel="noreferrer">
                            <Landmark size={13} />
                            {source.scheme_name}
                            <ExternalLink size={12} />
                          </a>
                        ))}
                      </div>
                    )}
                    {message.response?.has_conflicts && (
                      <div className="conflict-note">
                        <CircleHelp size={15} />
                        {lang === "kn"
                          ? "ನಿಮ್ಮ ಹಿಂದಿನ ವಿವರಗಳಿಗೆ ವ್ಯತ್ಯಾಸ ಕಂಡುಬಂದಿದೆ. ಪ್ರೊಫೈಲ್ ಪರಿಶೀಲಿಸಿ."
                          : `Some details differ from earlier answers: ${message.response.conflicting_fields?.join(
                              ", "
                            )}. Please review your profile.`}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {busy && (
                <div className="message-row assistant">
                  <div className="message-avatar">
                    <Sparkles size={15} />
                  </div>
                  <div className="message-content">
                    <div className="message-author">Sahayaka</div>
                    <div className="typing-bubble">
                      <LoaderCircle size={16} className="spin" />
                      {t.typing}
                    </div>
                  </div>
                </div>
              )}
              <div ref={endRef} />
            </div>
          )}

          <div className="composer-wrap">
            <form className="composer" onSubmit={handleSubmit}>
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={t.placeholder}
                rows={1}
                aria-label={t.placeholder}
                disabled={busy}
              />
              {input.trim().length > 0 && (
                <button
                  type="button"
                  className="composer-clear"
                  onClick={() => setInput("")}
                  title="Clear input"
                  aria-label="Clear input"
                >
                  <X size={15} />
                </button>
              )}
              <button className="send-button" type="submit" aria-label={t.send} disabled={busy || !input.trim()}>
                {busy ? <LoaderCircle size={18} className="spin" /> : <Send size={17} />}
              </button>
            </form>
            <div className="composer-hint">
              <span>↵ {lang === "kn" ? "ಕಳುಹಿಸಲು Enter ಒತ್ತಿ" : "Press Enter to send · Shift + Enter for new line"}</span>
              <span>
                <ShieldCheck size={13} />
                {t.privacy}
              </span>
            </div>
          </div>
          <footer className="page-footer">
            <span>© {new Date().getFullYear()} Sahayaka · Public Service NLP Project</span>
            <span>{t.disclaimer}</span>
          </footer>
        </section>

        <aside className={`profile-column ${mobileProfileOpen ? "mobile-open" : ""}`}>
          <div className="profile-header">
            <div className="profile-heading-icon">
              <UserRound size={17} />
            </div>
            <div>
              <h2>{t.profile}</h2>
              <p>{t.profileSub}</p>
            </div>
            <button className="mobile-close" onClick={() => setMobileProfileOpen(false)} aria-label="Close profile">
              <X size={17} />
            </button>
          </div>

          <div className="profile-completeness">
            <div className="completeness-top">
              <span>{lang === "kn" ? "ಸಂಗ್ರಹಿಸಿದ ವಿವರಗಳು" : "Details collected"}</span>
              <strong>
                {latestResponse?.intake_completed ?? completedProfileCount} / {latestResponse?.intake_total ?? PROFILE_KEYS.length}
              </strong>
            </div>
            <div className="progress-track">
              <span
                style={{
                  width: `${Math.min(
                    100,
                    ((latestResponse?.intake_completed ?? completedProfileCount) /
                      (latestResponse?.intake_total ?? PROFILE_KEYS.length)) *
                      100
                  )}%`,
                }}
              />
            </div>
          </div>

          {knownProfile.length === 0 ? (
            <div className="profile-empty">
              <div className="empty-illustration">
                <UserRound size={25} />
              </div>
              <strong>{t.emptyProfile}</strong>
              <p>{t.profileNote}</p>
            </div>
          ) : (
            <div className="profile-fields">
              {knownProfile.map((key) => (
                <div className="profile-field" key={key}>
                  <span>{FIELD_LABELS[key]?.[lang] ?? key}</span>
                  <strong>{formatValue(key, profile[key], lang)}</strong>
                  {profile.confidences?.[key] !== undefined && (
                    <small>{Math.round(profile.confidences[key] * 100)}% confidence</small>
                  )}
                </div>
              ))}
            </div>
          )}

          <div className="profile-tip">
            <ShieldCheck size={16} />
            <p>{t.profileNote}</p>
          </div>

          <div className="panel-divider" />

          <div className="matches-header">
            <div>
              <span className="section-kicker">{t.discovered}</span>
              <p>{lang === "kn" ? "ನಿಮ್ಮ ವಿವರಗಳಿಗೆ ಹೊಂದಿಕೆ" : "Matched to your details"}</p>
            </div>
            <span className="matches-count">{schemes.length}</span>
          </div>

          {schemes.length === 0 ? (
            <div className="matches-empty">
              <div>
                <Landmark size={19} />
              </div>
              <p>{t.noMatches}</p>
            </div>
          ) : (
            <div className="scheme-results">
              {schemes.map((scheme) => (
                <SchemeCard
                  key={scheme.scheme_id}
                  scheme={scheme}
                  lang={lang}
                  provisional={latestResponse?.is_final_assessment === false}
                />
              ))}
            </div>
          )}

          {schemes.length > 0 && (
            <p className="results-disclaimer">
              {latestResponse?.is_final_assessment === false
                ? lang === "kn"
                  ? "ಇವು ಪ್ರಾಥಮಿಕ ಸಾಧ್ಯತೆಗಳು ಮಾತ್ರ; ಅಂತಿಮ ಮೌಲ್ಯಮಾಪನ ವಿವರ ಸಂಗ್ರಹ ಪೂರ್ಣವಾದ ನಂತರ ಬರುತ್ತದೆ."
                  : "These are preliminary possibilities only. Final eligibility results appear after profile collection is complete."
                : t.notGuarantee}
            </p>
          )}

          {messages.length > 0 && (
            <button className="reset-button" onClick={resetConversation}>
              <RotateCcw size={15} />
              {t.reset}
            </button>
          )}

          <div className="service-status">
            <div className={`service-indicator ${apiState}`}>
              <span />
            </div>
            <div>
              <strong>{t.online}</strong>
              <p>{apiState === "connected" ? t.connected : apiState === "checking" ? "Checking…" : t.offline}</p>
            </div>
            <span className="service-shield">
              <ShieldCheck size={16} />
            </span>
          </div>
        </aside>

        <button className="mobile-profile-toggle" onClick={() => setMobileProfileOpen(true)}>
          <UserRound size={16} />
          {t.profile}
          {knownProfile.length > 0 && <span>{knownProfile.length}</span>}
          <ArrowDown size={14} />
        </button>
        {mobileProfileOpen && <button className="mobile-backdrop" aria-label="Close profile panel" onClick={() => setMobileProfileOpen(false)} />}
      </div>
    </main>
  );
}
