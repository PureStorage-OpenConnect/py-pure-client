from pypureclient.flashblade import Array, Reference

# Set the banner to "example-banner"
# Rename the array to "example-name"
# Set the NTP server to "0.example.ntp.server"
# Change the array time zone to "America/Los_Angeles"
# Change the default TLS policy that applies to inbound TLS on all vips without
# a more specific policy that applies to them
new_default_tls_policy = Reference(name='my-strong-tls-policy')
array_settings = Array(banner="example-banner",
                       name="example-name",
                       ntp_servers=["0.example.ntp.server"],
                       time_zone="America/Los_Angeles",
                       default_inbound_tls_policy=new_default_tls_policy)
res = client.patch_arrays(array=array_settings)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
