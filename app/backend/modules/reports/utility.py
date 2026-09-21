def recommendations_from_analytics(analytics_payload: dict) -> list[str]:
    recommendations: list[str] = []
    categories = analytics_payload["charts"].get("category_analysis", [])
    top_category = categories[0]["label"] if categories else None
    if top_category:
        recommendations.append(
            f"Review approval controls and historical thresholds for the '{top_category}' category."
        )
    locations = analytics_payload["charts"].get("location_analysis", [])
    if locations:
        recommendations.append(
            f"Investigate location concentration around '{locations[0]['label']}' for unusual transaction clustering."
        )
    recommendations.append("Capture analyst feedback for flagged records to improve future retraining datasets.")
    return recommendations
