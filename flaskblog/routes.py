import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ItemForm, SearchForm, UpdateItem, \
    DeleteItem, AdvancedSearchFrontForm, SearchMaxForm, SearchExpirationForm, DisplayItemsForm, \
    SimulatedTransactionForm, HomeForm, StoreManagementForm, \
    EmployeeManagementForm, StoreAddOrDeleteForm
from flaskblog.models import User, Employees, Product, Product_Information, Part_Of_Relationship, Store
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.gendata import genData, instantiateItem, instantiateProductInfo, instantiateRelationship, resetDatabase, \
    nextHighestIndividualId, monthToIntTranslation, seperateQueryResult, resetDatabase
from sqlalchemy import text, Table, Column, Integer, String, MetaData
from sqlalchemy import func


@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    form = HomeForm()
    if form.validate_on_submit():
        resetDatabase()
        print('RESET')
        flash('Your Database has been reset!', 'success')
        return render_template('home.html', form=form)
    test = Employees.query.all()
    print(len(test))
    if len(test) < 1:
        print('inside genData loop')
        genData()

    if Product.query.first() == None:
        instantiateItem()
    if Product_Information.query.first() == None:
        print('inside productinformation test loop')
        instantiateProductInfo()
    if Part_Of_Relationship.query.first() == None:
        instantiateRelationship()

    posts = Product.query.all()

    return render_template(('home.html'), form=form, posts=posts)


@app.route("/about")
def about():
    test = Employees.query.all()
    if len(test) < 1:
        genData()
    else:
        posts = Product_Information.query.all()
        return render_template('about.html', title='About', posts=posts)
    posts = Product_Information.query.all()
    return render_template('about.html', title='About', posts=posts)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/add", methods=['GET', 'POST'])
@login_required
def add_item():
    test = Product.query.all()
    if len(test) < 1:
        instantiateItem()
    form = ItemForm()
    if form.validate_on_submit():
        item = Product(Product_ID=form.Product_ID.data,
                       price=form.price.data,
                       product_name=form.product_name.data,
                       quantity=form.quantity.data, )
        itemInfo = Product_Information(Individual_ID=form.Individual_ID.data,
                                       expiration_date=form.expiration_date.data,
                                       product_weight=form.product_weight.data)
        db.session.add(item)
        db.session.add(itemInfo)
        db.session.commit()
        flash('Your item has been added!', 'success')
        return redirect(url_for('home'))
    return render_template('add_item.html', title='New Product',
                           form=form, legend='New Product')


@app.route("/post/updateItem", methods=['GET', 'POST'])
@login_required
def updateItem():
    form = UpdateItem()
    if form.validate_on_submit():
        # Set Variables (Example of Prepared Statements)
        updateID = form.Product_ID.data
        print(updateID)
        updateExpiration = form.expirationDate.data
        updateProduct = db.session.query(Product).filter(Product.Product_ID == updateID).all()[0]
        print(updateProduct)
        updatequantity = form.amountToAdd.data
        print(updatequantity)
        ##logic for changing the item instance
        if updatequantity != None:
            currentquantity = updateProduct.quantity
            updateProduct.quantity = updatequantity + currentquantity

            sampleID = db.session.query(Part_Of_Relationship).filter \
                (Part_Of_Relationship.Product_ID == updateID).first().Individual_ID
            sampleWeight = db.session.query(Product_Information).filter \
                (Product_Information.Individual_ID == sampleID).first().product_weight
            for newitem in range(updatequantity):
                newIndividualID = nextHighestIndividualId()
                newPI = Product_Information(Individual_ID=newIndividualID,
                                            expiration_date=updateExpiration,
                                            product_weight=sampleWeight)
                newPOR = Part_Of_Relationship(Individual_ID=newIndividualID, Product_ID=updateID)
                db.session.add(newPI)
                db.session.add(newPOR)

        db.session.commit()
        flash('Your update has been processed!', 'success')
        return redirect(url_for('updateItem', title='Update Item', form=form, legend='Update Item'))

    return render_template('updateItem.html', title='Update Item',
                           form=form, legend='Update Item')


