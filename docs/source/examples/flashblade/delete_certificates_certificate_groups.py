# remove 'posix-cert' from the 'all-trusted-certs' group
all_trusted_group = 'all-trusted-certs'
posix_cert = 'posix-cert'
client.delete_certificates_certificate_groups(certificate_names=[posix_cert],
                                              certificate_group_names=[all_trusted_group])

# remove both 'ad-cert-2' and 'ad-cert-1' from both the 'all-trusted-certs' group and the
# 'all-ad-certs' group
ad_cert1 = 'ad-cert-1'
ad_cert2 = 'ad-cert-2'
all_ad_group = 'all-ad-certs'
client.delete_certificates_certificate_groups(certificate_names=[ad_cert1, ad_cert2],
                                              certificate_group_names=[all_trusted_group, all_ad_group])

# Other valid fields: certificate_ids, certificate_group_ids
# See section "Common Fields" for examples
