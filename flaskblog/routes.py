import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ItemForm, SearchForm, SearchTextForm, JoinForm
from flaskblog.models import User, Post, Employees, Product, Product_Information, Part_Of_Relationship
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.gendata import genData, instantiateItem, instantiateProductInfo, instantiateRelationship
from sqlalchemy import text, Table, Column, Integer, String, MetaData


@app.route("/")
@app.route("/home")
def home():
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

        # productInfo = Product_Information(Individual_ID=11, expiration_date="April 10 2020", product_weight=13.00)
        # print(productInfo)
        # db.session.add(productInfo)
        # db.session.commit()

    posts = Employees.query.all()
    return render_template(('home.html'), posts=posts)


@app.route("/about")
def about():
    test = Employees.query.all()
    if len(test) < 1:
        genData()
    else:
        posts = Employees.query.all()
        return render_template('about.html', title='About', posts=posts)
    posts = Employees.query.all()
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
    return render_template('add_item.html', title='New Item',
                           form=form, legend='New Item')

# @app.route("/post/search", methods=['GET', 'POST'])
# @login_required
# def join():
#
#     form = JoinForm()
#     if form.validate_on_submit():
#         categoryOne = form.categoryOne.data
#         categoryTwo = form.categoryTwo.data
#         inputData = [[categoryOne, categoryTwo]]  # , searchText]]



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
        inputData = [[category, searchInt]]  # , searchText]]

        print(inputData[0][0])
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

        print(outputList)

        # query = text("SELECT * FROM" + inputData[0][0] + "where Product_ID is " + str(searchInt))

    return render_template('search.html', title='New Search',
                           form=form, legend='New Search', outputList=outputList, listLength=listLength)


@app.route("/post/searchText", methods=['GET', 'POST'])
@login_required
def searchText():
    listLength = 0
    outputList = []
    inputData = []
    name = 'none'
    query = Product_Information.query.first()
    test = Product.query.all()
    if len(test) < 1:
        instantiateItem()
    form = SearchTextForm()
    if form.validate_on_submit():
        category = form.category.data
        searchText = form.searchCritereaText.data
        inputData = [[category, searchText]]  # , searchText]]

        print(inputData[0][0])
        if inputData[0][0] == 'Product':
            query = Product.query.filter(Product.product_name == searchText).all()

            name = query[0].product_name
            price = query[0].price
            ID = query[0].Product_ID
            quantity = query[0].quantity
            outputList = [['name', name], ['price', price],
                          ['ID', ID], ['quantity', quantity]]
            listLength = len(outputList)

        elif inputData[0][0] == 'Product_Information':
            query = Product_Information.query.filter(Product_Information.expiration_date
                                                     == searchText).all()

            IndividualID = query[0].Individual_ID
            expirationDate = query[0].expiration_date
            product_weight = query[0].product_weight
            outputList = [['Individual ID', IndividualID], ['Expiration Date', expirationDate],
                          ['Product Weight', product_weight]]
            listLength = len(outputList)

        elif inputData[0][0] == 'Employees':
            query = Employees.query.filter(Employees.name
                                           == searchText).all()

            EmployeeID = query[0].Employee_ID
            Name = query[0].name
            Title = query[0].title
            Salary = query[0].salary
            JoinDate = query[0].join_date
            outputList = [['Employee ID', EmployeeID], ['Name', Name],
                          ['Title', Title], ['Salary', Salary], ['Join Date', JoinDate]]
            listLength = len(outputList)

    return render_template('searchText.html', title='New Text Search',
                           form=form, legend='New Text Search',
                           outputList=outputList, listLength=listLength)


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
