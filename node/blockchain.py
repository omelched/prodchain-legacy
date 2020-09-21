import json
import time
from typing import List
from hashlib import sha256

import requests

import node.utils

logger = node.utils.get_logger(__name__)


class Block(object):
    hash = None

    def __init__(self, index: int, txs: List, timestamp, prev, nonce: int = 0):
        self.index = index
        self.txs = txs
        self.timestamp = timestamp
        self.prev_hash = prev
        self.nonce = nonce

        logger.debug('INIT {}'.format(self))

    def __str__(self):
        return 'Block #{}\ttime: {}\tprev: {}\thash: {}'.format(self.index,
                                                                self.timestamp,
                                                                self.prev_hash,
                                                                self.hash)

    def compute_hash(self):
        return sha256(json.dumps(self.__dict__, sort_keys=True).encode()).hexdigest()


class Blockchain(object):
    difficulty = 4

    def __init__(self):
        self.unconfirmed_txs = []
        self.chain = []

        logger.debug('INIT {}'.format(self))

    def create_genesis_block(self):
        genesis_block = Block(0, [], 0, '0')
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
        logger.info('Genesis block created!')

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        logger.info('Attempt to add <{}> to <{}> with proof:<{}>'.format(str(block), self, proof))

        if self.last_block.hash != block.prev_hash:
            logger.info(
                'block.prev_hash mismatch\t-\tblock:<{}>\t|\tchain:<{}>.\tAbort append.'.format(block.prev_hash,
                                                                                                self.last_block.hash))
            return False

        if not Blockchain.is_valid_proof(block, proof):
            logger.info('Proof <{}> not valid.\tAbort append.'.format(proof))
            return False

        block.hash = proof
        self.chain.append(block)
        logger.info('Append <{}> success.'.format(block))
        return True

    @staticmethod
    def proof_of_work(block: Block):

        now = time.time()
        logger.info('PoW(difficulty - <{}>) for <{}>.'.format(Blockchain.difficulty,
                                                              str(block)))

        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        logger.info('PoW ended with <{}> iterations in <{}> sec.'.format(block.nonce + 1,
                                                                         time.time() - now))
        return computed_hash

    def add_new_tx(self, tx):

        self.unconfirmed_txs.append(tx)

        logger.info('New tx: <{}>'.format(tx))

    @classmethod
    def is_valid_proof(cls, block: Block, block_hash: str):
        if not block_hash.startswith('0' * Blockchain.difficulty):
            logger.debug(
                'Blockchain.difficulty mismatch\t-\tblock:<{}>\t|\tchain:<{}>'.format(
                    node.utils.get_nonzero_symbol_index(block_hash),
                    Blockchain.difficulty))
            return False

        if not block_hash == block.compute_hash():
            logger.debug('block_hash incorrect\t-\tdeclared:<{}>\t|\treal:<{}>'.format(block_hash,
                                                                                       block.compute_hash()))

        return True

    @classmethod
    def check_chain_validity(cls, chain):
        logger.info('Chain {} is being checked for validity'.format(chain))

        result = True
        previous_hash = '0'

        for block in chain:

            logger.info('Checking <{}>'.format(block))

            block_hash = block.hash
            delattr(block, 'hash')

            if not cls.is_valid_proof(block, block_hash):
                logger.info('Proof <{}> not valid.\tDrop chain.'.format(block_hash))

                result = False
                break

            if not previous_hash == block.prev_hash:
                result = False

                logger.info(
                    'block.prev_hash mismatch\t-\tblock:<{}>\t|\tchain:<{}>.\tDrop chain.'.format(block.prev_hash,
                                                                                                  previous_hash))

                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self):
        if not self.unconfirmed_txs:
            logger.info('No txs to mine!')

            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          txs=self.unconfirmed_txs,
                          timestamp=time.time(),
                          prev=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)

        logger.info('<{}> mined.'.format(new_block))

        self.unconfirmed_txs = []

        return True


class BlockchainHandler(object):
    peers = None
    busy = None

    def __init__(self):

        self.blockchain = Blockchain()
        self.blockchain.create_genesis_block()

        logger.debug('INIT {}'.format(self))

    def consensus(self):

        logger.info('Calling to consensus!')

        longest_chain = None
        longest_chain_node = None
        current_len = len(self.blockchain.chain)

        for _node in self.peers:

            logger.debug('Comparing with {}'.format(_node))
            response = requests.get('{}chain'.format(_node))
            length = response.json()['length']
            chain = response.json()['chain']
            if length > current_len and self.blockchain.check_chain_validity(chain):
                current_len = length
                longest_chain = chain
                longest_chain_node = _node

        if longest_chain:
            logger.info('Chain from {} adopted as main!'.format(longest_chain_node))
            self.blockchain = longest_chain
            return True

        logger.info('Current chain is OK!')
        return False

    def create_chain_from_dump(self, chain_dump):

        generated_blockchain = Blockchain()
        generated_blockchain.create_genesis_block()

        for idx, block_data in enumerate(chain_dump):
            if idx == 0:
                continue
            block = Block(block_data['index'],
                          block_data['txs'],
                          block_data['timestamp'],
                          block_data['prev_hash'],
                          block_data['nonce'])
            proof = block_data['hash']
            added = self.blockchain.add_block(block, proof)
            if not added:
                raise Exception('The chain dump is tampered!!')
        return generated_blockchain
