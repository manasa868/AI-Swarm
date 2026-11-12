"""FastAPI Inference Service for Fake News Detection."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.model_pipeline import LightweightFakeNewsClassifier

app = FastAPI(title="Fake News Detection API", version="1.0.0")

classifier = LightweightFakeNewsClassifier()
# Train on startup sample corpus
training_texts = [
    "Government announces science grant for university research",
    "Aliens land on Moon during solar eclipse secret documents reveal",
    "Tech giant unveils energy efficient CPU silicon architecture",
    "Drinking seawater turns hair golden overnight miracle cure",
    "Vaccine trial results publish successful Phase 3 randomized test",
    "Celebrity discovers infinite energy device using simple magnets",
    "Central bank lowers interest rates by 25 basis points",
    "Eating rocks proven to improve human digestion drastically"
]
training_labels = ["REAL", "FAKE", "REAL", "FAKE", "REAL", "FAKE", "REAL", "FAKE"]
classifier.fit(training_texts, training_labels)


class NewsRequest(BaseModel):
    title: str = Field(..., example="Central bank adjusts inflation targets")
    content: str = Field(..., example="The committee concluded meetings today with a 25 basis point adjustment.")


class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    is_fake: bool
    raw_score: float


@app.get("/health")
def health():
    return {"status": "healthy", "model_trained": classifier.is_trained}


@app.post("/predict", response_model=PredictionResponse)
def predict(request: NewsRequest):
    full_text = f"{request.title} {request.content}"
    result = classifier.predict(full_text)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)
