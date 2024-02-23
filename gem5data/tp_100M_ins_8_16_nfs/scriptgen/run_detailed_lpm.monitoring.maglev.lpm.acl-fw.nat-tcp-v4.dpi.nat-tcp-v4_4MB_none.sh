#!/bin/bash
build/ARM/gem5.fast \
    --remote-gdb-port=0 \
    --outdir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/m5out/detailed_lpm.monitoring.maglev.lpm.acl-fw.nat-tcp-v4.dpi.nat-tcp-v4_4MB_none \
    --stats-file=detailed_lpm.monitoring.maglev.lpm.acl-fw.nat-tcp-v4.dpi.nat-tcp-v4_4MB_none_stats.txt \
    configs/dramsim2/dramsim2_se.py \
    --cpu-type=detailed --clock=2.4GHz \
    --cacheline_size=128 \
    --caches --l2cache \
    --l2config=shared \
    --l2_size=4MB --l2_assoc=16 \
    --dramsim2 \
    --tpturnlength=6 \
    --devicecfg=./ext/DRAMSim2/ini/DDR3_micron_16M_8B_x8_sg15.ini \
    --systemcfg=./ext/DRAMSim2/system_none.ini \
    --outputfile=/dev/null \
    --fast-forward=1000000000 \
    --maxinsts=100000000\
    --maxtick=2000000000000 \
    --numpids=8 \
    --p0=/users/yangzhou/NFShield/lpm \
    --p1=/users/yangzhou/NFShield/monitoring \
    --p2=/users/yangzhou/NFShield/maglev \
    --p3=/users/yangzhou/NFShield/lpm \
    --p4=/users/yangzhou/NFShield/acl-fw \
    --p5=/users/yangzhou/NFShield/nat-tcp-v4 \
    --p6=/users/yangzhou/NFShield/dpi \
    --p7=/users/yangzhou/NFShield/nat-tcp-v4 \
    > /users/yangzhou/GEM5_DRAMSim2/sgx_nic/results/stdout_detailed_lpm.monitoring.maglev.lpm.acl-fw.nat-tcp-v4.dpi.nat-tcp-v4_4MB_none.out \
    2> /users/yangzhou/GEM5_DRAMSim2/sgx_nic/stderr/stderr_detailed_lpm.monitoring.maglev.lpm.acl-fw.nat-tcp-v4.dpi.nat-tcp-v4_4MB_none.out