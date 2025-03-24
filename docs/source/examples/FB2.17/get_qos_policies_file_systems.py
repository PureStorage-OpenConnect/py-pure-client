# list all qos policies and their file system members
res = client.get_qos_policies_file_systems()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list qos policies attached to a set of file systems using their names
res = client.get_qos_policies_file_systems(member_names=["my_fs_1", "my_fs_2"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list qos policies attached to a set of file systems using their ids
res = client.get_qos_policies_file_systems(member_ids=["ac46ad53-de6e-432b-a543-64838dddd100",
                                                       "bdfab698-7213-4902-8f93-346d48fa8daa"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list file systems associated with a set of qos policies using their names
res = client.get_qos_policies_file_systems(policy_names=["my_qos_policy_1", "my_qos_policy_2"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list file systems associated with a set of qos policies using their ids
res = client.get_qos_policies_file_systems(policy_ids=["fe0534ab-045e-4627-aeb6-3f92591a34dd",
                                                       "f170146e-72f0-4c12-b909-33ce74534685"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