@app.route("/post/deleteItem", methods=['GET', 'POST'])
@login_required
def deleteItem():
    form = DeleteItem()
    if form.validate_on_submit():
        updateIndividualID = form.Individual_ID.data
        updateProductID = form.Product_ID.data
        POR_ToDelete = db.session.query(Part_Of_Relationship).filter \
            (Part_Of_Relationship.Individual_ID == updateIndividualID).all()[0]
        print(POR_ToDelete)
        PI_ToDelete = db.session.query(Product_Information).filter \
            (Product_Information.Individual_ID == updateIndividualID).all()[0]
        print(PI_ToDelete)
        updateQuantity = db.session.query(Product).filter \
            (Product.Product_ID == updateProductID).all()[0].quantity
        print("Update Before:", updateQuantity)
        updateQuantity = updateQuantity - 1
        print("Update After:", updateQuantity)
        db.session.query(Product).filter(Product.Product_ID == updateProductID).all()[0].quantity = updateQuantity
        testQuery = db.session.query(Product).filter(Product.Product_ID == updateProductID).all()[0].quantity
        print(testQuery)
        db.session.delete(POR_ToDelete)
        db.session.delete(PI_ToDelete)
        if updateQuantity == 0:
            product = db.session.query(Product).filter(Product.Product_ID == updateProductID).all()[0]
            db.session.delete(product)
        db.session.commit()
        flash('Your item has been Deleted!', 'success')
        return redirect(url_for('deleteItem', title='Delete Item', form=form, legend='Delete Item'))

    return render_template('deleteItem.html', title='Delete Item',
                           form=form, legend='Delete Item')


@app.route("/displayAllItems", methods=['GET', 'POST'])
@login_required
def displayAllItems():
    form = DisplayItemsForm()
    resultsList = []
    listLength = len(resultsList)
    if form.validate_on_submit():
        # Join Example between Product and Product_Information
        resultsList = db.session.query(Product.product_name, Product.Product_ID,
                                       Part_Of_Relationship.Individual_ID).join \
            (Part_Of_Relationship).all()
        listLength = len(resultsList)

    return render_template('displayAllItems.html', title='Display Items',
                           form=form, legend='Display Items', resultsList=resultsList)


@app.route("/post/search", methods=['GET', 'POST'])
@login_required
def search():
    listLength = 0
    outputList = []
    inputData = []
    name = 'none'
    query = Product_Information.query.first()
    test = Product.query.all()
    if len(test) < 1:
        instantiateItem()
    form = SearchForm()
    if form.validate_on_submit():
        category = form.category.data
        searchInt = form.searchCritereaNumber.data
        searchText = form.searchCritereaText.data
        searchOption = form.SearchOption.data
        inputData = [[category, searchInt, searchText]]

        print(inputData[0][0])
        if searchOption == 'Search By ID':
            if inputData[0][0] == 'Product':
                name = Product.query.get(searchInt).product_name
                price = Product.query.get(searchInt).price
                ID = Product.query.get(searchInt).Product_ID
                quantity = Product.query.get(searchInt).quantity
                outputList = [['name', name], ['price', price],
                              ['ID', ID], ['quantity', quantity]]
                listLength = len(outputList)
            elif inputData[0][0] == 'Product_Information':
                IndividualID = Product_Information.query.get(searchInt).Individual_ID
                expirationDate = Product_Information.query.get(searchInt).expiration_date
                product_weight = Product_Information.query.get(searchInt).product_weight
                outputList = [['Individual ID', IndividualID], ['Expiration Date', expirationDate],
                              ['Product Weight', product_weight]]
                listLength = len(outputList)
            elif inputData[0][0] == 'Part_Of_Relationship':
                IndividualID = Part_Of_Relationship.query.get(searchInt).IndividualID
                ProductID = Part_Of_Relationship.query.get(searchInt).Product_ID
                outputList = [['Individual ID', IndividualID], ['Product ID', ProductID]]
                listLength = len(outputList)
            elif inputData[0][0] == 'Employees':
                EmployeeID = Employees.query.get(searchInt).Employee_ID
                Name = Employees.query.get(searchInt).name
                Title = Employees.query.get(searchInt).title
                Salary = Employees.query.get(searchInt).salary
                JoinDate = Employees.query.get(searchInt).join_date
                outputList = [['Employee ID', EmployeeID], ['Name', Name],
                              ['Title', Title], ['Salary', Salary], ['Join Date', JoinDate]]
                listLength = len(outputList)
        elif searchOption == 'Search By Name':
            if inputData[0][0] == 'Product':
                productInstance = db.session.query(Product).filter \
                    (Product.product_name == searchText).all()[0]
                name = productInstance.product_name
                price = productInstance.price
                ID = productInstance.Product_ID
                quantity = productInstance.quantity
                outputList = [['name', name], ['price', price],
                              ['ID', ID], ['quantity', quantity]]
                listLength = len(outputList)
            elif inputData[0][0] == 'Employees':
                productInstance = db.session.query(Employees).filter \
                    (Employees.name == searchText).all()[0]
                EmployeeID = productInstance.Employee_ID
                Name = productInstance.name
                Title = productInstance.title
                Salary = productInstance.salary
                JoinDate = productInstance.join_date
                outputList = [['Employee ID', EmployeeID], ['Name', Name],
                              ['Title', Title], ['Salary', Salary], ['Join Date', JoinDate]]
                listLength = len(outputList)

    return render_template('search.html', title='New Search',
                           form=form, legend='Search', outputList=outputList, listLength=listLength)


