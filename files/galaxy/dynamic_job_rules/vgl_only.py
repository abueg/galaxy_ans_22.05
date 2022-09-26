from galaxy.jobs import JobDestination
from galaxy.jobs.mapper import JobMappingException
import os
VGL_EMAILS = ["admin@admin.org"]

def vgl_only(user_email):
    if user_email in VGL_EMAILS:
        return JobDestination(id="vgl_only", runner="local")
    else:
        return JobMappingException("This tool is for VGL staff only.")
