res = client.post_fleets(names=["my-fleet"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
