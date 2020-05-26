# !/bin/bash

node0=clnode239.clemson.cloudlab.us
node1=clnode223.clemson.cloudlab.us
node2=clnode162.clemson.cloudlab.us
node3=clnode144.clemson.cloudlab.us
node4=c220g1-031123.wisc.cloudlab.us
node5=c220g1-031120.wisc.cloudlab.us
node6=c220g1-031108.wisc.cloudlab.us
node7=c220g1-031104.wisc.cloudlab.us

m5out_dir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/m5out/*
stdout_dir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/results/*
stderr_dir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/stderr/*
scriptgen_dir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/scriptgen/*

datadir=gem5data/lowl2cache
mkdir -p ./$datadir

mkdir -p ./$datadir/m5out/
mkdir -p ./$datadir/results/
mkdir -p ./$datadir/stderr/
mkdir -p ./$datadir/scriptgen/
mkdir -p ./$datadir/drawdata/

for node in $node0 $node1 $node2 $node3 $node4 $node5 $node6 $node7
do
    rsync -auv -e ssh yangzhou@$node:$m5out_dir ./$datadir/m5out/
    rsync -auv -e ssh yangzhou@$node:$stdout_dir ./$datadir/results/
    rsync -auv -e ssh yangzhou@$node:$stderr_dir ./$datadir/stderr/
    rsync -auv -e ssh yangzhou@$node:$scriptgen_dir ./$datadir/scriptgen/
done