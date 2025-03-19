from pypureclient.flashblade.FB_2_14 import SshCertificateAuthorityPolicy, ReferenceWritable


certificate = ReferenceWritable(name='external', resource_type='certificates')
policy_attr = SshCertificateAuthorityPolicy(signing_authority=certificate,
                                            static_authorized_principals=["user1", "user2"])
res = client.patch_ssh_certificate_authority_policies(names=["test-policy"], policy=policy_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

public_key_by_id = ReferenceWritable(id='83efe671-3265-af1e-6dd2-c9ff15533a19', resource_type='public-keys')
policy_attr = SshCertificateAuthorityPolicy(signing_authority=public_key_by_id,
                                            static_authorized_principals=[])
# update the policy with id '83efe671-3265-af1e-6dd2-c9ff155c2a18'
res = client.patch_ssh_certificate_authority_policies(ids=['83efe671-3265-af1e-6dd2-c9ff155c2a18'],
                                                      policy=policy_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)

# Other valid fields: ids
# See section "Common Fields" for examples
