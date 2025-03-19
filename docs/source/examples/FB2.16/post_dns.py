from pypureclient.flashblade import DnsPost, Reference

# post the dns configuration object mydns on the array
attr = DnsPost(domain="example-domain.com", nameservers=['126.24.5.1', '126.24.5.2'])
res = client.post_dns(names=["mydns"], dns=attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: references
# See section "Common Fields" for examples
