#PRODUCTS
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
        return {"message": f"car {product.product} has been created successfully."}
        
    elif request.method == 'GET':
       
        products = ProductsModel.query.all()
        results = [
            {
                "id": product.id,
                "product": product.product,
                
            } for product in products]

        context= {"count": len(results), "Products": results}
        return render_template('productos.html',**context)