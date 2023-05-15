import json
from web3 import Web3
# In the video, we forget to `install_solc`
# from solcx import compile_standard
from solcx import compile_standard, install_solc
import os
from dotenv import load_dotenv
from web3.middleware import geth_poa_middleware
load_dotenv()
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
# print(compiled_sol)
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["CommunityDapp.sol"]["CommunityDapp"]["evm"][
    "bytecode"
]["object"]
# print(bytecode)
abi = json.loads(
    compiled_sol["contracts"]["CommunityDapp.sol"]["CommunityDapp"]["metadata"]
)["output"]["abi"]
#print(abi)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_address = "0x107Ff9b117A6b28cda9a7ADE54D8C355F170f3ca" # static to be changed 
private_key = "0x0ba31be91070aa6351388b97a5c562718f6e9d5661d3678dc42fd40cc18cda4b" # static to be changed 
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
def post(interactive_functions,what_to_send , chain_id , my_address ):
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
def get_all_post(interactive_functions):
    return interactive_functions.functions.getUsersWithPosts().call()
CommunityChat_interactive_functions = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)# we can use static address here for the contract 
user_name = input("please enter user name : ")

register(CommunityChat_interactive_functions, user_name, chain_id , my_address)
print("regsiter successfully ! ")
while True: 
    what_to_send = input("enter what to send : ")
    post(CommunityChat_interactive_functions, what_to_send, chain_id,my_address)
    print("post successfully !  ")
    print(get_all_post(CommunityChat_interactive_functions), "all posts !!")
