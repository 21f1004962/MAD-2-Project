from flask import request, jsonify, make_response
from OGS import app, db, bcrypt
from OGS.models import User, Order, ProductSold, Category, Product, Cart, StoreManagerSignUpRequest, CategoryRequest
from sqlalchemy.exc import IntegrityError
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask_cors import cross_origin
from OGS import cache



def token_required(allowed_roles=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']
                # print(token)
            if not token:
                return make_response('Token is missing!', 401)
            try:
                # print(app.config['SECRET_KEY'])
                data = jwt.decode(str(token), str(
                    app.config['SECRET_KEY']), algorithms=["HS256"])
                current_user = User.query.filter_by(
                    userid=data['userid']).first()
                if allowed_roles and current_user.role not in allowed_roles:
                    return make_response('Insufficient permissions!', 403)
            except jwt.ExpiredSignatureError:
                return make_response('Token has expired!', 401)
            except jwt.InvalidTokenError:
                # print(f"Invalid token: {e}")
                return make_response('Invalid token!', 401)

            return f(current_user, *args, **kwargs)

        return decorated

    return decorator

@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    auth = request.form

    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response(
            'Could not verify',
            400,
            {'WWW-Authenticate': 'Basic realm ="Login Credentials required!"'}
        )

    smrequest = StoreManagerSignUpRequest.query.filter_by(
        username=auth.get('username')).first()

    if smrequest:
        return make_response(
            "Sign up request still hasn't been accepted by the admin. Please try again later!",
            202,
            {'WWW-Authenticate': 'Basic realm ="Sign up request pending."'}
        )

    user = User.query.filter_by(username=auth.get('username')).first()

    if not user:
        return make_response(
            'Could not verify',
            404,
            {'WWW-Authenticate': 'Basic realm ="User does not exist!"'}
        )

    if bcrypt.check_password_hash(user.password, auth.get('password')):
        token = jwt.encode({
            'userid': str(user.userid),
            'role': str(user.role),
            'exp': datetime.utcnow() + timedelta(minutes=3000)
        }, app.config['SECRET_KEY'])

        return make_response(jsonify({'token': token}), 201)

    else:
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Wrong Password!"'}
        )


@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    data = request.form

    username, email = data.get('username'), data.get('email')
    role = data.get('role')
    password = data.get('password')

    if all([username, email, role, password]):
        user1 = User.query.filter_by(email=email).first()
        user2 = User.query.filter_by(username=username).first()
        if not (user1 or user2):
            if role == 'user':
                user = User(
                    username=username,
                    email=email,
                    password=bcrypt.generate_password_hash(
                        password).decode("utf-8"),
                    role=role
                )

                try:
                    db.session.add(user)
                    db.session.commit()
                    return make_response('Successfully registered.', 201)
                except IntegrityError:
                    db.session.rollback()
                    return make_response('An error occurred while creating an account! Please try again later.', 500)

            elif role == 'storeManager':
                user1 = StoreManagerSignUpRequest.query.filter_by(email=email).first()
                user2 = StoreManagerSignUpRequest.query.filter_by(username=username).first()

                if user2:
                    return make_response('Sign Up request already exists with the given username.', 409)
                if user1:
                    return make_response('Sign Up request already exists with the given email.', 409)

                user = StoreManagerSignUpRequest(
                    username=username,
                    email=email,
                    password=bcrypt.generate_password_hash(
                        password).decode("utf-8")
                )
                try:
                    db.session.add(user)
                    db.session.commit()
                    return make_response('Successfully raised a request! Please wait for the admin to approve before trying to login.', 201)
                except IntegrityError:
                    db.session.rollback()
                    return make_response('An error occurred while creating an account! Please try again later.', 500)

        else:
            if user2:
                return make_response('User already exists with the given username. Please Log in.', 202)
            if user1:
                return make_response('User already exists with the given email. Please Log in.', 202)
    else:
        return make_response("Missing form data!", 400)


@app.route('/getCategories')
@cross_origin()
@token_required(['admin', 'storeManager'])
def adminGetCategories(current_user):
    categories = Category.query.all()
    category_dict = {
        category.categoryid: category.name for category in categories} if categories else None

    return make_response(jsonify({"categories":category_dict}), 200)


