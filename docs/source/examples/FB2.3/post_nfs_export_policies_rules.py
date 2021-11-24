from pypureclient.flashblade import NfsExportPolicyRule

policyname = "export_policy_1"

# Create a new export policy rule in the export policy named 'export_policy_1'
res = client.post_nfs_export_policies_rules(rule=NfsExportPolicyRule(client='10.20.30.1',
                                                                     permission='rw'),
                                            policy_names=[policyname])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Create a new export policy rule in the export policy named 'export_policy_1'
# and insert it at index 1. (indexes are 1 based.)
res = client.post_nfs_export_policies_rules(rule=NfsExportPolicyRule(client='10.20.30.2',
                                                                     permission='rw',
                                                                     index=1),
                                            policy_names=[policyname])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Create a new export policy rule in the export policy named 'export_policy_1'
# and insert it before the rule named 'export_policy_1.1'.
res = client.post_nfs_export_policies_rules(rule=NfsExportPolicyRule(client='10.20.30.3',
                                                                     permission='rw'),
                                            policy_names=[policyname],
                                            before_rule_name='export_policy_1.1')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Create a new export policy rule in the export policy named 'export_policy_1'
# and insert it before the rule with id '10314f42-020d-7080-8013-000ddt400090'.
res = client.post_nfs_export_policies_rules(rule=NfsExportPolicyRule(client='10.20.30.4',
                                                                     permission='rw'),
                                            policy_names=[policyname],
                                            before_rule_id='10314f42-020d-7080-8013-000ddt400090')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Create a new export policy rule in the export policy named 'export_policy_1'
# specifying a subnet mask for the client, readwrite permissions, and rootsquash to anonuid=400
# and anongid=500.
res = client.post_nfs_export_policies_rules(rule=NfsExportPolicyRule(client='10.20.0.0/24',
                                                                     permission='rw',
                                                                     access='root-squash',
                                                                     anonuid='400',
                                                                     anongid='500'),
                                            policy_names=[policyname])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))


# Create a new export policy rule in the export policy named 'export_policy_1'
# specifying a netgroup for the client, and the atime, fileid_32bit, secure, and security attributes.
res = client.post_nfs_export_policies_rules(rule=NfsExportPolicyRule(client='@dev_group',
                                                                     atime=True,
                                                                     secure=True,
                                                                     security=['sys'],
                                                                     anongid='500'),
                                            policy_names=[policyname])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = list(res.items)
    print(res_items)
    policy_version = res_items[0].policy_version

# Create a new export policy ensuring that the policy has not been changed since the last rule was added.
res = client.post_nfs_export_policies_rules(rule=NfsExportPolicyRule(client='*'),
                                            policy_names=[policyname],
                                            versions=[policy_version])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: policy_ids
# See section "Common Fields" for examples
