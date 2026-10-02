# API Changelog 2.28 vs. 2.29

## GET /arrays/defaults
-  endpoint added


## PATCH /arrays/defaults
-  endpoint added


## GET /arrays/ssh-certificate-authority-policies
-  added the success response with the status '207'


## GET /arrays/telemetry-metrics-policies
-  endpoint added


## GET /bucket-replica-links
-  added the optional property 'items/version_deletes_enabled' to the response with the '200' status
-  added the optional property 'items/version_deletes_enabled' to the response with the '207' status
-  added the optional property 'total/version_deletes_enabled' to the response with the '200' status
-  added the optional property 'total/version_deletes_enabled' to the response with the '207' status


## PATCH /bucket-replica-links
-  added the new optional request property 'version_deletes_enabled'
-  added the optional property 'items/version_deletes_enabled' to the response with the '200' status
-  added the optional property 'total/version_deletes_enabled' to the response with the '200' status


## POST /bucket-replica-links
-  added the new optional request property 'version_deletes_enabled'
-  added the optional property 'items/version_deletes_enabled' to the response with the '200' status
-  added the optional property 'total/version_deletes_enabled' to the response with the '200' status


## GET /buckets
-  added the optional property 'items/node_group' to the response with the '200' status
-  added the optional property 'items/node_group' to the response with the '207' status
-  added the optional property 'items/workload' to the response with the '200' status
-  added the optional property 'items/workload' to the response with the '207' status
-  added the optional property 'total/node_group' to the response with the '200' status
-  added the optional property 'total/node_group' to the response with the '207' status
-  added the optional property 'total/workload' to the response with the '200' status
-  added the optional property 'total/workload' to the response with the '207' status


## PATCH /buckets
-  added the new optional request property 'workload'
-  added the optional property 'items/node_group' to the response with the '200' status
-  added the optional property 'items/workload' to the response with the '200' status


## POST /buckets
-  added the new optional request property 'node_group'
-  added the new optional request property 'workload'
-  the 'query' request parameter 'names' became optional
-  added the optional property 'items/node_group' to the response with the '200' status
-  added the optional property 'items/workload' to the response with the '200' status


## GET /buckets/lifecycle-policies
-  endpoint added


## PATCH /buckets/lifecycle-policies
-  endpoint added


## DELETE /buckets/lifecycle-policies/rules
-  endpoint added


## GET /buckets/lifecycle-policies/rules
-  endpoint added


## PATCH /buckets/lifecycle-policies/rules
-  endpoint added


## POST /buckets/lifecycle-policies/rules
-  endpoint added


## GET /lifecycle-rules
-  added the optional property 'items/keep_previous_versions_count' to the response with the '200' status
-  added the optional property 'items/keep_previous_versions_count' to the response with the '207' status
-  added the optional property 'items/tags' to the response with the '200' status
-  added the optional property 'items/tags' to the response with the '207' status


## PATCH /lifecycle-rules
-  added the optional property 'items/keep_previous_versions_count' to the response with the '200' status
-  added the optional property 'items/tags' to the response with the '200' status


## POST /lifecycle-rules
-  added the optional property 'items/keep_previous_versions_count' to the response with the '200' status
-  added the optional property 'items/tags' to the response with the '200' status


## GET /network-interfaces/network-connection-statistics
-  added the new optional 'query' request parameter 'local_address'
-  added the new optional 'query' request parameter 'remote_address'


## GET /presets/workload
-  added the optional property 'items/bucket_configurations' to the response with the '200' status
-  added the optional property 'items/lifecycle_configurations' to the response with the '200' status


## PATCH /presets/workload
-  added the optional property 'items/bucket_configurations' to the response with the '200' status
-  added the optional property 'items/lifecycle_configurations' to the response with the '200' status


## POST /presets/workload
-  added the new optional request property 'bucket_configurations'
-  added the new optional request property 'lifecycle_configurations'
-  added the optional property 'items/bucket_configurations' to the response with the '200' status
-  added the optional property 'items/lifecycle_configurations' to the response with the '200' status


## PUT /presets/workload
-  added the new optional request property 'bucket_configurations'
-  added the new optional request property 'lifecycle_configurations'
-  added the optional property 'items/bucket_configurations' to the response with the '200' status
-  added the optional property 'items/lifecycle_configurations' to the response with the '200' status


## POST /software-patches
-  added the new optional 'query' request parameter 'local'


## GET /telemetry-metrics
-  endpoint added


## GET /telemetry-metrics-collections
-  endpoint added


## GET /telemetry-metrics-collections/metrics
-  endpoint added


## DELETE /telemetry-metrics-policies
-  endpoint added


## GET /telemetry-metrics-policies
-  endpoint added


## PATCH /telemetry-metrics-policies
-  endpoint added


## POST /telemetry-metrics-policies
-  endpoint added


## GET /telemetry-metrics-policies/arrays
-  endpoint added


## GET /telemetry-metrics-policies/members
-  endpoint added


## DELETE /telemetry-metrics-policies/rules
-  endpoint added


## GET /telemetry-metrics-policies/rules
-  endpoint added


## PATCH /telemetry-metrics-policies/rules
-  endpoint added


## POST /telemetry-metrics-policies/rules
-  endpoint added


## DELETE /telemetry-targets
-  endpoint added


## GET /telemetry-targets
-  endpoint added


## PATCH /telemetry-targets
-  endpoint added


## POST /telemetry-targets
-  endpoint added


## GET /telemetry-targets/test
-  endpoint added


## GET /worm-data-policies
-  added the optional property 'items/autocommit_config' to the response with the '200' status
-  added the optional property 'items/autocommit_config' to the response with the '207' status
-  added the optional property 'items/commit_mode' to the response with the '200' status
-  added the optional property 'items/commit_mode' to the response with the '207' status


## PATCH /worm-data-policies
-  added the new optional request property 'autocommit_config'
-  added the new optional request property 'commit_mode'
-  added the optional property 'items/autocommit_config' to the response with the '200' status
-  added the optional property 'items/commit_mode' to the response with the '200' status


## POST /worm-data-policies
-  added the new optional request property 'autocommit_config'
-  added the new optional request property 'commit_mode'
-  added the optional property 'items/autocommit_config' to the response with the '200' status
-  added the optional property 'items/commit_mode' to the response with the '200' status


