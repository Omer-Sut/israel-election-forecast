"""Build copy sheets and printable source HTML from the adopted forecast.

This never submits a form or changes forecast values. Render the generated HTML to
PDF with scripts/render_submission_pdfs.cjs and visually inspect both PDFs.
"""
from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "submission-package-2026-10-26"
FORECAST = ROOT / "reports" / "forecast-decision-2026-10-25" / "forecast.json"
FIELDS = ROOT / "config" / "submission-fields.json"
SNAPSHOT = ROOT / "data" / "snapshots" / "polls-2026-10-24.json"
REPO = "https://github.com/Omer-Sut/israel-election-forecast"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    forecast = read_json(FORECAST)
    contract = read_json(FIELDS)
    assert list(forecast["seats"]) == [f["id"] for f in contract["seat_fields"]]
    assert len(forecast["seats"]) == 15
    assert sum(forecast["seats"].values()) == contract["seat_total"] == 120
    assert all(n == 0 or n >= 3 for n in forecast["seats"].values())
    turnout = float(forecast["national_turnout_pct"])
    bounds = contract["turnout_field"]
    assert bounds["minimum"] <= turnout <= bounds["maximum"]
    assert f"{turnout:.2f}" == forecast["national_turnout_pct"]
    assert forecast["source_freeze_complete"] is False
    assert forecast["exact_current_bader_ofer"] is False

    snapshot = read_json(SNAPSHOT)
    assert snapshot  # source manifest must exist
    sources_en = (
        "Reviewed published seat polls through 24 October 2026 from Midgam/N12, "
        "Channel 13, Lazar/Maariv, Kantar/Israel Hayom, Direct Polls/i24NEWS, "
        "Next Data/Channel 14 and Tatika/Zman; exact release URLs and dates are in "
        "data/snapshots/polls-2026-10-24.json. "
        "official Central Elections Committee national turnout results for the 2020, 2021 "
        "and 2022 Knesset elections (data/snapshots/turnout-history-2026-10-24/inputs.json). "
        "The current Joint List-to-Hadash-Ta'al form mapping is documented in "
        "config/poll-mappings.json."
    )
    sources_he = (
        "סקרי מנדטים שפורסמו ונבדקו עד 24 באוקטובר 2026 מאת מידגם/N12, "
        "ערוץ 13, לזר/מעריב, קנטאר/ישראל היום, דיירקט פולס/i24NEWS, "
        "נקסט דאטה/ערוץ 14 וטאטיקה/זמן. קישורים לפרסומים ותאריכים מופיעים בקובץ "
        "data/snapshots/polls-2026-10-24.json. "
        "תוצאות שיעור ההצבעה הארצי הרשמיות של ועדת הבחירות המרכזית בבחירות לכנסת "
        "בשנים 2020, 2021 ו־2022 (data/snapshots/turnout-history-2026-10-24/inputs.json). "
        "מיפוי הרשימה המשותפת לשדה חד״ש־תע״ל מתועד בקובץ config/poll-mappings.json."
    )
    data_link = f"{REPO}/blob/main/data/snapshots/polls-2026-10-24.json"
    turnout_link = f"{REPO}/blob/main/data/snapshots/turnout-history-2026-10-24/inputs.json"
    code_link = f"{REPO}/blob/main/scripts/forecast_decision.py"
    doc_link = f"{REPO}/tree/main/reports/submission-package-2026-10-26"

    counts = {}
    for lang, sources in (("en", sources_en), ("he", sources_he)):
        method = (OUT / f"method.{lang}.txt").read_text(encoding="utf-8").strip()
        counts[lang] = len(method.split())
        assert counts[lang] <= 500
        title = "Individual systematic forecast - method note" if lang == "en" else "תחזית שיטתית אישית - תיאור השיטה"
        source_title = "Data sources" if lang == "en" else "מקורות הנתונים"
        note = ("This is a prepared forecast, not a submitted form. Source verification remains incomplete."
                if lang == "en" else "זוהי תחזית מוכנה לבדיקה, ולא טופס שהוגש. אימות המקורות טרם הושלם.")
        direction = "ltr" if lang == "en" else "rtl"
        paras = "\n".join(f"<p>{html.escape(p)}</p>" for p in method.split("\n\n"))
        markup = f'''<!doctype html><html lang="{lang}" dir="{direction}"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>@page {{ size: A4; margin: 17mm 19mm 17mm 19mm; }} body {{ font-family: Arial, sans-serif; color:#18212b; font-size:10.5pt; line-height:1.46; }} h1 {{ font-size:18pt; margin:0 0 4mm; }} h2 {{ font-size:11pt; margin:5mm 0 2mm; }} p {{ margin:0 0 3mm; }} .meta {{ color:#4c5663; font-size:9pt; margin-bottom:6mm; }} .sources {{ border-top:1px solid #aeb8c2; padding-top:3mm; font-size:9pt; }} .url {{ direction:ltr; unicode-bidi:embed; word-break:break-all; font-size:8.5pt; }} footer {{ margin-top:5mm; color:#4c5663; font-size:8.5pt; }}</style></head>
<body><h1>{html.escape(title)}</h1><p class="meta">26 October 2026 | {counts[lang]} words in the copy-ready method description</p>
<main>{paras}</main><section class="sources"><h2>{source_title}</h2><p>{html.escape(sources)}</p><p class="url">{html.escape(REPO)}</p></section><footer>{html.escape(note)}</footer></body></html>'''
        (OUT / f"method.{lang}.html").write_text(markup, encoding="utf-8")

        lines = [
            ("INDIVIDUAL SYSTEMATIC ENTRY - COPY SHEET" if lang == "en" else "הגשה אישית שיטתית - דף העתקה"),
            ("Prepared for review; not submitted." if lang == "en" else "הוכן לבדיקה; לא הוגש."), "",
            ("Track: Systematic/competitive - individual" if lang == "en" else "מסלול: שיטתי/תחרותי - יחיד"),
            ("Email and full name: enter privately in the form." if lang == "en" else "דוא״ל ושם מלא: יש להזין באופן פרטי בטופס."), "",
            ("SEATS - form order" if lang == "en" else "מנדטים - לפי סדר השדות בטופס"),
        ]
        for i, field in enumerate(contract["seat_fields"], 1):
            label = field["label_en"] if lang == "en" else field["label_he"]
            lines.append(f'{i:02d}. {label}: {forecast["seats"][field["id"]]}')
        lines += [
            f'Total / סך הכול: {sum(forecast["seats"].values())}',
            f'{"National turnout" if lang == "en" else "שיעור הצבעה ארצי"}: {forecast["national_turnout_pct"]}%', "",
            ("METHOD DESCRIPTION - paste this language only" if lang == "en" else "תיאור השיטה - להדביק שפה זו בלבד"),
            method, "",
            ("DATA SOURCES" if lang == "en" else "מקורות הנתונים"), sources, data_link, turnout_link, "",
            ("CODE LINK" if lang == "en" else "קישור לקוד"), code_link, "",
            ("PREFERRED DOCUMENT LINK" if lang == "en" else "קישור מועדף למסמך"), doc_link, "",
            ("Presentation agreement: select your own answer in the form; no consent is assumed."
             if lang == "en" else "הסכמה להצגת השיטה: יש לבחור תשובה אישית בטופס; לא הונחה הסכמה."),
        ]
        (OUT / f"form-fields.{lang}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    validation = {
        "source_forecast": str(FORECAST.relative_to(ROOT)).replace("\\", "/"),
        "source_forecast_sha256": sha256(FORECAST),
        "poll_snapshot": str(SNAPSHOT.relative_to(ROOT)).replace("\\", "/"),
        "source_freeze_complete": False,
        "exact_current_bader_ofer": False,
        "seat_field_count": 15,
        "seat_sum": 120,
        "one_or_two_seat_fields": 0,
        "national_turnout_pct": forecast["national_turnout_pct"],
        "method_word_counts_whitespace": counts,
        "form_live_authenticated": False,
        "submitted": False,
        "pdf_sha256": {
            lang: sha256(OUT / f"method.{lang}.pdf")
            for lang in ("en", "he") if (OUT / f"method.{lang}.pdf").exists()
        },
    }
    (OUT / "validation.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    build()
