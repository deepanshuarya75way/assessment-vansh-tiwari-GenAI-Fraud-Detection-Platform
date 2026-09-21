"""Machine learning and deep learning module for dataset-driven fraud detection."""

from app.backend.modules.ml.artifacts import (
    EvaluationArtifact,
    FeatureEngineeringArtifact,
    FeatureSelectionArtifact,
    FraudDetectionArtifact,
    LearningDatasetArtifact,
    ModelArtifact,
    ModelTrainingArtifact,
    PredictionRecord,
)
from app.backend.modules.ml.fraud_engine import FraudDetectionEngine
from app.backend.modules.ml.learning_dataset_manager import LearningDatasetManager
from app.backend.modules.ml.model_factory import ModelFactory
from app.backend.modules.ml.model_manager import ModelManager
from app.backend.modules.ml.training import FraudModelTrainer

__all__ = [
    "EvaluationArtifact",
    "FeatureEngineeringArtifact",
    "FeatureSelectionArtifact",
    "FraudDetectionArtifact",
    "FraudDetectionEngine",
    "FraudModelTrainer",
    "LearningDatasetArtifact",
    "LearningDatasetManager",
    "ModelArtifact",
    "ModelFactory",
    "ModelManager",
    "ModelTrainingArtifact",
    "PredictionRecord",
]