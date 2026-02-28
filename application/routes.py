from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from application import database
from application.models import Company, Project, ProjectAreaMap

api = Blueprint("api", __name__)


def _validate_pagination_param(value, name, default):
    if value is None:
        return default, None

    try:
        integer_value = int(value)
    except (ValueError, TypeError):
        return None, (
            jsonify({"error": f"'{name}' must be a positive integer"}),
            400,
        )

    if integer_value < 1:
        return None, (
            jsonify({"error": f"'{name}' must be a positive integer (>= 1)"}),
            400,
        )

    return integer_value, None


@api.route("/projects", methods=["GET"])
def get_projects():
    area = request.args.get("area")
    if not area:
        return jsonify({"error": "Missing required parameter: 'area'"}), 400

    page, error = _validate_pagination_param(request.args.get("page"), "page", 1)
    if error:
        return error

    per_page, error = _validate_pagination_param(
        request.args.get("per_page"), "per_page", 10
    )
    if error:
        return error

    try:
        query = (
            database.session.query(Project, Company.company_name)
            .join(ProjectAreaMap, Project.project_id == ProjectAreaMap.project_id)
            .join(Company, Project.company_id == Company.company_id)
            .filter(ProjectAreaMap.area == area)
            .order_by(Project.project_value.desc(), Project.project_name.asc())
        )

        total = query.count()

        if total == 0:
            return (
                jsonify({"error": f"No projects found for area: '{area}'"}),
                404,
            )

        offset = (page - 1) * per_page
        results = query.offset(offset).limit(per_page).all()

        projects = [project.to_dict(company_name) for project, company_name in results]

    except SQLAlchemyError as exception:
        return (
            jsonify({"error": "A database error occurred", "details": str(exception)}),
            500,
        )

    return jsonify(
        {
            "area": area,
            "page": page,
            "per_page": per_page,
            "total": total,
            "projects": projects,
        }
    )
