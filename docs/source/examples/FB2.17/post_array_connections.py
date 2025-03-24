from pypureclient.flashblade import ArrayConnectionPost

# connect to an array with specified hostname, using a provided connection key
hostname = "https://my.array.com"
connection_key = "6207d123-d123-0b5c-5fa1-95fabc5c7123"
myAC = ArrayConnectionPost(management_address=hostname, connection_key=connection_key)

# post the array connection object on the array we're connection from
res = client.post_array_connections(array_connection=myAC)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# connect to an array by ip address and specifying replication addresses, using a provided connection key
mgmt_addr = "10.202.101.78"
repl_addr = ["10.202.101.70"]
connection_key = "6207d123-d123-0b5c-5fa1-95fabc5c7123"
myAC = ArrayConnectionPost(management_address=mgmt_addr, replication_addresses=repl_addr, connection_key=connection_key)

# post the array connection object on the array we're connection from
res = client.post_array_connections(array_connection=myAC)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See section "Common Fields" for examples