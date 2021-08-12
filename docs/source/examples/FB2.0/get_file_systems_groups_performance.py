# list performance for all groups
res = client.get_file_systems_groups_performance(file_system_names=["fs1"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list performance for one group
res = client.get_file_systems_groups_performance(file_system_names=["fs1"],
                                                 gids=[100])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list performance for one group by filesystem id
res = client.get_file_systems_groups_performance(file_system_ids=["10314f42-020d-7080-8013-000ddt400090"],
                                                 group_names=["group1"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list performance by name
res = client.get_file_systems_groups_performance(names=["fs1/100"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: filter, limit, sort, total_only
# See section "Common Fields" for examples