@app.route("/storeManagementFront", methods=['GET', 'POST'])
@login_required
def storeManagementFront():
    form = StoreManagementForm()
    searchOption = form.SearchOption.data
    if form.validate_on_submit():
        if searchOption == 'Add/Delete Employee':
            return redirect(
                url_for('employeeManagement', title='Add/Delete Employee', form=form, legend='Add/Delete Employee'))
        elif searchOption == 'Add/Delete Store':
            return redirect(
                url_for('storeManagement', title='Add/Delete Store', form=form, legend='Add/Delete Store'))

    return render_template('StoreManagementFront.html', title='Store Management Front',
                           form=form, legend='Store Management Front')


@app.route("/storeManagementFront/employeeManagement", methods=['GET', 'POST'])
@login_required
def employeeManagement():
    form = EmployeeManagementForm()
    searchOption = form.SearchOption.data
    if form.validate_on_submit():
        if searchOption == 'Add Employee':
            newEmployee = Employees(Employee_ID=form.EmployeeID.data,
                                    name=form.EmployeeName.data,
                                    title=form.EmployeeTitle.data,
                                    salary=form.EmployeeSalary.data,
                                    join_date=form.EmployeeJoinDate.data)
            db.session.add(newEmployee)
            db.session.commit()
            flash('Your Employee has been added!', 'success')
        elif searchOption == 'Delete Employee':
            employeeID = form.EmployeeID.data
            employeeToDelete = db.session.query(Employees).filter \
                (Employees.Employee_ID == employeeID).all()[0]
            db.session.delete(employeeToDelete)
            db.session.commit()
            flash('Your Employee has been deleted!', 'success')
    return render_template('EmployeeManagement.html', title='Employee Management',
                           form=form, legend='Employee Management')


@app.route("/storeManagementFront/storeManagement", methods=['GET', 'POST'])
@login_required
def storeManagement():
    form = StoreAddOrDeleteForm()
    searchOption = form.SearchOption.data
    if form.validate_on_submit():
        if searchOption == 'Add Store':
            newStore = Store(Store_ID=form.StoreID.data,
                             location=form.StoreLocation.data)
            db.session.add(newStore)
            db.session.commit()
            flash('Your Store has been added!', 'success')
        elif searchOption == 'Delete Store':
            StoreID = form.StoreID.data
            StoreToDelete = db.session.query(Store).filter \
                (Store.Store_ID == StoreID).all()[0]
            db.session.delete(StoreToDelete)
            db.session.commit()
            flash('Your Store has been deleted!', 'success')
    return render_template('StoreManagement.html', title='Store Management',
                           form=form, legend='Store Management')


