from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+mysqlconnector://sqlproject:enterpasswordhere@localhost/crud"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Department(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Department({self.id},{self.name})"


class Employee(db.Model):
    id = db.Column(
        db.String(50), primary_key=True
    )  # Modified to allow manual insertion
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_of_birth = db.Column(db.Date(), nullable=False)
    department_id = db.Column(db.String(20), db.ForeignKey(Department.id))
    department = db.relationship(
        "Department", backref=db.backref("employees", lazy="select")
    )

    def __repr__(self):
        return f"Employee({self.name}, {self.email})"


class Attendance(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    employee_id = db.Column(db.String(20), db.ForeignKey(Employee.id))
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
        identity = request.form["id"]
        name = request.form["name"]
        new_department = Department(name=name, id=identity)
        db.session.add(new_department)
        db.session.commit()
        return redirect(url_for("show_departments"))
    return render_template("department.html")


@app.route("/edit_department/<string:id>", methods=["GET", "POST"])
def edit_department(id):
    department = Department.query.get_or_404(id)
    if request.method == "POST":
        department.name = request.form["name"]
        db.session.commit()
        return redirect(url_for("show_departments"))
    return render_template("department.html", department=department)


@app.route("/delete_department/<string:id>", methods=["GET", "POST"])
def delete_department(id):
    department = Department.query.get_or_404(id)
    if request.method == "POST":
        # Delete all employees in this department
        employees_to_delete = Employee.query.filter_by(department_id=id).all()
        for employee in employees_to_delete:
            # Delete attendance records for each employee
            attendance_records_to_delete = Attendance.query.filter_by(
                employee_id=employee.id
            ).all()
            for attendance_record in attendance_records_to_delete:
                db.session.delete(attendance_record)
            db.session.delete(employee)
        db.session.delete(department)
        db.session.commit()
        return redirect(url_for("show_departments"))
    return render_template("delete_department.html", department=department)


@app.route("/employees")
def list_employees():
    search_query = request.args.get("q", "")
    if search_query:
        employees = Employee.query.filter(Employee.name.contains(search_query)).all()
    else:
        employees = Employee.query.all()
    return render_template("employee.html", employees=employees)


@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        employee_id = request.form[
            "employee_id"
        ]  # Get the employee_id from the form input
        name = request.form["name"]
        email = request.form["email"]
        date_of_birth = request.form["date_of_birth"]
        department_id = request.form["department_id"]
        new_employee = Employee(
            id=employee_id,  # Use the provided employee_id
            name=name,
            email=email,
            date_of_birth=date_of_birth,
            department_id=department_id,
        )
        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for("list_employees"))

    # Fetch all departments and pass them to the template
    departments = Department.query.all()
    return render_template(
        "employee.html", employees=Employee.query.all(), departments=departments
    )


@app.route("/edit_employee/<string:id>", methods=["GET", "POST"])
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    if request.method == "POST":
        employee.name = request.form["name"]
        employee.email = request.form["email"]
        employee.date_of_birth = request.form["date_of_birth"]
        employee.department_id = request.form["department_id"]
        db.session.commit()
        return redirect(url_for("list_employees"))
    departments = Department.query.all()
    return render_template("employee.html", employee=employee, departments=departments)


@app.route("/delete_employee/<string:id>", methods=["GET", "POST"])
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    if request.method == "POST":
        attendance_records_to_delete = Attendance.query.filter_by(employee_id=id).all()
        for attendance_record in attendance_records_to_delete:
            db.session.delete(attendance_record)
        db.session.delete(employee)
        db.session.commit()
        return redirect(url_for("list_employees"))
    return render_template("delete_employee.html", employee=employee)


@app.route("/attendance")
def list_attendance():
    search_query = request.args.get("q", "")
    if search_query:
        attendance = Attendance.query.filter(
            Attendance.employee_id.contains(search_query)
        ).all()
    else:
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
