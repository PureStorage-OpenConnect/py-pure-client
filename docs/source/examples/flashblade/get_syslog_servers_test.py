# Log two test messages to each configured syslog server.
res = client.get_syslog_servers_test()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token
# See section "Common Fields" for examples
