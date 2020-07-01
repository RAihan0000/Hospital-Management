from flask import Flask, render_template, request, redirect, session, url_for, flash, logging
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps

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
    status = db.Column(db.String(10), nullable=False, default='active')

    def __repr__(self):
        return 'Patient '+str(self.id)

class Meds(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column(db.String(20), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    price = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return self.name

class Issuemeds(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    ssn  = db.Column(db.Integer, nullable = False)
    med = db.Column(db.String(20), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    price = db.Column(db.Integer, nullable = False)
    amount = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return str(self.ssn)

class Diagnostics(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    test = db.Column(db.String(20), nullable = False)
    price = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return self.test

class PatientDiag(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    ssn = db.Column(db.Integer, nullable = False)
    test_id = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return str(self.ssn)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

beds = ['General Ward', 'Semi Sharing', 'Single']
states = ['AP', 'Telangana']
cities = ['Kadapa', 'Kurnool']
diags = list()
ds = Diagnostics.query.all()
for each in ds:
    diags.append(each.test)

class Medlist():
    def __init__(self,ssn,med,qty,price,amount):
        self.ssn = ssn
        self.med = med
        self.qty = qty
        self.price = price
        self.amount = amount
medlist = list()

class Diaglist():
    def __init__(self,ssn,test_id,test,price):
        self.ssn = ssn
        self.test_id = test_id
        self.test = test
        self.price = price
diaglist = list()
dcon = list()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
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
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
@is_logged_in
def register():

    if request.method == 'POST':
        allid = Patient.query.all()
        ids = []
        for each in allid:
            ids.append(each.ssn)
        ssn = request.form['id']
        name = request.form['name']
        age = request.form['age']
        y, m, d = request.form['date'].split('-')
        date_admitted = datetime(int(y), int(m), int(d))
        bed_type = request.form['bed']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        if len(ssn) == 9 and int(ssn) not in ids and len(name) != 0 and len(age) != 0 and len(y) == 4 and len(m) == 2 and len(d) == 2 and len(address) != 0 and bed_type != 'select' and state != 'select' and city != 'select':

            new_patient = Patient(ssn=ssn, name=name, age=age, date_admitted=date_admitted,
                                  bed_type=bed_type, address=address, city=city, state=state)
            db.session.add(new_patient)
            db.session.commit()

            flash('Patient is regisitered successfully with ABC Hosptial', 'success')
            return redirect(url_for('register'))
        else:
            flash('The details entered does not match the required conditions. Please re-enter them accordingly', 'danger')
            return redirect(url_for('register'))
    else:
        return render_template('patient_registration.html', beds=beds, states=states, cities=cities)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@is_logged_in
def update(id):
    patient = Patient.query.filter_by(ssn=id).all()[0]

    if request.method == 'POST':

        patient.name = request.form['name']
        patient.age = request.form['age']
        y, m, d = request.form['date'].split('-')
        patient.date_admitted = datetime(int(y), int(m), int(d))
        patient.bed_type = request.form['bed']
        patient.address = request.form['address']
        patient.state = request.form['state']
        patient.city = request.form['city']

        db.session.commit()

        flash('Patient has been updated sucessfully', 'success')
        return redirect(url_for('register'))


@app.route('/viewall')
@is_logged_in
def allpatients():
    all = Patient.query.all()
    return render_template('view-patients.html', all=all)


@app.route('/update-patient', methods=['GET', 'POST'])
@is_logged_in
def update_patient():
    if request.method == 'POST':
        id = request.form['id']
        patient = Patient.query.filter_by(ssn=id).all()
        if len(patient) == 1:
            patient = Patient.query.filter_by(ssn=id).all()[0]
            session['display'] = 'yes'
            return render_template('update-patient.html', patient=patient, beds=beds, states=states, cities=cities)
        else:
            flash('No Patient with given id is found', 'danger')
            return render_template('update-patient.html')
    else:
        session['display'] = 'no'
        return render_template('update-patient.html')


@app.route('/delete-patient', methods=['GET', 'POST'])
@is_logged_in
def delete_patient():
    if request.method == 'POST':
        id = request.form['id']
        patient = Patient.query.filter_by(ssn=id).all()
        if len(patient) != 0:
            patient = Patient.query.filter_by(ssn=id).all()[0]
            session['display'] = 'yes'
            return render_template('delete-patient.html', patient=patient)
        else:
            flash('Patient with given id is not found', 'danger')
            return render_template('delete-patient.html')
    else:
        session['display'] = 'no'
        return render_template('delete-patient.html')


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@is_logged_in
def delete(id):
    patient = Patient.query.filter_by(ssn=id).all()[0]

    db.session.delete(patient)
    db.session.commit()

    flash('Patient deleted successfully', 'success')
    return redirect(url_for('register'))


@app.route('/viewone', methods=['GET', 'POST'])
@is_logged_in
def viewone():
    if request.method == 'POST':
        id = request.form['id']
        patient = Patient.query.filter_by(ssn=id).all()
        if len(patient) == 1:
            patient = Patient.query.filter_by(ssn=id).all()[0]
            session['display'] = 'yes'
            return render_template('view-patient.html', patient=patient)
        else:
            flash('Patient with given id not found', 'danger')
            return render_template('view-patient.html')
    else:
        session['display'] = 'no'
        return render_template('view-patient.html')

'''********************************Pharmacy**************************************************'''


@app.route('/patmeds', methods=['POST', 'GET'])
@is_logged_in
def patmeds():
    if request.method == 'POST':
        id = request.form['id']
        patient = Patient.query.filter_by(ssn=id).all()
        if len(patient) == 1:
            patient = Patient.query.filter_by(ssn=id).all()[0]
            meds = Issuemeds.query.filter_by(ssn=id).all()
            dmeds = len(meds)
            session['display'] = 'yes'
            return render_template('med-details.html', patient=patient, meds = meds, dmeds = dmeds)
        else:
            flash('Patient with given id does not exist','danger')
            return redirect('patmeds')
    else:
        session['display'] = 'no'
        medlist.clear()
        return render_template('med-details.html')

@app.route('/addmeds/<int:id>', methods = ['POST','GET'])
@is_logged_in
def addmeds(id):
    if request.method == 'POST':
        med = request.form['meds']
        qty = request.form['qty']
        check = Meds.query.filter_by(name=med).all()
        if len(check) ==1:
            if check[0].quantity >= int(qty):
                price = check[0].price
                amount = check[0].price * int(qty)
                medlist.append(Medlist(id,med,qty,price,amount))
                lmed = len(medlist)
                return render_template('issue-medicines.html',id = id, medlist = medlist, lmed = lmed)
                
            else:
                lmed = len(medlist)
                flash('Requested quantity is not available','danger')
                return render_template('issue-medicines.html',id = id, medlist = medlist, lmed =lmed)
            
        else:
            lmed = len(medlist)
            flash('Medicine is not available','danger')
            return render_template('issue-medicines.html',id = id, medlist = medlist, lmed = lmed)

    else:
        session['display'] ='no'
        return render_template('issue-medicines.html',id = id)

@app.route('/updatemeds/<int:id>')
@is_logged_in
def upadtemeds(id):
    if len(medlist) != 0:
        for each in medlist:
            db.session.add(Issuemeds(ssn = each.ssn, med =each.med, quantity = each.qty, price  = each.price, amount = each.amount))
            db.session.commit()
        medlist.clear()
        flash('Medicines have been issued to the Patient', 'success')
        return redirect(url_for('register'))
    else:
        lmed = len(medlist)
        flash('Can not update without issuing any medicines','danger')
        return render_template('issue-medicines.html',id = id, medlist = medlist, lmed = lmed)

'''***********************************Diagnostics****************************************'''


@app.route('/patdiags', methods = ['GET', 'POST'])
@is_logged_in
def patdiags():
    if request.method == 'POST':
        id = request.form['id']
        patient = Patient.query.filter_by(ssn=id).all()
        if len(patient) == 1:
            patient = Patient.query.filter_by(ssn=id).all()[0]
            did = PatientDiag.query.filter_by(ssn=id).all()
            if len(did) != 0:
                for each in did:
                    dcon.append(Diagnostics.query.get(each.test_id))
            ld = len(dcon) 

            session['display'] = 'yes'
            return render_template('diag-details.html', patient=patient, dcon = dcon, ld = ld)
        else:
            dcon.clear()
            flash('Patient with given id does not exist','danger')
            return redirect('patdiags')
    else:
        session['display'] = 'no'
        diaglist.clear()
        dcon.clear()
        return render_template('diag-details.html')


@app.route('/adddiags/<int:id>', methods = ['POST','GET'])
@is_logged_in
def adddiags(id):
    if request.method == 'POST':
        test = request.form['test']
        if test in diags:
            diag = Diagnostics.query.filter_by(test=test).all()[0]
            diaglist.append(Diaglist(ssn = id, test_id = diag.id, test = diag.test, price = diag.price))
            dlen = len(diaglist)
            return render_template('add-diagnostics.html', id=id, diags = diags, diaglist = diaglist, dlen = dlen)
        else:
            flash('Select any test before adding', 'danger')
            dlen = len(diaglist)
            return render_template('add-diagnostics.html', id=id, diags = diags, diaglist = diaglist, dlen = dlen)

    else:
        session['display'] ='no'
        dlen = len(diaglist)
        return render_template('add-diagnostics.html',id = id, diags = diags, dlen = dlen)


@app.route('/updatediags/<int:id>')
@is_logged_in
def updatediags(id):
    if len(diaglist) != 0:
        for each in diaglist:
            db.session.add(PatientDiag(ssn=id,test_id=each.test_id))
            db.session.commit()
        diaglist.clear()
        flash('Diagnostics to be performed are added to the patient','success')
        return redirect(url_for('register'))
    else:
        flash('You cannot update without adding any tests', 'danger')
        dlen = len(diaglist)
        return render_template('add-diagnostics.html', id=id, diags = diags, diaglist = diaglist, dlen = dlen)

'''*************************************Final Billing***********************************'''


@app.route('/billing', methods=['GET','POST'])
@is_logged_in
def billing():
    if request.method == 'POST':
        id = request.form['id']
        days = int(request.form['days'])
        dcon.clear()
        patient = Patient.query.filter_by(ssn=id).all()
        if len(patient) == 1 :
            patient = Patient.query.filter_by(ssn=id).all()[0]
            if patient.bed_type == 'General Ward':
                room = days * 2000
            elif patient.bed_type == 'Semi Sharing':
                room = days * 4000
            else:
                room = days * 8000

            meds = Issuemeds.query.filter_by(ssn=id).all()
            dmeds = len(meds)
            pharmacy = 0
            if dmeds != 0:
                for each in meds:
                    pharmacy += each.amount

            did = PatientDiag.query.filter_by(ssn=id).all()
            if len(did) != 0:
                for each in did:
                    dcon.append(Diagnostics.query.get(each.test_id))
            ld = len(dcon)
            diagbill = 0
            if ld != 0:
                for each in dcon:
                    diagbill += each.price

            total = room + pharmacy + diagbill
            session['display'] = 'yes'
            return render_template('final-billing.html', patient = patient, days = days, room = room,
                     meds = meds, dmeds = dmeds, pharmacy = pharmacy, dcon = dcon, ld = ld, 
                     diagbill = diagbill, total = total)
        else:
            flash('Patient with given id not found','danger')
            return redirect(url_for('billing'))
    else:
        dcon.clear()
        session['display'] = 'no'
        return render_template('final-billing.html')


if __name__ == '__main__':
    app.secret_key = '123456'
    app.run(debug=True)