@app.route('/getCategoryName')
@cross_origin()
@token_required(['admin', 'storeManager'])
def adminGetCategoryName(current_user):
    category_id = request.args.get('categoryId')
    category = Category.query.filter_by(categoryid = category_id).first()
    if category:
        return make_response(jsonify({"category_name":category.name}), 200)
    else:
        return make_response(f"There exists no category with id {category_id}!", 404)


# admin api calls


@app.route('/adminAddCategory', methods=['POST'])
@cross_origin()
@token_required(['admin'])
def adminAddCategory(current_user):
    name = request.form.get('name')

    if not name:
        return make_response("Missing form data!", 400)

    name = name.capitalize()
    category = Category.query.filter_by(name=name).first()

    if category:
        return make_response(f'There already exists a category with the name {name}.', 500)

    try:
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        return make_response('New Category has been added!', 201)
    except IntegrityError:
        db.session.rollback()
        return make_response('An error occurred while adding the category. Please try again later.', 500)


@app.route('/adminEditCategory', methods=['PUT'])
@cross_origin()
@token_required(['admin'])
def adminEditCategory(current_user):
    category_id = request.form.get('categoryid')
    name = request.form.get('name')
    if category_id and name:
        name = name.capitalize()
        category = Category.query.filter_by(categoryid=category_id).first()
        if category:
            if name != category.name:
                existing_category = Category.query.filter_by(name=name).first()
                if existing_category:
                    return make_response('A category with that name already exists. Please choose another name!', 409)
            category.name = name
            try:
                db.session.commit()
                return make_response(f"Category with ID {category_id} updated to {name}!", 201)
            except IntegrityError:
                db.session.rollback()
                return make_response('An error occurred while editing the category name!', 500)
        else:
            return make_response(f"Category with ID {category_id} not found!", 404)
    else:
        return make_response("Missing form data!", 400)


@app.route('/adminDeleteCategory', methods=['DELETE'])
@cross_origin()
@token_required(['admin'])
def adminDeleteCategory(current_user):
    category_id = request.form.get('categoryid')

    if not category_id:
        return make_response("Missing form data!", 400)

    category = Category.query.filter_by(categoryid=category_id).first()

    if category:
        try:

            products = Product.query.filter_by(categoryid=category_id).all()

            if products:
                for product in products:
                    db.session.query(Cart).filter_by(
                        productid=product.productid).delete()
                    db.session.delete(product)
            
            smrequests = CategoryRequest.query.filter_by(categoryid = category_id).all()
            if smrequests:
                for smrequest in smrequests:
                    smrequest.status = "Rejected"
                    smrequest.categoryid = None

            db.session.query(Category).filter_by(
                categoryid=category_id).delete()
            db.session.commit()

            return make_response(f"Category with ID {category_id} has been deleted!", 200)

        except IntegrityError:
            db.session.rollback()
            return make_response('An error occurred while deleting the category. Please try again later.', 500)
    else:
        return make_response(f"Category with ID {category_id} not found!", 404)


