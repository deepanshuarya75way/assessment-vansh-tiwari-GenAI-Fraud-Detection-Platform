from pydantic import BaseModel


class PreprocessingResponse(BaseModel):
    original_feature_columns: list[str]
    numeric_columns: list[str]
    categorical_columns: list[str]
    feature_names: list[str]
    label_column: str | None
    transformer_path: str
    engineered_frame_path: str
