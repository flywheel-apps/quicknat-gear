from ...quickNAT import evaluate_bulk, Settings

def exec(context):
    #settings = Settings('/opt/quickNAT_pytorch/settings.ini')
    #common_params, data_params, net_params, train_params, eval_params = settings['COMMON'], \
    #                                                                    settings['DATA'], \
    #                                                                    settings['NETWORK'], \
    #                                                                    settings['TRAINING'], \
    #                                                                    settings['EVAL']

    settings_eval = Settings('/opt/quickNAT_pytorch/settings_eval.ini')
    evaluate_bulk(settings_eval['EVAL_BULK'])