@app.route('/adminApproveCategoryRequest', methods=['POST'])
@cross_origin()
@token_required(['admin'])
def adminApproveCategoryRequest(current_user):
    request_id = request.form.get('requestid')
    admin_response = request.form.get('adminResponse')

    if request_id and admin_response:
        if admin_response == 'True':
            admin_response = True
        else:
            admin_response = False
        smrequest = CategoryRequest.query.filter_by(
            requestid=request_id).first()
        if smrequest:
            if admin_response == False:
                smrequest.status = 'Rejected'
                try:
                    db.session.commit()
                    return make_response('Request successfully rejected.', 200)
                except IntegrityError:
                    db.session.rollback()
                    return make_response('An error occured while rejecting the request. Please try again later.', 500)
            else:
                smrequest.status = 'Accepted'
                operation = smrequest.operation.capitalize()
                if operation == 'Add':
                    category = Category.query.filter_by(
                        name=smrequest.name).first()
                    if category:
                        smrequest.status = 'Rejected'
                        try:
                            db.session.commit()
                            return make_response(f'Request rejected! There already exists a category with the name {smrequest.name}!', 500)
                        except IntegrityError:
                            db.session.rollback()
                            return make_response('An error occured while accepting the request. Please try again later.', 500)
                    category = Category(name=smrequest.name)
                    try:
                        db.session.add(category)
                        db.session.commit()
                        return make_response('Request successfully accepted.', 200)
                    except IntegrityError:
                        db.session.rollback()
                        return make_response('An error occured while accepting the request. Please try again later.', 500)
                elif operation == 'Edit':
                    category = Category.query.filter_by(
                        categoryid=smrequest.categoryid).first()
                    if not category:
                        smrequest.status = 'Rejected'
                        try:
                            db.session.commit()
                            return make_response(f'Request rejected! There is no category with id {smrequest.categoryid}!', 500)
                        except IntegrityError:
                            db.session.rollback()
                            return make_response('An error occured while accepting the request. Please try again later.', 500)
                    category.name = smrequest.newName
                    try:
                        db.session.commit()
                        return make_response('Request successfully accepted.', 200)
                    except IntegrityError:
                        db.session.rollback()
                        return make_response('An error occured while accepting the request. Please try again later.', 500)
                elif operation == 'Delete':
                    category = Category.query.filter_by(
                        categoryid=smrequest.categoryid).first()
                    if not category:
                        smrequest.status = 'Rejected'
                        try:
                            db.session.commit()
                            return make_response(f'Request rejected! There is no such category.', 500)
                        except IntegrityError:
                            db.session.rollback()
                            return make_response('An error occured while accepting the request. Please try again later.', 500)
                    try:
                        products = Product.query.filter_by(categoryid=category.categoryid).all()

                        if products:
                            for product in products:
                                db.session.query(Cart).filter_by(
                                    productid=product.productid).delete()
                                db.session.delete(product)
                        
                        smrequests = CategoryRequest.query.filter_by(categoryid = category.categoryid).all()
                        if smrequests:
                            for smrequest in smrequests:
                                smrequest.status = "Rejected"
                                smrequest.categoryid = None


                        db.session.delete(category)
                        db.session.commit()
                        return make_response('Request successfully accepted.', 200)
                    except IntegrityError:
                        db.session.rollback()
                        return make_response('An error occured while accepting the request. Please try again later.', 500)
                else:
                    smrequest.status = 'Rejected'
                    try:
                        db.session.commit()
                        return make_response('Request rejected since the operation mentioned in the request was not valid.', 400)
                    except IntegrityError:
                        db.session.rollback()
                        return make_response('An error occured while accepting the request. Please try again later.', 500)
        else:
            return make_response(f"Category request with ID {request_id} not found!", 404)
    else:
        return make_response("Missing form data!", 400)


@app.route('/adminApproveSignUpRequest', methods=['POST'])
@cross_origin()
@token_required(['admin'])
def adminApproveSignUpRequest(current_user):
    request_id = request.form.get('requestid')
    admin_response = request.form.get('adminResponse')
    if request_id and admin_response:
        if admin_response == 'True':
            admin_response = True
        else:
            admin_response = False
        smrequest = StoreManagerSignUpRequest.query.filter_by(
            requestid=request_id).first()
        if smrequest:
            if admin_response == False:
                try:
                    db.session.delete(smrequest)
                    db.session.commit()
                    return make_response('Request successfully rejected.', 200)
                except IntegrityError:
                    db.session.rollback()
                    return make_response('An error occured while rejecting the request. Please try again later.', 500)
            else:
                user1 = User.query.filter_by(
                    username=smrequest.username).first()
                user2 = User.query.filter_by(email=smrequest.email).first()
                if user1 or user2:
                    try:
                        db.session.delete(smrequest)
                        db.session.commit()
                        return make_response('Request could not be accepted! User with same username or password exists!', 500)
                    except IntegrityError:
                        db.session.rollback()
                        return make_response('An error occured while accepting the request. Please try again later.', 500)

                user = User(username=smrequest.username, email=smrequest.email,
                            password=smrequest.password, role='storeManager')
                smrequest1 = StoreManagerSignUpRequest.query.filter_by(
                    username=smrequest.username).all()
                smrequest2 = StoreManagerSignUpRequest.query.filter_by(
                    email=smrequest.email).all()
                try:
                    db.session.add(user)
                    if smrequest1:
                        for smrequest in smrequest1:
                            db.session.delete(smrequest)
                    if smrequest2:
                        for smrequest in smrequest2:
                            db.session.delete(smrequest)
                    db.session.commit()
                    return make_response('Request successfully accepted! Store Manager account has been activated!', 201)
                except IntegrityError:
                    db.session.rollback()
                    return make_response('An error occured while accepting the request. Please try again later.', 500)
        else:
            return make_response(f"Store Manager sign up request with ID {request_id} not found!", 404)
    else:
        return make_response("Missing form data!", 400)
    
