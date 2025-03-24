# list all audit policies
res = client.get_audit_file_systems_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

policyname = 'audit_policy_1'

# list audit policy for policy policyname
res = client.get_audit_file_systems_policies(names=[policyname])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# List audit policies specified by id.
res = client.get_audit_file_systems_policies(ids=['83efe671-3265-af1e-6dd2-c9ff155c2a18'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, filter, limit, offset, sort, continuation_token
# See section "Common Fields" for examples
