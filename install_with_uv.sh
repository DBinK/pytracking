#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "ERROR! Illegal number of parameters. Usage: bash install.sh environment_name"
    exit 0
fi

uv_install_path=$(which uv)
if [ -z "$uv_install_path" ]; then
    echo "ERROR! uv is not installed. Please install uv first: pip install uv"
    exit 0
fi

env_name=$1

echo "****************** Creating virtual environment ${env_name} with Python 3.7 ******************"
uv venv $env_name --python 3.10.18

echo ""
echo ""
echo "****************** Activating virtual environment ${env_name} ******************"
source $env_name/bin/activate

echo ""
echo ""
echo "****************** Installing pytorch with cuda10 ******************"
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu100

echo ""
echo ""
echo "****************** Installing packages with uv ******************"
uv pip install matplotlib pandas tqdm opencv-python tb-nightly visdom scikit-image tikzplotlib gdown cython pycocotools lvis spatial-correlation-sampler jpeg4py

echo ""
echo ""
echo "****************** Installing ninja-build to compile PreROIPooling ******************"
echo "************************* Need sudo privilege ******************"
sudo apt-get install ninja-build

echo ""
echo ""
echo "****************** Downloading networks ******************"
mkdir -p pytracking/networks

echo ""
echo ""
echo "****************** DiMP50 Network ******************"
uv pip install gdown
gdown https://drive.google.com/uc\?id\=1qgachgqks2UGjKx-GdO1qylBDdB1f9KN -O pytracking/networks/dimp50.pth

echo ""
echo ""
echo "****************** Setting up environment ******************"
python -c "from pytracking.evaluation.environment import create_default_local_file; create_default_local_file()"
python -c "from ltr.admin.environment import create_default_local_file; create_default_local_file()"

echo ""
echo ""
echo "****************** Installing jpeg4py ******************"
while true; do
    read -p "Install jpeg4py for reading images? This step required sudo privilege. Installing jpeg4py is optional, however recommended. [y,n]  " install_flag
    case $install_flag in
        [Yy]* ) sudo apt-get install libturbojpeg; break;;
        [Nn]* ) echo "Skipping jpeg4py installation!"; break;;
        * ) echo "Please answer y or n  ";;
    esac
done

echo ""
echo ""
echo "****************** Installation complete! ******************"

echo ""
echo ""
echo "****************** More networks can be downloaded from the google drive folder https://drive.google.com/drive/folders/1WVhJqvdu-_JG1U-V0IqfxTUa1SBPnL0O ******************"
echo "****************** Or, visit the model zoo at https://github.com/visionml/pytracking/blob/master/MODEL_ZOO.md ******************"