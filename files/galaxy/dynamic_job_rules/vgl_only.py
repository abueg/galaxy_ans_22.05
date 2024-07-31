from galaxy.jobs import JobDestination
from galaxy.jobs.mapper import JobMappingException
import os
VGL_EMAILS = ["admin@admin.org","njain@rockefeller.edu","labueg@rockefeller.edu","cjohnson02@rockefeller.edu","ofedrigo@rockefeller.edu","ptraore@rockefeller.edu","sburmeiste@rockefeller.edu","gformenti@rockefeller.edu"]

def vgl_only(user_email):
    if user_email in VGL_EMAILS:
        return JobDestination(id="vgl_only", runner="local")
    else:
        return JobMappingException("This tool is for VGL staff only.")
