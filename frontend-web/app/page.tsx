"use client";

export const dynamic = "force-dynamic";

import { FormEvent, KeyboardEvent, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient, isSupabaseConfigured } from "@/lib/supabase/client";
import {
  ArrowDown,
  ArrowRight,
  Check,
  CheckCheck,
  ChevronDown,
  CircleHelp,
  Columns,
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
import { AuthNav } from "@/components/AuthNav";
import { SaveSchemeButton } from "@/components/SaveSchemeButton";

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
    ledger: "Eligibility Ledger",
    hideLedger: "Hide Ledger",
    showLedger: "Show Ledger",
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
    ledger: "ಅರ್ಹತಾ ಲೆಡ್ಜರ್",
    hideLedger: "ಲೆಡ್ಜರ್ ಮರೆಮಾಡಿ",
    showLedger: "ಲೆಡ್ಜರ್ ತೋರಿಸಿ",
  },
  te: {
    gov: "ప్రభుత్వ పథకాల సహాయకుడు",
    title: "అందరికీ సులభంగా అర్థమయ్యే ప్రభుత్వ సంక్షేమ పథకాలు.",
    subtitle: "కేంద్ర, ఆంధ్రప్రదేశ్, కర్ణాటక, తమిళనాడు, కేరళ ప్రభుత్వ పథకాలపై సీనియర్ సిటిజన్లు, రైతులు, విద్యార్థులు మరియు కుటుంబాలకు స్పష్టమైన మార్గదర్శకత్వం.",
    placeholder: "తెలుగు లేదా English లో రాయండి, ఉదా: 'నా వయస్సు 65 సంవత్సరాలు, పింఛను కావాలి'…",
    send: "సందేశం పంపండి",
    start: "సంభాషణ ప్రారంభించండి",
    examples: "సులభంగా ప్రారంభించడానికి మీ వర్గాన్ని ఎంచుకోండి",
    privacy: "DPDP చట్టం 2023 ప్రకారం మీ వివరాలు ఈ సెషన్‌లో పథకాల అర్హతను పరిశీలించడానికి మాత్రమే ఉపయోగించబడతాయి.",
    profile: "మీ ప్రొఫైల్",
    profileSub: "సంభాషణ ద్వారా సేకరించిన వివరాలు",
    emptyProfile: "మీరు వివరాలు పంచుకున్నప్పుడు ఇక్కడ కనిపిస్తాయి.",
    age: "వయస్సు",
    income: "వార్షిక కుటుంబ ఆదాయం",
    state: "రాష్ట్రం",
    work: "వృత్తి",
    education: "విద్యార్హత",
    category: "సామాజిక వర్గం",
    status: "అర్హత స్థితి",
    discovered: "సరిపోలే పథకాలు",
    noMatches: "కొన్ని వివరాలు అందించిన తర్వాత మీకు వర్తించే పథకాలు ఇక్కడ కనిపిస్తాయి.",
    pass: "అర్హత ఉండే అవకాశం ఉంది",
    unknown: "మరిన్ని వివరాలు అవసరం",
    fail: "నిబంధనలు సరిపోలలేదు",
    source: "అధికారిక మూలం",
    benefit: "ప్రయోజనం",
    missing: "ఇంకా కావాల్సిన వివరాలు",
    reset: "కొత్త సంభాషణ",
    online: "సహాయక సేవ",
    connected: "API కనెక్ట్ అయింది",
    offline: "API అందుబాటులో లేదు",
    greeting: "నమస్కారం! స్వాగతం!",
    greetingText: "కేంద్ర మరియు రాష్ట్ర ప్రభుత్వ సంక్షేమ పథకాలను కనుగొనడంలో నేను మీకు సహాయం చేస్తాను. దిగువ వర్గాన్ని ఎంచుకోండి లేదా మీ వయస్సు, నివాసం, వృత్తి లేదా అవసరమైన సహాయం గురించి చెప్పండి.",
    clear: "సంభాషణను క్లియర్ చేయండి",
    typing: "అధికారిక నిబంధనలను పరిశీలిస్తోంది…",
    results: "మీరు అందించిన వివరాల ఆధారంగా",
    notGuarantee: "ఇది ప్రాథమిక మార్గదర్శకత్వం మాత్రమే. తుది అర్హతను సంబంధిత ప్రభుత్వ శాఖ నిర్ణయిస్తుంది.",
    evidence: "ఈ పథకం ఎందుకు సరిపోలుతుంది",
    verified: "అధికారిక పోర్టల్",
    language: "భాష",
    sources: "మూలాలు",
    details: "అర్హత నిబంధనలను చూడండి",
    hide: "నిబంధనలను దాచండి",
    profileNote: "మీరు స్వయంగా తెలిపిన వివరాలు మాత్రమే పరిగణించబడతాయి. సున్నిత సమాచారం ఊహించబడదు.",
    startOver: "మళ్లీ ప్రారంభించండి",
    intro: "ప్రభుత్వ సంక్షేమ ఫలాలకు సరళమైన మార్గం",
    apiError: "సహాయక సేవకు కనెక్ట్ కాలేదు. FastAPI బ్యాకెండ్ నడుస్తోందో లేదో తనిఖీ చేయండి.",
    disclaimer: "సహాయక అనేది విద్యా పరిశోధనా పబ్లిక్ సర్వీస్ ప్రాజెక్ట్; ఇది ప్రభుత్వ శాఖ కాదు. అధికారిక పోర్టల్ ద్వారా ఎల్లప్పుడూ ధృవీకరించుకోండి.",
    textSize: "అక్షర పరిమాణం",
    howItWorks: "సహాయక ఎలా సహాయపడుతుంది",
    step1Title: "1. వివరాలు తెలపండి",
    step1Sub: "మీ వయస్సు, వృత్తి, రాష్ట్రాన్ని మీ స్వంత మాటల్లో చెప్పండి.",
    step2Title: "2. నిబంధనల పరిశీలన",
    step2Sub: "ప్రభుత్వ నియమాలను ఊహించకుండా స్పష్టంగా తనిఖీ చేస్తాము.",
    step3Title: "3. ప్రయోజనాలు పొందండి",
    step3Sub: "అధికారిక దరఖాస్తు లింకులు మరియు పత్రాల జాబితా.",
    printSlip: "పత్రాల స్లిప్ ప్రింట్ / సేవ్ చేయండి",
    docChecklistTitle: "కావలసిన పత్రాల జాబితా",
    docsReady: "దరఖాస్తుకు సిద్ధం",
    ledger: "అర్హత లెడ్జర్",
    hideLedger: "లెడ్జర్ దాచు",
    showLedger: "లెడ్జర్ చూపించు",
  },
  ta: {
    gov: "அரசு நலத்திட்ட உதவியாளர்",
    title: "அனைவருக்கும் எளிதில் புரியும் அரசு நலத்திட்டங்கள்.",
    subtitle: "மத்திய மற்றும் தமிழ்நாடு, கர்நாடகா, ஆந்திரா, கேரளா அரசு திட்டங்கள் குறித்து முதியவர்கள், விவசாயிகள், மாணவர்கள் மற்றும் குடும்பங்களுக்கு நேரடி வழிகாட்டுதல்.",
    placeholder: "தமிழ் அல்லது English-ல் தட்டச்சு செய்க, எ.கா: 'எனக்கு 65 வயது, முதியோர் ஓய்வூதியம் வேண்டும்'…",
    send: "அனுப்புக",
    start: "உரையாடலைத் தொடங்குங்கள்",
    examples: "எளிதாகத் தொடங்க உங்கள் பிரிவைத் தேர்ந்தெடுக்கவும்",
    privacy: "DPDP சட்டம் 2023-ன் கீழ் உங்கள் விவரங்கள் இந்த அமர்வில் திட்டத் தகுதியை மதிப்பாய்வு செய்ய மட்டுமே பயன்படுத்தப்படும்.",
    profile: "உங்கள் விவரங்கள்",
    profileSub: "உரையாடல் மூலம் பெறப்பட்ட தகவல்கள்",
    emptyProfile: "நீங்கள் விவரங்களைப் பகிரும்போது இங்கே தோன்றும்.",
    age: "வயது",
    income: "ஆண்டு குடும்ப வருமானம்",
    state: "மாநிலம்",
    work: "தொழில்",
    education: "கல்வித்தகுதி",
    category: "சமூகப் பிரிவு",
    status: "தகுதி நிலை",
    discovered: "பொருத்தமான திட்டங்கள்",
    noMatches: "சில விவரங்களை வழங்கிய பிறகு உங்களுக்குப் பொருந்தும் திட்டங்கள் இங்கே தோன்றும்.",
    pass: "தகுதி பெற வாய்ப்புள்ளது",
    unknown: "கூடுதல் விவரங்கள் தேவை",
    fail: "விதிகள் பொருந்தவில்லை",
    source: "அதிகாரப்பூர்வ ஆதாரம்",
    benefit: "பயன்",
    missing: "இன்னும் தேவைப்படும் விவரங்கள்",
    reset: "புதிய உரையாடல்",
    online: "உதவியாளர் சேவை",
    connected: "API இணைக்கப்பட்டது",
    offline: "API இணைக்கப்படவில்லை",
    greeting: "வணக்கம்! நல்வரவு!",
    greetingText: "மத்திய மற்றும் மாநில அரசு நலத்திட்டங்களை அறிய நான் உதவுகிறேன். கீழே உள்ள பிரிவைத் தேர்ந்தெடுக்கவும் அல்லது உங்கள் வயது, இருப்பிடம், தொழில் அல்லது தேவைப்படும் உதவியைக் கூறவும்.",
    clear: "உரையாடலை அழிக்கவும்",
    typing: "அதிகாரப்பூர்வ விதிகளைச் சரிபார்க்கிறது…",
    results: "நீங்கள் வழங்கிய விவரங்களின் அடிப்படையில்",
    notGuarantee: "இது ஆரம்ப வழிகாட்டுதல் மட்டுமே. இறுதித் தகுதியை சம்பந்தப்பட்ட அரசுத் துறை தீர்மானிக்கும்.",
    evidence: "இத்திட்டம் ஏன் பொருந்துகிறது",
    verified: "அதிகாரப்பூர்வ தளம்",
    language: "மொழி",
    sources: "ஆதாரங்கள்",
    details: "தகுதி விதிகளைக் காண்க",
    hide: "விதிகளை மறைக்கவும்",
    profileNote: "நீங்கள் வழங்கும் விவரங்கள் மட்டுமே பயன்படுத்தப்படும். முக்கியமான விவரங்கள் யூகிக்கப்படாது.",
    startOver: "மீண்டும் தொடங்குக",
    intro: "அரசு நலத்திட்டங்களுக்கான எளிய வழி",
    apiError: "உதவியாளர் சேவையுடன் இணைக்க முடியவில்லை. FastAPI இயங்குகிறதா எனச் சரிபார்க்கவும்.",
    disclaimer: "சஹாயகா ஒரு கல்வி மற்றும் பொது சேவை ஆய்வுத் திட்டம்; இது அரசுத் துறை அல்ல. அதிகாரப்பூர்வ போர்ட்டலில் உறுதிப்படுத்தவும்.",
    textSize: "எழுத்து அளவு",
    howItWorks: "சஹாயகா எவ்வாறு உதவுகிறது",
    step1Title: "1. விவரங்களைப் பகிரவும்",
    step1Sub: "உங்கள் வயது, தொழில், மாநிலத்தை உங்கள் சொந்த வார்த்தைகளில் கூறுங்கள்.",
    step2Title: "2. விதிமுறை சரிபார்ப்பு",
    step2Sub: "அரசு விதிமுறைகளைத் துல்லியமாகச் சரிபார்க்கிறோம்.",
    step3Title: "3. தகவல்களைப் பெறுங்கள்",
    step3Sub: "அதிகாரப்பூர்வ விண்ணப்ப இணைப்புகள் & ஆவணப் பட்டியல்.",
    printSlip: "ஆவணச் சீட்டை அச்சிடுக / சேமிக்க",
    docChecklistTitle: "தயார் செய்ய வேண்டிய ஆவணங்கள்",
    docsReady: "விண்ணப்பிக்க தயார்",
    ledger: "தகுதிப் பதிவேடு",
    hideLedger: "பதிவேட்டை மறை",
    showLedger: "பதிவேட்டைக் காட்டு",
  },
  ml: {
    gov: "സർക്കാർ ക്ഷേമപദ്ധതി സഹായി",
    title: "എല്ലാവർക്കും എളുപ്പത്തിൽ മനസ്സിലാകുന്ന സർക്കാർ പദ്ധതികൾ.",
    subtitle: "കേന്ദ്ര, കേരള, കർണാടക, തമിഴ്നാട്, ആന്ധ്രാപ്രദേശ് സർക്കാർ പദ്ധതികളെക്കുറിച്ച് വയോജനങ്ങൾ, കർഷകർ, വിദ്യാർത്ഥികൾ, കുടുംബങ്ങൾ എന്നിവർക്ക് വ്യക്തമായ മാർഗ്ഗനിർദ്ദേശം.",
    placeholder: "മലയാളത്തിലോ English-ലോ എഴുതുക, ഉദാ: 'എനിക്ക് 65 വയസ്സുണ്ട്, പെൻഷൻ പദ്ധതികൾ വേണം'…",
    send: "സന്ദേശം അയയ്ക്കുക",
    start: "സംഭാഷണം ആരംഭിക്കുക",
    examples: "എളുപ്പത്തിൽ ആരംഭിക്കാൻ നിങ്ങളുടെ വിഭാഗം തിരഞ്ഞെടുക്കുക",
    privacy: "DPDP നിയമം 2023 പ്രകാരം നിങ്ങളുടെ വിവരങ്ങൾ ഈ സെഷനിൽ പദ്ധതി യോഗ്യത പരിശോധിക്കാൻ മാത്രമാണ് ഉപയോഗിക്കുന്നത്.",
    profile: "നിങ്ങളുടെ വിവരങ്ങൾ",
    profileSub: "സംഭാഷണത്തിലൂടെ ശേഖരിച്ച വിവരങ്ങൾ",
    emptyProfile: "വിവരങ്ങൾ നൽകുമ്പോൾ ഇവിടെ കാണാം.",
    age: "വയസ്സ്",
    income: "വാർഷിക കുടുംബ വരുമാനം",
    state: "സംസ്ഥാനം",
    work: "തൊഴിൽ",
    education: "വിദ്യാഭ്യാസം",
    category: "സാമൂഹിക വിഭാഗം",
    status: "യോഗ്യതാ നില",
    discovered: "അനുയോജ്യമായ പദ്ധതികൾ",
    noMatches: "വിവരങ്ങൾ നൽകിയ ശേഷം നിങ്ങൾക്ക് അനുയോജ്യമായ പദ്ധതികൾ ഇവിടെ ദൃശ്യമാകും.",
    pass: "യോഗ്യതയുള്ളതായി കാണുന്നു",
    unknown: "കൂടുതൽ വിവരങ്ങൾ ആവശ്യമാണ്",
    fail: "മാനദണ്ഡങ്ങൾ പൊരുത്തപ്പെടുന്നില്ല",
    source: "ഔദ്യോഗിക ഉറവിടം",
    benefit: "ആനുകൂല്യം",
    missing: "ഇനിയും ആവശ്യമുള്ള വിവരങ്ങൾ",
    reset: "പുതിയ സംഭാഷണം",
    online: "സഹായി സേവനം",
    connected: "API കണക്റ്റുചെയ്തു",
    offline: "API ലഭ്യമല്ല",
    greeting: "നമസ്കാരം! സ്വാഗതം!",
    greetingText: "കേന്ദ്ര, സംസ്ഥാന സർക്കാർ പദ്ധതികൾ കണ്ടെത്താൻ ഞാൻ സഹായിക്കാം. താഴെയുള്ള വിഭാഗം തിരഞ്ഞെടുക്കുക അല്ലെങ്കിൽ നിങ്ങളുടെ വയസ്സ്, താമസസ്ഥലം, തൊഴിൽ എന്നിവ പറയുക.",
    clear: "സംഭാഷണം മായ്‌ക്കുക",
    typing: "ഔദ്യോഗിക നിബന്ധനകൾ പരിശോധിക്കുന്നു…",
    results: "നിങ്ങൾ പങ്കിട്ട വിവരങ്ങളുടെ അടിസ്ഥാനത്തിൽ",
    notGuarantee: "ഇത് പ്രാഥമിക വിവരങ്ങൾ മാത്രമാണ്. അന്തിമ യോഗ്യത ബന്ധപ്പെട്ട സർക്കാർ വകുപ്പാണ് തീരുമാനിക്കുന്നത്.",
    evidence: "ഈ പദ്ധതി എന്തുകൊണ്ട് അനുയോജ്യമാണ്",
    verified: "ഔദ്യോഗിക പോർട്ടൽ",
    language: "ഭാഷ",
    sources: "ഉറവിടങ്ങൾ",
    details: "യോഗ്യതാ നിയമങ്ങൾ കാണുക",
    hide: "നിയമങ്ങൾ മറയ്ക്കുക",
    profileNote: "നിങ്ങൾ നൽകുന്ന വിവരങ്ങൾ മാത്രമേ ഉപയോഗിക്കൂ. പ്രധാന വിവരങ്ങൾ ഊഹിച്ചെടുക്കില്ല.",
    startOver: "വീണ്ടും ആരംഭിക്കുക",
    intro: "സർക്കാർ ആനുകൂല്യങ്ങളിലേക്ക് എളുപ്പവഴി",
    apiError: "സഹായി സേവനവുമായി ബന്ധപ്പെടാൻ കഴിഞ്ഞില്ല. FastAPI ബാക്കെൻഡ് പ്രവർത്തിക്കുന്നുണ്ടോ എന്ന് പരിശോധിക്കുക.",
    disclaimer: "സഹായക ഒരു അക്കാദമിക് പബ്ലിക് സർവീസ് പ്രോജക്റ്റാണ്; ഇതൊരു സർക്കാർ വകുപ്പല്ല. ഔദ്യോഗിക പോർട്ടലിൽ സ്ഥിരീകരിക്കുക.",
    textSize: "അക്ഷര വലുപ്പം",
    howItWorks: "സഹായക എങ്ങനെ സഹായിക്കുന്നു",
    step1Title: "1. വിവരങ്ങൾ പങ്കിടുക",
    step1Sub: "നിങ്ങളുടെ വയസ്സ്, തൊഴിൽ, സംസ്ഥാനം എന്നിവ സ്വന്തം വാക്കുകളിൽ പറയുക.",
    step2Title: "2. നിയമ പരിശോധന",
    step2Sub: "സർക്കാർ നിബന്ധനകൾ കൃത്യമായി പരിശോധിക്കുന്നു.",
    step3Title: "3. വിവരങ്ങൾ നേടുക",
    step3Sub: "ഔദ്യോഗിക അപേക്ഷാ ലിങ്കുകളും രേഖകളുടെ പട്ടികയും.",
    printSlip: "രേഖകളുടെ സ്ലിപ്പ് പ്രിന്റ് ചെയ്യുക / സൂക്ഷിക്കുക",
    docChecklistTitle: "തയ്യാറാക്കേണ്ട രേഖകളുടെ പട്ടിക",
    docsReady: "അപേക്ഷിക്കാൻ തയ്യാറാണ്",
    ledger: "യോഗ്യതാ ലെഡ്ജർ",
    hideLedger: "ലെഡ്ജർ മറയ്ക്കുക",
    showLedger: "ലെഡ്ജർ കാണിക്കുക",
  },
} as const;

