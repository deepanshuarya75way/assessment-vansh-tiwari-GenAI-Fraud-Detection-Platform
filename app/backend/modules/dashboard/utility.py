def build_filters(payload: dict) -> dict:
    dataset_columns = payload["dataset_statistics"]["columns"]
    semantic = payload["dataset_statistics"]["semantic_columns"]
    return {
        "searchable_columns": dataset_columns[:25],
        "semantic_columns": semantic,
        "available_charts": list(payload["charts"].keys()),
    }
