# create groups to use for all certificates, as well as for all AD certificates
group_for_all_certs = 'all-trusted-certs'
group_for_active_directory_certs = 'all-ad-certs'
res = client.post_certificate_groups(names=[group_for_all_certs,
                                     group_for_active_directory_certs])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
