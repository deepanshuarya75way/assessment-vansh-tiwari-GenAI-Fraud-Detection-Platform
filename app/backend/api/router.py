from tarfile import RECORDSIZE

from app.backend.utils import dataframe
from fastapi import APIRouter
from httpx2 import HTTPError
from pandas.core.ops import invalid
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from app.backend.core.config import get_settings
from app.backend.modules.analytics.controller import router as analytics_router
from app.backend.modules.auth.controller import router as auth_router
from app.backend.modules.chatbot.controller import router as chatbot_router
from app.backend.modules.cleaning.controller import router as cleaning_router
from app.backend.modules.dashboard.controller import router as dashboard_router
from app.backend.modules.detection.controller import router as detection_router
from app.backend.modules.explainability.controller import router as explainability_router
from app.backend.modules.feedback.controller import router as feedback_router
from app.backend.modules.logs.controller import router as logs_router
from app.backend.modules.preprocessing.controller import router as preprocessing_router
from app.backend.modules.projects.controller import router as projects_router
from app.backend.modules.reports.controller import router as reports_router
from app.backend.modules.settings.controller import router as settings_router
from app.backend.modules.uploads.controller import router as uploads_router
from app.backend.modules.validation.controller import router as validation_router

settings = get_settings()
api_router = APIRouter(prefix=settings.api_prefix)

api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(uploads_router)
api_router.include_router(validation_router)
api_router.include_router(cleaning_router)
api_router.include_router(preprocessing_router)
api_router.include_router(detection_router)
api_router.include_router(explainability_router)
api_router.include_router(analytics_router)
api_router.include_router(dashboard_router)
api_router.include_router(reports_router)
api_router.include_router(logs_router)
api_router.include_router(settings_router)
api_router.include_router(chatbot_router)
api_router.include_router(feedback_router)
from datetime import datetime
import uuid
from fastapi import APIRouter, HTTPException, status 
from fastapi.responses import JSONResponse
import pandas as pd
from app.backend.common.schemas import FeedbackCreate

feedback_router = APIRouter(prefix="/feesdback", tags=["feedback"])
FEEDBACK_STORE = {}     
SEEN_SUBMISSIONS = set()

def validate_feedback(payload: Feedbackcreate)->bool:
  if payload.actual_label not in (0,1):
    return false
    if not payload.features or not isinstance(payload.features,dict):
      ruturn false
return True
@feedback_router.post("",status_code=status,HTTP_201_CREATED)
def submit_feedback(payload:FeedbackCreate)
dedup_key = (payload.prediction_id,payload.analyst_id)
if dedup_key in SEEN_SUBMISSION:
  raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail=""
Duplicate feedback submission detected,
  )
  is_valid = validate_feedback(payload)
  if not is_valid:
    raise HTTPException(
       status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
       detail="invalid feedback payload."

    )
SEEN_SUBMISSIONS.add(dedup_key)
feedback_id = str(uuid.uuid4())

record = {
  "feedback_id" : feedback_id,
  "prediction_id" : payload.prediction_id,
  "pridiction_label": payload.pridiction_label,
  "actual_label" : payload.actual_label
}
FEEDBACK_STORE[feedback_id] = record 
return record
@feedback_router.get("/training-dataset")
def get_training_dataset():
  eligible = [item for item in FEEDBACK_STORE.values()if item.get("is_valid",false)]
  rows = [
    {
      feedback_id" : item["pridiction_id"],
   "target": item [actual_label],
   **item["features"]

    }
   for item in eligible 
  ]
  def = pd.dataframe(rows)
  return{
    "total_records": len(df),
    "dataset": df.to_dict(*orient="records")
  }
  @feedback_router.get("/training-dataset/export")
  def export_training_dataset(export_formate: str= "json"):
    eligible = [item for item in FEEDBACK_STORE.values()if item.get("is_valid",False)]
    rows =[
      {
        "prediction_id": item["prediction_id"],
        "target": item["actual_label"],
        **item["features"]
      }
      for item in eligible
    ]
    df = pd.Dataframe(rows)
    if export_formate.lower() == "csv":
      return JSONResponse(content={"csv_data": df.to_csv(index=false)})
      return {"records": df.to_dict(orient="records")}
 


  

 