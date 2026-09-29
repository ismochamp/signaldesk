import unittest
from engine import predict
class ClassificationTests(unittest.TestCase):
    samples=[('invoice payment refund billing','Billing'),('invoice duplicate payment','Billing'),('server error timeout crash','Support'),('backend service error timeout','Support')]
    def test_known_category(self):self.assertEqual(predict(self.samples,'duplicate invoice payment')['label'],'Billing')
    def test_unknown_abstains(self):
        r=predict(self.samples,'orchid butterfly lavender');self.assertTrue(r['needs_review']);self.assertEqual(r['label'],'Unclassified')
    def test_sparse_overlap_review(self):self.assertTrue(predict(self.samples,'invoice spaceship telescope')['needs_review'])
    def test_requires_two_categories(self):
        with self.assertRaises(ValueError):predict([('invoice','Billing')],'invoice')
    def test_scores_normalized(self):self.assertAlmostEqual(sum(x['score'] for x in predict(self.samples,'error')['scores']),1,places=3)
    def test_unicode(self):self.assertEqual(predict([('réparation fenêtre','Support'),('facture paiement','Billing')],'réparation fenêtre')['label'],'Support')
if __name__=='__main__':unittest.main()
