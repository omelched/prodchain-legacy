import time
import json

import requests
from flask import request

from node import application
from node import utils
from node.blockchain import Block


@application.route('/')
def root():
    return 'Hello, world', 200


@application.route('/new_tx', methods=['POST'])
def new_tx():
    tx_data = request.get_json()
    required_fields = ['author', 'content']

    for field in required_fields:
        if not tx_data.get(field):
            return str(utils.InvalidTXDataException), 404
    tx_data['timestamp'] = time.time()

    application.blockchain.add_new_tx(tx_data)

    return 'Success', 201


@application.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in application.blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(application.peers)})


@application.route('/mine', methods=['GET'])
def mine_unconfirmed_tx():
    result = application.blockchain.mine()
    if not result:
        return 'No transactions to mine'
    else:
        chain_length = len(application.blockchain.chain)
        application.consensus()

        if chain_length == len(application.blockchain.chain):
            application.announce_new_block(application.blockchain.last_block)

        return 'Block #{} is mined'.format(application.blockchain.last_block.index)


@application.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()['node_address']
    if not node_address:
        return 'Invalid data', 400

    application.peers.add(node_address)

    return get_chain()


@application.route('/register_with', methods=['POST'])
def register_with_existing_node():
    node_address = request.get_json()['node_address']
    if not node_address:
        return 'Invalid data', 400

    data = {'node_address': request.host_url}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(node_address + 'register_node',
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        chain_dump = response.json()['chain']
        application.blockchain = application.create_chain_from_dump(chain_dump)
        application.peers.update(response.json()['peers'])
        return 'Registration successful', 200
    else:
        return response.content, response.status_code


@application.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = application.blockchain.add_block(block, proof)

    if not added:
        return 'The block was discarded by the node', 400

    return 'Block added to the chain', 201


@application.route('/pending_tx')
def get_pending_tx():
    return json.dumps(application.blockchain.unconfirmed_txs)

