# List all SMB open files, limit response to 10
res = client.get_file_systems_open_files(protocols=['smb'], limit=10)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get single SMB open file by open file ID
res = client.get_file_systems_open_files(protocols=['smb'], ids=['54043195528445954'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get all SMB files opened by clients with specified client IPs
res = client.get_file_systems_open_files(protocols=['smb'], client_names=['1.1.1.1', '2.2.2.2'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get all SMB files opened by clients with specified users
res = client.get_file_systems_open_files(protocols=['smb'], user_names=['0:0', '1:1'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get all SMB open file records for a specific file
res = client.get_file_systems_open_files(protocols=['smb'], file_system_names=['root'], paths=['/dir/file'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get all SMB files opened in session with specified session names
res = client.get_file_systems_open_files(protocols=['smb'], session_names=['456135-smb', '456136-smb'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, file_system_ids
# See section "Common Fields" for examples

# session_names = None,  # type: List[str]
