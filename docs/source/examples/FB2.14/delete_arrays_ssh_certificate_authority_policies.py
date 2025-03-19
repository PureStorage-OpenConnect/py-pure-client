# remove an array member from a policy
res = client.delete_arrays_ssh_certificate_authority_policies(
    member_names=["test-array"], policy_names=["test-ca-policy"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# add a member to a policy by id
client.delete_arrays_ssh_certificate_authority_policies(
    member_ids=["10314f42-020d-7080-8013-000ddt400090"], policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
