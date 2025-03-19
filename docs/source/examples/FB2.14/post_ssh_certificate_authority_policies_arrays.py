# add array member to a ssh certificate authority policy
res = client.post_ssh_certificate_authority_policies_arrays(
    member_names=["test-array"], policy_names=["test-ca-policy"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# add a member to a policy by id
res = client.post_ssh_certificate_authority_policies_arrays(
    member_ids=["10314f42-020d-7080-8013-000ddt400090"], policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
