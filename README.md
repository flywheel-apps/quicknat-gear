# quicknat-gear

This is a [Flywheel Gear](https://github.com/flywheel-io/gears/tree/master/spec) that wraps the [PyTorch implementation](https://github.com/ai-med/quickNAT_pytorch) of [quickNAT](https://github.com/ai-med/QuickNATv2). QuickNAT is a Deep Learning architecture that allows fast whole brain segmentation (within 30 seconds on specific GPUs).

This gear makes predictions in the "eval_bulk" mode of quickNAT_pytorch for the required T1-weighted input (below).  The default embedded models perform predictive segementation of brain regions. Compatible models can be used to predict other areas of interest.

## Required inputs

1. **T1W**
    * T1-weighted anatomical volume (eg: MPRAGE)
2. **FreeSurferLicense**
    * A FreeSurfer license must exist as this input (txt file), a configuration parameter (space-delimited string "FREESURFER_LICENSE") or project-level metadata tag (FREESURFER_LICENSE).

## Optional inputs

1. **coronal_model_path**
    * This is a PyTorch model trained on coronally sliced MRI images (.pth.tar).
    * If left blank, it will revert to the finetuned_alldata_coronal.pth.tar final model of the quickNAT_pytorch project stored within the gear.
2. **axial_model_path**
    * This is a PyTorch model trained on axially sliced MRI images (.pth.tar).
    * If left blank, it will revert to the finetuned_alldata_axial.pth.tar final model of the quickNAT_pytorch project stored within the gear.

## Configuration Options

1. **device**
    * whether to run on CPUs or GPUs
    * will utilize all available cores
    * if a GPU and CUDA libraries are not available a GPU setting will revert to a CPU setting..
2. **device_num**
    * An integer representing which GPU to use, 0-7.
3. **batch_size**
    * Controls how many layers of an MRI volume are interated on at once.
    * Dependent on how much memory is available.
4. **view_agg**
    * Uses the maximum value between the coronal and axial model predictions
    * requires both coronal and axial models.
5. **estimate_uncertainty**
    * Indicates if you want to estimate the structure-wise uncertainty for segmentation Quality control. Refer to "Bayesian QuickNAT" paper for more details.
    * Will increase prediction time.
6. **mc_samples**
    * Active only if estimate_uncertainty flag is "True". Indicates the number of Monte-Carlo samples used for uncertainty estimation.

## GPU Execution

Interactive docker sessions of this gear have been tested in a GPU environment with significant speedup in inference time (25 seconds (gpu) vs. 2 hours (cpu)) on an NVIDIA GTX 1080 Ti.  Although all guest requirements (see below) are embedded within the docker container, this functionality is not enabled unless the host requirements are met.

Unfortunately, the host requirements necessary for GPU execution are not yet available on a Flywheel instance. They are scheduled to be available in early summer of 2020.

Local execution must be done with sample data, a valid configuration file (config.json), and the following nvidia container runtime command:

``nvidia-docker run --rm -v <local input directory>:<container input directory> -v <local config.json>:<container config.json> -v <local output directory>:<container output directory> -it <image id>``

See Host and Container Requirements below:

### Host Requirements

1. NVIDIA Driver 410.48 was used in an ubuntu 18.04 (bionic). See [Driver Compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/#binary-compatibility)

### Guest Requirements

1. Cuda: v10.0
2. CuDNN: installed with pytorch
3. torch: 1.3.1+cu92 (minimum 1.0.0. See requirements-gpu.txt)
4. torchvision: 0.4.2+cu92 (minimum 0.2.0. See requirements-gpu.txt)
5. Python 3.6
