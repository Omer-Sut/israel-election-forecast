"""Geographic aggregate linkage, source format boundaries and denominator checks."""
import gzip
import hashlib
import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / file)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


builder = module('cbs_builder', 'build_database.py')
reporter = module('cbs_reporter', 'cbs_report.py')


class CBSTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.temp.name) / 'cbs.sqlite'
        builder.build(ROOT / 'data/database', cls.path)
        cls.db = sqlite3.connect(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls.temp.cleanup()

    def test_archived_cbs_sources_match_all_response_hashes(self):
        rows = self.db.execute('SELECT source_id,sha256 FROM cbs_sources').fetchall()
        self.assertEqual(len(rows), 19)
        for name, digest in rows:
            raw = gzip.decompress((ROOT / 'data/cbs-2026-10-21/raw-sources' / (name + '.gz')).read_bytes())
            self.assertEqual(hashlib.sha256(raw).hexdigest(), digest, name)

    def test_published_2019_city_total_not_added_to_its_subareas(self):
        population, method = self.db.execute("SELECT population,method FROM cbs_age_sex WHERE reference_year=2019 AND locality_code='3000' AND sex='total'").fetchone()
        self.assertEqual(population, 936425)
        self.assertEqual(method, 'published locality total')

    def test_mixed_city_and_changed_age_bands_are_retained(self):
        for year in [2020, 2021]:
            rows = self.db.execute("SELECT sex,population,age_bands FROM cbs_age_sex WHERE reference_year=? AND locality_code='5000'", (year,)).fetchall()
            self.assertEqual({r[0] for r in rows}, {'total', 'male', 'female'})
            bands = json.loads(next(r[2] for r in rows if r[0] == 'total'))
            self.assertGreater(bands['age_65_plus'], 0)
            self.assertNotIn('age_65_69', bands)  # CBS publishes a combined 65+ band here.

    def test_zero_party_votes_still_keep_the_denominator(self):
        self.assertGreater(self.db.execute('SELECT COUNT(*) FROM cbs_locality_vote_shares WHERE votes=0').fetchone()[0], 0)
        for k in range(20, 26):
            expected = self.db.execute("SELECT SUM(valid) FROM geography_totals WHERE knesset=? AND granularity='locality'", (k,)).fetchone()[0]
            # A rare party has many zero-vote localities; each still belongs in its denominator.
            ballot = self.db.execute('SELECT ballot_code FROM official_lists WHERE knesset=? ORDER BY votes LIMIT 1', (k,)).fetchone()[0]
            actual = self.db.execute('SELECT SUM(valid) FROM cbs_locality_vote_shares WHERE knesset=? AND ballot_code=?', (k, ballot)).fetchone()[0]
            self.assertEqual(actual, expected)

    def test_reference_date_does_not_imply_publication_eligibility(self):
        self.assertEqual(self.db.execute('SELECT SUM(historical_availability_verified) FROM cbs_sources').fetchone()[0], 0)
        row = self.db.execute("SELECT descriptive_only,demographic_reference_after_election FROM cbs_locality_election_context WHERE knesset=20 AND demographic_year=2022 LIMIT 1").fetchone()
        self.assertEqual(row, (1, 1))
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM cbs_ballot_locality_links WHERE locality_code='0'").fetchone()[0], 0)

    def test_published_district_median_is_preserved(self):
        row = self.db.execute("SELECT attributes FROM cbs_census_records WHERE source_id='census-broad.xlsx' AND sheet='District Sub-District Natural  ' AND district_code='4' AND subdistrict_code IS NULL AND natural_area_code IS NULL").fetchone()
        self.assertEqual(json.loads(row[0])['m_age_median'], 32)

    def test_missing_measure_has_its_own_weighted_denominator(self):
        result = reporter.weighted_percent([
            {'population': 100, 'x': 20}, {'population': 900, 'x': 40}, {'population': 1000, 'x': None}], 'x')
        self.assertEqual(result['percent'], 38)
        self.assertEqual(result['population_with_measure'], 1000)

    def test_special_ballot_codes_change_between_elections(self):
        result = reporter.report(self.db)
        rows = result['linkage_coverage']
        self.assertEqual(rows[0]['special_unlocated_valid_votes'], 232681)
        self.assertEqual(rows[1]['special_unlocated_valid_votes'], 238822)
        self.assertEqual(rows[-1]['special_unlocated_valid_votes'], 458714)
        self.assertTrue(all(99 < r['matched_share_of_located_valid_percent'] <= 100 for r in rows))
        self.assertIsNone(self.db.row_factory)


if __name__ == '__main__':
    unittest.main()
