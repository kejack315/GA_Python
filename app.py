from flask import Flask, request, render_template, redirect
from flask_paginate import Pagination, get_page_parameter
import pandas as pd
import csv

FILE = 'combined.csv'


# Function to read reviews from the CSV file
def read_combined():
    combineds = []
    try:
        with open(FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                combineds.append(row)
        return combineds
    except FileNotFoundError as e:
        with open(FILE, 'w') as file:
            return combineds


# Function to write reviews to the CSV file
def write_combineds(combineds):
    with open(FILE, 'w', newline='') as file:
        fieldnames = ['%KEY','Customer', 'Product Group', 'Product Line','City']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for combined in combineds:
            writer.writerow(combined)


user = "Jason_Ke"
app = Flask(__name__)
combineds = list(reversed(read_combined()))

@app.route("/")
def index_route():
    return render_template("index.html",user = user)

@app.route("/privacy")
def privacy():
    return render_template("privacy.html",user = user)

@app.route("/contact")
def contact():
    return render_template("contact.html",user = user)


@app.route("/products")
def product_route():

    page = request.args.get('page', 1, type=int)
    pagination = Pagination(page=page, per_page=10,total = len(combineds))
    start_index = (page - 1) * pagination.per_page
    end_index = start_index + pagination.per_page

    # Retrieve only the items for the current page
    items_for_page = combineds[start_index:end_index]
    return render_template("products.html", combineds = items_for_page, user = user,  pagination= pagination)
@app.route("/city")
def city():

    page = request.args.get('page', 1, type=int)
    pagination = Pagination(page=page, per_page=10,total = len(combineds))
    start_index = (page - 1) * pagination.per_page
    end_index = start_index + pagination.per_page

    # Retrieve only the items for the current page
    items_for_page = combineds[start_index:end_index]
    return render_template("city.html", combineds = items_for_page, user = user,  pagination= pagination)
@app.route("/customer")
def customer():

    page = request.args.get('page', 1, type=int)
    pagination = Pagination(page=page, per_page=10,total = len(combineds))
    start_index = (page - 1) * pagination.per_page
    end_index = start_index + pagination.per_page

    # Retrieve only the items for the current page
    items_for_page = combineds[start_index:end_index]
    return render_template("customer.html", combineds = items_for_page, user = user,  pagination= pagination)

@app.route("/dashboard")
def dashboard():
    # Assume combineds is your list containing the data
    combineds = read_combined()

    # Convert the list to a DataFrame
    combineds_df = pd.DataFrame(combineds, columns=['Customer', 'Product Line', 'City', ...])  # Add column names

    # Group by and get counts
    customer_product_data = combineds_df.groupby(['Customer', 'Product Line']).size().unstack().fillna(0)
    customer_city_data = combineds_df.groupby(['Customer', 'City']).size().unstack().fillna(0)
    city_product_data = combineds_df.groupby(['City', 'Product Line']).size().unstack().fillna(0)

    # Select top 10 data points based on total counts
    top_10_customer_product = customer_product_data.sum(axis=1).nlargest(10).index
    top_10_customer_city = customer_city_data.sum(axis=1).nlargest(10).index
    top_10_city_product = city_product_data.sum(axis=1).nlargest(10).index

    # Filter data for top 10 points
    customer_product_data = customer_product_data.loc[top_10_customer_product]
    customer_city_data = customer_city_data.loc[top_10_customer_city]
    city_product_data = city_product_data.loc[top_10_city_product]

    return render_template('dashboard.html',
                           user = user,
                           customer_product_data=customer_product_data.to_dict(),
                           customer_city_data=customer_city_data.to_dict(),
                           city_product_data=city_product_data.to_dict())

@app.route('/products/<int:index>', methods=['GET'])
def show_product(index):

    combined = combineds[index]
    if combined:
        return render_template('show_product.html', combined=combined,combined_index=index)

@app.route('/edit_products/<int:index>', methods=['GET', 'POST'])
def edit_product(index):
    combined = combineds[index]

    if request.method == 'POST':
        Key = int(combineds[index]['%KEY'])
        Customer = request.form['Customer']
        Product_Group = request.form['Product Group']
        Product_Line = request.form['Product Line']
        City = request.form['City']
        combineds[index] = {'%KEY':Key,'Customer':Customer, 'Product Group': Product_Group, 'Product Line':Product_Line,'City':City}
        write_combineds(combineds)

        return redirect('/products')

    return render_template('edit_products.html', combined=combined, combined_index=index)
@app.route('/delete_products/<int:index>', methods=['POST'])
def destroy_product(index):
    combineds.pop(index)
    write_combineds(combineds)
    return redirect('/products')
# "/reviews/"	DELETE	delete	Delete an item
@app.route('/delete_products/<int:index>', methods=['GET'])
def delete_product(index):
    combined = combineds[index]
    return render_template('delete_products.html', combined=combined,  combined_index=index)

@app.route('/create_products', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        # Find the maximum %KEY value
        max_key = max(int(combined['%KEY']) for combined in combineds) if combineds else 0
        # Increment the maximum %KEY value by 1 for the new product
        new_key = max_key + 1
        Customer = request.form['Customer']
        Product_Group = request.form['Product Group']
        Product_Line = request.form['Product Line']
        City = request.form['City']
        # Create a new product with the incremented %KEY value
        new_product = {'%KEY': new_key, 'Customer': Customer, 'Product Group': Product_Group, 'Product Line': Product_Line, 'City': City}
        combineds.append(new_product)
        write_combineds(combineds)
        return redirect('/products')

    return render_template('create_products.html', combineds=combineds)

if __name__ == '__main__':
    app.run(debug=True, port=5000)