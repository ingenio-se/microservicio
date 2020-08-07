from flask import Flask, request, make_response,redirect,render_template,url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import json


app = Flask(__name__)




app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:80085700@localhost:5432/market"
db = SQLAlchemy(app)

#sell

@app.route('/sellDelete', methods=['POST'])
def sellDelete():
    id=request.form['id']
    query ="delete from products_suppliers where id = " + str(id)
    sql = text(query)
    result = db.engine.execute(sql)
    return redirect(url_for('sell'))

@app.route('/sell', methods=['POST', 'GET'])
def sell():
    resultsp = getProducts()
    resultsc=getCities()
    resultss= getSuppliers() 
    resultscu = getCurrencies()
    table = getProductsSuppliers()
    if request.method == 'POST':
        product= request.form['product']
        supplier=request.form['supplier']
        price = request.form['price']
        currency = request.form['currency']

        id =maxId('products_suppliers')
        
        query ="insert into products_suppliers values ("+ str(id) + "," + str(product) + "," + str(supplier) + "," + str(price) + "," + str(currency) +")"
        sql = text(query)
        result = db.engine.execute(sql)

        return redirect(url_for('sell'))
        #return {"message": f"car {product.product} has been created successfully."}
        
    elif request.method == 'GET':  
        context= {"Products":resultsp, "Suppliers": resultss, "Cities": resultsc, "Currencies": resultscu,
                "table":table    
        }

        return render_template('sell.html',**context)

class CurrenciesModel(db.Model):
    __tablename__ = 'currencies'

    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String())
    abbreviation = db.Column(db.String())
    us_equ =db.Column(db.Float())

    def __init__(self, id,currency,abbreviation,us_equ):
        self.id = id
        self.currency = currency
        self.abbreviation = abbreviation
        self.us_equ = us_equ

    def __repr__(self):
        return f"<Currency {self.currency}>"
#CITIES
class CitiesModel(db.Model):
    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String())
    country_id =db.Column(db.Integer())

    def __init__(self, id,city,country_id):
        self.id = id
        self.city = city
        self.country_id = country_id

    def __repr__(self):
        return f"<City {self.city}>"


#SUPPLIERS
class SuppliersModel(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city_id =db.Column(db.Integer())

    def __init__(self, id,name,city_id):
        self.id = id
        self.name = name
        self.city_id = city_id

    def __repr__(self):
        return f"<Supplier {self.supplier}>"

@app.route('/changeSuppliers', methods=['POST'])
def changeSuppliers():
    if request.method == 'POST':
        action = request.form['action']
        supplier = request.form['supplier']
        if action == "save":
            name= request.form['name']
            city =request.form['city']
            queryId ="update suppliers set name = '"+name + "', city_id="+ city + " where id = " + supplier
            
        if action == "delete":
            queryId ="delete from suppliers where id = " + supplier

        sql = text(queryId)
        result = db.engine.execute(sql)
        return redirect(url_for('suppliers'))

@app.route('/suppliers', methods=['POST', 'GET'])
def suppliers():
    
    if request.method == 'POST':
        name= request.form['name']
        city=request.form['city']

        id =maxId('suppliers')
        supplier= SuppliersModel(id = id , name=name, city_id=city)
        db.session.add(supplier)
        db.session.commit()

        return redirect(url_for('suppliers'))
        return {"message": f"car {product.product} has been created successfully."}
        
    elif request.method == 'GET':  
        resultsc=getCities()
        results= getSuppliers() 
        context= {"count": len(results), "Suppliers": results, "Cities": resultsc}
        return render_template('suppliers.html',**context)



#PRODUCTS
class ProductsModel(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String())
    

    def __init__(self, id,product):
        self.id = id
        self.product = product

    def __repr__(self):
        return f"<Product {self.product}>"

@app.route('/changeProducts', methods=['POST'])
def changeProducts():
    if request.method == 'POST':
        action = request.form['action']
        product = request.form['product']
        if action == "save":
            name= request.form['name']
            queryId ="update products set product = '"+name + "' where id = " + product
            
        if action == "delete":
            queryId ="delete from products where id = " + product

        sql = text(queryId)
        result = db.engine.execute(sql)
        return redirect(url_for('products'))

@app.route('/products', methods=['POST', 'GET'])
def products(): 
    if request.method == 'POST':
        nuevo= request.form['name']
        id =maxId('products')
        product = ProductsModel(id = id , product=nuevo)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('products'))
        #return {"message": f"car {product.product} has been created successfully."}
        
    elif request.method == 'GET':
        results = getProducts()
        context= {"count": len(results), "Products": results}
        return render_template('productos.html',**context)