const FIELD_LABELS: Record<string, { en: string; kn: string; te: string; ta: string; ml: string }> = {
  age: { en: "Age", kn: "ವಯಸ್ಸು", te: "వయస్సు", ta: "வயது", ml: "വയസ്സ്" },
  annual_income: { en: "Annual income", kn: "ವಾರ್ಷಿಕ ಆದಾಯ", te: "వార్షిక ఆదాయం", ta: "ஆண்டு வருமானம்", ml: "വാർഷിക വരുമാനം" },
  state: { en: "State", kn: "ರಾಜ್ಯ", te: "రాష్ట్రం", ta: "மாநிலம்", ml: "സംസ്ഥാനം" },
  occupation: { en: "Occupation", kn: "ವೃತ್ತಿ", te: "వృత్తి", ta: "தொழில்", ml: "തൊഴിൽ" },
  education_level: { en: "Education", kn: "ಶಿಕ್ಷಣ", te: "విద్యార్హత", ta: "கல்வி", ml: "വിദ്യാഭ്യാസം" },
  is_student: { en: "Student", kn: "ವಿದ್ಯಾರ್ಥಿ", te: "విద్యార్థి", ta: "மாணவர்", ml: "വിദ്യാർത്ഥി" },
  gender: { en: "Gender", kn: "ಲಿಂಗ", te: "లింగం", ta: "பாலினம்", ml: "ലിംഗം" },
  social_category: { en: "Social category", kn: "ಸಾಮಾಜಿಕ ವರ್ಗ", te: "సామాజిక వర్గం", ta: "சமூகப் பிரிவு", ml: "സാമൂഹിക വിഭാഗം" },
  has_bpl_card: { en: "BPL card", kn: "ಬಿಪಿಎಲ್ ಕಾರ್ಡ್", te: "బిపిఎల్ కార్డు", ta: "பிபிஎல் அட்டை", ml: "ബിപിഎൽ കാർഡ്" },
  land_ownership_ha: { en: "Land owned", kn: "ಭೂಮಿ", te: "వ్యవసాయ భూమి", ta: "நில உரிமை", ml: "ഭൂമിയുടെ അളവ്" },
  residence_type: { en: "Residence", kn: "ವಾಸಸ್ಥಳ", te: "నివాస ప్రాంతం", ta: "இருப்பிடம்", ml: "താമസസ്ഥലം" },
  is_disabled: { en: "Disability status", kn: "ಅಂಗವಿಕಲತೆ", te: "దివ్యాంగుల స్థితి", ta: "மாற்றுத்திறனாளி", ml: "ഭിന്നശേഷി" },
  unemployed_duration_months: { en: "Unemployment duration", kn: "ನಿರುದ್ಯೋಗ ಅವಧಿ", te: "నిరుద్యోగ కాలం", ta: "வேலையின்மை காலம்", ml: "തൊഴിലില്ലായ്മ കാലയളവ്" },
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

const INTAKE_QUESTIONS: Record<(typeof PROFILE_KEYS)[number], { en: string; kn: string; te: string; ta: string; ml: string }> = {
  age: {
    en: "How old are you?",
    kn: "ನಿಮ್ಮ ವಯಸ್ಸು ಎಷ್ಟು?",
    te: "మీ వయస్సు ఎంత?",
    ta: "உங்கள் வயது என்ன?",
    ml: "നിങ്ങൾക്ക് എത്ര വയസ്സായി?",
  },
  state: {
    en: "Which state do you currently live in?",
    kn: "ನೀವು ಪ್ರಸ್ತುತ ಯಾವ ರಾಜ್ಯದಲ್ಲಿ ವಾಸಿಸುತ್ತಿದ್ದೀರಿ?",
    te: "మీరు ప్రస్తుతం ఏ రాష్ట్రంలో నివసిస్తున్నారు?",
    ta: "நீங்கள் தற்போது எந்த மாநிலத்தில் வசிக்கிறீர்கள்?",
    ml: "നിങ്ങൾ ഇപ്പോൾ ഏത് സംസ്ഥാനത്താണ് താമസിക്കുന്നത്?",
  },
  occupation: {
    en: "What best describes your current status: farmer, student, senior citizen/retired, salaried, self-employed, homemaker, daily wager, or unemployed?",
    kn: "ನಿಮ್ಮ ಪ್ರಸ್ತುತ ಸ್ಥಿತಿ ಯಾವುದು: ರೈತ, ವಿದ್ಯಾರ್ಥಿ, ಹಿರಿಯ ನಾಗರಿಕ/ನಿವೃತ್ತ, ಸಂಬಳದ ಉದ್ಯೋಗಿ, ಸ್ವಯಂ ಉದ್ಯೋಗಿ, ಗೃಹಿಣಿ, ದಿನಗೂಲಿ ಅಥವಾ ನಿರುದ್ಯೋಗಿ?",
    te: "మీ ప్రస్తుత వృత్తి ఏది: రైతు, విద్యార్థి, సీనియర్ సిటిజన్/రిటైర్డ్, ఉద్యోగి, స్వయం ఉపాధి, గృహిణి, దినసరి కూలీ లేదా నిరుద్యోగి?",
    ta: "உங்கள் தற்போதைய நிலை என்ன: விவசாயி, மாணவர், முதியவர்/ஓய்வு பெற்றவர், மாதச் சம்பளக்காரர், சுயதொழில், இல்லத்தரசி, தினக்கூலி அல்லது வேலையில்லாதவரா?",
    ml: "നിങ്ങളുടെ ഇപ്പോഴത്തെ തൊഴിൽ എന്താണ്: കർഷകൻ, വിദ്യാർത്ഥി, വയോജന/വിരമിച്ചയാൾ, ശമ്പളക്കാരൻ, സ്വയംതൊഴിൽ, വീട്ടമ്മ, ദിവസക്കൂലിക്കാരൻ അല്ലെങ്കിൽ തൊഴിൽരഹിതൻ?",
  },
  annual_income: {
    en: "What is your approximate total annual family income in rupees?",
    kn: "ನಿಮ್ಮ ಕುಟುಂಬದ ಅಂದಾಜು ವಾರ್ಷಿಕ ಆದಾಯ ಎಷ್ಟು?",
    te: "రూపాయల్లో మీ కుటుంబ వార్షిక ఆదాయం సుమారు ఎంత?",
    ta: "உங்கள் குடும்பத்தின் தோராயமான ஆண்டு வருமானம் ரூபாயில் எவ்வளவு?",
    ml: "നിങ്ങളുടെ കുടുംബത്തിന്റെ ഏകദേശ വാർഷിക വരുമാനം എത്ര രൂപയാണ്?",
  },
  residence_type: {
    en: "Do you live in a rural, urban, or semi-urban area?",
    kn: "ನೀವು ಗ್ರಾಮೀಣ, ನಗರ ಅಥವಾ ಅರೆ-ನಗರ ಪ್ರದೇಶದಲ್ಲಿ ವಾಸಿಸುತ್ತೀರಾ?",
    te: "మీరు గ్రామీణ, పట్టణ లేదా సెమీ అర్బన్ ప్రాంతంలో నివసిస్తున్నారా?",
    ta: "நீங்கள் கிராமப்புறம், நகர்ப்புறம் அல்லது பகுதி-நகர்ப்புறப் பகுதியில் வசிக்கிறீர்களா?",
    ml: "നിങ്ങൾ ഗ്രാമത്തിലോ നഗരത്തിലോ അർദ്ധ നഗര പ്രദേശത്തോ ആണോ താമസിക്കുന്നത്?",
  },
  education_level: {
    en: "What is your current or highest education level (10th/SSLC, 12th/PUC, Graduate, Postgraduate, or other)?",
    kn: "ನಿಮ್ಮ ಪ್ರಸ್ತುತ ಅಥವಾ ಗರಿಷ್ಠ ಶಿಕ್ಷಣದ ಮಟ್ಟ ಯಾವುದು (10ನೇ/SSLC, 12ನೇ/PUC, ಪದವಿ, ಸ್ನಾತಕೋತ್ತರ ಅಥವಾ ಇತರೆ)?",
    te: "మీ విద్యార్హత ఎంత (10వ తరగతి/SSLC, 12వ తరగతి/ఇంటర్, డిగ్రీ, పీజీ లేదా ఇతర)?",
    ta: "உங்கள் தற்போதைய அல்லது அதிகபட்ச கல்வித்தகுதி என்ன (10-ஆம் வகுப்பு, 12-ஆம் வகுப்பு, பட்டதாரி, முதுகலை அல்லது பிற)?",
    ml: "നിങ്ങളുടെ ഇപ്പോഴത്തെ അല്ലെങ്കിൽ ഉയർന്ന വിദ്യാഭ്യാസ നിലവാരം എന്താണ് (10th/SSLC, 12th/Plus Two, ബിരുദം, ബിരുദാനന്തര ബിരുദം അല്ലെങ്കിൽ മറ്റുള്ളവ)?",
  },
  gender: {
    en: "What is your gender? You may reply 'skip' if you prefer not to share it.",
    kn: "ನಿಮ್ಮ ಲಿಂಗ ಯಾವುದು? ಹಂಚಿಕೊಳ್ಳಲು ಇಷ್ಟವಿಲ್ಲದಿದ್ದರೆ 'skip' ಎಂದು ಬರೆಯಬಹುದು.",
    te: "మీ లింగం ఏమిటి? చెప్పడం ఇష్టం లేకపోతే 'skip' అని బదులివ్వవచ్చు.",
    ta: "உங்கள் பாலினம் என்ன? பகிர விருப்பமில்லை என்றால் 'skip' என்று பதிலளிக்கலாம்.",
    ml: "നിങ്ങളുടെ ലിംഗം എന്താണ്? പങ്കിടാൻ താൽപ്പര്യമില്ലെങ്കിൽ 'skip' എന്ന് മറുപടി നൽകാം.",
  },
  social_category: {
    en: "If relevant, what is your social category (General, OBC, SC, ST, EWS, or minority)? You may reply 'skip'.",
    kn: "ಅನ್ವಯಿಸಿದರೆ ನಿಮ್ಮ ಸಾಮಾಜಿಕ ವರ್ಗ ಯಾವುದು (General, OBC, SC, ST, EWS ಅಥವಾ ಅಲ್ಪಸಂಖ್ಯಾತ)? 'skip' ಎಂದು ಹೇಳಬಹುದು.",
    te: "వర్తిస్తే మీ సామాజిక వర్గం ఏది (General, OBC, SC, ST, EWS లేదా మైనారిటీ)? 'skip' అని చెప్పవచ్చు.",
    ta: "பொருந்துமானால் உங்கள் சமூகப் பிரிவு எது (General, OBC, SC, ST, EWS அல்லது சிறுபான்மையினர்)? 'skip' எனலாம்.",
    ml: "ബാധകമെങ്കിൽ നിങ്ങളുടെ സാമൂഹിക വിഭാഗം ഏതാണ് (General, OBC, SC, ST, EWS അല്ലെങ്കിൽ ന്യൂനപക്ഷം)? 'skip' എന്ന് പറയാം.",
  },
  has_bpl_card: {
    en: "Does your household have a BPL or Antyodaya ration card? Reply yes, no, or skip.",
    kn: "ನಿಮ್ಮ ಕುಟುಂಬದ ಬಳಿ BPL ಅಥವಾ ಅಂತ್ಯೋದಯ ಪಡಿತರ ಚೀಟಿ ಇದೆಯೇ? ಹೌದು, ಇಲ್ಲ ಅಥವಾ skip ಎಂದು ಹೇಳಿ.",
    te: "మీ కుటుంబానికి BPL లేదా అంత్యోదయ రేషన్ కార్డు ఉందా? అవును, కాదు లేదా skip అని చెప్పండి.",
    ta: "உங்கள் குடும்பத்தில் BPL அல்லது அந்த்யோதயா ரேஷன் அட்டை உள்ளதா? ஆம், இல்லை அல்லது skip எனப் பதிலளிக்கவும்.",
    ml: "നിങ്ങളുടെ കുടുംബത്തിന് BPL അല്ലെങ്കിൽ അന്ത്യോദയ റേഷൻ കാർഡ് ഉണ്ടോ? ഉണ്ട്, ഇല്ല അല്ലെങ്കിൽ skip എന്ന് പറയുക.",
  },
  land_ownership_ha: {
    en: "Do you own agricultural land? If yes, approximately how many acres or hectares? You may reply '0' or 'skip'.",
    kn: "ನಿಮ್ಮ ಬಳಿ ಕೃಷಿ ಭೂಮಿ ಇದೆಯೇ? ಇದ್ದರೆ ಅಂದಾಜು ಎಷ್ಟು ಎಕರೆ ಅಥವಾ ಹೆಕ್ಟೇರ್? '0' ಅಥವಾ 'skip' ಎಂದು ಹೇಳಬಹುದು.",
    te: "మీకు వ్యవసాయ భూమి ఉందా? ఉంటే సుమారు ఎన్ని ఎకరాలు లేదా హెక్టార్లు? '0' లేదా 'skip' అని చెప్పవచ్చు.",
    ta: "உங்களுக்கு விவசாய நிலம் உள்ளதா? இருந்தால் தோராயமாக எத்தனை ஏக்கர் அல்லது ஹெக்டேர்? '0' அல்லது 'skip' எனலாம்.",
    ml: "നിങ്ങൾക്ക് കൃഷിഭൂമി സ്വന്തമായുണ്ടോ? ഉണ്ടെങ്കിൽ ഏകദേശം എത്ര ഏക്കർ അല്ലെങ്കിൽ ഹെക്ടർ? '0' അല്ലെങ്കിൽ 'skip' എന്ന് പറയാം.",
  },
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
  if (typeof value === "boolean") {
    if (value) {
      if (lang === "kn") return "ಹೌದು";
      if (lang === "te") return "అవును";
      if (lang === "ta") return "ஆம்";
      if (lang === "ml") return "അതെ";
      return "Yes";
    } else {
      if (lang === "kn") return "ಇಲ್ಲ";
      if (lang === "te") return "కాదు";
      if (lang === "ta") return "இல்லை";
      if (lang === "ml") return "അല്ല";
      return "No";
    }
  }
  if (key === "annual_income" && typeof value === "number") return `₹${value.toLocaleString("en-IN")}`;
  if (key === "land_ownership_ha" && typeof value === "number") return `${value} ha (~${Math.round(value * 2.471 * 10) / 10} acres)`;
  if (key === "unemployed_duration_months" && typeof value === "number") {
    const monthWord =
      lang === "kn" ? "ತಿಂಗಳು" : lang === "te" ? "నెలలు" : lang === "ta" ? "மாதங்கள்" : lang === "ml" ? "മാസങ്ങൾ" : "months";
    return `${value} ${monthWord}`;
  }
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
      : lang === "te"
      ? "సంభావ్య సరిపోలిక"
      : lang === "ta"
      ? "சாத்தியமான பொருத்தம்"
      : lang === "ml"
      ? "സാധ്യതയുള്ള പൊരുത്തം"
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
        <div style={{ marginLeft: "auto" }}>
          <SaveSchemeButton
            schemeId={scheme.scheme_id}
            schemeName={scheme.scheme_name}
            benefitsSummary={scheme.benefits_summary}
            officialPortalUrl={scheme.official_portal_url}
            lang={lang}
          />
        </div>
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
          <Printer size={13} /> {lang === "kn" ? "ಮುದ್ರಿಸಿ" : lang === "te" ? "ప్రింట్" : lang === "ta" ? "அச்சிடுக" : lang === "ml" ? "പ്രിന്റ്" : "Print"}
        </button>
      </div>
    </article>
  );
}

