# API Changelog 2.58 vs. 2.59

## DELETE /certificate-groups
-  added the new optional 'query' request parameter 'context_names'


## GET /certificate-groups
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## POST /certificate-groups
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## DELETE /certificate-groups/certificates
-  added the new optional 'query' request parameter 'context_names'


## GET /certificate-groups/certificates
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## POST /certificate-groups/certificates
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## GET /certificate-groups/uses
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## DELETE /certificates
-  added the new optional 'query' request parameter 'context_names'


## GET /certificates
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## PATCH /certificates
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## POST /certificates
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## DELETE /certificates/certificate-groups
-  added the new optional 'query' request parameter 'context_names'


## GET /certificates/certificate-groups
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## POST /certificates/certificate-groups
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## POST /certificates/certificate-signing-requests
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## GET /certificates/uses
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## GET /host-groups
-  added the optional property 'items/priority' to the response with the '200' status
-  added the optional property 'items/priority' to the response with the '207' status
-  added the optional property 'items/priority_adjustment' to the response with the '200' status
-  added the optional property 'items/priority_adjustment' to the response with the '207' status
-  added the optional property 'items/qos/bandwidth_floor' to the response with the '200' status
-  added the optional property 'items/qos/bandwidth_floor' to the response with the '207' status
-  added the optional property 'items/qos/iops_floor' to the response with the '200' status
-  added the optional property 'items/qos/iops_floor' to the response with the '207' status


## PATCH /host-groups
-  added the new optional request property 'priority_adjustment'
-  added the new optional request property 'qos/bandwidth_floor'
-  added the new optional request property 'qos/iops_floor'
-  added the optional property 'items/priority' to the response with the '200' status
-  added the optional property 'items/priority_adjustment' to the response with the '200' status
-  added the optional property 'items/qos/bandwidth_floor' to the response with the '200' status
-  added the optional property 'items/qos/iops_floor' to the response with the '200' status


## POST /host-groups
-  added the new optional request property 'priority_adjustment'
-  added the new optional request property 'qos/bandwidth_floor'
-  added the new optional request property 'qos/iops_floor'
-  added the optional property 'items/priority' to the response with the '200' status
-  added the optional property 'items/priority_adjustment' to the response with the '200' status
-  added the optional property 'items/qos/bandwidth_floor' to the response with the '200' status
-  added the optional property 'items/qos/iops_floor' to the response with the '200' status


## GET /host-groups/qos
-  added the optional property 'items/bandwidth_floor' to the response with the '200' status
-  added the optional property 'items/bandwidth_floor' to the response with the '207' status
-  added the optional property 'items/iops_floor' to the response with the '200' status
-  added the optional property 'items/iops_floor' to the response with the '207' status
-  added the optional property 'items/priority' to the response with the '200' status
-  added the optional property 'items/priority' to the response with the '207' status
-  added the optional property 'items/priority_adjustment_value' to the response with the '200' status
-  added the optional property 'items/priority_adjustment_value' to the response with the '207' status


## GET /hosts
-  added the optional property 'items/priority' to the response with the '200' status
-  added the optional property 'items/priority' to the response with the '207' status
-  added the optional property 'items/priority_adjustment' to the response with the '200' status
-  added the optional property 'items/priority_adjustment' to the response with the '207' status
-  added the optional property 'items/qos/bandwidth_floor' to the response with the '200' status
-  added the optional property 'items/qos/bandwidth_floor' to the response with the '207' status
-  added the optional property 'items/qos/iops_floor' to the response with the '200' status
-  added the optional property 'items/qos/iops_floor' to the response with the '207' status


## PATCH /hosts
-  added the new optional request property 'priority_adjustment'
-  added the new optional request property 'qos/bandwidth_floor'
-  added the new optional request property 'qos/iops_floor'
-  added the optional property 'items/priority' to the response with the '200' status
-  added the optional property 'items/priority_adjustment' to the response with the '200' status
-  added the optional property 'items/qos/bandwidth_floor' to the response with the '200' status
-  added the optional property 'items/qos/iops_floor' to the response with the '200' status


