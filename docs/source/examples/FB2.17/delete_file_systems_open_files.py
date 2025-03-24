# Close open files with specified IDs
res = client.delete_file_systems_open_files(ids=['54043195528445954', '54043195528445955'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
