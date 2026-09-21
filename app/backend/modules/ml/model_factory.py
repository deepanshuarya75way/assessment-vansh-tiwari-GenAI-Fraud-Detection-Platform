from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from sklearn.ensemble import GradientBoostingClassifier, IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier


@dataclass(slots=True)
class ModelSpec:
    name: str
    kind: str
    config: dict[str, Any] = field(default_factory=dict)


class ModelFactory:
    def __init__(self) -> None:
        self._registry: dict[str, Callable[[dict[str, Any]], Any]] = {
            "logistic_regression": self._build_logistic_regression,
            "random_forest": self._build_random_forest,
            "gradient_boosting": self._build_gradient_boosting,
            "mlp": self._build_mlp,
            "deep_neural_network": self._build_mlp,
            "isolation_forest": self._build_isolation_forest,
        }

    def register(self, name: str, builder: Callable[[dict[str, Any]], Any]) -> None:
        self._registry[name] = builder

    def create(self, spec: ModelSpec | str, config: dict[str, Any] | None = None) -> Any:
        if isinstance(spec, str):
            name = spec
            merged_config = config or {}
        else:
            name = spec.name
            merged_config = {**spec.config, **(config or {})}
        if name not in self._registry:
            raise ValueError(f"Unsupported model type: {name}")
        return self._registry[name](merged_config)

    @staticmethod
    def _build_logistic_regression(config: dict[str, Any]) -> LogisticRegression:
        return LogisticRegression(
            max_iter=int(config.get("max_iter", 1000)),
            class_weight=config.get("class_weight", "balanced"),
            solver=config.get("solver", "lbfgs"),
        )

    @staticmethod
    def _build_random_forest(config: dict[str, Any]) -> RandomForestClassifier:
        return RandomForestClassifier(
            n_estimators=int(config.get("n_estimators", 250)),
            max_depth=config.get("max_depth"),
            random_state=int(config.get("random_state", 42)),
            class_weight=config.get("class_weight", "balanced"),
            n_jobs=int(config.get("n_jobs", -1)),
        )

    @staticmethod
    def _build_gradient_boosting(config: dict[str, Any]) -> GradientBoostingClassifier:
        return GradientBoostingClassifier(
            n_estimators=int(config.get("n_estimators", 200)),
            learning_rate=float(config.get("learning_rate", 0.1)),
            max_depth=int(config.get("max_depth", 3)),
            random_state=int(config.get("random_state", 42)),
        )

    @staticmethod
    def _build_mlp(config: dict[str, Any]) -> MLPClassifier:
        hidden_layers = config.get("hidden_layer_sizes", (128, 64))
        if isinstance(hidden_layers, list):
            hidden_layers = tuple(hidden_layers)
        return MLPClassifier(
            hidden_layer_sizes=hidden_layers,
            activation=config.get("activation", "relu"),
            alpha=float(config.get("alpha", 0.0001)),
            batch_size=config.get("batch_size", "auto"),
            learning_rate_init=float(config.get("learning_rate_init", 0.001)),
            max_iter=int(config.get("max_iter", 500)),
            early_stopping=bool(config.get("early_stopping", True)),
            random_state=int(config.get("random_state", 42)),
        )

    @staticmethod
    def _build_isolation_forest(config: dict[str, Any]) -> IsolationForest:
        return IsolationForest(
            n_estimators=int(config.get("n_estimators", 300)),
            contamination=config.get("contamination", "auto"),
            random_state=int(config.get("random_state", 42)),
        )