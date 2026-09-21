from sqlalchemy.orm import Session

from app.backend.modules.cleaning.repository import CleaningRepository


class PreprocessingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.cleaning_repository = CleaningRepository(session)

    def latest_cleaned(self, project_id: str):
        dataset = self.cleaning_repository.latest_dataset(project_id)
        if not dataset:
            return None, None
        return dataset, self.cleaning_repository.cleaned_repository.latest_for_dataset(dataset.id)
