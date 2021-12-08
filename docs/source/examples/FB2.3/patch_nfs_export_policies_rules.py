from pypureclient.flashblade import NfsExportPolicyRule

rulename = 'export_policy_1.2'

# Patch export policy rule 'export_policy_1.2' in the export policy named 'export_policy_1'
res = client.patch_nfs_export_policies_rules(names=[rulename],
                                             rule=NfsExportPolicyRule(permission='ro'))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Move an export policy rule in the rules list.
# to index 1. (indexes are 1 based.)
res = client.patch_nfs_export_policies_rules(names=[rulename],
                                             rule=NfsExportPolicyRule(index=1))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Move an exported rule before the rule named 'export_policy_1.1'.
res = client.patch_nfs_export_policies_rules(names=[rulename],
                                             rule=NfsExportPolicyRule(),
                                             before_rule_name='export_policy_1.1')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Move an export rule before the rule with id '38e24e2d-9e24-46c3-9701-52a7d97a7343'.
res = client.patch_nfs_export_policies_rules(names=[rulename],
                                             rule=NfsExportPolicyRule(),
                                             before_rule_id='38e24e2d-9e24-46c3-9701-52a7d97a7343')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Patch an existing rule specifying the client, readwrite permissions, rootsquash, anonuid,
# anongid, atime, fileid_32bit, secure and security attributes.
res = client.patch_nfs_export_policies_rules(names=[rulename],
                                             rule=NfsExportPolicyRule(client='10.20.0.0/24',
                                                                      permission='rw',
                                                                      access='root-squash',
                                                                      anonuid='400',
                                                                      anongid='500',
                                                                      atime=True,
                                                                      secure=True,
                                                                      security=['sys']))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = list(res.items)
    print(res_items)
    policy_version = res_items[0].policy_version

# Patch an existing rule while ensuring that the policy has not been changed since the last patch.
res = client.patch_nfs_export_policies_rules(names=[rulename],
                                             rule=NfsExportPolicyRule(permission='ro'),
                                             versions=[policy_version])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: ids
# See section "Common Fields" for examples