@app.route('/adminGetSignUpRequests', methods=['GET'])
@cross_origin()
@token_required(['admin'])
def adminGetSignUpRequests(current_user):
    smrequests = StoreManagerSignUpRequest.query.all()
    smrequests_data = []
    if smrequests:
        smrequests_data = [
            {
                'id': request.requestid,
                'username': request.username, 
                'email': request.email,
            }
            for request in smrequests
        ]
    
    return make_response(jsonify({'signup_requests': smrequests_data}),200)

@app.route('/adminGetCategoryRequests', methods=['GET'])
@cross_origin()
@token_required(['admin'])
def adminGetCategoryRequests(current_user):
    requests = CategoryRequest.query.filter_by(status = 'Pending').all()
    requests_data = []
    if requests:
        for request in requests:
            temp = {
                'id': request.requestid,
                'name': request.name,
                'operation': request.operation,
                'newName': request.newName,
                'status': request.status, 
                'requestedBy': request.user.username,
            }
            requests_data.append(temp)
        
    
    return make_response(jsonify({'category_requests': requests_data}),200)


    


# store manager api calls


@app.route('/storeManagerCategoryRequest', methods=['POST'])
@cross_origin()
@token_required(['storeManager'])
def storeManagerCategoryRequest(current_user):
    operation = request.form.get('operation')
    if operation:
        operation = operation.capitalize()
        smrequest = None
        if operation == 'Add' or operation == 'Edit':
            if operation == 'Add':
                name = request.form.get('name')

                if not name:
                    return make_response('Missing form data! Please specify the name of the category to be added.', 400)

                name = name.capitalize()

                category = Category.query.filter_by(name=name).first()

                if category:
                    return make_response(f'There already exists a category with the name {name}.', 409)

                smrequest = CategoryRequest(
                    name=name, operation='Add', status='Pending', userid=current_user.userid)
            else:
                category_id = request.form.get('categoryid')

                if not category_id:
                    return make_response('Missing form data! Please specify the id of the category to be edited.', 400)

                newName = request.form.get('newName')
                if not newName:
                    return make_response('Missing form data! Please specify the modified name of the category to be edited.', 400)

                newName = newName.capitalize()

                category = Category.query.filter_by(
                    categoryid=category_id).first()

                if category.name == newName:
                    return make_response(f'Please assign the category {newName} a new name, if you wish to modify it.', 409)

                category = Category.query.filter_by(name=newName).first()

                if category:
                    return make_response(f'There already exists a category with the name {newName}.', 409)

                category = Category.query.filter_by(
                    categoryid=category_id).first()

                if not category:
                    return make_response(f'There is no category with id {category_id}!', 404)

                smrequest = CategoryRequest(
                    name=category.name,newName=newName, operation='Edit', status='Pending', userid=current_user.userid, categoryid=category_id)
        elif operation == 'Delete':
            category_id = request.form.get('categoryid')

            if not category_id:
                return make_response('Missing form data! Please specify the id of the category to be deleted.', 400)

            category = Category.query.filter_by(
                categoryid=category_id).first()

            if not category:
                return make_response(f'There is no category with id {category_id}!', 404)

            smrequest = CategoryRequest(
                name=category.name,operation='Delete', status='Pending', userid=current_user.userid, categoryid=category_id)
        try:
            db.session.add(smrequest)
            db.session.commit()
            return make_response('Request has been successfully raised!', 201)
        except IntegrityError:
            db.session.rollback()
            return make_response('An error occured while raising the request. Please try again later.', 500)
    else:
        return make_response('Missing form data! Please specify the operation to be performed.', 400)


@app.route('/storeManagerGetProducts')
@cross_origin()
@token_required(['storeManager'])
def storeManagerGetProducts(current_user):
    category_id = request.args.get('categoryid')
    category = Category.query.filter_by(categoryid=category_id).first()
    if category:
        products = Product.query.filter_by(
            categoryid=category_id).all()
        products_list = []
        i = 1
        for product in products:
            product_dict = {
                'sno': i,
                'productid': product.productid,
                'name': product.name,
                'categoryid': product.categoryid,
                'quantity': product.quantity,
                'rate': product.rate,
                'rateunits': product.rateunits
            }
            products_list.append(product_dict)
            i += 1
        return make_response(jsonify(products_list), 200)
    else:
        return make_response('No such category exists.', 404)


