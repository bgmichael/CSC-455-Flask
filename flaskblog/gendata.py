import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Employees, Product, Product_Information, Part_Of_Relationship, Store, Sold_By_Relationship,\
Works_At_Relationship
    #Product, Product_Information, \
    #Part_Of_Relationship, Sold_By_Relationship, Store, Works_At_Relationship
from flask_login import login_user, current_user, logout_user, login_required
from random import randint
from sqlalchemy import func

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

products = [[959742, 6.00, "Turkey Jerky", 1],
            [50255224003, 3.50, "Dark Chocolate", 1],
            [80432106419, 20.00, "Irish Whiskey", 1],
            [859612001024, 9.99, "Wheat Beer", 1],
            [805002000375, 4.00, "Deodorant", 1],
            [321134771643, 3.00, "Mouth Rinse", 1],
            [123456789, 1.00, "Banana", 1],
            [234567891, 8.00, "Ham", 1],
            [345678912, 6.00, "Oatmeal", 1],
            [456789123, 3.00, "Beef", 1]]

productInformationAndRelationship = [[1, "November 2022", 4.00, 959742],
                                     [2, "January 2021", 3.00, 50255224003],
                                     [3, "January 2030", 10.00, 80432106419],
                                     [4, "January 2022", 12.00, 859612001024],
                                     [5, "February 2021,", 4.00, 805002000375],
                                     [6, "March 2022", 12.00, 321134771643],
                                     [7, "May 2020", 8.00, 234567891],
                                     [8, "May 2021", 6.00, 345678912],
                                     [9, "June 2020", 3.00, 456789123]]



def resetDatabase():
    db.drop_all()
    genData()


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
    if db.session.query(Store).all() == []:
        firstStore = Store(Store_ID=1, location='Wilmington, NC')
        db.session.add(firstStore)
    if db.session.query(Product).all() == []:
        instantiateItem()
    if db.session.query(Product_Information).all() == []:
        instantiateProductInfo()
    if db.session.query(Part_Of_Relationship).all() == []:
        instantiateRelationship()
    if db.session.query(Works_At_Relationship).all() == []:
        linkEmployees()
    if db.session.query(Sold_By_Relationship).all() == []:
        instantiateStoreToProduct()
    try:
        db.session.commit()
    except:
        db.session.rollback()

def instantiateStoreToProduct():
    print('inside instantiateStore')
    for product in products:
        productInStore = Sold_By_Relationship(Store_ID= 1, Product_ID=product[0])
        db.session.add(productInStore)
    db.session.commit()

def linkEmployees():
    print('inside linkEmployees')
    for employee in employeeData:
        employeeLink = Works_At_Relationship(Store_ID=1, Employee_ID= employee[0])
        db.session.add(employeeLink)
    db.session.commit()

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

def nextHighestIndividualId():
    maxIndvId = db.session.query(func.max(Product_Information.Individual_ID))
    maxId = maxIndvId[0]
    maxId = maxId[0]
    if maxId == None:
        nextMaxId = 1
    else:
        nextMaxId = maxId + 1
    return nextMaxId

def monthToIntTranslation(month):
    intTranslation = 0
    if month == 'January':
        intTranslation = 1
    elif month == 'February':
        intTranslation = 2
    elif month == 'March':
        intTranslation = 3
    elif month == 'April':
        intTranslation = 4
    elif month == 'May':
        intTranslation = 5
    elif month == 'June':
        intTranslation = 6
    elif month == 'July':
        intTranslation = 7
    elif month == 'August':
        intTranslation = 8
    elif month == 'September':
        intTranslation = 9
    elif month == 'October':
        intTranslation = 10
    elif month == 'November':
        intTranslation = 11
    elif month == 'December':
        intTranslation = 12

    return intTranslation

def seperateQueryResult(expirationString):
    seperatedList = expirationString.split()
    expirationMonth = seperatedList[0]
    expirationYear = int(seperatedList[1][0:4])
    resultList = [expirationMonth, expirationYear]
    return resultList





