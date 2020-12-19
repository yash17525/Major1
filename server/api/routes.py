from hashlib import sha256
import json
import time
import datetime
from datetime import datetime
from flask import Flask, request, render_template
import requests

from api import app, db
from api import models


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        product_number = self.get_product_number(block)
        p = models.Product(product_id = product_number,chain_index = len(self.chain) - 1)
        db.session.add(p)
        db.session.commit()
        print(models.Product.query.all())
        return True

    def get_product_number(self, block):
        block_data = block.transactions[0]
        wholesaler_details = block_data['Wholesaler Details']
        return wholesaler_details['product_Number']


    @staticmethod
    def proof_of_work(block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)

        self.unconfirmed_transactions = []

        return True


# app = Flask(__name__)

# the node's copy of blockchain
blockchain = Blockchain()
blockchain.create_genesis_block()

# the address to other participating members of the network
peers = set()


# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
@app.route('/new_farmer_transaction', methods=['POST'])
def new_farmer_transaction():
    tx_data = request.get_json()
    farmer_ID, content, transaction_ID = tx_data['Farmer_ID'], tx_data['content'], tx_data['transaction_ID']
    f = models.Farmer(transaction_ID = transaction_ID, farmer_ID = farmer_ID, details = content)
    print(f)
    db.session.add(f)
    db.session.commit()
    print(models.Farmer.query.all())
    return "Success", 201

@app.route('/new_refiner_transaction', methods=['POST'])
def new_refiner_transaction():
    tx_data = request.get_json()
    refiner_ID, content, transaction_ID = tx_data['Refiner_ID'], tx_data['content'], tx_data['transaction_ID']
    r = models.Refiner(transaction_ID = transaction_ID, refiner_ID = refiner_ID, details = content)
    print(r)
    db.session.add(r)
    db.session.commit()
    print(models.Refiner.query.all())
    return "Success", 201

@app.route('/new_wholesaler_transaction', methods=['POST'])
def new_wholesaler_transaction():
    tx_data = request.get_json()
    wholesaler_ID, content, transaction_ID, product_Number = tx_data['WholeSaler_ID'], tx_data['content'], tx_data['transaction_ID'], tx_data['product_Number']
    w = models.Wholesaler(transaction_ID = transaction_ID, Wholesaler_ID = wholesaler_ID, details = content, product_Number = product_Number)
    print(w)
    db.session.add(w)
    db.session.commit()
    print(models.Wholesaler.query.all())
    generate_block(transaction_ID)
    return "Success", 201

def generate_block(transaction_ID):
    farmer_details = {}
    refiner_details = {}
    wholesaler_details = {}
    tx_data = {}

    f = models.Farmer.query.filter_by(transaction_ID = transaction_ID).first()
    print(f)
    farmer_details['farmer_ID'] = f.farmer_ID 
    farmer_details['content'] = f.details

    r = models.Refiner.query.filter_by(transaction_ID = transaction_ID).first()
    print(r)
    refiner_details['refiner_ID'] = r.refiner_ID 
    refiner_details['content'] = r.details

    w = models.Wholesaler.query.filter_by(transaction_ID = transaction_ID).first()
    print(w)
    wholesaler_details['wholesaler_ID'] = w.Wholesaler_ID
    wholesaler_details['content'] = w.details
    wholesaler_details['product_Number'] = w.product_Number

    tx_data['Transaction ID'] = transaction_ID
    tx_data['Farmer Details'] = farmer_details
    tx_data['Refiner Details'] = refiner_details
    tx_data['Wholesaler Details'] = wholesaler_details
    tx_data['Timestamp'] = time.time()
    print(tx_data)
    blockchain.add_new_transaction(tx_data)
    mine_unconfirmed_transactions()

@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ["author", "content"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data" + str(tx_data.get(field)), 404

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    return "Success", 201

@app.route('/fetch_product', methods=['GET'])
def fetch_product():
    # print(request.args)
    product_id = request.args.get('product_id')
    print(models.Product.query.all())
    p = models.Product.query.filter_by(product_id = product_id).first()
    print(p)
    testvar="yuvraj"
    # return render_template('result.html',
    #                        title='Product Details',val=testvar)
    if not p.chain_index:
        return 'invalid product number'
    index = int(p.chain_index)
    print(index)
    print(p.product_id)
    block = blockchain.chain[index]
    print(block.transactions)
    print(block.transactions[0]['Transaction ID'])
    Transaction_ID=block.transactions[0]["Transaction ID"]
    Farmer_ID=block.transactions[0]["Farmer Details"]["farmer_ID"]
    FarmerContent=block.transactions[0]["Farmer Details"]["content"]
    Refiner_ID=block.transactions[0]["Refiner Details"]["refiner_ID"]
    RefinerContent=block.transactions[0]["Refiner Details"]["content"]
    Wholesaler_ID=block.transactions[0]["Wholesaler Details"]["wholesaler_ID"]
    WholesalerContent=block.transactions[0]["Wholesaler Details"]["content"]
    ProductNumber=block.transactions[0]["Wholesaler Details"]["product_Number"]
    timestamp=block.transactions[0]["Timestamp"]
    dt_object = datetime.fromtimestamp(timestamp)
    currdatetime=dt_object.strftime("%m/%d/%Y, %H:%M:%S")
    return render_template('result.html',
                           title='Product Details',Transaction_ID=Transaction_ID,Farmer_ID=Farmer_ID,FarmerContent=FarmerContent,
                           Refiner_ID=Refiner_ID,RefinerContent=RefinerContent,Wholesaler_ID=Wholesaler_ID,WholesalerContent=WholesalerContent,
                           ProductNumber=ProductNumber,timestamp=currdatetime)
    

@app.route('/testing', methods=['GET'])
def testing():
    # product_id = request.args.get('product_id')
    # print(product_id)
    return 'success'

# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.index)


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.add(node_address)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


def consensus():
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)

# Uncomment this line if you want to specify the port number in the code
#app.run(debug=True, port=8000)
