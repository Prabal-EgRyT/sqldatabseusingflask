from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+mysqlconnector://sqlproject:9192631770@localhost/crud"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Department(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Department({self.name})"


class Employee(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_of_birth = db.Column(db.Date(), nullable=False)
    department_id = db.Column(db.Integer(), db.ForeignKey(Department.id))
    department = db.relationship(
        "Department", backref=db.backref("employees", lazy="select")
    )

    def __repr__(self):
        return f"Employee({self.name}, {self.email})"


class Attendance(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    employee_id = db.Column(db.Integer(), db.ForeignKey(Employee.id))
    employee = db.relationship(
        "Employee", backref=db.backref("attendance_records", lazy="select")
    )
    date = db.Column(db.Date(), nullable=False)
    status = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Attendance({self.employee}, {self.date}, {self.status})"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/departments")
def show_departments():
    departments = Department.query.all()
    return render_template("department.html", departments=departments)


@app.route("/add_department", methods=["GET", "POST"])
def add_department():
    if request.method == "POST":
        name = request.form["name"]
        new_department = Department(name=name)
        db.session.add(new_department)
        db.session.commit()
        return redirect(url_for("show_departments"))
    return render_template("add_department.html")


@app.route("/edit_department/<int:id>", methods=["GET", "POST"])
def edit_department(id):
    department = Department.query.get_or_404(id)
    if request.method == "POST":
        department.name = request.form["name"]
        db.session.commit()
        return redirect(url_for("show_departments"))
    return render_template("department.html", department=department)


@app.route("/delete_department/<int:id>", methods=["GET", "POST"])
def delete_department(id):
    department = Department.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(department)
        db.session.commit()
        return redirect(url_for("show_departments"))
    return render_template("delete_department.html", department=department)


@app.route("/employees")
def list_employees():
    employees = Employee.query.all()
    return render_template("employee.html", employees=employees)


@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        date_of_birth = request.form["date_of_birth"]
        department_id = request.form["department_id"]
        new_employee = Employee(
            name=name,
            email=email,
            date_of_birth=date_of_birth,
            department_id=department_id,
        )
        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for("list_employees"))
    return render_template("add_employee.html")


@app.route("/edit_employee/<int:id>", methods=["GET", "POST"])
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    if request.method == "POST":
        employee.name = request.form["name"]
        employee.email = request.form["email"]
        employee.date_of_birth = request.form["date_of_birth"]
        employee.department_id = request.form["department_id"]
        db.session.commit()
        return redirect(url_for("list_employees"))
    return render_template("edit_employee.html", employee=employee)


@app.route("/delete_employee/<int:id>", methods=["GET", "POST"])
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(employee)
        db.session.commit()
        return redirect(url_for("list_employees"))
    return render_template("delete_employee.html", employee=employee)


@app.route("/attendance")
def list_attendance():
    attendance = Attendance.query.all()
    return render_template("attendance.html", attendance=attendance)


@app.route("/add_attendance", methods=["GET", "POST"])
def add_attendance():
    if request.method == "POST":
        employee_id = request.form["employee_id"]
        date = request.form["date"]
        status = request.form["status"]
        new_attendance = Attendance(employee_id=employee_id, date=date, status=status)
        db.session.add(new_attendance)
        db.session.commit()
        return redirect(url_for("list_attendance"))
    employees = Employee.query.all()
    return render_template("attendance.html", employees=employees)


@app.route("/edit_attendance/<int:id>", methods=["GET", "POST"])
def edit_attendance(id):
    attendance = Attendance.query.get_or_404(id)
    if request.method == "POST":
        attendance.date = request.form["date"]
        attendance.status = request.form["status"]
        db.session.commit()
        return redirect(url_for("list_attendance"))
    return render_template("attendance.html", attendance=attendance)


@app.route("/delete_attendance/<int:id>", methods=["GET", "POST"])
def delete_attendance(id):
    attendance = Attendance.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(attendance)
        db.session.commit()
        return redirect(url_for("list_attendance"))
    return render_template("attendance.html", attendance=attendance)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=6969)
