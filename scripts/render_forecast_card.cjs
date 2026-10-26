// Render a shareable Hebrew forecast card from the adopted, versioned export.
// Requires Playwright and a Chromium executable; both can be supplied by env.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const root = path.resolve(__dirname, '..');
const out = path.join(root, 'reports', 'submission-package-2026-10-26');
const forecast = JSON.parse(fs.readFileSync(path.join(root, 'reports', 'forecast-decision-2026-10-25', 'forecast.json'), 'utf8'));
const fields = JSON.parse(fs.readFileSync(path.join(root, 'config', 'submission-fields.json'), 'utf8')).seat_fields;
const seats = forecast.seats;
if (Object.keys(seats).length !== 15 || Object.values(seats).reduce((a, b) => a + b, 0) !== 120) throw new Error('Seat vector invalid');
if (Object.values(seats).some(n => n !== 0 && n < 3)) throw new Error('One- or two-seat list');
if (forecast.national_turnout_pct !== '69.86') throw new Error('Unexpected turnout');

const labels = Object.fromEntries(fields.map(f => [f.id, f.label_he.replace(/^מנדטים:\s*/, '')]));
const colors = ['#4238d4', '#23779c', '#ad4c89', '#ab6e16', '#1d8a71'];
const entries = fields.map((f, i) => ({id: f.id, label: labels[f.id], seats: seats[f.id], order: i}));
entries.sort((a, b) => b.seats - a.seats || a.order - b.order);
const safe = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[c]));
const cards = entries.map((p, i) => {
  const accent = p.seats ? colors[i % colors.length] : '#9aa8b8';
  const zero = p.seats === 0 ? ' zero' : '';
  return `<article class="card${zero}" style="--accent:${accent}"><div class="party">${safe(p.label)}</div><div class="bottom"><div class="num">${p.seats}</div><div class="unit">מנדטים</div></div></article>`;
}).join('');

const html = `<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><title>תחזית המנדטים - 26.10.2026</title>
<style>
*{box-sizing:border-box}html,body{margin:0;width:1400px;height:1600px}body{font-family:Arial,"Segoe UI",sans-serif;color:#f6f8ff;background:#101a31}main{width:1400px;height:1600px;padding:62px 70px 42px;position:relative;overflow:hidden;background:radial-gradient(circle at 15% 5%,#26345b 0,transparent 39%),linear-gradient(145deg,#101a31 0%,#151c30 100%)}main:before{content:"";position:absolute;left:-160px;top:180px;width:480px;height:480px;border:1px solid #ffffff16;border-radius:50%}main:after{content:"";position:absolute;left:-230px;top:110px;width:680px;height:680px;border:1px solid #ffffff10;border-radius:50%}.top{display:flex;justify-content:space-between;align-items:start;position:relative;z-index:1}.eyebrow{font-size:21px;letter-spacing:.3px;color:#9fddf2;font-weight:700}.date{font-size:18px;color:#d0d8e8;background:#ffffff15;border:1px solid #ffffff20;padding:11px 19px;border-radius:30px}.title{font-size:70px;line-height:1.05;letter-spacing:-1.8px;font-weight:800;margin:16px 0 9px}.subtitle{color:#c8d5e5;font-size:22px;margin:0}.hero{display:flex;gap:15px;margin:35px 0 32px;position:relative;z-index:1}.metric{background:#ffffff12;border:1px solid #ffffff24;border-radius:19px;padding:15px 23px;min-width:200px;display:flex;align-items:baseline;gap:11px}.metric strong{font-size:39px;line-height:1;color:#fff}.metric span{font-size:20px;color:#c8d5e5}.metric.turnout{background:#31c6aa20;border-color:#44d2b857}.metric.turnout strong{color:#77e4cc}.grid{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(5,194px);gap:15px;position:relative;z-index:1}.card{background:#f9fbff;color:#152139;border-radius:18px;padding:23px 26px 20px;box-shadow:0 4px 0 #00000014;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden}.card:before{content:"";position:absolute;right:0;top:0;bottom:0;width:9px;background:var(--accent)}.card.zero{background:#e8edf3;color:#687789}.party{font-weight:700;font-size:25px;line-height:1.22;max-width:100%;min-height:58px}.bottom{display:flex;align-items:baseline;gap:12px}.num{font-size:68px;line-height:.91;letter-spacing:-2px;font-weight:800;color:var(--accent)}.unit{font-size:19px;color:#718098}.zero .unit{color:#8794a2}.footer{display:flex;justify-content:space-between;gap:25px;align-items:end;margin-top:25px;position:relative;z-index:1}.note{font-size:18px;line-height:1.48;color:#c8d5e5;max-width:930px}.note strong{color:#fff}.mark{font-size:17px;color:#91a2bc;white-space:nowrap;text-align:left}
</style></head><body><main><div class="top"><div><div class="eyebrow">הבחירות לכנסת ה־26 · תחזית מודל</div><h1 class="title">תחזית המנדטים</h1><p class="subtitle">הערכה שיטתית על בסיס סקרים · אינה סקר דעת קהל חדש</p></div><div class="date">26.10.2026</div></div><div class="hero"><div class="metric"><strong>120</strong><span>מנדטים בסך הכול</span></div><div class="metric turnout"><strong>${safe(forecast.national_turnout_pct)}%</strong><span>שיעור הצבעה חזוי</span></div></div><section class="grid">${cards}</section><div class="footer"><div class="note"><strong>מקור:</strong> תחזית israel-election-forecast, על בסיס סקרים שנבדקו עד 24.10.2026.<br>מיפוי הרשימה המשותפת לשדה חד״ש־תע״ל הוא הנחה; התחזית טרם הוגשה.</div><div class="mark">israel-election-forecast</div></div></main></body></html>`;

async function main() {
  fs.mkdirSync(out, {recursive:true});
  fs.writeFileSync(path.join(out, 'forecast-card.he.html'), html, 'utf8');
  const browser = await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE || undefined,headless:true});
  try {
    const page = await browser.newPage({viewport:{width:1400,height:1600},deviceScaleFactor:1});
    await page.goto('file:///' + path.join(out, 'forecast-card.he.html').replaceAll('\\','/'));
    await page.screenshot({path:path.join(out,'forecast-card.he.png'),fullPage:true});
    await page.close();
  } finally { await browser.close(); }
  console.log('Rendered forecast-card.he.png: 15 fields, 120 seats, turnout ' + forecast.national_turnout_pct + '%');
}
main().catch(err => {console.error(err);process.exitCode=1});
