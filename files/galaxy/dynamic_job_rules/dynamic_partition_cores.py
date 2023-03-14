import logging
from galaxy.jobs import JobDestination
from galaxy.jobs.mapper import JobMappingException

log = logging.getLogger(__name__)

DESTINATION_IDS = {
    1 : 'vgl',
    2 : 'bigmem'
}
FAILURE_MESSAGE = 'This tool could not be run because of a misconfiguration in the Galaxy job running system, please report this error (error from my_rules.py)'


def dynamic_partition_cores(app, tool, job, user_email):
    
    destination = None
    destination_id = 'vgl_default'

    # build the param dictionary
    param_dict = job.get_param_values(app)

    if param_dict.get('__job_resource', {}).get('__job_resource__select') != 'yes':
        log.info("Job resource parameters not selected, returning default destination")
        return destination_id

    # handle job resource parameters
    try:
        # validate params
        partition = int(param_dict['__job_resource']['partition'])
        cores = int(param_dict['__job_resource']['cores'])
        destination_id = DESTINATION_IDS[partition]
        destination = app.job_config.get_destination(destination_id)
#        if 'nativeSpecification' not in destination.params:
#            destination.params['nativeSpecification'] = ''
        destination.params['nativeSpecification'] += ' --partition=' + destination_id
        destination.params['nativeSpecification'] += ' --cpus-per-task=' + str(cores)
    except:
        # resource param selector not sent with tool form, job_conf.xml misconfigured
        log.warning('(%s) error, keys were: %s', job.id, param_dict.keys())
        raise JobMappingException(FAILURE_MESSAGE)

    log.info('returning destination: %s', destination_id)
    log.info('native specification: %s', destination.params.get('nativeSpecification'))
    return destination or destination_id
