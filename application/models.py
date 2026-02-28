from application import database


class Company(database.Model):
    __tablename__ = "companies"

    company_id = database.Column(database.Text, primary_key=True)
    company_name = database.Column(database.Text, nullable=False)

    projects = database.relationship("Project", back_populates="company")

    def __repr__(self):
        return f"<Company {self.company_name}>"


class Project(database.Model):
    __tablename__ = "projects"

    project_id = database.Column(database.Text, primary_key=True)
    project_name = database.Column(database.Text, nullable=False)
    project_start = database.Column(database.Text, nullable=False)
    project_end = database.Column(database.Text, nullable=False)
    company_id = database.Column(database.Text, database.ForeignKey("companies.company_id"), nullable=False)
    description = database.Column(database.Text)
    project_value = database.Column(database.Integer, nullable=False)

    company = database.relationship("Company", back_populates="projects")
    areas = database.relationship("ProjectAreaMap", back_populates="project")

    def to_dict(self, company_name=None):
        return {
            "project_name": self.project_name,
            "project_start": self.project_start,
            "project_end": self.project_end,
            "company": company_name or self.company.company_name,
            "description": self.description or "",
            "project_value": self.project_value,
        }

    def __repr__(self):
        return f"<Project {self.project_name}>"


class ProjectAreaMap(database.Model):
    __tablename__ = "project_area_map"

    project_id = database.Column(database.Text, database.ForeignKey("projects.project_id"), primary_key=True)
    area = database.Column(database.Text, primary_key=True)

    project = database.relationship("Project", back_populates="areas")

    def __repr__(self):
        return f"<ProjectAreaMap {self.project_id} – {self.area}>"