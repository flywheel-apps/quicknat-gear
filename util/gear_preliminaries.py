import json
from zipfile import ZipFile
import re
import logging
import os, os.path as op
import psutil
import torch
from .custom_logger import get_custom_logger

log = logging.getLogger(__name__)

def initialize_gear(context):
    """
    Used to initialize the gear context 'gear_dict' dictionary with objects that 
    are used by all gears.
    Environment Variables
    Manifest
    Logging
    dry-run
    """
    # This gear will use a "gear_dict" dictionary as a custom-user field 
    # on the gear context.

    # grab environment for gear
    with open('/tmp/gear_environ.json', 'r') as f:
        context.gear_dict['environ'] = json.load(f)

    # grab the manifest for use later
    with open('/flywheel/v0/manifest.json','r',errors='ignore') as f:
        context.gear_dict['manifest_json'] = json.load(f)

    #get_Custom_Logger is defined in utils.py
    context.log = get_custom_logger(context)

    # Set dry-run parameter
    context.gear_dict['dry-run'] = context.config['dry-run']

    # Set number of cores for pytorch to use
    cpu_cores = psutil.cpu_count()
    torch.set_num_threads(cpu_cores)
    torch.set_num_interop_threads(cpu_cores)

def validate_config_against_manifest(context):
    """
    This function compares the automatically produced configuration file 
    (config.json) to the contstraints listed in the manifest (manifest.json). 
    This adds a layer of redundancy and transparency to that the process in the 
    web-gui and the SDK.
    This function:
    - checks for the existence of required inputs and the file type of all inputs
    - checks for the ranges of values on config parameters
    - checks for the length of arrays submitted
    - prints out a description of all errors found through a raised Exception.
    """
    c_config = context.config
    manifest = context.gear_dict['manifest_json']
    m_config = manifest['config']
    errors = []
    if 'config' in manifest.keys():
        for key in m_config.keys():
            m_item = m_config[key]
            # Check if config value is optional
            if key not in c_config.keys():
                if 'optional' not in m_item.keys():
                    errors.append(
                        'The config parameter, {}, is not optional.'.format(key)
                    )
                elif not m_item['optional']:
                    errors.append(
                        'The config parameter, {}, is not optional.'.format(key)
                    )
            else:
                c_val = c_config[key]
                if 'maximum' in m_item.keys():
                    if c_val > m_item['maximum']:
                        errors.append(
                            'The value of {}, {}, exceeds '.format(key,c_val) + \
                            'the maximum of {}.'.format(m_item['maximum'])
                        )
                if 'minimum' in m_item.keys():
                    if c_val < m_item['minimum']:
                        errors.append(
                            'The value of {}, {}, is less than '.format(key,c_val) + \
                            'the minimum of {}.'.format(m_item['minimum'])
                        )
                if 'items' in m_item.keys():
                    if 'maxItems' in m_item['items'].keys():
                        maxItems = m_item['items']['maxItems']
                        if len (c_val) > maxItems:
                            errors.append(
                                'The array {} has {} '.format(key,len(c_val)) + \
                                'elements. More than the {} '.format(maxItems) + \
                                'required.'
                            )
                    if 'minItems' in m_item['items'].keys():
                        minItems = m_item['items']['minItems']
                        if len (c_val) > minItems:
                            errors.append(
                                'The array {} has {} '.format(key,len(c_val)) + \
                                'elements. Less than the {} '.format(minItems) + \
                                'required.'
                            )
                if 'enum' in m_item.keys():
                    # This means the value of the config MUST be one of the 
                    # enumerated values.
                    if c_val not in m_item['enum']:
                        errors.append(
                        'The {} configuration value of {} '.format(key,c_val) + \
                        'is not in the list: {}'.format(m_item['enum'])
                        )
    if 'inputs' in manifest.keys():
        c_inputs = context._invocation['inputs']
        m_inputs = manifest['inputs']
        for key in m_inputs.keys():
            # if a manifest input is not in the invocation inputs
            # check if it needs to be
            if key not in c_inputs.keys():
                m_input = m_inputs[key]
                if 'optional' not in m_input.keys():
                    errors.append(
                        'The input, {}, is not optional.'.format(key)
                    )
                elif not m_input['optional']:
                    errors.append(
                        'The input, {}, is not optional.'.format(key)
                    )
            # Or if it is there, check to see if it is the right type
            elif 'type' in m_inputs[key].keys():
                m_f_type = m_inputs[key]['type']['enum'][0] ##??
                c_f_type = c_inputs[key]['object']['type']
                if m_f_type != c_f_type:
                    errors.append(
                    'The input, {}, '.format(key) + \
                    ' is a "{}" file.'.format(c_f_type) + \
                    ' It needs to be a "{}" file.'.format(m_f_type)
                    )
    if len(errors) > 0:
        raise Exception(
        'Your gear is not configured correctly: \n{}'.format('\n'.join(errors))
        )

def set_freesurfer_license(context):
    """Sets the freesurfer license.txt file depending on(in order of precedence)
    1) A license string set in the config parameters
    2) A license.txt passed as a file
    3) A license string set in the project metadata
    or an exception is raised.
    
    :param context: gear context object with gear_dict attribute
    :type context: GearConfig
    :raises Exception: If FreeSurfer license.txt not created.
    """    
    config = context.config
    freesurfer_path = context.gear_dict['environ']['FREESURFER_HOME']
    if context.get_input('api-key'):
        fw = context.client
        project_id = fw.get_analysis(context.destination.get('id')).parents.project
        project = fw.get_project(project_id)

    license_txt = ''
    # Look for license string
    if config.get('FREESURFER_LICENSE'):
        license_txt = config.get('FREESURFER_LICENSE')
    # Look for license.txt file
    elif context.get_input_path('FreeSurferLicense'):
        with open(context.get_input_path('FreeSurferLicense'),'r') as f:
            license_txt = f.readlines()
            license_txt = ' '.join(license_txt)
    # Look for license string in project metadata
    elif context.get_input('api-key'):
        if project.info.get('FREESURFER_LICENSE'):
            license_txt = project.info.get('FREESURFER_LICENSE')
        else:
            raise Exception('No project level freesurfer license.')
    # If not found, raise descriptive exception
    else:
        raise Exception(
            'FreeSurfer license not set.\n Check submission configuration ' + \
            'or project metadata.'
        )
    
    with open(op.join(freesurfer_path,'license.txt'), 'w') as fs_license:
            fs_license.write('\n'.join(license_txt.split()))
