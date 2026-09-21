from __future__ import annotations

import time
from pathlib import Path

from app.backend.agents.base import AgentContext, AgentLog, AgentResult, BaseAgent
from app.backend.core.exceptions import ProcessingError


class UploadAgent(BaseAgent):
    name = "upload_agent"
    allowed_extensions = {".csv", ".xlsx", ".xls"}

    async def execute(self, context: AgentContext) -> AgentResult:
        started_at = time.time()
        logs = [AgentLog(level="INFO", message="Validating uploaded artifact metadata.")]
        input_data = context.input_data
        file_name = str(input_data.get("file_name") or "")
        file_size = int(input_data.get("file_size_bytes") or 0)
        stored_path = str(input_data.get("stored_path") or "")

        if not file_name:
            raise ProcessingError("Upload agent requires a file name.")

        extension = Path(file_name).suffix.lower()
        if extension not in self.allowed_extensions:
            raise ProcessingError(f"Unsupported file extension: {extension}")

        max_size_mb = int(context.configuration.get("max_upload_size_mb", 200))
        if file_size > max_size_mb * 1024 * 1024:
            raise ProcessingError("Uploaded file exceeds the configured size limit.")

        payload = {
            "dataset_id": context.dataset_id,
            "file_name": file_name,
            "file_extension": extension.lstrip("."),
            "file_size_bytes": file_size,
            "stored_path": stored_path,
            "upload_mode": input_data.get("upload_mode", "single"),
            "metadata": {
                "original_filename": file_name,
                "checksum": input_data.get("checksum"),
                "row_count": input_data.get("row_count"),
                "column_count": input_data.get("column_count"),
            },
        }
        return self._build_result(
            status="success",
            summary="Upload metadata validated and registered.",
            metadata={"dataset_id": context.dataset_id, "stored_path": stored_path},
            payload=payload,
            logs=logs,
            started_at=started_at,
            result_location=stored_path or None,
        )