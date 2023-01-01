from galaxy.jobs import JobDestination

DEFAULT_INITIAL_DESTINATION = "vgl_default"

#def initial_destination(resource_params):
#    return resource_params.get("initial_destination", None) or DEFAULT_INITIAL_DESTINATION

def resubmit_to_bigmem(resource_params):
    job_destination = JobDestination()
    job_destination['vgl_default'] = "slurm"
    # Resubmit to a valid destination.
    job_destination['resubmit'] = [dict(
        condition="any_failure",
        destination="bigmem_64cpu",
    )]
    return job_destination