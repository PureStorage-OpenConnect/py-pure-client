from pypureclient.flashblade.FB_2_14 import SshCertificateAuthorityPolicyPost, Reference

# create the ssh certificate authority policy with a reference to the existing certificate
certificate = Reference(name='external', resource_type='certificates')
policy_attr = SshCertificateAuthorityPolicyPost(signing_authority=certificate,
                                                static_authorized_principals=["user1", "user2"])
res = client.post_ssh_certificate_authority_policies(names=["test-policy"], policy=policy_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# create the ssh certificate authority policy with a different signing authority, also
# omitting the principals list.
public_key_by_id = Reference(id='83efe671-3265-af1e-6dd2-c9ff15533a19', resource_type='public-keys')
policy_attr_with_key = SshCertificateAuthorityPolicyPost(signing_authority=public_key_by_id)
res = client.post_ssh_certificate_authority_policies(names=['ca-policy-with-key-reference'],
                                                     policy=policy_attr_with_key)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)
