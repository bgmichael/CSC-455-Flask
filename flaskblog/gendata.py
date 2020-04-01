import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post, Employees
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




def genData():

    db.drop_all()
    db.create_all()

    for x in employeeData:
        newEmployee = Employees(Employee_ID=x[0], name=x[1],
                               title=x[2], salary=x[3],
                               join_date=x[4])
        print(newEmployee)
        db.session.add(newEmployee)
    try:
        db.session.commit()
    except:
        db.session.rollback()



