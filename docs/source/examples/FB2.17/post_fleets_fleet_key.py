res = client.post_fleets_fleet_key()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
