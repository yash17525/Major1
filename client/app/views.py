import datetime
import json

import requests
from flask import render_template, redirect, request

from app import app

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []


def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/index')
def index():
    fetch_posts()
    return render_template('index.html',
                           title='YourNet: Decentralized '
                                 'content sharing',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)

@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    post_content = request.form["content"]
    author = request.form["author"]

    post_object = {
        'author': author,
        'content': post_content,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')

# **************************** ******************* *********************** ***************
@app.route('/')
def home():
    return render_template('home.html',
                           title='YourNet: Decentralized '
                                 'content sharing',
                           )

@app.route('/farmer')
def farmer():
    return render_template('farmer.html',
                           title='Blockchain: For '
                                 'the farmers',
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)

@app.route('/refiners')
def refiners():
    return render_template('refiner.html',
                           title='Blockchain: For '
                                 'the refiners',
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)

@app.route('/wholesalers')
def wholesalers():
    return render_template('wholesaler.html',
                           title='Blockchain: For '
                                 'the wholesalers',
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)

@app.route('/product')
def product():
    return render_template('product.html',
                           title='Blockchain: For '
                                 'the Public',
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/submitFarmer', methods=['POST'])
def submitFarmer():
    """
    Endpoint to create a new transaction via our application.
    """
    post_content = request.form["content"]
    farmer_ID = request.form["farmer_ID"]
    transaction_ID = request.form["transaction_ID"]

    post_object = {
        'Farmer_ID': farmer_ID,
        'content': post_content,
        'transaction_ID': transaction_ID
    }

    new_tx_address = "{}/new_farmer_transaction".format(CONNECTED_NODE_ADDRESS)
    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')


@app.route('/submitRefiner', methods=['POST'])
def submitRefiner():
    """
    Endpoint to create a new transaction via our application.
    """
    post_content = request.form["content"]
    refiner_ID = request.form["refiner_ID"]
    transaction_ID = request.form["transaction_ID"]

    post_object = {
        'Refiner_ID': refiner_ID,
        'content': post_content,
        'transaction_ID': transaction_ID
    }

    new_tx_address = "{}/new_refiner_transaction".format(CONNECTED_NODE_ADDRESS)
    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')


@app.route('/submitWholeSaler', methods=['POST'])
def submitWholeSaler():
    """
    Endpoint to create a new transaction via our application.
    """
    post_content = request.form["content"]
    WholeSaler_ID = request.form["WholeSaler_ID"]
    transaction_ID = request.form["transaction_ID"]
    product_Number = request.form["product_Number"]

    post_object = {
        'WholeSaler_ID': WholeSaler_ID,
        'content': post_content,
        'transaction_ID': transaction_ID,
        'product_Number': product_Number
    }

    new_tx_address = "{}/new_wholesaler_transaction".format(CONNECTED_NODE_ADDRESS)
    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')


@app.route('/product_fetch', methods=['GET','POST'])
def product_fetch():
    product_id = request.form['product_id']
    print(product_id)
    url = "{}/fetch_product".format(CONNECTED_NODE_ADDRESS)
    print(url)
    response = requests.get(url, params={'product_id': product_id})
    # response = requests.get(url)
    print(response.text)
    return response.text


    # if response.status_code == 200:
    #     content = []
    #     chain = json.loads(response.content)
    #     for block in chain["chain"]:
    #         for tx in block["transactions"]:
    #             tx["index"] = block["index"]
    #             tx["hash"] = block["previous_hash"]
    #             content.append(tx)






def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
