# !/bin/bash

node0=clnode207.clemson.cloudlab.us
node1=clnode187.clemson.cloudlab.us
node2=clnode205.clemson.cloudlab.us
node3=clnode005.clemson.cloudlab.us
node4=pc91.cloudlab.umass.edu

m5out_dir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/m5out/*
stdout_dir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/results/*
stderr_dir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/stderr/*
scriptgen_dir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/scriptgen/*

datadir=gem5data/tp_10M_ins_8_16_nfs
mkdir -p ./$datadir

mkdir -p ./$datadir/m5out/
mkdir -p ./$datadir/results/
mkdir -p ./$datadir/stderr/
mkdir -p ./$datadir/scriptgen/
mkdir -p ./$datadir/drawdata/

for node in $node0 $node1 $node2 $node3 $node4
do
    rsync -auv -e ssh yangzhou@$node:$m5out_dir ./$datadir/m5out/
    rsync -auv -e ssh yangzhou@$node:$stdout_dir ./$datadir/results/
    rsync -auv -e ssh yangzhou@$node:$stderr_dir ./$datadir/stderr/
    rsync -auv -e ssh yangzhou@$node:$scriptgen_dir ./$datadir/scriptgen/
done