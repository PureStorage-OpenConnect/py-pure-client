# Rotate the external RDL key
res = client.post_rapid_data_locking_rotate()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