@app.route('/storeManagerAddProduct', methods=['POST'])
@cross_origin()
@token_required(['storeManager'])
def storeManagerAddProduct(current_user):
    name = request.form.get('name')
    category_id = request.form.get('categoryid')
    quantity = request.form.get('quantity')
    rate = request.form.get('rate')
    rateunits = request.form.get('rateunits')

    if all([name, category_id, quantity, rate, rateunits]):
        name = name.capitalize()
        product = Product.query.filter_by(name=name).first()
        if product:
            return make_response(f'Product with the name {name} already exists!', 409)
        product = Product(name=name, categoryid=category_id, quantity=quantity,
                          rate=rate, rateunits=rateunits)
        try:
            db.session.add(product)
            db.session.commit()
            return make_response('Product successfully added!', 201)
        except IntegrityError:
            db.session.rollback()
            return make_response('An error occured while creating the product! Please try again later.', 500)
    else:
        return make_response('Missing form data!', 400)


@app.route('/storeManagerEditProduct', methods=['PUT'])
@cross_origin()
@token_required(['storeManager'])
def storeManagerEditProduct(current_user):
    product_id = request.form.get('productid')
    if not product_id:
        return make_response('Missing form data!', 400)

    product = Product.query.filter_by(productid=product_id).first()

    if not product:
        return make_response(f"No product with product id {product_id} exists!", 404)

    name = request.form.get('name')
    if not name:
        return make_response('Missing form data!', 400)

    name = name.capitalize()

    if name != product.name:
        existing_product = Product.query.filter_by(name=name).first()
        if existing_product:
            print("True")
            return make_response(
                f"A product with that name already exists. Please choose another name.", 409)

    quantity = request.form.get('quantity')
    rate = request.form.get('rate')
    rateunits = request.form.get('rateunits')

    if all([quantity, rate, rateunits]):
        product.name = name
        product.quantity = quantity
        product.rate = rate
        product.rateunits = rateunits
        try:
            db.session.commit()
            return make_response('Product successfully modified!', 200)
        except IntegrityError:
            db.session.rollback()
            return make_response('An error occured while editing the product! Please try again later.', 500)
    else:
        return make_response('Missing form data!', 400)


@app.route('/storeManagerDeleteProduct', methods=['DELETE'])
@cross_origin()
@token_required(['storeManager'])
def storeManagerDeleteProduct(current_user):
    product_id = request.form.get('productid')
    if not product_id:
        return make_response('Missing form data!', 400)

    product = Product.query.filter_by(productid=product_id).first()

    if not product:
        return make_response(f"No product with product id {product_id} exists!", 404)

    try:
        cart = Cart.query.filter_by(productid = product.productid).all()
        for cartEntry in cart:
            db.session.delete(cartEntry)
        db.session.delete(product)
        db.session.commit()
        return make_response('Product successfully deleted!', 200)
    except IntegrityError:
        db.session.rollback()
        return make_response('An error occured while deleting the product! Please try again later.', 500)


# user api calls
    
