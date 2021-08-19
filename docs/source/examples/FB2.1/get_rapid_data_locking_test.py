# Test Rapid Data Locking
res = client.get_rapid_data_locking_test()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
