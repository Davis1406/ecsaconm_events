// Mirrors api/utils/abstract_book_generator.py's section parsing so the
// on-screen abstract view (admin + participant) bolds/indents the same
// Background / Methods / Results / Conclusion style headings the printed
// Abstract Book uses.

const SECTION_LABELS = [
  "Background", "Introduction", "Aim", "Aims", "Objective", "Objectives",
  "Purpose", "Methodology", "Methods", "Method", "Results", "Findings",
  "Result", "Discussion", "Conclusion", "Conclusions", "Recommendation",
  "Recommendations", "Implications",
];
const LABEL_RE = new RegExp(`\\b(${SECTION_LABELS.join("|")})\\s*:\\s*`, "gi");

const BOILERPLATE_RE = /please read and follow the guide below.*?format provided\.\s*(note:\s*no tables,\s*figures,\s*or references should be included in the abstract\.\s*)?/is;

function escapeHtml(text) {
  return (text || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// Returns [{label, body}] — label is '' for any leading text before the
// first recognised heading.
export function parseAbstractSections(rawText) {
  const text = (rawText || "").replace(BOILERPLATE_RE, "").trim();
  if (!text) return [];

  const matches = [...text.matchAll(LABEL_RE)];
  if (matches.length === 0) return [{ label: "", body: text }];

  const sections = [];
  if (matches[0].index > 0) {
    const lead = text.slice(0, matches[0].index).trim();
    if (lead) sections.push({ label: "", body: lead });
  }
  matches.forEach((m, i) => {
    const label = m[1].trim().replace(/\w\S*/g, w => w[0].toUpperCase() + w.slice(1).toLowerCase());
    const start = m.index + m[0].length;
    const end = i + 1 < matches.length ? matches[i + 1].index : text.length;
    const body = text.slice(start, end).replace(/\s+/g, " ").trim();
    if (body) sections.push({ label, body });
  });
  return sections;
}

// Renders the abstract body as HTML with each recognised section label bold,
// and the body text indented beneath it — for use with v-html.
export function formatAbstractHtml(rawText) {
  const sections = parseAbstractSections(rawText);
  if (sections.length === 0) return "";
  return sections
    .map(({ label, body }) => {
      const safeBody = escapeHtml(body);
      if (!label) return `<p class="mb-2">${safeBody}</p>`;
      return `<p class="mb-2 pl-3 border-l-2 border-gray-200"><strong>${escapeHtml(label)}:</strong> ${safeBody}</p>`;
    })
    .join("");
}
