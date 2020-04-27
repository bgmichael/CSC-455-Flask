from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    #posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"



class Employees(db.Model):
    Employee_ID = db.Column(db.Integer, primary_key=True)  # db.ForeignKey('works_at_relationship.Employee_ID')
    name = db.Column(db.String(25), nullable=False)
    title = db.Column(db.String(25), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    join_date = db.Column(db.String(25), nullable=False)

    # lists = db.relationship("Store", backref="employees", cascade="all, delete")

    def __repr__(self):
        return f"Employees('{self.Employee_ID}', '{self.name}', '{self.title}','{self.salary}','{self.join_date}')"

###### After this come my personal additions. I will try to create the tables for our databases.##########################

class Product(db.Model):
    Product_ID = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float(), nullable=False)
    product_name = db.Column(db.String(40), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Product('{self.Product_ID}', '{self.price}', '{self.product_name}','{self.quantity}')"

class Product_Information(db.Model):
    Individual_ID = db.Column(db.Integer, primary_key=True)
    expiration_date = db.Column(db.String(25), nullable=False)
    product_weight = db.Column(db.Float(), nullable=False)

    def __repr__(self):
        return f"Product_Information('{self.Individual_ID}', '{self.expiration_date}','{self.product_weight}')"

class Part_Of_Relationship(db.Model):
    Individual_ID = db.Column(db.Integer, db.ForeignKey('product__information.Individual_ID'), primary_key=True)
    Product_ID = db.Column(db.Integer, db.ForeignKey('product.Product_ID'), primary_key=True)
    #db.ForeignKey('product_information.Individual_ID'), db.ForeignKey('product.Product_ID')

    name = db.relationship("Product", backref="part_of_relationship")

    def __repr__(self):
        return f"Part_Of_Relationship('{self.Individual_ID}', '{self.Product_ID}')"



class Sold_By_Relationship(db.Model):
    Store_ID = db.Column(db.Integer, db.ForeignKey('store.Store_ID'), primary_key=True, )
    Product_ID = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"Sold_By_Relationship('{self.Individual_ID}', '{self.Product_ID}')"


class Store(db.Model):
    Store_ID = db.Column(db.Integer, db.ForeignKey('sold__by__relationship.Store_ID'), primary_key=True, )
    location = db.Column(db.String(25), nullable=False)

    def __repr__(self):
        return f"Store('{self.Store_ID}', '{self.location}')"

class Works_At_Relationship(db.Model):
    Store_ID = db.Column(db.Integer, db.ForeignKey('store.Store_ID'), primary_key=True, )
    Employee_ID = db.Column(db.Integer, db.ForeignKey('employees.Employee_ID'), primary_key=True, )

    name = db.relationship("Employees", backref="works_at_relationship", cascade="all, delete")

    def __repr__(self):
        return f"Works_At_Relationship('{self.Store_ID}', '{self.Employee_ID}')"


#
# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     content = db.Column(db.Text, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#
#     def __repr__(self):
#         return f"Post('{self.title}', '{self.date_posted}')"
#

#
# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
#     password = db.Column(db.String(60), nullable=False)
#     posts = db.relationship('Post', backref='author', lazy=True)
#
#     def __repr__(self):
#         return f"User('{self.username}', '{self.email}', '{self.image_file}')"


