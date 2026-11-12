"""Text classification and inference pipeline."""
import re
import math
from typing import List, Dict, Any, Tuple


class TextPreprocessor:
    @staticmethod
    def clean_text(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
        return " ".join(text.split())


class LightweightFakeNewsClassifier:
    """Production-ready text classifier with TF-IDF weighting and linear classification."""
    def __init__(self):
        self.vocabulary = {}
        self.idf = {}
        self.weights = {}
        self.bias = 0.0
        self.is_trained = False

    def fit(self, texts: List[str], labels: List[str]):
        cleaned_texts = [TextPreprocessor.clean_text(t) for t in texts]
        doc_count = len(cleaned_texts)
        
        # Build vocabulary & Document frequencies
        df = {}
        for text in cleaned_texts:
            tokens = set(text.split())
            for t in tokens:
                df[t] = df.get(t, 0) + 1
        
        self.vocabulary = {term: idx for idx, term in enumerate(df.keys())}
        self.idf = {term: math.log((1 + doc_count) / (1 + count)) + 1.0 for term, count in df.items()}
        
        # Train linear weights (REAL=+1, FAKE=-1)
        self.weights = {term: 0.0 for term in self.vocabulary}
        for epoch in range(15):
            for text, label in zip(cleaned_texts, labels):
                target = 1.0 if label == "REAL" else -1.0
                tokens = text.split()
                score = sum(self.weights.get(t, 0.0) * self.idf.get(t, 1.0) for t in tokens) + self.bias
                if target * score <= 1.0:
                    for t in tokens:
                        if t in self.weights:
                            self.weights[t] += 0.2 * target * self.idf.get(t, 1.0)
                    self.bias += 0.1 * target
        
        self.is_trained = True

    def predict(self, text: str) -> Dict[str, Any]:
        cleaned = TextPreprocessor.clean_text(text)
        tokens = cleaned.split()
        score = sum(self.weights.get(t, 0.0) * self.idf.get(t, 1.0) for t in tokens) + self.bias
        probability = 1.0 / (1.0 + math.exp(-max(-10.0, min(10.0, score))))
        predicted_label = "REAL" if score >= 0.0 else "FAKE"
        confidence = probability if predicted_label == "REAL" else (1.0 - probability)

        return {
            "prediction": predicted_label,
            "confidence": round(confidence, 4),
            "raw_score": round(score, 4),
            "is_fake": predicted_label == "FAKE"
        }
