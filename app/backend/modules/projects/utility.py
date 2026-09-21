from app.backend.db.enterprise_models import Project


def project_slug(project: Project) -> str:
    return project.name.lower().replace(" ", "-")
