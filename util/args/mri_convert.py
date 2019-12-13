import os, os.path as op
from collections import OrderedDict
from .common import build_command_list, exec_command

def build(context):
    config = context.config

    params = OrderedDict()

    params['T1W'] = context.get_input_path('T1W')
    params['Output'] = op.join(context.work_dir, 'Brain_Segmentation.nii.gz')
    
    context.gear_dict['params'] = params

def validate(context):
    pass

def execute(context):
    command = ['mri_convert', '--conform']
    command = build_command_list(command, context.gear_dict['params'],include_keys=False)
    exec_command(context,command,cont_output=True)