@app.route("/advancedSearchFront", methods=['GET', 'POST'])
@login_required
def advancedSearchFront():
    form = AdvancedSearchFrontForm()
    searchOption = form.SearchOption.data
    if form.validate_on_submit():
        if searchOption == 'Get Max':
            return redirect(url_for('advancedSearchMax', title='Search Max', form=form, legend='Search Max'))
        elif searchOption == 'Search Expiration':
            return redirect(
                url_for('advancedSearchExpiration', title='Search Expiration', form=form, legend='Search Expiration'))
        elif searchOption == 'Simulate Transaction':
            return redirect(
                url_for('advancedSearchTransaction', title='Simulate Transaction', form=form,
                        legend='Simulate Transaction'))

    return render_template('AdvancedSearchFront.html', title='Advanced Search',
                           form=form, legend='Advanced Search')


@app.route("/advancedSearchFront/searchMax", methods=['GET', 'POST'])
@login_required
def advancedSearchMax():
    form = SearchMaxForm()
    max = 'None'
    searchOption = form.SearchOption.data

    if form.validate_on_submit():
        if searchOption == 'Price':
            max = db.session.query(func.max(Product.price))[0][0]
            print(max)
            # return redirect(url_for('advancedSearchMax', title='Search Max', form=form, legend='Search Max', max=max))
        elif searchOption == 'Product ID':
            max = db.session.query(func.max(Product.Product_ID))[0][0]
            # return redirect(url_for('advancedSearchMax', title='Search Max', form=form, legend='Search Max', max=max))
        elif searchOption == 'Weight':
            max = db.session.query(func.max(Product_Information.product_weight))[0][0]
            # return redirect(url_for('advancedSearchMax', title='Search Max', form=form, legend='Search Max', max=max))

    return render_template('AdvancedSearchMax.html', title='Advanced Search',
                           form=form, legend='Advanced Search', max=max)


