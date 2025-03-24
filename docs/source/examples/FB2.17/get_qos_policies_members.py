# list all qos policies and their managed object members
res = client.get_qos_policies_members()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list qos policies attached to a set of members using their names
res = client.get_qos_policies_members(member_names=["my_fs_1", "my_fs_2"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list qos policies attached to a set of members using their ids
res = client.get_qos_policies_members(member_ids=["635c0a0c-37ad-4f91-acq0-5224c284c2ad",
                                                  "dc227307-c29a-4868-b5da-7f249777f222"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list members associated with a set of qos policies using their names
res = client.get_qos_policies_members(policy_names=["my_qos_policy_1", "my_qos_policy_2"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list members associated with a set of qos policies using their ids
res = client.get_qos_policies_members(policy_ids=["18f91fa7-840e-453a-9313-eed2914dea3a",
                                                  "d9b82931-0e58-4834-a59f-d2d751bba927"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
