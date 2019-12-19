from ..quickNAT import evaluate_bulk
import os, os.path as op

def build(context):
    """
    The parameters for quickNAT follow the format found in the settings_eval.ini
    file on their github repository. For more information, see 
    https://github.com/ai-med/quickNAT_pytorch
    """
    config = context.config

    params = {}
    # Create parameters consistent with what is in settings_eval.ini
    # Load the settings from our default file
    # settings_eval = Settings('/flywheel/v0/settings_eval.ini')
    
    if config['device'] == 'GPU':
        params['device'] = config['device_num']
    else:
        params['device'] = 'cpu'

    # Use specified coronal model
    if context.get_input_path('coronal_model_path'):
        
            context.get_input_path('coronal_model_path')
    # Else use default coronal model
    else: 
        params['coronal_model_path'] = \
        '/opt/quickNAT_pytorch/saved_models/finetuned_alldata_coronal.pth.tar'

    # Use specified coronal model 
    if context.get_input_path('axial_model_path'):
        params['axial_model_path'] = \
            context.get_input_path('axial_model_path')
    # Else use default coronal model
    else:
        params['axial_model_path'] = \
        '/opt/quickNAT_pytorch/saved_models/finetuned_alldata_axial.pth.tar'

    params['data_dir'] = context.work_dir

    # Valid options : "FS" , "part_FS", "Linear"
    params['directory_struct'] = 'Linear'

    volumes_path = op.join(context.work_dir,'test_list.txt')
    params['volumes_txt_file'] = volumes_path
    volumes_fl = open(volumes_path,'w')
    volumes_fl.write('Brain_Segmentation.nii.gz')
    volumes_fl.close()

    params['batch_size'] = config['batch_size']

    params['save_predictions_dir'] = context.output_dir

    params['view_agg'] = str(config['view_agg'])

    params['estimate_uncertainty'] = str(config['estimate_uncertainty'])

    params['mc_samples'] = config['mc_samples']
    
    # the 'EVAL_BULK' settings are meant to iterate through multiple images
    # and skip those that produce error.
    # Since we are only doing one at a time (for now), with this gear, we will
    #  exit on error, if we encounter one. 
    params['exit_on_error'] = True

    context.gear_dict['params'] = params

def validate(context):
    # when we start including other pretrained models, it will be essential
    # to test whether or not they are compatible with the current code framework
    # otherwise, 
    pass

def exec(context):
    params = context.gear_dict['params']
    context.log.info('Running with settings:')
    context.log.info(params)
    if not context.gear_dict['dry-run']:
        evaluate_bulk(params)

