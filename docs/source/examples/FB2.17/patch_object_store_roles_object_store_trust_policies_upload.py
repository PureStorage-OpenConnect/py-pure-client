# upload trust policy by object store role id
body = {
    "Version": "2012-10-07",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam:::saml-provider/ADFS"
            },
            "Action": "sts:AssumeRoleWithSAML",
            "Condition": {
                "StringEquals": {
                    "SAML:aud": "https://signin.aws.amazon.com/saml"
                }
            }
        }
    ]
}
res = client.patch_object_store_roles_object_store_trust_policies_upload(role_ids=["f8b3b3b3-3b3b-3b3b-3b3b-3b3b3b3b3b3b"], policy_document=body)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(res.items)
# upload trust policy by object store role name
res = client.patch_object_store_roles_object_store_trust_policies_upload(role_names=["acc1/myobjrole"], policy_document=body)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(res.items)
# upload trust policy by trust policy name
res = client.patch_object_store_roles_object_store_trust_policies_upload(names=["acc1/myobjrole/trust-policy"], policy_document=body)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(res.items)

# Other valid fields: context_names
# See section "Common Fields" for examples
