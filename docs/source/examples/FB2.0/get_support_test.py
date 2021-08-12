# Test phonehome
res = client.get_support_test(test_type='phonehome')
# print the results
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Test remote assist
res = client.get_support_test(test_type='remote-assist')
# print the results
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Test both
res = client.get_support_test()
# print the results
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: filter, sort
# See section "Common Fields" for examples
