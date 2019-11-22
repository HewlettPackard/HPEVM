#!/bin/bash
# Install prerequisites following https://spdk.io/doc/nvmf.html

# git clone https://github.com/spdk/spdk to $HOME/github/
spdk_root=/home/tdc/github/spdk
pushd $spdk_root
sudo ./scripts/setup.sh
sudo ./app/nvmf_tgt/nvmf_tgt
popd


