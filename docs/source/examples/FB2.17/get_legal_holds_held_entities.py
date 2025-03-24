# Get all legal holds held entities
res = client.get_legal_holds_held_entities()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list by the legal hold name
res = client.get_legal_holds_held_entities(
    names=['test_legal_hold']
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list by filesystem names
res = client.get_legal_holds_held_entities(
    file_system_names=['test_fs']
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list by filesystem ids
res = client.get_legal_holds_held_entities(
    file_system_ids=['10314f42-020d-7080-8013-000ddt400013']
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list by legal hold ids
res = client.get_legal_holds_held_entities(
    ids=['10314f42-0120d-7080-8013-000ddt400013']
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list by filesystem names and paths
res = client.get_legal_holds_held_entities(
    file_system_names=['test_fs'],
    paths=['/']
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list by filesystem names, paths and legal hold names
res = client.get_legal_holds_held_entities(
    names=['test_legal_hold'],
    file_system_names=['test_fs'],
    paths=['/']
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: limit, continuation_token
# See section "Common Fields" for examples
