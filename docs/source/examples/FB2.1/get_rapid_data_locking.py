# List Rapid Data Locking configuration
res = client.get_rapid_data_locking()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
