from pypureclient.flashblade.FB_2_17 import FleetPatch

fleet_patch = FleetPatch(name='my-new-fleet-name')

# rename an existing fleet using fleet name
res = client.patch_fleets(
    names=['my-fleet'],
    fleet=fleet_patch)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# rename an existing fleet using fleet id
res = client.patch_fleets(
    ids=['635c0a0c-37ad-4f91-bad7-5224c284c2ad'],
    fleet=fleet_patch)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
