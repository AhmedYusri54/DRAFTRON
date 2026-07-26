# graph/nodes/_shared.py
def find_project(projects: list[dict], project_id: str | None) -> dict | None:
    if not project_id:
        return None
    project = next((p for p in projects if p["id"] == project_id), None)
    if project is None:
        raise ValueError(f"lead_project id '{project_id}' not found in candidate_profile projects")
    return project