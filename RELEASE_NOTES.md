# API Changelog 2.29 vs. 2.30

## GET /array-connections/connection-key
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## POST /array-connections/connection-key
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'items/context' to the response with the '200' status


## GET /array-connections/performance/replication
-  added the new optional 'query' request parameter 'allow_errors'
-  added the new optional 'query' request parameter 'context_names'
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the optional property 'total/context' to the response with the '200' status
-  added the success response with the status '207'


## PATCH /arrays
-  added the new optional 'query' request parameter 'context_names'


## GET /audit-file-systems-policy-operations
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## GET /buckets
-  added the new optional 'query' request parameter 'workload_ids'
-  added the new optional 'query' request parameter 'workload_names'


## GET /log-targets/file-systems
-  added the optional property 'errors' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '200' status
-  added the success response with the status '207'


## PATCH /log-targets/file-systems
-  added the optional property 'items/context' to the response with the '200' status


## POST /log-targets/file-systems
-  added the optional property 'items/context' to the response with the '200' status


## DELETE /software
-  endpoint added


## GET /software
-  endpoint added


## POST /software
-  endpoint added


## GET /software-bundle
-  added the optional property 'items/bytes_downloaded' to the response with the '200' status
-  added the optional property 'items/bytes_total' to the response with the '200' status
-  added the optional property 'items/software_name' to the response with the '200' status
-  added the optional property 'items/software_version' to the response with the '200' status


## POST /software-bundle
-  added the optional property 'items/bytes_downloaded' to the response with the '200' status
-  added the optional property 'items/bytes_total' to the response with the '200' status
-  added the optional property 'items/software_name' to the response with the '200' status
-  added the optional property 'items/software_version' to the response with the '200' status


## POST /software-check
-  added the new optional 'query' request parameter 'local'


## GET /software-installation-steps
-  endpoint added


## GET /software-installations
-  endpoint added


## PATCH /software-installations
-  endpoint added


## POST /software-installations
-  endpoint added


## GET /software-versions
-  endpoint added


## DELETE /ssh-certificate-authority-policies
-  added the new optional 'query' request parameter 'context_names'


## PATCH /ssh-certificate-authority-policies
-  added the new optional 'query' request parameter 'context_names'


## POST /ssh-certificate-authority-policies
-  added the new optional 'query' request parameter 'context_names'


## GET /storage-class-tiering-policies/members
-  added the optional property 'items/context' to the response with the '200' status
-  added the optional property 'items/context' to the response with the '207' status


## GET /workloads
-  added the optional property 'items/space' to the response with the '200' status
-  added the optional property 'items/space' to the response with the '207' status


## PATCH /workloads
-  added the optional property 'items/space' to the response with the '200' status


## POST /workloads
-  added the optional property 'items/space' to the response with the '200' status


## GET /workloads/performance
-  endpoint added


## GET /workloads/space
-  endpoint added


