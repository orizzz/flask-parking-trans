from flask import Flask,request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from datetime import date
import uuid
import random, string

app = Flask(__name__)
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Motorcycle(db.Model):
    id = db.Column(db.String(12))
    license_plate = db.Column(db.String(25), primary_key=True)
    created_at = db.Column(db.Text)
    updated_at = db.Column(db.Text)

class Transaction(db.Model):
    id = db.Column(db.String(12), primary_key=True)
    motorcycle_id = db.Column(db.Integer, db.ForeignKey('motorcycle.id'))
    ticket_code = db.Column(db.String(25))
    status = db.Column(db.String(1))
    created_at = db.Column(db.Text)
    updated_at = db.Column(db.Text)
    deleted_at = db.Column(db.Text)

class TransactionSchema(ma.Schema):
    class Meta:
        fields = ('id', 'motorcycle_id', 'ticket_code', 'status', 'created_at', 'updated_at', 'deleted_at')

class MotorcycleSchema(ma.Schema):
    class Meta:
        fields = ('id', 'license_plate', 'created_at', 'updated_at')


Motorcycle_schema = MotorcycleSchema()
Transaction_schema = TransactionSchema()

Motorcycles_schema = MotorcycleSchema(many=True)
Transactions_schema = TransactionSchema(many=True)

class TransactionsResource(Resource):
    def get(self):
        return Transactions_schema.dump(Transaction.query.all())
    def post(self):
        data = request.json
        motorcylceId = CreateMotorcycle(data['license_plate'])
        postTransaction = Transaction(
            id = ''.join(random.choice(string.ascii_letters) for i in range(12)),
            motorcycle_id = motorcylceId,
            ticket_code = str(uuid.uuid4()).replace('-',''),
            status = 'M',
            created_at = str(date.today())
        )
        db.session.add(postTransaction)
        db.session.commit()
        return Transaction_schema.dump(postTransaction)
    def put(self):
        data = request.json
        check = Transaction.query.filter_by(id=data['id']).first()
        check.status = data['status']
        check.updated_at = str(date.today())
        db.session.commit()
        return Transaction_schema.dump(check)
    def delete(self):
        data = request.json
        check = Transaction.query.filter_by(id=data['id']).first()
        check.deleted_at = str(date.today())
        db.session.commit()
        return Transaction_schema.dump(check)

class MotorcyclesResource(Resource):
    def get(self):
        return Motorcycles_schema.dump(Motorcycle.query.all())

def CreateMotorcycle(license):
    check = Motorcycle.query.filter_by(license_plate=license).first()
    if check is None:
        postMotorcycle  = Motorcycle(
            id = ''.join(random.choice(string.ascii_letters) for i in range(12)),
            license_plate = license,
            created_at = date.today() 
            )
        db.session.add(postMotorcycle)
        db.session.commit()
        return postMotorcycle.id
    else :
        check.updated_at = date.today()
        db.session.commit()
        return check.id

api.add_resource(TransactionsResource,'/Transactions')
api.add_resource(MotorcyclesResource,'/Motorcycles')
    
if __name__ == "__main__":
    app.run(debug=True)