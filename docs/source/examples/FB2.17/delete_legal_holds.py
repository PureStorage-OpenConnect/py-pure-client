# delete a legal hold by name
res = client.delete_legal_holds(names=['test_legal_hold'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# delete a legal hold by id
res = client.delete_legal_holds(ids=['10314f42-020d-7080-8013-000ddt400013'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
