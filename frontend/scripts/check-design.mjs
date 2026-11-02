import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, extname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const SRC = fileURLToPath(new URL('../src', import.meta.url));
const EXT = new Set(['.svelte', '.ts', '.css', '.html']);

const RULES = [
  { id: 'raw-color', skipTokens: true, msg: 'Warna mentah di luar tokens.css',
    re: /#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(|\boklch\(/g },
  { id: 'tailwind-default-palette', msg: 'Kelas warna bawaan Tailwind dilarang',
    re: /\b(?:bg|text|border|ring|fill|stroke|from|to|via)-(?:white|black|(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3})\b/g },
  { id: 'banned-font', msg: 'Font terlarang',
    re: /\b(?:Inter|Roboto|Open Sans|Lato|Poppins|Montserrat|Raleway|Work Sans|DM Sans|Nunito|Arial|Helvetica)\b/g },
  { id: 'transition-all', msg: 'transition-all dilarang', re: /transition-all|transition:\s*all\b/g },
  { id: 'gradient', msg: 'Gradien dilarang', re: /linear-gradient|radial-gradient|conic-gradient|bg-gradient-|bg-clip-text|background-clip:\s*text/g },
  { id: 'hover-scale', msg: 'hover:scale dilarang', re: /hover:scale-/g },
  { id: 'viewport-hero', msg: 'Hero 100vh / 100vw dilarang', re: /min-h-screen|min-height:\s*100d?vh|\b100vw\b/g },
  { id: 'emoji-icon', msg: 'Emoji/simbol sebagai ikon dilarang (pakai Lucide)',
    re: /[\u{1F300}-\u{1FAFF}\u2600-\u27BF\u2B50]/gu },
  { id: 'dark-mode', msg: 'Tema gelap tidak dipakai',
    re: /\bdark:|prefers-color-scheme:\s*dark/g },
  { id: 'side-stripe', msg: 'Garis tebal satu sisi dilarang',
    re: /\bborder-l-[2-9]\b|border-left:\s*[2-9]px/g },
  { id: 'italic-heading', msg: 'Judul tidak boleh italic', re: /<h[1-3][^>]*\bitalic\b/g },
  { id: 'z-index', msg: 'z-index bilangan besar dilarang', re: /z-index:\s*\d{3,}|z-\[\d{3,}\]/g },
  { id: 'html-raw', msg: '{@html} dilarang pada konten pesan', re: /\{@html\b/g },
  { id: 'straight-ellipsis', msg: 'Gunakan … bukan ... pada teks UI', re: />[^<{]*\.\.\.[^<{]*</g },
];

function* walk(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    const s = statSync(p);
    if (s.isDirectory()) yield* walk(p);
    else if (EXT.has(extname(p))) yield p;
  }
}

let violations = 0;
for (const file of walk(SRC)) {
  const isTokens = basename(file) === 'tokens.css';
  const lines = readFileSync(file, 'utf8').split(/\r?\n/);
  lines.forEach((line, i) => {
    for (const r of RULES) {
      if (r.skipTokens && isTokens) continue;
      r.re.lastIndex = 0;
      if (r.re.test(line)) {
        violations++;
        console.error(`${file}:${i + 1}  [${r.id}] ${r.msg}\n    ${line.trim()}`);
      }
    }
  });
}

if (violations) {
  console.error(`\n${violations} pelanggaran desain.`);
  process.exit(1);
}
console.log('lint:design bersih.');
