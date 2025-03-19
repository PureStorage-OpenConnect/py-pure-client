from pypureclient.flashblade.FB_2_14 import AuditFileSystemsPoliciesPatch, Reference

policyname = 'audit_policy_1'

# Disable the policy.
policy = AuditFileSystemsPoliciesPatch(enabled=False)
res = client.patch_audit_file_systems_policies(names=[policyname], policy=policy) # need to change body name to policy in PURest
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))


# add one log target and remove old log target
policy = AuditFileSystemsPoliciesPatch(enabled=True)
policy.add_log_targets = [Reference(name='syslog2')]
policy.remove_log_targets = [Reference(name='syslog1')]
res = client.patch_audit_file_systems_policies(names=[policyname], policy=policy) # need to change body name to policy in PURest
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: ids
# See section "Common Fields" for examples