@app.route("/advancedSearchExpiration/searchExpiration", methods=['GET', 'POST'])
@login_required
def advancedSearchExpiration():
    form = SearchExpirationForm()
    searchOption = form.SearchOption.data
    resultsList = []
    listLength = len(resultsList)
    if form.validate_on_submit():
        if searchOption == 'Show All':
            print("Inside Show all")
            resultsList = db.session.query \
                (Product.product_name, Part_Of_Relationship.Individual_ID, Part_Of_Relationship.Product_ID,
                 Product_Information.expiration_date) \
                .filter(Product.Product_ID == Part_Of_Relationship.Product_ID,
                        Part_Of_Relationship.Individual_ID == Product_Information.Individual_ID) \
                .all()
            print(resultsList)
            listLength = -1
            print(listLength)
            # return redirect(url_for('advancedSearchExpiration', title='Search Expiration', form=form, legend='Search Expiration',
            #                         resultsList=resultsList, listLength=listLength))
        elif searchOption == 'Search By Range':
            print("Inside search by range")
            monthList = ['January', 'February', 'March', 'April', 'May',
                         'June', 'July', 'August', 'September', 'October',
                         'November', 'December']

            textOne = form.SearchTextOne.data
            numberOne = form.SearchIntOne.data
            textTwo = form.SearchTextTwo.data
            numberTwo = form.SearchIntTwo.data

            textOneToInt = monthToIntTranslation(textOne)
            textTwoToInt = monthToIntTranslation(textTwo)
            print("TextOneToInt: ", textOneToInt)
            print("TextTwoToInt: ", textTwoToInt)

            LowerBoundMonthRange = monthList[textOneToInt: -1]
            UpperBoundMonthRange = monthList[0: textTwoToInt]
            print("Month Range Lower:", LowerBoundMonthRange)
            print("Month Range Upper:", UpperBoundMonthRange)

            queryListFull = db.session.query \
                (Product.product_name, Product_Information.expiration_date) \
                .filter(Product.Product_ID == Part_Of_Relationship.Product_ID,
                        Part_Of_Relationship.Individual_ID ==
                        Product_Information.Individual_ID).all()
            print("Number Two: ", numberTwo)
            print("Number One: ", numberOne)
            for queryresult in queryListFull:
                expirationString = queryresult[1]
                queryResultSeperate = seperateQueryResult(expirationString)

                expirationDateYear = queryResultSeperate[1]
                expirationDateMonth = queryResultSeperate[0]

                # In this case, the year is between the two years in question
                if numberTwo > expirationDateYear > numberOne:
                    resultsList.append(queryresult)
                # In this case, the query's year is equal to the Lower Bound year
                if expirationDateYear == numberOne:
                    # The month's are equal, therefore the query is included
                    if expirationDateMonth == textOne:
                        resultsList.append(queryresult)
                    # Testing the query to see if it is in a range of months after the Lower Bound
                    elif expirationDateMonth in LowerBoundMonthRange:
                        resultsList.append(queryresult)
                # Now testing for if query's year is equal to Upper Bound year
                if expirationDateYear == numberTwo:
                    if expirationDateMonth == textTwo:
                        resultsList.append(queryresult)
                    elif expirationDateMonth in UpperBoundMonthRange:
                        resultsList.append(queryresult)

            print(resultsList)
            listLength = len(resultsList)
            # return redirect(
            #     url_for('advancedSearchExpiration', title='Search Expiration', form=form, legend='Search Expiration',
            #             resultsList=resultsList, listLength=listLength))
        elif searchOption == 'Search For Date':
            print("Inside Search For Date")
            textOne = form.SearchTextOne.data
            numberOne = form.SearchIntOne.data

            queryListFull = db.session.query \
                (Product.product_name, Product_Information.expiration_date) \
                .filter(Product.Product_ID == Part_Of_Relationship.Product_ID,
                        Part_Of_Relationship.Individual_ID ==
                        Product_Information.Individual_ID).all()

            for queryresult in queryListFull:
                expirationString = queryresult[1]
                queryResultSeperate = seperateQueryResult(expirationString)

                expirationDateYear = queryResultSeperate[1]
                expirationDateMonth = queryResultSeperate[0]

                if expirationDateYear == numberOne and expirationDateMonth == textOne:
                    resultsList.append(queryresult)
            print(resultsList)
            listLength = len(resultsList)
            # return redirect(
            #     url_for('advancedSearchExpiration', title='Search Expiration', form=form, legend='Search Expiration',
            #             resultsList=resultsList, listLength=listLength))
    return render_template('AdvancedSearchExpiration.html', title='Advanced Search',
                           form=form, legend='Advanced Search', resultsList=resultsList, listLength=listLength)


@app.route("/advancedSearchFront/simulatedTransaction", methods=['GET', 'POST'])
@login_required
def advancedSearchTransaction():
    form = SimulatedTransactionForm()
    resultsList = []
    transactionListProduct = []
    priceList = []
    listLength = len(resultsList)
    itemCount = len(transactionListProduct)
    transactionCost = 0

    if form.validate_on_submit():
        transactionInput = form.transaction.data
        transactionListString = transactionInput.split(", ")

        print(transactionListString)
        for item in transactionListString:
            productName = db.session.query(Product).filter \
                (Product.product_name == item).all()
            transactionListProduct.append(productName)
            print(transactionListProduct)
        for product in transactionListProduct:
            itemPrice = product[0].price
            priceList.append(itemPrice)
            print(priceList)
        transactionCost = sum(priceList)
        transactionCost = round(transactionCost, 2)
        itemCount = len(transactionListProduct)

    return render_template('AdvancedSearchTransaction.html', title='Simulated Transaction',
                           form=form, legend='Simulated Transaction', transactionListProduct=transactionListProduct,
                           itemCount=itemCount, transactionCost=transactionCost)


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))
