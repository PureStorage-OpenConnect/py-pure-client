# delete an existing qos policy named 'my_qos_policy'
res = client.delete_qos_policies(names=['my_qos_policy'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# delete an existing qos policy using id
res = client.delete_qos_policies(ids=['635c0a0c-37ad-4f91-bad7-5224c284c2ad'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
