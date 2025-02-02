#!/usr/bin/env python3
import os, os.path as op
import json
import subprocess as sp
import copy
import shutil
import glob
import logging

import flywheel
from util import gear_preliminaries
from util.args import mri_convert, quick_NAT


if __name__ == '__main__':
    # Get the Gear Context
    context = flywheel.GearContext()

    context.gear_dict = {}
    context.config['dry-run'] = False
    gear_preliminaries.initialize_gear(context)
    context.log_config()

    # Utilize FreeSurfer license from config or project metadata
    try:
        gear_preliminaries.set_freesurfer_license(context)
    except Exception as e:
        context.log.exception(e)
        context.log.fatal(
            'A valid FreeSurfer license must be present to run.' + \
            'Please check your configuration and try again.'
        )
        os.sys.exit(1)

    # Validate gear configuration against gear manifest
    try:
        gear_preliminaries.validate_config_against_manifest(context)
    except Exception as e:
        context.log.exception(e)
        context.log.fatal(
            'Please make the prescribed corrections and try again.'
        )
        os.sys.exit(1)

    # Build, Validate, and execute mri_convert Parameters 
    try:
        mri_convert.build(context)
        mri_convert.validate(context)
        mri_convert.execute(context)

    except Exception as e:
        context.log.fatal(e,)
        context.log.fatal(
            'Error executing mri_convert.',
        )
        os.sys.exit(1)
    
    # Prepare and run quickNAT Bulk Evaluation Routine
    try:
        quick_NAT.build(context)
        quick_NAT.validate(context)
        quick_NAT.exec(context)
    except Exception as e:
        context.log.exception(e)
        context.log.fatal('Error evaluating quickNAT pytorch!!!')
        os.sys.exit(1)

    context.log.info("quickNAT completed Successfully!")
    os.sys.exit(0)