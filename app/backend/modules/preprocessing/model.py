from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(slots=True)
class PreparedFeatures:
    dataframe: pd.DataFrame
    feature_matrix: np.ndarray
    feature_names: list[str]
    original_feature_columns: list[str]
    numeric_columns: list[str]
    categorical_columns: list[str]
    label_column: str | None
    label_series: pd.Series | None
    transformer_path: str
    engineered_frame_path: str
