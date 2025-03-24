# Release a legal hold from a directory
res = client.patch_legal_holds_held_entities(
    names=['test_legal_hold'],
    file_system_names=['test_fs'],
    paths=['/'],
    recursive=True,
    released=True
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Release a legal hold from a file
res = client.patch_legal_holds_held_entities(
    ids=['10314f42-020d-7080-8013-000ddt400012'],
    file_system_ids=['10314f42-020d-7080-8013-000ddt400013'],
    paths=['test_file'],
    released=True
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
