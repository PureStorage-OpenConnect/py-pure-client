from pypureclient.flashblade import SmbClientPolicy, SmbClientPolicyRule

# Create a client policy with a rule which allows Read (but no other) permissions and
# requires encryption for everyone.
policyname = 'client_policy_1'
policy = SmbClientPolicy()
policy.rules = [SmbClientPolicyRule(client='*',  permission='ro', encryption='required')]

res = client.post_smb_client_policies(names=[policyname], policy=policy)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See section "Common Fields" for examples
