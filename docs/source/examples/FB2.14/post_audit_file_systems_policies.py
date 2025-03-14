from pypureclient.flashblade.FB_2_14 import AuditFileSystemsPolicy, Reference

# Create an audit policy with a syslog target named 'syslog1'
policyname = 'audit_policy_1'
policy = AuditFileSystemsPolicy()
policy.log_targets = [Reference(name='syslog1')]

res = client.post_audit_file_systems_policies(names=[policyname], policy=policy)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
