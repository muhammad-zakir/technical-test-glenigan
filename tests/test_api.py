import pytest


def test_valid_request_default_pagination(client):
    response = client.get("/projects?area=Manchester")
    assert response.status_code == 200

    data = response.get_json()
    assert data["area"] == "Manchester"
    assert data["page"] == 1
    assert data["per_page"] == 10
    assert isinstance(data["total"], int)
    assert isinstance(data["total_pages"], int)
    assert len(data["projects"]) <= 10

    project = data["projects"][0]
    for key in ("project_name", "project_start", "project_end", "company", "description", "project_value"):
        assert key in project


def test_custom_pagination(client):
    response = client.get("/projects?area=Manchester&page=2&per_page=5")
    assert response.status_code == 200

    data = response.get_json()
    assert data["page"] == 2
    assert data["per_page"] == 5
    assert len(data["projects"]) <= 5


def test_sorting_order(client):
    response = client.get("/projects?area=Manchester&per_page=100")
    assert response.status_code == 200

    projects = response.get_json()["projects"]
    for iteration in range(len(projects) - 1):
        current_project, next_project = projects[iteration], projects[iteration + 1]
        assert (
            current_project["project_value"] > next_project["project_value"]
            or (
                current_project["project_value"] == next_project["project_value"]
                and current_project["project_name"] <= next_project["project_name"]
            )
        ), f"Sort violation at index {iteration}: {current_project} vs {next_project}"


def test_per_page_capped_at_max(client):
    response = client.get("/projects?area=Manchester&per_page=999")
    assert response.status_code == 200

    data = response.get_json()
    assert data["per_page"] == 100


def test_total_pages_in_response(client):
    response = client.get("/projects?area=Manchester&per_page=5")
    assert response.status_code == 200

    data = response.get_json()
    assert data["total_pages"] == -(-data["total"] // 5)  # ceil division


def test_page_out_of_range(client):
    response = client.get("/projects?area=Manchester&page=9999")
    assert response.status_code == 400
    assert "out of range" in response.get_json()["error"].lower()


def test_missing_area(client):
    response = client.get("/projects")
    assert response.status_code == 400
    assert "area" in response.get_json()["error"].lower()


def test_area_not_found(client):
    response = client.get("/projects?area=Narnia")
    assert response.status_code == 404
    assert "Narnia" in response.get_json()["error"]


@pytest.mark.parametrize(
    "query_parameters",
    [
        "area=Manchester&page=0",
        "area=Manchester&page=-1",
        "area=Manchester&page=abc",
        "area=Manchester&per_page=0",
        "area=Manchester&per_page=-5",
        "area=Manchester&per_page=xyz",
    ],
)
def test_invalid_pagination(client, query_parameters):
    response = client.get(f"/projects?{query_parameters}")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_config_overrides():
    from application import create_app

    application = create_app({"TESTING": True, "CUSTOM_KEY": "custom_value"})
    assert application.config["CUSTOM_KEY"] == "custom_value"


def test_model_repr(client):
    from application.models import Company, Project, ProjectAreaMap

    company = Company(company_id="c1", company_name="Test Co")
    assert "Test Co" in repr(company)

    project = Project(
        project_id="p1",
        project_name="Test Project",
        project_start="2025-01-01 00:00:00",
        project_end="2026-01-01 00:00:00",
        company_id="c1",
        project_value=100,
    )
    assert "Test Project" in repr(project)

    mapping = ProjectAreaMap(project_id="p1", area="London")
    assert "p1" in repr(mapping)
    assert "London" in repr(mapping)


def test_database_error(client, monkeypatch):
    from application import database

    def raise_error(*args, **kwargs):
        from sqlalchemy.exc import OperationalError
        raise OperationalError("test", {}, Exception("db error"))

    monkeypatch.setattr(database.session, "query", raise_error)

    response = client.get("/projects?area=Manchester")
    assert response.status_code == 500
    assert "database error" in response.get_json()["error"].lower()
