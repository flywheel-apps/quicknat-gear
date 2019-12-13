from ...quickNAT import evaluate_bulk, Settings

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

    settings_eval['EVAL_BULK']['batch_size'] = config['batch_size']

    if config['view_agg']:
        settings_eval['EVAL_BULK']['view_agg'] = "True"

    if config['estimate_uncertainty']:
        settings_eval['EVAL_BULK']['estimate_uncertainty'] = "True"
        settings_eval['EVAL_BULK']['mc_samples'] = config['mc_samples']


    context.gear_dict['settings_eval'] = settings_eval

def validate(context):
    pass

def exec(context):
    settings_eval = context.gear_dict['settings_eval']
    
    if not context.gear_dict['dry-run']:
        evaluate_bulk(settings_eval['EVAL_BULK'])

