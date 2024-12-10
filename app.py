from flask import Flask, request, jsonify
import hashlib
import time

app = Flask(__name__)

# Route pour la page d'accueil
@app.route('/')
def index():
    return "Bienvenue sur l'API de suivi des colis !"

# Route pour le suivi des colis
@app.route('/track_package/<colis_id>', methods=['GET'])
def track_package(colis_id):
    # Find events related to the given colis_id
    events = [block for block in blockchain.chain if block['colis_id'] == colis_id]
    if not events:
        return jsonify({"message": f"Colis {colis_id} non trouvé"}), 404
    
    # Return the list of events related to the colis_id
    return jsonify({
        'colis_id': colis_id,
        'events': events
    })

# Route pour obtenir la blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    return jsonify({
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    })

# Route pour le favicon
@app.route('/favicon.ico')
def favicon():
    return '', 204  # Pas de contenu pour le favicon

# Classe simplifiée pour la Blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(previous_hash='1', proof=100, colis_id='0', status='initial', location='origin', payment_status='pending')

    def create_block(self, proof, previous_hash, colis_id, status, location, payment_status):
        block = {
           'index': len(self.chain) + 1,
           'timestamp': time.time(),
           'proof': proof,
           'previous_hash': previous_hash,
           'colis_id': colis_id,
           'status': status,
           'location': location,
           'payment_status': payment_status
        }
        self.chain.append(block)
        return block

    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 1
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    def valid_proof(self, last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'

# Initialize blockchain
blockchain = Blockchain()

# Route pour ajouter un événement
@app.route('/add_event', methods=['POST'])
def add_event():
    data = request.get_json()

    # Validate input
    if 'colis_id' not in data or 'status' not in data or 'location' not in data or 'payment_status' not in data:
        return jsonify({'message': 'Missing parameters'}), 400

    last_block = blockchain.last_block()
    proof = blockchain.proof_of_work(last_block['proof'])
    previous_hash = last_block['previous_hash']
    
    # Create new block with the provided event data
    block = blockchain.create_block(proof, previous_hash, data['colis_id'], data['status'], data['location'], data['payment_status'])

    # Return the newly added block
    return jsonify({
        'message': 'Event added to blockchain',
        'block': block
    })

if __name__ == '__main__':
    app.run(debug=True)
