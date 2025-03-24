# Apply a legal hold on a directory
res = client.post_legal_holds_held_entities(
    names=['test_legal_hold'],
    file_system_names=['test_fs'],
    paths=['/'],
    recursive=True
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Apply a legal hold on a file
res = client.post_legal_holds_held_entities(
    ids=['10314f42-020d-7080-8013-000ddt400012'],
    file_system_ids=['10314f42-020d-7080-8013-000ddt400013'],
    paths=['test_file']
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
