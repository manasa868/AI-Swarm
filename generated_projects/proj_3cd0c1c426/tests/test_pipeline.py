"""Automated Unit Tests for ML Pipeline."""
import unittest
from src.model_pipeline import LightweightFakeNewsClassifier, TextPreprocessor


class TestMLPipeline(unittest.TestCase):
    def setUp(self):
        self.classifier = LightweightFakeNewsClassifier()
        self.texts = [
            "Research institute publishes peer reviewed medical study",
            "Magic mineral removes all diseases in twenty four hours"
        ]
        self.labels = ["REAL", "FAKE"]
        self.classifier.fit(self.texts, self.labels)

    def test_text_cleaning(self):
        raw = "BREAKING News!!! Visit http://example.com/ #Shocking"
        cleaned = TextPreprocessor.clean_text(raw)
        self.assertTrue("breaking news" in cleaned)
        self.assertFalse("!" in cleaned)

    def test_model_training_and_prediction(self):
        self.assertTrue(self.classifier.is_trained)
        res_real = self.classifier.predict("Peer reviewed medical journal study published")
        res_fake = self.classifier.predict("Magic mineral cures every known sickness")
        
        self.assertEqual(res_real["prediction"], "REAL")
        self.assertEqual(res_fake["prediction"], "FAKE")
        
        # Validation threshold:
        self.assertGreaterEqual(res_real["confidence"], 0.75, "Model confidence meets deployment standard")


if __name__ == "__main__":
    unittest.main()