export default function Home() {
  const router = useRouter();
  const [lang, setLang] = useState<Language>("en");
  const [textSize, setTextSize] = useState<"normal" | "large" | "xlarge">("normal");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [profile, setProfile] = useState<Profile>({});
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [apiState, setApiState] = useState<"checking" | "connected" | "offline">("checking");
  const [mobileProfileOpen, setMobileProfileOpen] = useState(false);
  const [desktopLedgerOpen, setDesktopLedgerOpen] = useState(true);
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const t = COPY[lang];

  useEffect(() => {
    if (isSupabaseConfigured()) {
      const supabase = createClient();
      supabase.auth.getUser().then(({ data: { user } }) => {
        if (!user) {
          router.replace("/login");
        }
      });
    }
  }, [router]);

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
    document.documentElement.lang = lang;
  }, [lang]);

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
        const thankPrefix =
          lang === "kn"
            ? "ಧನ್ಯವಾದಗಳು. ನಿಮ್ಮ ವಿವರಗಳನ್ನು ದಾಖಲಿಸಿದ್ದೇನೆ."
            : lang === "te"
            ? "ధన్యవాదాలు. మీ వివరాలను నమోదు చేసుకున్నాను."
            : lang === "ta"
            ? "நன்றி. உங்கள் விவரங்களைப் பதிவு செய்துள்ளேன்."
            : lang === "ml"
            ? "നന്ദി. നിങ്ങളുടെ വിവരങ്ങൾ രേഖപ്പെടുത്തിയിട്ടുണ്ട്."
            : "Thanks, I've recorded your details.";
        const checkingText =
          lang === "kn"
            ? "ನಿಮ್ಮ ವಿವರಗಳನ್ನು ಪರಿಶೀಲಿಸುತ್ತಿದ್ದೇನೆ."
            : lang === "te"
            ? "మీ వివరాలను పరిశీలిస్తున్నాను."
            : lang === "ta"
            ? "உங்கள் விவரங்களைச் சரிபார்க்கிறேன்."
            : lang === "ml"
            ? "നിങ്ങളുടെ വിവരങ്ങൾ പരിശോധിക്കുന്നു."
            : "I'm checking your details.";
        result.reply = nextQuestion ? `${thankPrefix}\n\n${nextQuestion}` : checkingText;
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
      icon: "senior",
      title:
        lang === "kn"
          ? "ಹಿರಿಯ ನಾಗರಿಕರು & ಪಿಂಚಣಿ (60+)"
          : lang === "te"
          ? "సీనియర్ సిటిజన్లు & పింఛను (60+)"
          : lang === "ta"
          ? "முதியவர்கள் & ஓய்வூதியம் (60+)"
          : lang === "ml"
          ? "വയോജനങ്ങൾ & പെൻഷൻ (60+)"
          : "Senior Citizens & Pension (60+)",
      badge:
        lang === "kn"
          ? "ಪಿಂಚಣಿ / ಆರೋಗ್ಯ"
          : lang === "te"
          ? "పింఛను / ఆరోగ్యం"
          : lang === "ta"
          ? "ஓய்வூதியம் / மருத்துவம்"
          : lang === "ml"
          ? "പെൻഷൻ / ആരോഗ്യം"
          : "Pension / Health",
      sub:
        lang === "kn"
          ? "ವೃದ್ಧಾಪ್ಯ ಪಿಂಚಣಿ, ಆಯುಷ್ಮಾನ್ ಭಾರತ್ ಮತ್ತು ಸಂಧ್ಯಾ ಸುರಕ್ಷಾ"
          : lang === "te"
          ? "వృద్ధాప్య పింఛను, వైఎస్సార్ పెన్షన్ కానుక, ఆయుష్మాన్ భారత్"
          : lang === "ta"
          ? "முதியோர் ஓய்வூதியம், முதலமைச்சரின் விரிவான மருத்துவக் காப்பீடு"
          : lang === "ml"
          ? "ഇന്ദിരാഗാന്ധി വാർദ്ധക്യകാല പെൻഷൻ, കാരുണ്യ ആരോഗ്യ സുരക്ഷാപദ്ധതി"
          : "Old age pension, health cover & welfare support",
      prompt:
        lang === "kn"
          ? "ನಾನು ಕರ್ನಾಟಕದ 65 ವರ್ಷದ ಹಿರಿಯ ನಾಗರಿಕ, ವೃದ್ಧಾಪ್ಯ ಪಿಂಚಣಿ ಮತ್ತು ಆರೋಗ್ಯ ಯೋಜನೆಗಳು ಬೇಕು"
          : lang === "te"
          ? "నా వయస్సు 65 సంవత్సరాలు, సీనియర్ సిటిజన్ పింఛను మరియు ఆరోగ్య పథకాల వివరాలు కావాలి"
          : lang === "ta"
          ? "எனக்கு 65 வயது, முதியோர் ஓய்வூதியம் மற்றும் மருத்துவ காப்பீட்டுத் திட்டங்கள் பற்றி அறிய வேண்டும்"
          : lang === "ml"
          ? "എനിക്ക് 65 വയസ്സുണ്ട്, വയോജന പെൻഷനും ആരോഗ്യ ഇൻഷുറൻസ് പദ്ധതികളും അറിയണം"
          : "I am a 65 year old senior citizen looking for old age pension and health support",
    },
    {
      id: "farmer",
      icon: "farmer",
      title:
        lang === "kn"
          ? "ರೈತರು & ಕೃಷಿ ಕುಟುಂಬಗಳು"
          : lang === "te"
          ? "రైతులు & వ్యవసాయ కుటుంబాలు"
          : lang === "ta"
          ? "விவசாயிகள் & வேளாண் குடும்பங்கள்"
          : lang === "ml"
          ? "കർഷകർ & കാർഷിക കുടുംബങ്ങൾ"
          : "Farmers & Agriculture",
      badge:
        lang === "kn"
          ? "ಕೃಷಿ ಸಬ್ಸಿಡಿ"
          : lang === "te"
          ? "రైతు భరోసా / సబ్సిడీ"
          : lang === "ta"
          ? "வேளாண் மானியம்"
          : lang === "ml"
          ? "കർഷക ആനുകൂല്യങ്ങൾ"
          : "DBT / Irrigation",
      sub:
        lang === "kn"
          ? "ಪಿಎಂ-ಕಿಸಾನ್, ರೈತ ಸಿರಿ, ಬೆಳೆ ವಿಮೆ ಮತ್ತು ಗಂಗಾ ಕಲ್ಯಾಣ"
          : lang === "te"
          ? "వైఎస్సార్ రైతు భరోసా, పీఎం-కిసాన్, పంటల బీమా మరియు ఉచిత విద్యుత్"
          : lang === "ta"
          ? "கலைஞர் அனைத்துக் கிராம ஒருங்கிணைந்த வேளாண் வளர்ச்சி, பயிர் காப்பீடு"
          : lang === "ml"
          ? "സുഭിക്ഷ കേരളം, നെൽവയൽ ഉടമസ്ഥർക്കുള്ള റോയൽറ്റി, വിള ഇൻഷുറൻസ്"
          : "PM-KISAN, crop insurance & farm subsidies",
      prompt:
        lang === "kn"
          ? "ನಾನು ಕರ್ನಾಟಕದ 40 ವರ್ಷದ ರೈತ, 2 ಎಕರೆ ಭೂಮಿ ಇದೆ, ವಾರ್ಷಿಕ ಆದಾಯ 1.5 ಲಕ್ಷ"
          : lang === "te"
          ? "నేను 2 ఎకరాల భూమి ఉన్న రైతును, రైతు భరోసా మరియు పంటల బీమా వివరాలు కావాలి"
          : lang === "ta"
          ? "நான் 2 ஏக்கர் நிலமுள்ள விவசாயி, பயிர் காப்பீடு மற்றும் மானியத் திட்டங்கள் என்ன?"
          : lang === "ml"
          ? "ഞാൻ 2 ഏക്കർ ഭൂമിയുള്ള കർഷകനാണ്, കർഷക ആനുകൂല്യങ്ങളും വിള ഇൻഷുറൻസും അറിയണം"
          : "I am a 40 year old farmer with 2 acres of land and annual income of 1.5 lakh",
    },
    {
      id: "student",
      icon: "student",
      title:
        lang === "kn"
          ? "ವಿದ್ಯಾರ್ಥಿಗಳು & ಯುವಜನರು"
          : lang === "te"
          ? "విద్యార్థులు & యువత"
          : lang === "ta"
          ? "மாணவர்கள் & இளைஞர்கள்"
          : lang === "ml"
          ? "വിദ്യാർത്ഥികൾ & യുവാക്കൾ"
          : "Students & Job Seekers",
      badge:
        lang === "kn"
          ? "ವಿದ್ಯಾರ್ಥಿವೇತನ"
          : lang === "te"
          ? "ఫీజు రీయింబర్స్‌మెంట్ / స్కాలర్‌షిప్"
          : lang === "ta"
          ? "கல்வி உதவித்தொகை"
          : lang === "ml"
          ? "സ്കോളർഷിപ്പ്"
          : "Scholarships / Aid",
      sub:
        lang === "kn"
          ? "ಯುವನಿಧಿ, ವಿದ್ಯಾಸಿರಿ, ಮೆರಿಟ್ ಸ್ಕಾಲರ್‌ಶಿಪ್ ಮತ್ತು ಮುದ್ರಾ"
          : lang === "te"
          ? "జగనన్న విద్యా దీవెన, వసతి దీవెన, నిరుద్యోగ భృతి మరియు స్కాలర్‌షిప్‌లు"
          : lang === "ta"
          ? "புதுமைப் பெண் திட்டம், நான் முதல்வன், கல்வி உதவித்தொகை"
          : lang === "ml"
          ? "വിദ്യാകിരണം, ഡിജിറ്റൽ സർവ്വകലാശാല സ്കോളർഷിപ്പ്, യുവാക്കൾക്കുള്ള തൊഴിൽ സഹായം"
          : "Yuva Nidhi, scholarships & job training",
      prompt:
        lang === "kn"
          ? "ನಾನು 21 ವರ್ಷದ ನಿರುದ್ಯೋಗಿ ಪದವೀಧರ, ಕರ್ನಾಟಕದಲ್ಲಿ ವಾಸಿಸುತ್ತಿದ್ದೇನೆ, ವಿದ್ಯಾರ್ಥಿವೇತನ ಮತ್ತು ಉದ್ಯೋಗ ನೆರವು ಬೇಕು"
          : lang === "te"
          ? "నేను 21 సంవత్సరాల నిరుద్యోగ గ్రాడ్యుయేట్‌ను, స్కాలర్‌షిప్ మరియు ఉపాధి పథకాలు కావాలి"
          : lang === "ta"
          ? "நான் 21 வயது வேலையில்லாத பட்டதாரி, கல்வி உதவித்தொகை மற்றும் வேலைவாய்ப்பு பயிற்சி தேவை"
          : lang === "ml"
          ? "ഞാൻ 21 വയസ്സുള്ള തൊഴിൽരഹിത ബിരുദധാരിയാണ്, സ്കോളർഷിപ്പും തൊഴിൽ പരിശീലനവും വേണം"
          : "I am a 21 year old student looking for college fee scholarships and job training",
    },
    {
      id: "women",
      icon: "women",
      title:
        lang === "kn"
          ? "ಮಹಿಳೆಯರು & ಕುಟುಂಬ ಕಲ್ಯಾಣ"
          : lang === "te"
          ? "మహిళలు & కుటుంబ సంక్షేమం"
          : lang === "ta"
          ? "மகளிர் & குடும்ப நலம்"
          : lang === "ml"
          ? "വനിതകൾ & കുടുംബക്ഷേമം"
          : "Women & Family Welfare",
      badge:
        lang === "kn"
          ? "ಗೃಹ ಲಕ್ಷ್ಮಿ / ಶಕ್ತಿ"
          : lang === "te"
          ? "వైఎస్సార్ ఆసరా / చేయూత"
          : lang === "ta"
          ? "கலைஞர் மகளிர் உரிமை / விடியல் பயணம்"
          : lang === "ml"
          ? "കുടുംബശ്രീ / മാതൃവന്ദന"
          : "Women Welfare / Aid",
      sub:
        lang === "kn"
          ? "ಗೃಹ ಲಕ್ಷ್ಮಿ ಮಾಸಿಕ ₹2000, ಉಚಿತ ಬಸ್ ಪ್ರಯಾಣ ಮತ್ತು ಸುಕನ್ಯಾ ಸಮೃದ್ಧಿ"
          : lang === "te"
          ? "వైఎస్సార్ చేయూత, ఆసరా మరియు మహిళా సాధికారత పథకాలు"
          : lang === "ta"
          ? "கலைஞர் மகளிர் உரிமைத் தொகை ₹1000/மாதம் மற்றும் இலவச பேருந்து பயணம்"
          : lang === "ml"
          ? "കുടുംബശ്രീ മൈക്രോക്രെഡിറ്റ്, മാതൃവന്ദന, സ്വയംതొഴിൽ സഹായം"
          : "Gruha Lakshmi ₹2,000/mo, free RTC bus travel & Sukanya Samriddhi",
      prompt:
        lang === "kn"
          ? "ಕರ್ನಾಟಕದಲ್ಲಿ ಮಹಿಳೆಯರು ಮತ್ತು ಹೆಣ್ಣು ಮಕ್ಕಳ ಕಲ್ಯಾಣಕ್ಕಾಗಿ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳಿವೆ?"
          : lang === "te"
          ? "మహిళలు మరియు బాలికల సంక్షేమం కోసం అందుబాటులో ఉన్న ప్రభుత్వ పథకాలు ఏమిటి?"
          : lang === "ta"
          ? "மகளிர் மற்றும் பெண் குழந்தைகள் நலனுக்காக என்னென்ன அரசு திட்டங்கள் உள்ளன?"
          : lang === "ml"
          ? "വനിതകൾക്കും പെൺകുട്ടികൾക്കുമായി ലഭ്യമായ സർക്കാർ പദ്ധതികൾ ഏതെല്ലാമാണ്?"
          : "What government welfare, monthly grant and education schemes are available for women?",
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
            {lang === "kn"
              ? "ಎಲ್ಲಾ 111 ಯೋಜನೆಗಳು"
              : lang === "te"
              ? "అన్ని 111 పథకాలు"
              : lang === "ta"
              ? "அனைத்து 111 திட்டங்கள்"
              : lang === "ml"
              ? "എല്ലാ 111 പദ്ധതികളും"
              : "All 111 policies"}
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

          <button
            className={`ledger-toggle-btn ${desktopLedgerOpen ? "active" : ""}`}
            onClick={() => setDesktopLedgerOpen(!desktopLedgerOpen)}
            title={desktopLedgerOpen ? t.hideLedger : t.showLedger}
            aria-label={desktopLedgerOpen ? t.hideLedger : t.showLedger}
          >
            <Columns size={15} />
            <span>{t.ledger}</span>
            {schemes.length > 0 && <span className="ledger-badge">{schemes.length}</span>}
          </button>

          <AuthNav lang={lang} />
        </div>
      </header>

      <div className={`workspace ${desktopLedgerOpen ? "ledger-open" : "ledger-closed"}`} id="home">
        <section className="conversation-column">
          <div className="conversation-heading">
            <div>

              <h1>
                {messages.length
                  ? lang === "kn"
                    ? "ನಿಮ್ಮ ಯೋಜನೆಗಳನ್ನು ಹುಡುಕೋಣ."
                    : lang === "te"
                    ? "మీకు వర్తించే పథకాలను కనుగొందాం."
                    : lang === "ta"
                    ? "உங்களுக்கான திட்டங்களைக் கண்டறிவோம்."
                    : lang === "ml"
                    ? "നിങ്ങൾക്ക് അനുയോജ്യമായ പദ്ധതികൾ കണ്ടെത്താം."
                    : "Let's find what you qualify for."
                  : t.title}
              </h1>
              <p>
                {messages.length
                  ? lang === "kn"
                    ? "ನಿಮ್ಮ ವಿವರಗಳನ್ನು ಹಂಚಿಕೊಳ್ಳಿ. ನಾನು ಹಂತ ಹಂತವಾಗಿ ಸಹಾಯ ಮಾಡುತ್ತೇನೆ."
                    : lang === "te"
                    ? "మీ వివరాలను తెలియజేయండి. నేను దశలవారీగా సహాయం చేస్తాను."
                    : lang === "ta"
                    ? "உங்கள் விவரங்களைப் பகிருங்கள். நான் படிப்படியாக வழிகாட்டுகிறேன்."
                    : lang === "ml"
                    ? "വിവരങ്ങൾ പങ്കിടുക. ഞാൻ ഘട്ടങ്ങളായി സഹായിക്കാം."
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

              {/* Claude-inspired Centerpiece Composer in Empty State */}
              <form className="hero-composer-card" onSubmit={handleSubmit}>
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={t.placeholder}
                  rows={2}
                  aria-label={t.placeholder}
                  disabled={busy}
                />
                <div className="hero-composer-bottom">
                  <div className="hero-composer-hint">
                    <span>
                      ↵ {lang === "kn" ? "Enter ಒತ್ತಿ" : lang === "te" ? "Enter నొక్కండి" : lang === "ta" ? "Enter அழுத்தவும்" : lang === "ml" ? "Enter അമർത്തുക" : "Press Enter to send"}
                    </span>
                    <span>
                      <ShieldCheck size={13} />
                      {t.privacy}
                    </span>
                  </div>
                  <div className="hero-composer-actions">
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
                      {busy ? <LoaderCircle size={18} className="spin" /> : <Send size={16} />}
                    </button>
                  </div>
                </div>
              </form>

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
                      <span className="persona-icon">
                        {p.icon === "senior" && <Users size={16} strokeWidth={1.8} />}
                        {p.icon === "farmer" && <Sprout size={16} strokeWidth={1.8} />}
                        {p.icon === "student" && <GraduationCap size={16} strokeWidth={1.8} />}
                        {p.icon === "women" && <UserRound size={16} strokeWidth={1.8} />}
                      </span>
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
                      {message.role === "assistant"
                        ? "Sahayaka"
                        : lang === "kn"
                        ? "ನೀವು"
                        : lang === "te"
                        ? "మీరు"
                        : lang === "ta"
                        ? "நீங்கள்"
                        : lang === "ml"
                        ? "നിങ്ങൾ"
                        : "You"}
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
                                    lang === "kn"
                                      ? "ವಿವರಗಳು"
                                      : lang === "te"
                                      ? "వివరాలు"
                                      : lang === "ta"
                                      ? "விவரங்கள்"
                                      : lang === "ml"
                                      ? "വിവരങ്ങൾ"
                                      : "details"
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
                          : lang === "te"
                          ? "మునుపటి వివరాలతో తేడా ఉంది. దయచేసి ప్రొఫైల్ పరిశీలించండి."
                          : lang === "ta"
                          ? "முந்தைய விவரங்களில் முரண்பாடு உள்ளது. சுயவிவரத்தைச் சரிபார்க்கவும்."
                          : lang === "ml"
                          ? "മുമ്പത്തെ വിവരങ്ങളിൽ പൊരുത്തക്കേടുണ്ട്. പ്രൊഫൈൽ പരിശോധിക്കുക."
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

          {messages.length > 0 && (
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
              <span>
                ↵{" "}
                {lang === "kn"
                  ? "ಕಳುಹಿಸಲು Enter ಒತ್ತಿ"
                  : lang === "te"
                  ? "పంపడానికి Enter నొక్కండి"
                  : lang === "ta"
                  ? "அனுப்ப Enter அழுத்தவும்"
                  : lang === "ml"
                  ? "അയക്കാൻ Enter അമർത്തുക"
                  : "Press Enter to send · Shift + Enter for new line"}
              </span>
              <span>
                <ShieldCheck size={13} />
                {t.privacy}
              </span>
            </div>
          </div>
          )}
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
              <span>
                {lang === "kn"
                  ? "ಸಂಗ್ರಹಿಸಿದ ವಿವರಗಳು"
                  : lang === "te"
                  ? "సేకరించిన వివరాలు"
                  : lang === "ta"
                  ? "சேகரிக்கப்பட்ட விவரங்கள்"
                  : lang === "ml"
                  ? "ശേഖരിച്ച വിവരങ്ങൾ"
                  : "Details collected"}
              </span>
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
              <p>
                {lang === "kn"
                  ? "ನಿಮ್ಮ ವಿವರಗಳಿಗೆ ಹೊಂದಿಕೆ"
                  : lang === "te"
                  ? "మీ వివరాలకు సరిపోలిక"
                  : lang === "ta"
                  ? "உங்கள் விவரங்களுக்குப் பொருத்தம்"
                  : lang === "ml"
                  ? "നിങ്ങളുടെ വിവരങ്ങൾക്ക് പൊരുത്തം"
                  : "Matched to your details"}
              </p>
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
                  : lang === "te"
                  ? "ఇవి ప్రాథమిక అవకాశాలు మాత్రమే; పూర్తి వివరాల సేకరణ తర్వాత తుది అర్హత ఫలితాలు కనిపిస్తాయి."
                  : lang === "ta"
                  ? "இவை ஆரம்ப சாத்தியக்கூறுகள் மட்டுமே; முழு விவரங்கள் பெறப்பட்ட பின் இறுதி முடிவுகள் வரும்."
                  : lang === "ml"
                  ? "ഇവ പ്രാഥമിക സാധ്യതകൾ മാത്രമാണ്; മുഴുവൻ വിവരങ്ങളും ശേഖരിച്ച ശേഷം അന്തിമ ഫലം ലഭ്യമാകും."
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
