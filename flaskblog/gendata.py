import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post, Employees, Product, Product_Information, Part_Of_Relationship
    #Product, Product_Information, \
    #Part_Of_Relationship, Sold_By_Relationship, Store, Works_At_Relationship
from flask_login import login_user, current_user, logout_user, login_required
from random import randint
# from main.gendata import gendata

employeeData = [[123456,"Bob Dole","Manager",50000, '2019-06-11'], [123452,"Betsy Smith","Cashier",15000, '2019-02-09'],
                [123449,"Tyler Oliver","Cashier",15000, '2019-03-19'], [123438,"Donnie Macks","Clerk",26000, '2019-05-14'],
                [123443,"John Landers","Stocker",17000, '2016-07-14'], [123442,"Gilbert Stauffin","Stocker",19000, '2014-03-08'],
                [123455,"Wendy Reynolds","Manager",55000, '2011-03-14'], [123454,"Cliff Jones","Manager",55000, '2013-01-05'],
                [123451,"Kelly Walker","Cashier",15000, '2018-01-21'], [123450,"Ira Sawyer","Cashier",15000, '2019-07-01'],
                [123439,"Claire Butler","Clerk",27000, '2017-10-22'],[123445,"Dyaln Meyers","Stocker",17000, '2017-08-16'],
                [123444,"Abigal Spritz","Stocker",17000, '2015-04-03'], [123453,"Randy Gilmore","Manager",60000, '2002-11-20'],
                [123448,"Erica Allen","Cashier",15000, '2018-08-25'], [123447,"Ryan Leshmeir","Cashier",15000, '2019-12-05'],
                [123446,"Penny Diaz","Cashier",15000, '2020-06-18'], [123440,"Susan Reynolds","Clerk",26000, '2016-05-28'],
                [123441,"John Graham","Stocker",17000, '2020-01-17']]

products = [[959742, 6.00, "Turkey Jerky Teriyaki", 4],
            [50255224003, 3.50, "Ritter Sport Dark Chocolate", 3],
            [80432106419, 20.00, "Single Pot Still Irish Whiskey", 10],
            [859612001024, 9.99, "21st Amendment Hell or High Watermelon Wheat Beer", 12],
            [805002000375, 4.00, "Dusk Deodorant", 28],
            [321134771643, 3.00, "Blue Mint Antiseptic Mouth Rinse", 12]]

productInformationAndRelationship = [[1, "November 2022", 4.00, 959742],
                                     [2, "January 2021", 3.00, 50255224003],
                                     [3, "January 2030", 10.00, 80432106419],
                                     [4, "January 2022", 12.00, 859612001024],
                                     [5, "February 2021,", 4.00, 805002000375],
                                     [6, "March 2022", 12.00, 321134771643]]


def genData():

    #db.drop_all()
    db.create_all()
    print('just reset database inside genData')

    for x in employeeData:
        newEmployee = Employees(Employee_ID=x[0], name=x[1],
                               title=x[2], salary=x[3],
                               join_date=x[4])
        print(newEmployee)
        db.session.add(newEmployee)

    hashed_password = bcrypt.generate_password_hash('Password123').decode('utf-8')
    user = User(username='bgmichael', email='bgmichael@outlook.com', password=hashed_password)
    db.session.add(user)
    try:
        db.session.commit()
    except:
        db.session.rollback()

def instantiateItem():
    print('inside instantiateItem function2')

    for x in products:
        product = Product(Product_ID=x[0], price=x[1],
                    product_name=x[2], quantity=x[3])
        print(product)
        db.session.add(product)

    try:
        db.session.commit()
    except:
        print('inside instantiateItem product except')
        db.session.rollback()

def instantiateRelationship():
    print('inside instantiateItemRelationship function2')
    for x in productInformationAndRelationship:

        relationship = Part_Of_Relationship(Individual_ID=x[0],
                                        Product_ID=x[3])
        print(relationship)
        db.session.add(relationship)

    db.session.commit()


def instantiateProductInfo():
    print('inside instantiateProductInfo function')
    for x in productInformationAndRelationship:
        productInfo = Product_Information(Individual_ID=x[0],
                                          expiration_date=x[1],
                                          product_weight=x[2])
        print(productInfo)
        db.session.add(productInfo)
    db.session.commit()





