import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


class CropRecommendationEngine:
    def __init__(self):
        self.model = self._train_initial_model()

    def _train_initial_model(self) -> Pipeline:
        """
        Trains a baseline RandomForest model on synthetic agronomic data
        mapping soil moisture, temperature, precipitation, and humidity to crops
        well-suited for Canadian climates (e.g., Canola, Wheat, Barley, Soybeans).
        """
        # Features: [soil_moisture_mm, temperature_celsius, precipitation_mm, humidity_percentage]
        # Classes (Crops): 0 = Wheat, 1 = Canola, 2 = Barley, 3 = Soybean
        np.random.seed(42)
        X_train = np.array(
            [
                # Wheat (prefers moderate temp, moderate-to-low moisture)
                [45.0, 20.0, 2.0, 60.0],
                [50.0, 22.0, 5.0, 65.0],
                [40.0, 18.0, 1.0, 55.0],
                # Canola (prefers cooler temps, good moisture)
                [75.0, 16.0, 10.0, 75.0],
                [80.0, 15.0, 8.0, 80.0],
                [70.0, 17.0, 12.0, 70.0],
                # Barley (drought tolerant, adaptable)
                [35.0, 24.0, 0.5, 45.0],
                [30.0, 26.0, 1.0, 40.0],
                [40.0, 23.0, 2.0, 50.0],
                # Soybean (prefers warmer temps, high moisture)
                [85.0, 28.0, 15.0, 85.0],
                [90.0, 30.0, 20.0, 90.0],
                [80.0, 27.0, 14.0, 82.0],
            ]
        )

        y_train = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3])

        # Build pipeline with scaling and Random Forest
        pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    RandomForestClassifier(n_estimators=50, random_state=42),
                ),
            ]
        )

        pipeline.fit(X_train, y_train)
        return pipeline

    def predict_crop(
        self,
        soil_moisture: float,
        temperature: float,
        precipitation: float,
        humidity: float,
    ) -> dict:
        """
        Takes current field conditions and returns the recommended crop
        along with confidence probabilities.
        """
        crop_mapping = {0: "Spring Wheat", 1: "Canola", 2: "Barley", 3: "Soybeans"}

        features = np.array([[soil_moisture, temperature, precipitation, humidity]])
        prediction_idx = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]

        recommended_crop = crop_mapping.get(prediction_idx, "Unknown")
        confidence = float(probabilities[prediction_idx])

        return {
            "recommended_crop": recommended_crop,
            "confidence_score": round(confidence * 100, 2),
            "all_probabilities": {
                crop_mapping[i]: round(float(prob) * 100, 2)
                for i, prob in enumerate(probabilities)
            },
        }


# Global singleton instance for quick importing
crop_engine = CropRecommendationEngine()
