from api import db
class Farmer(db.Model):
    transaction_ID = db.Column(db.String(), primary_key=True)
    farmer_ID = db.Column(db.String())
    details = db.Column(db.String())

    def __repr__(self):
        return '<Farmer {}>'.format(self.transaction_ID) 

class Refiner(db.Model):
    transaction_ID = db.Column(db.String(), primary_key=True)
    refiner_ID = db.Column(db.String())
    details = db.Column(db.String())

    def __repr__(self):
        return '<Refiner {}>'.format(self.transaction_ID) 

class Wholesaler(db.Model):
    transaction_ID = db.Column(db.String(), primary_key=True)
    Wholesaler_ID = db.Column(db.String())
    details = db.Column(db.String())
    product_Number = db.Column(db.String())

    def __repr__(self):
        return '<Wholesaler {}>'.format(self.transaction_ID) 

class Product(db.Model):
    product_id = db.Column(db.String(), primary_key = True)
    chain_index = db.Column(db.String())

    def __repr__(self):
        return '<Product {}>'.format(self.product_id) 