## POST /hosts
-  added the new optional request property 'priority_adjustment'
-  added the new optional request property 'qos/bandwidth_floor'
-  added the new optional request property 'qos/iops_floor'
-  added the optional property 'items/priority' to the response with the '200' status
-  added the optional property 'items/priority_adjustment' to the response with the '200' status
-  added the optional property 'items/qos/bandwidth_floor' to the response with the '200' status
-  added the optional property 'items/qos/iops_floor' to the response with the '200' status


## GET /hosts/qos
-  added the optional property 'items/bandwidth_floor' to the response with the '200' status
-  added the optional property 'items/bandwidth_floor' to the response with the '207' status
-  added the optional property 'items/iops_floor' to the response with the '200' status
-  added the optional property 'items/iops_floor' to the response with the '207' status
-  added the optional property 'items/priority' to the response with the '200' status
-  added the optional property 'items/priority' to the response with the '207' status
-  added the optional property 'items/priority_adjustment_value' to the response with the '200' status
-  added the optional property 'items/priority_adjustment_value' to the response with the '207' status


## DELETE /kmip
-  added the new optional 'query' request parameter 'context_names'


## GET /kmip
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## PATCH /kmip
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## POST /kmip
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## GET /kmip/test
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the new optional 'query' request parameter 'continuation_token'
-  added the new optional 'query' request parameter 'limit'
-  added the new optional 'query' request parameter 'offset'
-  added the new optional 'query' request parameter 'total_item_count'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## DELETE /vchost-connections
-  added the new optional 'query' request parameter 'context_names'


## GET /vchost-connections
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## POST /vchost-connections
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## DELETE /vchosts
-  added the new optional 'query' request parameter 'context_names'


## GET /vchosts
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## PATCH /vchosts
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## POST /vchosts
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## DELETE /vchosts/certificates
-  added the new optional 'query' request parameter 'context_names'


## GET /vchosts/certificates
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## PATCH /vchosts/certificates
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## POST /vchosts/certificates
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## DELETE /vchosts/endpoints
-  added the new optional 'query' request parameter 'context_names'


## GET /vchosts/endpoints
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## PATCH /vchosts/endpoints
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## POST /vchosts/endpoints
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## GET /virtual-machine-snapshots
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## GET /virtual-machine-volume-snapshots
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## GET /virtual-machines
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## PATCH /virtual-machines
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## POST /virtual-machines
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## GET /volume-groups
-  added the optional property 'items/priority' to the response with the '200' status
-  added the optional property 'items/priority' to the response with the '207' status
-  added the optional property 'total/priority' to the response with the '200' status
-  added the optional property 'total/priority' to the response with the '207' status


## PATCH /volume-groups
- :warning: the 'priority_adjustment/priority_adjustment_value' request property type/format changed from 'integer'/'int32' to ''/''
-  added '#/components/schemas/_limit_unset_value, subschema #1' to the 'priority_adjustment/priority_adjustment_value' request property 'oneOf' list
-  added the optional property 'items/priority' to the response with the '200' status


## POST /volume-groups
-  added the optional property 'items/priority' to the response with the '200' status


## GET /volume-groups/qos
-  added the optional property 'items/priority' to the response with the '200' status
-  added the optional property 'items/priority' to the response with the '207' status
-  added the optional property 'items/priority_adjustment_value' to the response with the '200' status
-  added the optional property 'items/priority_adjustment_value' to the response with the '207' status


## PATCH /volumes
- :warning: the 'priority_adjustment/priority_adjustment_value' request property type/format changed from 'integer'/'int32' to ''/''
-  added '#/components/schemas/_limit_unset_value, subschema #1' to the 'priority_adjustment/priority_adjustment_value' request property 'oneOf' list


## GET /volumes/qos
-  added the optional property 'items/priority' to the response with the '200' status
-  added the optional property 'items/priority' to the response with the '207' status
-  added the optional property 'items/priority_adjustment_value' to the response with the '200' status
-  added the optional property 'items/priority_adjustment_value' to the response with the '207' status


