from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crud.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Department(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return "department({})".format(self.name)

@app.route('/departments')
def show_departments():
    with app.app_context():  # Create an application context
        departments = Department.query.all()
    return render_template('department.html', departments=departments)

@app.route('/add_department', methods=['POST'])
def add_department():
    if request.method == 'POST':
        name = request.form['name']
        new_department = Department(name=name)
        with app.app_context():  # Create an application context
            db.session.add(new_department)
            db.session.commit()
        return redirect(url_for('show_departments'))
    return render_template('add_department.html')

@app.route('/edit_department/<int:id>', methods=['GET', 'POST'])
def edit_department(id):
    department = Department.query.get_or_404(id)
    if request.method == 'POST':
        department.name = request.form['name']
        with app.app_context():  # Create an application context
            db.session.commit()
        return redirect(url_for('show_departments'))
    return render_template('edit_department.html', department=department)

@app.route('/delete_department/<int:id>', methods=['POST'])
def delete_department(id):
    department = Department.query.get_or_404(id)
    with app.app_context():  # Create an application context
        db.session.delete(department)
        db.session.commit()
    return redirect(url_for('show_departments'))

class Employee(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100),nullable=False,unique=True)
    date_of_birth=db.Column(db.Date(),nullable=False)
    department_id=db.Column(db.Integer(),db.ForeignKey(Department.id))
    department = db.relationship('Department', backref=db.backref('employees', lazy="select"))

@app.route('/employees')
def list_employees():
    employees = Employee.query.all()
    for employee in employees:
        print(f"Employee: {employee}")
    return "Employees haleko ." 
@app.route('/add_employee_form', methods=['POST'])
def add_employee():
   if request.method== 'POST':
       name=request.form['name']
       email=request.form['email']
       date_of_birth=request.form['date_of_birth']
       department_id=request.form['department_id']
       new_employee = Employee(name=name, email=email, date_of_birth=date_of_birth, department_id=department_id)
       db.session.add(new_employee)
        
       return redirect(url_for('list_employees'))
   return render_template('add_employee.html')





if __name__ == "__main__":
    with app.app_context():  # Create an application context for creating tables
        db.create_all()
    app.run(debug=True, port=6969)
