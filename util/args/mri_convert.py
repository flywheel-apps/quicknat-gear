import os, os.path as op
from collections import OrderedDict
from .common import build_command_list, exec_command

def build(context):
    params = OrderedDict()
    # TODO: make the Output into a Subject-specific filename???
    params['T1W'] = context.get_input_path('T1W')
    params['Output'] = op.join(context.work_dir, 'Brain_Segmentation.nii.gz')
    
    context.gear_dict['params'] = params

def validate(context):
    params = context.gear_dict['params']
    if (not op.exists(params['T1W'])) or (not op.exists(context.work_dir)):
        raise FileNotFoundError('File or directory missing.')

def execute(context):
    command = ['mri_convert', '--conform']
    command = build_command_list(command, context.gear_dict['params'],include_keys=False)
    exec_command(context,command,cont_output=True)
