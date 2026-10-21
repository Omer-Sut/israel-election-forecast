"""Check source reconciliation and important bulk-transcription boundaries."""
import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('database_builder', ROOT / 'scripts/build_database.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class DatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.temp.name) / 'test.sqlite'
        cls.report = builder.build(ROOT / 'data/database', cls.path)
        cls.db = sqlite3.connect(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls.temp.cleanup()

    def test_six_elections_and_both_geographies_reconcile(self):
        self.assertEqual(self.report['tables']['elections'], 6)
        builder.validate(self.db)

    def test_bulk_poll_dates_are_not_verified_publication_dates(self):
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM polls WHERE publication_date IS NOT NULL').fetchone()[0], 0)
        self.assertEqual(self.db.execute('SELECT COUNT(DISTINCT knesset) FROM campaign_poll_candidates').fetchone()[0], 6)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM campaign_poll_candidates WHERE record_kind!='poll_index_row' OR campaign_main!=1").fetchone()[0], 0)

    def test_2020_blue_white_is_a_value_not_metadata(self):
        rows = self.db.execute("""SELECT p.metadata,v.value FROM campaign_poll_candidates p
            JOIN poll_values v USING(poll_id) WHERE p.knesset=23 AND p.date_proxy='2020-02-28'
            AND v.list_label='Blue &White'"""
        ).fetchall()
        self.assertTrue(rows)
        self.assertTrue(all(value > 20 and len(json.loads(metadata)) == 2 for metadata, value in rows))

    def test_2018_polls_are_not_misdated_after_april_2019_election(self):
        count = self.db.execute("SELECT COUNT(*) FROM campaign_poll_candidates WHERE knesset=21 AND date_proxy LIKE '2018-%'").fetchone()[0]
        self.assertGreater(count, 15)

    def test_archived_raw_sources_match_response_hashes(self):
        import gzip
        import hashlib
        checked = 0
        for source_id, digest in self.db.execute('SELECT source_id,sha256 FROM sources'):
            path = ROOT / 'data/database/raw-sources' / (source_id + '.gz')
            if path.exists():
                checked += 1
                self.assertEqual(hashlib.sha256(gzip.decompress(path.read_bytes())).hexdigest(), digest, source_id)
        self.assertEqual(checked, 23)

    def test_2015_merged_numeric_cells_have_combined_labels(self):
        count = self.db.execute("SELECT COUNT(*) FROM poll_values v JOIN polls p USING(poll_id) WHERE p.knesset=20 AND v.list_label LIKE '%Labor + Hatnuah%' AND v.value>0").fetchone()[0]
        self.assertGreater(count, 0)

    def test_ines_stays_aggregate_and_unweighted(self):
        self.assertEqual(self.db.execute('SELECT SUM(respondents) FROM ines_studies').fetchone()[0], 9071)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM ines_frequencies WHERE count<5').fetchone()[0], 0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM ines_frequencies WHERE weighting!='unweighted'").fetchone()[0], 0)
        self.assertGreater(self.report['tables']['ines_value_labels'], 8000)


if __name__ == '__main__':
    unittest.main()