@app.route('/userGetProducts')
@cross_origin()
@token_required(['user'])
def userGetProducts(current_user):
    searchType = request.args.get('searchType')
    searchKey = request.args.get('searchKey')
    if searchType and searchKey:
        if searchType == 'products':
            products = Product.query.filter(Product.name.like('%' + searchKey + '%')).all()
            
            categories = Category.query.all()
            category_dict = {category.categoryid: category.name for category in categories} if categories else None

            products_dict = {}

            if products:
                count = 1
                for product in products:
                    categoryid = product.categoryid
                    categoryName = category_dict[categoryid]
                    if not categoryName in products_dict:
                        products_dict[categoryName] = []
                    temp = {}
                    temp['sno'] = count
                    temp['productid'] = product.productid
                    temp['name'] = product.name
                    temp['quantity'] = product.quantity
                    temp['rate'] = product.rate
                    temp['rateunits'] = product.rateunits
                    products_dict[categoryName].append(temp)
                    count += 1
        else:
            categories = Category.query.filter(Category.name.like('%' + searchKey + '%')).all()
            category_dict = {category.categoryid: category.name for category in categories} if categories else None

            products_dict = {}

            if category_dict:
                for i in category_dict:
                    products = Product.query.filter_by(categoryid=i).all()
                    if products:
                        products_dict[category_dict[i]] = []
                        count = 1
                        for product in products:
                            temp = {}
                            temp['sno'] = count
                            temp['productid'] = product.productid
                            temp['name'] = product.name
                            temp['quantity'] = product.quantity
                            temp['rate'] = product.rate
                            temp['rateunits'] = product.rateunits
                            products_dict[category_dict[i]].append(temp)
                            count += 1

    else:
        categories = Category.query.all()
        category_dict = {category.categoryid: category.name for category in categories} if categories else None

        products_dict = {}

        if category_dict:
            for i in category_dict:
                products = Product.query.filter_by(categoryid=i).all()
                if products:
                    products_dict[category_dict[i]] = []
                    count = 1
                    for product in products:
                        temp = {}
                        temp['sno'] = count
                        temp['productid'] = product.productid
                        temp['name'] = product.name
                        temp['quantity'] = product.quantity
                        temp['rate'] = product.rate
                        temp['rateunits'] = product.rateunits
                        products_dict[category_dict[i]].append(temp)
                        count += 1

    return make_response(jsonify(products_dict),200)


@app.route('/userAddProduct', methods=['POST'])
@cross_origin()
@token_required(['user'])
def userAddProduct(current_user):
    productid = int(request.form.get('productid'))
    quantity = int(request.form.get('quantity'))

    if not productid:
        make_response("Missing form data!",400)
    elif not quantity:
        quantity = 1
    
    product = Product.query.filter_by(productid=productid).first()
    category = Category.query.filter_by(categoryid=product.categoryid).first()
    
    if not product:
        make_response(f"No product with the product Id {productid} exists!",404)
    
    if quantity > product.quantity:
        make_response(f"The available quantity of {product.name} is {product.quantity} {product.rateunits}s!",409)
    
    cart = Cart.query.filter_by(userid=current_user.userid,productid=product.productid).first()
    try:
        if cart:
            if cart.quantity + quantity > product.quantity:
                return make_response(f"The available quantity of {product.name} is {product.quantity} {product.rateunits}s!",409)
            cart.quantity += quantity
            cart.cost = product.rate * cart.quantity
            
        else:
            cart = Cart(userid=current_user.userid,productid=productid,quantity=quantity,cost=product.rate*quantity)
            db.session.add(cart)

        db.session.commit()
        return make_response("Cart successfully updated!",201)
    except IntegrityError:
        db.session.rollback()
        return make_response('An error occurred while adding an item to the cart! Please try again later.', 500)


@app.route('/userGetCart')
@cross_origin()
@token_required(['user'])
def userGetCart(current_user):
    cart_products = Cart.query.filter_by(userid=current_user.userid).all()
    cart = []
    count = 1
    for cart_product in cart_products:
        temp_product = {}
        temp_product['productid'] = cart_product.productid
        temp_product['cartid'] = cart_product.cartid
        temp_product['sno'] = count
        temp_product['name'] = cart_product.product.name
        cart_product.quantity = min(cart_product.product.quantity,cart_product.quantity)
        temp_product['quantity'] = cart_product.quantity
        temp_product['availableQuantity'] = cart_product.product.quantity
        temp_product['category'] = cart_product.product.category.name
        temp_product['rate'] = cart_product.product.rate
        temp_product['rateunits'] = cart_product.product.rateunits
        temp_product['cost'] = cart_product.quantity * cart_product.product.rate
        cart_product.cost = cart_product.quantity * cart_product.product.rate
        cart.append(temp_product)
        count += 1
    try:
        db.session.commit()
        return make_response(jsonify(cart),200)
    except IntegrityError:
        db.session.rollback()
        return make_response('An error occurred while fetching the cart! Please try again later.', 500)


