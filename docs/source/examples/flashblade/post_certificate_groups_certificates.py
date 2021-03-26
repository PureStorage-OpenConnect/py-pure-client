# add 'posix-cert' to the 'all-trusted-certs' group
all_trusted_group = 'all-trusted-certs'
posix_cert = 'posix-cert'
res = client.post_certificate_groups_certificates(certificate_names=[posix_cert],
                                                  certificate_group_names=[all_trusted_group])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# add both 'ad-cert-2' and 'ad-cert-1' to both the 'all-trusted-certs' group and the
# 'all-ad-certs' group
ad_cert1 = 'ad-cert-1'
ad_cert2 = 'ad-cert-2'
all_ad_group = 'all-ad-certs'
res = client.post_certificate_groups_certificates(certificate_names=[ad_cert1, ad_cert2],
                                                  certificate_group_names=[all_trusted_group, all_ad_group])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: certificate_ids, certificate_group_ids
# See section "Common Fields" for examples
