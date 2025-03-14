res = client.get_arrays_space_storage_classes()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list storage class space of S500X-S storage class
res = client.get_arrays_space_storage_classes(storage_class_names='S500X-S')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list historical storage class space
res = client.get_arrays_space_storage_classes(start_time=START_TIME,
                              end_time=END_TIME,
                              resolution=30000)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, filter, limit, offset, sort, total_only
# See section "Common Fields" for examples
