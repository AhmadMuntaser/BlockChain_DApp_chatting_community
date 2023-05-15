from flask import Flask, render_template, request,session
import json
from web3 import Web3
# In the video, we forget to `install_solc`
# from solcx import compile_standard
from solcx import compile_standard, install_solc
import os
from dotenv import load_dotenv
from web3.middleware import geth_poa_middleware
from datetime import datetime
from web3.exceptions import ContractLogicError

load_dotenv()



app = Flask(__name__)

app.secret_key = 'SuperSecretKey' 

with open("./CommunityDapp.sol", "r") as file:
    community_file = file.read()
install_solc("0.8.0")

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"CommunityDapp.sol": {"content": community_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.8.0",
)


with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["CommunityDapp.sol"]["CommunityDapp"]["evm"][
    "bytecode"
]["object"]

abi = json.loads(
    compiled_sol["contracts"]["CommunityDapp.sol"]["CommunityDapp"]["metadata"]
)["output"]["abi"]


w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_address = "0xDC87250C275De057d24F1291C3935FF816EC8952" # static to be changed 
private_key = "0xdd291abde32f2625eb3783a90f3269f716b2090f6fa24bf00a25d61f1aca07b9" # static to be changed 
CommunityChat = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(my_address)
transaction = CommunityChat.constructor().build_transaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Done! Contract deployed to {tx_receipt.contractAddress}")




def register(interactive_functions,username , chain_id , my_address ):
    try: 
        global w3 ,private_key
        nonce = w3.eth.get_transaction_count(my_address)
        register_on_blockchain = interactive_functions.functions.register(username).build_transaction(
        {
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            "from": my_address,
            "nonce": nonce ,
        }
        )
        signed_greeting_txn = w3.eth.account.sign_transaction(
        register_on_blockchain, private_key=private_key
        )
        tx_greeting_hash = w3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
        return "Registered successfully ! "
    except  ContractLogicError: 
        return "User already registered or username is already exsists ! "






def post(interactive_functions,what_to_send , chain_id , my_address ):
    try: 
        global w3 , private_key
        nonce = w3.eth.get_transaction_count(my_address)
        register_on_blockchain = interactive_functions.functions.post(what_to_send).build_transaction(
        {
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            "from": my_address,
            "nonce": nonce ,
        }
        )
        signed_greeting_txn = w3.eth.account.sign_transaction(
        register_on_blockchain, private_key=private_key
        )
        tx_greeting_hash = w3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
        return " post successfully ! "
    except  ContractLogicError: 
        return "something happend ! "




def return_readable_timestamp(timestamp): 
    return str(datetime.fromtimestamp(timestamp))

def get_all_post(interactive_functions):
    filtt = interactive_functions.functions.getUsersWithPosts().call()
    posts = [] 

    for i in filtt: 
        username = i[1]
        temp_posts = [] 
        temp_timestamp = [] 
        temp_postId = [] 
        if (len(i[2])>0 ): 
            for  post in i[2]: 
                if(len(post[2]) > 0):
                    temp_postId.append(post[0])
                    temp_posts.append(post[2])
                    temp_timestamp.append(return_readable_timestamp( int(post[3])))
        if len(username) > 0:
            posts.append({"username": username ,"postIds": temp_postId, "posts":temp_posts, "timestamps":temp_timestamp}) 

    return posts



@app.route("/")
def home():
    return render_template("index.html")



@app.route('/register', methods=['POST'])
def reg():
    if request.method == 'POST':
        username1 = request.form.get('name')
        CommunityChat_interactive_functions = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

        register(CommunityChat_interactive_functions, username1, chain_id, my_address)

        print(f"registered successfully as {username1}")
        session['username'] = username1  # Store the username in a session variable
        return render_template('chat.html', username=username1) 
    return 'registered done!!'





@app.route('/post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        what_to_send = request.form.get('post_content')
        CommunityChat_interactive_functions = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

        post(CommunityChat_interactive_functions, what_to_send, chain_id, my_address)
        print("Post successful!")

        username1 = session.get('username')  # Retrieve the username from the session variable
        messages = get_all_post(CommunityChat_interactive_functions)  # Extracted messages
        return render_template('chat.html', username=username1, messages=messages)
    return render_template('posts.html')


if __name__ == "__main__":
    app.run(debug=True)        