import React from "react";
import { CheckCircle2, Info, Lightbulb, XCircle } from "lucide-react";

interface FormattedReplyProps {
  text: string;
}

const INLINE_TOKEN_RE = /(\[[^\]]+\]\(https?:\/\/[^)\s]+\)|\*\*[^*]+\*\*|\*[^*\n]+\*|`[^`\n]+`)/g;

function renderInline(text: string, keyPrefix: string): React.ReactNode[] {
  const parts = text.split(INLINE_TOKEN_RE);
  return parts.map((part, idx) => {
    const key = `${keyPrefix}-${idx}`;
    if (!part) return null;

    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      return <strong key={key}>{part.slice(2, -2)}</strong>;
    }

    if (part.startsWith("*") && part.endsWith("*") && part.length > 2) {
      return <em key={key}>{part.slice(1, -1)}</em>;
    }

    if (part.startsWith("`") && part.endsWith("`") && part.length > 2) {
      return <code key={key}>{part.slice(1, -1)}</code>;
    }

    const linkMatch = /^\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)$/.exec(part);
    if (linkMatch) {
      return (
        <a key={key} href={linkMatch[2]} target="_blank" rel="noreferrer">
          {linkMatch[1]}
        </a>
      );
    }

    return <React.Fragment key={key}>{part}</React.Fragment>;
  });
}

function getSectionHeadingBadge(heading: string): {
  icon: React.ReactNode;
  variant: "eligible" | "unknown" | "failed" | "alternative" | "default";
} {
  const lower = heading.toLowerCase();
  if (lower.includes("not currently qualify") || lower.includes("ineligible")) {
    return { icon: <XCircle size={15} strokeWidth={2} />, variant: "failed" };
  }
  if (lower.includes("appear eligible") || lower.includes("appears eligible")) {
    return { icon: <CheckCircle2 size={15} strokeWidth={2} />, variant: "eligible" };
  }
  if (lower.includes("alternative") || lower.includes("near-miss")) {
    return { icon: <Lightbulb size={15} strokeWidth={2} />, variant: "alternative" };
  }
  if (lower.includes("verification") || lower.includes("more information") || lower.includes("information needed")) {
    return { icon: <Info size={15} strokeWidth={2} />, variant: "unknown" };
  }
  return { icon: null, variant: "default" };
}

export function FormattedReply({ text }: FormattedReplyProps) {
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  const blocks: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i].trim();

    if (!line) {
      i++;
      continue;
    }

    if (/^---+$/.test(line)) {
      blocks.push(<hr key={`hr-${i}`} className="md-divider" />);
      i++;
      continue;
    }

    if (line.startsWith("### ")) {
      blocks.push(
        <h3 key={`h3-${i}`} className="md-h3">
          {renderInline(line.slice(4).trim(), `h3-${i}`)}
        </h3>
      );
      i++;
      continue;
    }

    if (line.startsWith("#### ")) {
      const headingText = line.slice(5).trim();
      const { icon, variant } = getSectionHeadingBadge(headingText);
      blocks.push(
        <h4 key={`h4-${i}`} className={`md-h4 md-h4-${variant}`}>
          {icon && <span className="md-h4-icon">{icon}</span>}
          <span>{renderInline(headingText, `h4-${i}`)}</span>
        </h4>
      );
      i++;
      continue;
    }

    if (line.startsWith(">")) {
      const quoteLines: string[] = [];
      const start = i;
      while (i < lines.length && lines[i].trim().startsWith(">")) {
        quoteLines.push(lines[i].trim().replace(/^>\s?/, ""));
        i++;
      }
      blocks.push(
        <blockquote key={`bq-${start}`} className="md-quote">
          {quoteLines.map((qLine, qIdx) =>
            qLine ? <p key={`bq-${start}-${qIdx}`}>{renderInline(qLine, `bq-${start}-${qIdx}`)}</p> : null
          )}
        </blockquote>
      );
      continue;
    }

    if (/^[-*•]\s+/.test(line)) {
      const items: string[] = [];
      const start = i;
      while (i < lines.length && /^[-*•]\s+/.test(lines[i].trim())) {
        items.push(lines[i].trim().replace(/^[-*•]\s+/, ""));
        i++;
      }
      blocks.push(
        <ul key={`ul-${start}`} className="md-list">
          {items.map((item, liIdx) => (
            <li key={`ul-${start}-${liIdx}`}>{renderInline(item, `ul-${start}-${liIdx}`)}</li>
          ))}
        </ul>
      );
      continue;
    }

    if (/^\d+\.\s+/.test(line)) {
      const items: string[] = [];
      const start = i;
      while (i < lines.length && /^\d+\.\s+/.test(lines[i].trim())) {
        items.push(lines[i].trim().replace(/^\d+\.\s+/, ""));
        i++;
      }
      blocks.push(
        <ol key={`ol-${start}`} className="md-list md-ordered">
          {items.map((item, liIdx) => (
            <li key={`ol-${start}-${liIdx}`}>{renderInline(item, `ol-${start}-${liIdx}`)}</li>
          ))}
        </ol>
      );
      continue;
    }

    const isSchemeHeading = line.startsWith("**") && !line.endsWith(".");
    blocks.push(
      <p key={`p-${i}`} className={isSchemeHeading ? "md-scheme-title" : undefined}>
        {renderInline(line, `p-${i}`)}
      </p>
    );
    i++;
  }

  return <div className="markdown-reply">{blocks}</div>;
}
