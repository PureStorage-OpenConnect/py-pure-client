from pypureclient.flashblade import Hardware

# turn visual identifier on
res = client.patch_hardware(names=['CH1.FB1'], hardware=Hardware(identify_enabled=True))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# turn visual identifier off
res = client.patch_hardware(names=['CH1.FB1'], hardware=Hardware(identify_enabled=False))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: ids
# See section "Common Fields" for examples
