import json
from web3 import Web3
from web3.exceptions import ContractLogicError
from solcx import compile_standard, install_solc
from flask import Flask, render_template, request,session, redirect
import os
from dotenv import load_dotenv
from web3.middleware import geth_poa_middleware
from datetime import datetime

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
my_address = "0xA6808c0cbaA925232fB92b0271E7384f184C965c" # static to be changed 
private_key = "0x4743f4f02319668d4d6f69e970381494eac669a0be7b86632a233a94b7986171" # static to be changed 
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
def Comment(interactive_functions,postId , what_to_send, my_address, chain_id ): 
    try: 
        global w3 , private_key
        nonce = w3.eth.get_transaction_count(my_address)
        register_on_blockchain = interactive_functions.functions.comment(postId, what_to_send).build_transaction(
        {
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            "from": my_address,
            "nonce": nonce ,
        }
        )
        signed_txn = w3.eth.account.sign_transaction(
        register_on_blockchain, private_key=private_key
        )
        tx_greeting_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return " Comment successfully ! "
    except  ContractLogicError: 
        return "something happend ! "   


def Like(interactive_functions,postId , my_address, chain_id):
    try: 
        global w3 , private_key
        nonce = w3.eth.get_transaction_count(my_address)
        register_on_blockchain = interactive_functions.functions.like(postId).build_transaction(
        {
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            "from": my_address,
            "nonce": nonce ,
        }
        )
        signed_txn = w3.eth.account.sign_transaction(
        register_on_blockchain, private_key=private_key
        )
        tx_greeting_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return " Like successfully ! "
    except  ContractLogicError: 
        return "something happend ! "   

def getUser(interactive_functions, my_address): 
    return interactive_functions.functions.getUser(my_address).call()

def getComments(interactive_functions , postId ): 
    Comments_before_filter = interactive_functions.functions.GetCommentsOnPost(postId).call()
    Comments_after_filter = [] 
    for i in Comments_before_filter:
        Comments_after_filter.append({"username": i[2] , "comment": i[4], "timestamp": return_readable_timestamp(i[5])} )
    return Comments_after_filter

def getLikes(interactive_functions , postId ): 
    return interactive_functions.functions.GetLikesOnPost(postId).call()


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
        temp_comments = [] 
        temp_likes_count  = [] 
        if (len(i[2])>0 ): 
            for  post in i[2]: 
                if(len(post[2]) > 0):
                    temp_postId.append(post[0])
                    temp_comments.append(getComments(interactive_functions, post[0] ))
                    temp_posts.append(post[2])
                    temp_timestamp.append(return_readable_timestamp( int(post[3])))
                    temp_likes_count.append(len(getLikes(interactive_functions,post[0])))
        #print("likes count :  ", len(temp_likes))
        if len(username) > 0:
            posts.append({"username": username ,"postIds": temp_postId, "posts":temp_posts, "timestamps":temp_timestamp , "Comments": temp_comments , "LikesCount": temp_likes_count}) 

    return posts

######################################### server code ####################################################

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True


CommunityChat_interactive_functions = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)# tx_receipt.contractAddress
username= '' 
@app.route("/")
def home():
    global CommunityChat_interactive_functions , username , my_address
    print(my_address)
    user_tuple= getUser(CommunityChat_interactive_functions , my_address)
    print(user_tuple)
    userSigned_Check = user_tuple[2]
    username = user_tuple[0]
    print(username)
    if (userSigned_Check): 
        return render_template("index.html", userSigned_Check =userSigned_Check , username=username )
    else: 
        return render_template("index.html", userSigned_Check =userSigned_Check,  username=username)




@app.route('/register', methods=['POST'])
def reg():
    global username
    if request.method == 'POST':
        username = request.form.get('name')
        CommunityChat_interactive_functions = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
        register(CommunityChat_interactive_functions, username, chain_id, my_address)
        #if(register(CommunityChat_interactive_functions, username1, chain_id, my_address) == "User already registered "):


        print(f"registered successfully as {username}")
        #session['username'] = username1  # Store the username in a session variable
        return render_template('chat.html', username=username) 
    else: 
        return 'registered done!!'
@app.route("/Comment" , methods=['POST'])
def create_comment(): 
    if request.method == 'POST':
        postId = request.form.get("post_id")
        print(postId.encode())
        content_of_comment = request.form.get("comment_content")
        CommunityChat_interactive_functions = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
        print(content_of_comment)
        Comment(CommunityChat_interactive_functions, int(postId), content_of_comment, my_address, chain_id)
        return redirect('/post')

@app.route("/Like" , methods=['POST'])
def Like_post(): 
    if request.method == 'POST':
        postId = request.form.get("post_id")
        print(postId.encode())
        CommunityChat_interactive_functions = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
        print(Like(CommunityChat_interactive_functions, int(postId), my_address, chain_id))
        return redirect('/post')


@app.route("/LikesForPost", methods= ['POST'])
def LikesForPost(): 
    if request.method == 'POST':
        postId = request.form.get("post_id")
        CommunityChat_interactive_functions = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
        Likes_Tuple = getLikes(CommunityChat_interactive_functions, int(postId))
        #print(Likes_Tuple)
        Likes= [] 
        for i in Likes_Tuple: 
            Likes.append({"username": i[2], "timestamp": return_readable_timestamp(i[3])})
        return render_template("Likes.html", len1=len(Likes) , Likes=Likes)
@app.route('/post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        what_to_send = request.form.get('post_content')
        CommunityChat_interactive_functions = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

        post(CommunityChat_interactive_functions, what_to_send, chain_id, my_address)
        #print("Post successful!")

        #username1 = session.get('username')  # Retrieve the username from the session variable
        messages = get_all_post(CommunityChat_interactive_functions)  # Extracted messages
        return render_template('chat.html', username=username, messages=messages)
    else: 
        CommunityChat_interactive_functions = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
        messages = get_all_post(CommunityChat_interactive_functions)
        #print(messages)
        return render_template('chat.html', username=username , messages=messages)


if __name__ == "__main__":
    app.run(debug=True)        