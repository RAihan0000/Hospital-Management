from flask import Flask, render_template, request, redirect, session, url_for, flash, logging
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
db = SQLAlchemy(app)


class userstore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(10), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)

    def __repr__(self):
        return str(self.username)


class Patient(db.Model):
    ssn = db.Column(db.Integer, nullable=False)
    id = db.Column(db.Integer, db.Sequence(
        'pid', start=100000000, increment=1), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    date_admitted = db.Column(db.DateTime, nullable=False)
    bed_type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(10), nullable = False, default='active')

    def __repr__(self):
        return 'Patient '+str(self.id)


beds = ['General Ward', 'Semi Sharing', 'Single']
states = ['AP', 'Telangana']
cities = ['Kadapa', 'Kurnool']


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user_pass = request.form['password']

        if len(userstore.query.filter_by(username=username).all()) != 0:
            password = userstore.query.filter_by(
                username=username).all()[0].password

            if user_pass == password:
                session['logged_in'] = True
                session['username'] = username
                session['display'] = 'no'

                flash('You are now logged in', 'success')
                return redirect(url_for('register'))
            else:
                flash('Wrong password', 'danger')
                return render_template('login.html')

        else:
            flash('Invalid username', 'danger')
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ssn = request.form['id']
        name = request.form['name']
        age = request.form['age']
        y, m, d = request.form['date'].split('-')
        date_admitted = datetime(int(y), int(m), int(d))
        bed_type = request.form['bed']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']

        new_patient = Patient(ssn=ssn, name=name, age=age, date_admitted=date_admitted,
                              bed_type=bed_type, address=address, city=city, state=state)
        db.session.add(new_patient)
        db.session.commit()

        flash('Patient is regisitered successfully with ABC Hosptial', 'success')
        return redirect(url_for('register'))
    else:
        return render_template('patient_registration.html', beds=beds, states=states, cities=cities)



@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    patient = Patient.query.filter_by(ssn=id).all()[0]

    if request.method == 'POST':

        patient.name = request.form['name']
        patient.age = request.form['age']
        y, m, d = request.form['date'].split('-')
        patient.date_admitted = datetime(int(y), int(m), int(d))
        patient.bed_type = request.form['bed']
        patient.address = request.form['address']
        patient.state =request.form['state']
        patient.city =request.form['city']

        db.session.commit()

        flash('Patient has been updated sucessfully','success')
        return redirect(url_for('register'))
        

@app.route('/viewall')
def allpatients():
    all = Patient.query.all()
    return render_template('view-patients.html', all=all)


@app.route('/update-patient', methods = ['GET', 'POST'])
def update_patient():
    if request.method == 'POST':
        id = request.form['id']
        patient = Patient.query.filter_by(ssn=id).all()
        if len(patient) == 1:
            patient = Patient.query.filter_by(ssn=id).all()[0]
            session['display'] ='yes'
            return render_template('update-patient.html', patient = patient, beds = beds, states = states, cities = cities)
        else:
            flash('No Patient with given id is found','danger')
            return render_template('update-patient.html')
    else:
        session['display'] = 'no'
        return render_template('update-patient.html')


@app.route('/delete-patient', methods=['GET', 'POST'])
def delete_patient():
    if request.method == 'POST':
        id = request.form['id']
        patient = Patient.query.filter_by(ssn=id).all()
        if len(patient) !=0:
            patient = Patient.query.filter_by(ssn=id).all()[0]
            session['display'] = 'yes'
            return render_template('delete-patient.html',patient = patient)
        else:
            flash('Patient with given id is not found', 'danger')
            return render_template('delete-patient.html')
    else:
        session['display'] = 'no'
        return render_template('delete-patient.html')

@app.route('/delete/<int:id>', methods = ['GET','POST'])
def delete(id):
    patient = Patient.query.filter_by(ssn=id).all()[0]

    db.session.delete(patient)
    db.session.commit()
        
    flash('Patient deleted successfully', 'success')
    return render_template('patient_registration.html', beds= beds, states = states, cities = cities)




@app.route('/viewone', methods = ['GET','POST'])
def viewone():
    if request.method == 'POST':
        id = request.form['id']
        patient = Patient.query.filter_by(ssn=id).all()
        if len(patient) ==1:
            patient = Patient.query.filter_by(ssn=id).all()[0]
            session['display'] = 'yes'
            return render_template('view-patient.html', patient = patient)
        else:
            flash('Patient with given id not found','danger')
            return render_template('view-patient.html')
    else:
        session['display'] = 'no'
        return render_template('view-patient.html')



if __name__ == '__main__':
    app.secret_key = '123456'
    app.run(debug=True)
