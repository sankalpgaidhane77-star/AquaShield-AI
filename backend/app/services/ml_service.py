import sys
import os

# Add repo root to sys.path so ml.predict can be loaded
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.predict import get_predictor

class MLService:
    def __init__(self):
        self.predictor = get_predictor()

    def predict_water_quality(self, ph: float, turbidity: float, tds: float, temperature: float):
        return self.predictor.predict(
            ph=ph,
            turbidity=turbidity,
            tds=tds,
            temperature=temperature
        )

ml_service = MLService()
