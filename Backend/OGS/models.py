from OGS import app,db,bcrypt
from sqlalchemy import event


class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)
    cart = db.relationship('Cart', backref='user', lazy=True)
    requests = db.relationship('CategoryRequest', backref='user',lazy=True)

    def get_id(self):
        return (self.userid)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

@event.listens_for(User.__table__, 'after_create')
def createAdmin(*args, **kwargs):
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
        user = User(username='Admin',email='Admin@gmail.com',password=hashed_password,role='admin')
        db.session.add(user)
        db.session.commit()

    
class StoreManagerSignUpRequest(db.Model):
    requestid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def get_id(self):
        return (self.userid)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"
    
class CategoryRequest(db.Model):
    requestid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    operation = db.Column(db.String(50), nullable=False)
    newName = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    categoryid = db.Column(db.Integer, db.ForeignKey('category.categoryid'), nullable=True)


    def __repr__(self):
        return f"Category('{self.categoryid}', '{self.name}')"


class Order(db.Model):
    orderid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    totalCost = db.Column(db.Float, nullable=False)
    products = db.relationship('ProductSold', backref='order', lazy=True)

    def __repr__(self):
        return f"Order('{self.orderid}', '{self.totalCost}')"
    

class ProductSold(db.Model):
    productid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    categoryName = db.Column(db.String(50))
    quantitySold = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    rateunits = db.Column(db.String(20), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    orderid = db.Column(db.Integer, db.ForeignKey('order.orderid'), nullable=False)

    def __repr__(self):
        return f"Product('{self.productid}','{self.name}','{self.categoryName}','{self.quantitySold}','{self.rate}', '{self.rateunits}', '{self.cost}')"
    

class Category(db.Model):
    categoryid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)
    requests = db.relationship('CategoryRequest', backref='category',lazy=True)

    def __repr__(self):
        return f"Category('{self.categoryid}', '{self.name}')"
    
class Product(db.Model):
    productid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    categoryid = db.Column(db.Integer, db.ForeignKey('category.categoryid'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    rateunits = db.Column(db.String(20), nullable=False)
    cart = db.relationship('Cart', backref='product', lazy=True)

    def __repr__(self):
        return f"Product('{self.productid}','{self.name}','{self.quantity}', '{self.rate}', '{self.rateunits}')"
    

class Cart(db.Model):
    cartid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable = False)
    productid = db.Column(db.Integer, db.ForeignKey('product.productid'), nullable = False)
    quantity = db.Column(db.Integer,nullable=False)
    cost = db.Column(db.Float,nullable=False)

    def __repr__(self):
        return f"Cart('{self.cartid}','{self.productid}','{self.quantity}', '{self.cost}')"
