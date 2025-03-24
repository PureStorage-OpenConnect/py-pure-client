from pypureclient.flashblade.FB_2_17 import QosPolicy

# patch an existing QoS policy named 'my_qos_policy' with the desired settings
# name field can be used in patch operation to rename the policy
QOS_POLICY_NAME = 'my_qos_policy'
QOS_POLICY_RENAME = 'my_qos_policy_renamed'
qos_policy = QosPolicy(
    name=QOS_POLICY_RENAME,
    max_total_bytes_per_sec=1073741824,
    max_total_ops_per_sec=24000,
    enabled=False
)

# patch using name
res = client.patch_qos_policies(names=[QOS_POLICY_NAME], policy=qos_policy)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# patch using id
res = client.patch_qos_policies(ids=['635c0a0c-37ad-4f91-bad7-5224c284c2ad'], policy=qos_policy)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
