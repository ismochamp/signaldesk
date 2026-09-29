"""Persistence regressions: reviews keep independent training provenance."""
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest
import app


class ResponseProbe:
    def send(self, data, *args, **kwargs):
        return data


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.previous_db = app.DB
        app.DB = str(Path(self.temp.name) / 'triage.sqlite')
        self.probe = ResponseProbe()
        with app.connect() as conn:
            conn.executemany('INSERT INTO examples(text,label) VALUES(?,?)', [
                ('invoice payment refund', 'Billing'),
                ('backend service error', 'Support'),
            ])

    def tearDown(self):
        app.DB = self.previous_db
        self.temp.cleanup()

    def request(self, text):
        with app.connect() as conn:
            return conn.execute(
                'INSERT INTO requests(text,prediction,created) VALUES(?,?,?)',
                (text, json.dumps({'label': 'Billing', 'score': .8, 'needs_review': False}), 'verification'),
            ).lastrowid

    def review(self, key, label):
        return app.App.post_api(self.probe, '/api/review', {'id': key, 'label': label})

    def learned(self):
        with app.connect() as conn:
            return set(app.examples(conn))

    def test_correction_preserves_independent_curated_example(self):
        key = self.request('invoice payment refund')
        self.review(key, 'Billing')
        self.review(key, 'Support')
        self.assertIn(('invoice payment refund', 'Billing'), self.learned())
        self.assertIn(('invoice payment refund', 'Support'), self.learned())
        with app.connect() as conn:
            self.assertEqual(conn.execute('SELECT count(*) FROM examples').fetchone()[0], 2)
            # Both categories remain available to the real classifier.
            self.assertIn(app.predict(app.examples(conn), 'invoice payment')['label'], {'Billing', 'Support'})

    def test_correction_replaces_only_current_request_feedback(self):
        key = self.request('please handle this separate record')
        self.review(key, 'Billing')
        self.review(key, 'Support')
        self.assertNotIn(('please handle this separate record', 'Billing'), self.learned())
        self.assertIn(('please handle this separate record', 'Support'), self.learned())

    def test_same_text_requests_keep_independent_current_reviews(self):
        first = self.request('shared verification request')
        second = self.request('shared verification request')
        self.review(first, 'Billing')
        self.review(second, 'Billing')
        self.review(first, 'Support')
        self.assertIn(('shared verification request', 'Billing'), self.learned())
        self.assertIn(('shared verification request', 'Support'), self.learned())
        self.review(second, 'Support')
        self.assertNotIn(('shared verification request', 'Billing'), self.learned())

    def test_repeated_reviews_and_curated_overlap_do_not_inflate_counts(self):
        key = self.request('invoice payment refund')
        self.review(key, 'Billing')
        result = self.review(key, 'Billing')
        self.assertEqual(result['training_count'], 2)
        self.assertEqual(sum(row['count'] for row in result['training']), len(self.learned()))
        key2 = self.request('independent feedback')
        result = self.review(key2, 'Support')
        self.assertEqual(result['training_count'], 3)
        self.assertEqual(sum(row['count'] for row in result['training']), len(self.learned()))

    def test_csv_export_retains_empty_review_and_guards_formulas(self):
        self.request('=1+1')
        content = app.App.get_api(self.probe, '/api/export')
        rows = list(csv.DictReader(io.StringIO(content)))
        self.assertEqual(rows[0]['reviewed_category'], '')
        self.assertEqual(rows[0]['request'], "'=1+1")


if __name__ == '__main__':
    unittest.main()
