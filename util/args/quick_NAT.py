from ..quickNAT import evaluate_bulk, Settings

def build(context):
    config = context.config
    # Load the settings from our default file
    settings_eval = Settings('/flywheel/v0/settings_eval.ini')
    
    # Update from input and other config parameters
    if context.get_input_path('coronal_model_path'):
        settings_eval['EVAL_BULK']['coronal_model_path'] = \
            context.get_input_path('coronal_model_path')
    
    if context.get_input_path('axial_model_path'):
        settings_eval['EVAL_BULK']['axial_model_path'] = \
            context.get_input_path('axial_model_path')

    if config['device'] == 'GPU':
        settings_eval['EVAL_BULK']['device'] = config['device_num']
    else:
        settings_eval['EVAL_BULK']['device'] = 'cpu'

    settings_eval['EVAL_BULK']['batch_size'] = config['batch_size']

    if config['view_agg']:
        settings_eval['EVAL_BULK']['view_agg'] = "True"

    if config['estimate_uncertainty']:
        settings_eval['EVAL_BULK']['estimate_uncertainty'] = "True"
        settings_eval['EVAL_BULK']['mc_samples'] = config['mc_samples']
    
    # the 'EVAL_BULK' settings are meant to iterate through multiple images
    # and skip those that produce error.
    # Since we are only doing one at a time, with this gear, we will exit on 
    # error, if we encounter one. 
    settings_eval['EVAL_BULK']['exit_on_error'] = True

    context.gear_dict['settings_eval'] = settings_eval

def validate(context):
    pass

def exec(context):
    settings_eval = context.gear_dict['settings_eval']
    context.log.info('Running with settings:')
    context.log.info(settings_eval['EVAL_BULK'])
    if not context.gear_dict['dry-run']:
        evaluate_bulk(settings_eval['EVAL_BULK'])