#CONSULTAS
@app.route('/query', methods=['POST', 'GET'])
def handle_query():

    queryProducts ="select distinct(product) from products order by product asc"
    sql = text(queryProducts)
    result = db.engine.execute(sql)
    listaProducts = [row for row in result]

    print(listaProducts)

    if request.method == 'GET':
        lista = []
    if request.method == 'POST':
        product = request.form['product']
          
        sql = text("SELECT products.product,countries.country,currencies.abbreviation,ps.price, \
        (ps.price * currencies.us_equ) as USD \
        FROM \
        products inner join products_suppliers as ps on products.id = ps.product_id \
        inner join suppliers on ps.supplier_id = suppliers.id \
        inner join cities on cities.id = suppliers.city_id \
        inner join countries on countries.id = cities.country_id \
        inner join currencies on currencies.id = ps.currency_id\
        where  \
            products.product = '" + product + "' order by USD desc")
        result = db.engine.execute(sql)
        lista = [row for row in result]
    
        print(lista)

    context ={
        'lista': lista,
        'listaProducts':listaProducts,
       
    }
    #return 'hola'
    return render_template('consulta.html',**context)


#AUXILIAR
def getProducts():
    products = ProductsModel.query.all()
    results = [
            {
                "id": product.id,
                "product": product.product,
                
            } for product in products]
    return results

def getSuppliers():
    suppliers = SuppliersModel.query.all()
    results = [
    {
                "id": supplier.id,
                "name": supplier.name,
                "city": cityName(supplier.city_id)
                
    } for supplier in suppliers]
    return results

def getCities():
    cities = CitiesModel.query.all()
    resultsc = [
            {
                "id": city.id,
                "city": city.city,
                "country_id": city.country_id
                
            } for city in cities]
    return resultsc
def getCurrencies():
    currencies = CurrenciesModel.query.all()
    results = [
            {
                "id": currency.id,
                "currency": currency.currency,
                "abbreviation": currency.abbreviation,
                "us_equ" : currency.us_equ                
            } for currency in currencies]
    return results

def getProductsSuppliers():
    queryId ="select * from products_suppliers"
    sql = text(queryId)
    result = db.engine.execute(sql)
    results=[]
    for row in result:
        l =[row[0],productName(row[1]),supplierName(row[2]),row[3],currencyName(row[4])]
        results.append(l)
    return results

def currencyName(id):
     currencies= CurrenciesModel.query.all()
     for curr in currencies:
         if curr.id == id:
             return curr.abbreviation

def supplierName(id):
     suppliers= SuppliersModel.query.all()
     for supplier in suppliers:
         if supplier.id == id:
             return supplier.name

def productName(id):
     products= ProductsModel.query.all()
     for product in products:
         if product.id == id:
             return product.product

def cityName(id):
     cities = CitiesModel.query.all()
     for city in cities:
         if city.id == id:
             return city.city
        
      
def maxId(table):
    queryId ="select max(id) as max from " + table
    sql = text(queryId)
    result = db.engine.execute(sql)
    id= [row for row in result]
    return int(id[0][0])+1


#INICIO
@app.route('/')
def index():
    return render_template('menu.html')


if __name__ == '__main__':
    app.run(port = 5000, debug = True)
    