@app.route('/userReviewEditProduct', methods=['PUT'])
@cross_origin()
@token_required(['user'])
def userReviewEditProduct(current_user):
    cartid = int(request.form.get('cartid'))
    productid = int(request.form.get('productid'))
    quantity = int(request.form.get('quantity'))

    if not productid:
        return make_response("Please specify the product Id of the product to be modified!",400)
    elif not cartid:
        return make_response("Please specify the cart Id of the product to be modified!",400)
    elif not quantity:
        return make_response("Please specify the modified quantity of the product!",400)

    
    product = Product.query.filter_by(productid=productid).first()
    
    if not product:
        return make_response(f"No product with the product Id {productid} exists!",404)
    
    if quantity > product.quantity:
        return make_response(f"The available quantity of {product.name} is {product.quantity} {product.rateunits}s!",409)
    
    cart = Cart.query.filter_by(cartid=cartid).first()

    if not cart:
        return make_response(f"No item in cart with cart Id {cartid} exists!",409)
    
    try:
        cart.quantity = quantity
        cart.cost = quantity * product.rate
        db.session.commit()
        return make_response("Cart Successfully updated!",201)
    except IntegrityError:
        db.session.rollback()
        return make_response('An error occurred while editing the product! Please try again later.', 500) 


@app.route('/userDeleteProduct', methods=['DELETE'])
@cross_origin()
@token_required(['user'])
def userDeleteProduct(current_user):
    productid = int(request.form.get('productid'))
    cartid = int(request.form.get('cartid'))

    if not productid and not cartid:
        return make_response("Please specify the product Id and cart Id of the product to be deleted!",400)
    elif not productid:
        return make_response("Please specify the product Id of the product to be modified!",400)
    elif not cartid:
        return make_response("Please specify the cart Id of the product to be modified!",400)

    cart = Cart.query.filter_by(cartid=cartid).first()

    if cart:
        try:
            db.session.delete(cart)
            db.session.commit()
            return make_response("Cart Successfully updated!",201)
        except IntegrityError:
            db.session.rollback()
            return make_response('An error occurred while deleting the item! Please try again later.', 500) 
        

@app.route('/checkout')
@cross_origin()
@token_required(['user'])
def checkout(current_user):
    cart = Cart.query.filter_by(userid = current_user.userid).all()
    if cart:
        totalCost = 0
        for item in cart:
            product = Product.query.filter_by(productid=item.productid).first()
            try:
                item.cost = item.quantity * product.rate
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return make_response('An error occurred while placing an order! Please try again later.', 500) 
            
            if item.quantity > product.quantity:
                name = item.product.name
                quantity = item.product.quantity
                units = item.product.rateunits
                try:
                    db.session.delete(item)
                    db.session.commit()
                    return make_response(f"Order could not be placed. The available quantity of {name} is {quantity} {units}s!",409)
                except IntegrityError:
                    db.session.rollback()
                    return make_response('2An error occurred while placing an order! Please try again later.', 500) 
            else:
                totalCost += item.cost
        order = Order(userid=current_user.userid,totalCost=totalCost)
        try:
            db.session.add(order)
            db.session.commit()
            for item in cart:
                product = Product.query.filter_by(productid=item.productid).first()
                product.quantity -= item.quantity
                productSold = ProductSold(name=item.product.name,categoryName=item.product.category.name,quantitySold=item.quantity,rate=item.product.rate,rateunits=item.product.rateunits,cost=item.quantity*item.product.rate,orderid=order.orderid)
                db.session.add(productSold)
                db.session.delete(item)
                db.session.commit()
            return make_response("Order successfully placed!",201)    
        except IntegrityError:
            db.session.rollback()
            return make_response("1There was an error while placing the order. Please try again later!",500) 
    else:
        return make_response("Please add items to the cart to checkout!",202)
    

@app.route('/userOrderHistory')
@cross_origin()
@cache.cached(timeout=30)
@token_required(['user'])
def userOrderHistory(current_user):
    order_dict = {}
    total_cost = {}
    orders = Order.query.filter_by(userid=current_user.userid).all()
    if orders:
        for order in orders:
            temp_order = []
            products = ProductSold.query.filter_by(orderid=order.orderid).all()
            if products:
                for product in products:
                    temp_product = {}
                    temp_product['name'] = product.name
                    temp_product['categoryName'] = product.categoryName
                    temp_product['quantitySold'] = product.quantitySold
                    temp_product['rate'] = product.rate
                    temp_product['rateunits'] = product.rateunits
                    temp_product['cost'] = product.cost
                    temp_order.append(temp_product.copy())
            order_dict[order.orderid] = temp_order.copy()
            total_cost[order.orderid] = order.totalCost
    return make_response(jsonify({"order_dict": order_dict,"total_cost":total_cost}),200)