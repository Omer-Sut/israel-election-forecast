"""Rebuild a six-election screening panel offline from reviewed facts and frozen results."""

from __future__ import annotations

import argparse
import copy
import gzip
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.baseline import ROOT, load_json
from scripts.backtest import historical_vector, score_seats

PANEL = ROOT / "data/snapshots/screening-six-elections-2026-10-21"


def table(name):
    path = ROOT / f"data/database/{name}.jsonl.gz"
    return [json.loads(line) for line in gzip.decompress(path.read_bytes()).decode("utf-8").splitlines()]


def prepare():
    audit = load_json(PANEL / "audit.json")
    official = table("official_lists")
    elections = {e["knesset"]: e for e in table("elections")}
    sources = {s["source_id"]: s for s in table("sources")}
    old_config = load_json(ROOT / "config/historical-backtest.json")
    outcomes = copy.deepcopy(load_json(ROOT / old_config["outcomes_path"]))
    outcomes.update(snapshot_id="screening-six-election-outcomes-2026-10-21-a",
                    status="final_results_official_except_2015_secondary_seats",
                    coverage="Six elections; every official seat-winning list and modeled zero-seat list. Omitted lists have zero final seats. 2015 seats/turnout are IDI secondary transcription; votes reconcile to official data.")
    files, specifications = {}, []
    earlier_reference = {"election_id": "knesset_19_2013", "election_date": "2013-01-22",
                         "turnout_pct": 67.77,
                         "source_url": "https://www.gov.il/apps/elections/elections-knesset-19/eng/list/Results_eng.html",
                         "retrieved_on": audit["retrieved_on"],
                         "availability_basis": "Completed earlier election. Official CEC indexed results checked October 21, 2026; first historical publication timestamp not reconstructed."}
    for specification in audit["elections"]:
        k, eid = specification["knesset"], specification["id"]
        definitions = specification["lists"]
        ids = sorted(row[0] for row in definitions)
        names = {row[2]: row[0] for row in definitions}
        codes = {row[1]: row[0] for row in definitions}
        if len(ids) != len(set(ids)) or len(names) != len(ids) or len(codes) != len(ids):
            raise ValueError("Ambiguous historical list mapping")
        result_rows = [r for r in official if r["knesset"] == k]
        if {r["ballot_code"] for r in result_rows if r["seats"] > 0} - set(codes):
            raise ValueError("An actual seat-winning list is missing from the panel")
        result_by_code = {r["ballot_code"]: r for r in result_rows}
        actual = {row[0]: result_by_code[row[1]]["seats"] for row in definitions}
        score_seats(actual, actual)
        polls = []
        for raw in specification["polls"]:
            if set(raw["raw_seats_by_label"]) != set(names):
                raise ValueError("Every audited normalized source label must map exactly once")
            poll = {key: value for key, value in raw.items() if key != "raw_seats_by_label"}
            poll.update(election_id=eid, kind="pre_election_poll", seat_projection_complete=True,
                        reported_seats={names[label]: value for label, value in raw["raw_seats_by_label"].items()},
                        source_reported_seats_english_labels=raw["raw_seats_by_label"],
                        audit_status=audit["audit_tier"], retrieved_on=audit["retrieved_on"])
            historical_vector(poll, ids)
            polls.append(poll)
        lists = [{"id": sid, "ballot_code": code, "label_en": en, "label_he": he,
                  "official_source_label_he": result_by_code[code].get("party_name_he")}
                 for sid, code, en, he in sorted(definitions)]
        snapshot = {"snapshot_id": f"screening-{eid}-2026-10-21-a", "election_id": eid,
                    "election_date": specification["election_date"], "retrieved_on": audit["retrieved_on"],
                    "audit_tier": audit["audit_tier"], "rights_note": audit["rights_note"],
                    "historical_vintage_limit": audit["historical_vintage_limit"],
                    "coverage": "Three declared polling groups; retrospective convenience panel, not exhaustive campaign coverage or necessarily each group's final release.",
                    "zero_seat_policy": "Only complete reviewed 120-seat allocations; percentages stay separate. No zero-support inference.",
                    "lists": lists, "polls": polls}
        filename = f"polls-{k}.json"
        files[filename] = snapshot
        election = elections[k]
        source_url = sources[election["source_id"]]["url"]
        outcomes["elections"][eid] = {"election_date": election["election_date"], "turnout_pct": election["turnout"],
                                      "seat_results": actual, "source_url": source_url,
                                      "source_id": election["source_id"],
                                      "source_tier": "secondary_idi_seats_official_votes_reconciled" if k == 20 else "official_cec",
                                      "source_list_codes": {sid: code for sid, code, _, _ in definitions},
                                      "omitted_official_lists": [{"ballot_code": r["ballot_code"], "seats": r["seats"]}
                                                                 for r in result_rows if r["ballot_code"] not in codes]}
        specifications.append({"id": eid, "polls_path": str((PANEL / "prepared" / filename).relative_to(ROOT)).replace("\\", "/"),
                               "period": "election_2015" if k == 20 else "repeated_elections_2019_2021",
                               "turnout_reference": earlier_reference})
        earlier_reference = {"election_id": eid, "election_date": election["election_date"],
                             "turnout_pct": election["turnout"], "source_url": source_url,
                             "retrieved_on": audit["retrieved_on"],
                             "availability_basis": "Previous completed election; exact first results-publication timestamp not reconstructed."}
    specifications.extend(copy.deepcopy(old_config["elections"]))
    files["outcomes.json"] = outcomes
    files["historical.json"] = dict(old_config, status="six_election_t1_retrospective_screening",
                                    horizons_days=[1], elections=specifications,
                                    outcomes_path=str((PANEL / "prepared/outcomes.json").relative_to(ROOT)).replace("\\", "/"))
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=PANEL / "prepared")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    files = prepare()
    for name, value in files.items():
        (args.out_dir / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                                          encoding="utf-8", newline="\n")
    print(f"Prepared {len(files)} files: four earlier poll snapshots, six-election outcomes/config; original pilot unchanged.")


if __name__ == "__main__":
    main()
