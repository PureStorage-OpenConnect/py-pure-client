res = client.get_arrays_space()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list array space of file systems
res = client.get_arrays_space(type='file-system')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list historical array space
res = client.get_arrays_space(start_time=START_TIME,
                              end_time=END_TIME,
                              resolution=30000)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names
# See section "Common Fields" for examples
