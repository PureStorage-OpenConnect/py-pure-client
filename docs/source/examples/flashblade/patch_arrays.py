from pypureclient.flashblade import Array

# Set the banner to "example-banner"
# Rename the array to "example-name"
# Set the NTP server to "0.example.ntp.server"
# Change the array time zone to "America/Los_Angeles"
array_settings = Array(banner="example-banner",
                       name="example-name",
                       ntp_servers=["0.example.ntp.server"],
                       time_zone="America/Los_Angeles")
res = client.patch_arrays(array=array_settings)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
