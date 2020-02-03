#!/bin/bash
build/ARM/gem5.fast \
    --remote-gdb-port=0 \
    --outdir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/m5out/detailed_acl-fw.nat-tcp-v4.maglev.monitoring_2MB_tp \
    --stats-file=detailed_acl-fw.nat-tcp-v4.maglev.monitoring_2MB_tp_stats.txt \
    configs/dramsim2/dramsim2_se.py \
    --cpu-type=detailed --clock=2.4GHz \
    --cacheline_size=128 \
    --caches --l2cache \
    --l2config=private \
    --l2_size=512kB --l2_assoc=16 \
    --fixaddr \
    --rr_nc \
    --split_mshr \
    --split_rport \
    --dramsim2 \
    --tpturnlength=6 \
    --devicecfg=./ext/DRAMSim2/ini/DDR3_micron_16M_8B_x8_sg15.ini \
    --systemcfg=./ext/DRAMSim2/system_tp.ini \
    --outputfile=/dev/null \
    --fast-forward=1000000000 \
    --maxinsts=100000000\
    --maxtick=2000000000000 \
    --numpids=4 \
    --p0=/users/yangzhou/NF-GEM5/acl-fw \
    --p1=/users/yangzhou/NF-GEM5/nat-tcp-v4 \
    --p2=/users/yangzhou/NF-GEM5/maglev \
    --p3=/users/yangzhou/NF-GEM5/monitoring \
    > /users/yangzhou/GEM5_DRAMSim2/sgx_nic/results/stdout_detailed_acl-fw.nat-tcp-v4.maglev.monitoring_2MB_tp.out \
    2> /users/yangzhou/GEM5_DRAMSim2/sgx_nic/stderr/stderr_detailed_acl-fw.nat-tcp-v4.maglev.monitoring_2MB_tp.out
