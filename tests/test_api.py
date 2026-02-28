import pytest

from application import create_app


@pytest.fixture()
def client():
    application = create_app()
    application.config["TESTING"] = True
    with application.test_client() as client:
        yield client


def test_valid_request_default_pagination(client):
    response = client.get("/projects?area=Manchester")
    assert response.status_code == 200

    data = response.get_json()
    assert data["area"] == "Manchester"
    assert data["page"] == 1
    assert data["per_page"] == 10
    assert isinstance(data["total"], int)
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
