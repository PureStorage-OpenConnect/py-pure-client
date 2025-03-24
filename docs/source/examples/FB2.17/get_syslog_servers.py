# List all configured syslog servers
res = client.get_syslog_servers()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# List first two syslog servers beginning with 'main_syslog'. Use default sorting.
res = client.get_syslog_servers(limit=2, names=["main_syslog"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))    # List the first syslog server when sorting by name.
res = client.get_syslog_servers(limit=1, sort="name")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# List all syslog servers using TCP connections
res = client.get_syslog_servers(filter='uri=\'tcp*\'')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, continuation_token, filter, ids, offset
# See section "Common Fields" for examples
