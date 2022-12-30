from galaxy.jobs import JobDestination

DEFAULT_INITIAL_DESTINATION = "dynamic_partition_cores"

def initial_destination(resource_params):
    return resource_params.get("initial_destination", None) or DEFAULT_INITIAL_DESTINATION

def resubmit_to_bigmem(resource_params):
    job_destination = JobDestination()
#    job_destination['dynamic_parition_cores'] = "dynamic"
    # Resubmit to a valid destination.
    job_destination['resubmit'] = [dict(
        condition="any_failure",
        destination="bigmem_64cpu",
    )]
    return job_destination