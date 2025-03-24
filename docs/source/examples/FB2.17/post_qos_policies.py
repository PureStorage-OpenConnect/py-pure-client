from pypureclient.flashblade.FB_2_17 import QosPolicy

# create a QoS policy object with the desired settings
# note that name field is used for rename operation and NOT specified during creation
# the policy is enabled by default
qos_policy = QosPolicy(
    max_total_bytes_per_sec=1073741824,
    max_total_ops_per_sec=12000
)
QOS_POLICY_NAME = 'my_qos_policy'
res = client.post_qos_policies(names=[QOS_POLICY_NAME], policy=qos_policy)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
