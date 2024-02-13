#!/bin/bash
build/ARM/gem5.fast \
    --remote-gdb-port=0 \
    --outdir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/m5out/detailed_monitoring.dpi.lpm.maglev.monitoring.monitoring.nat-tcp-v4.acl-fw.lpm.nat-tcp-v4.maglev.lpm.lpm.nat-tcp-v4.maglev.monitoring_4MB_tp \
    --stats-file=detailed_monitoring.dpi.lpm.maglev.monitoring.monitoring.nat-tcp-v4.acl-fw.lpm.nat-tcp-v4.maglev.lpm.lpm.nat-tcp-v4.maglev.monitoring_4MB_tp_stats.txt \
    configs/dramsim2/dramsim2_se.py \
    --cpu-type=detailed --clock=2.4GHz \
    --cacheline_size=128 \
    --caches --l2cache \
    --l2config=setpartition \
    --l2_size=256kB --l2_assoc=16 \
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
    --maxinsts=10000000\
    --maxtick=2000000000000 \
    --numpids=16 \
    --p0=/users/yangzhou/NFShield/monitoring \
    --p1=/users/yangzhou/NFShield/dpi \
    --p2=/users/yangzhou/NFShield/lpm \
    --p3=/users/yangzhou/NFShield/maglev \
    --p4=/users/yangzhou/NFShield/monitoring \
    --p5=/users/yangzhou/NFShield/monitoring \
    --p6=/users/yangzhou/NFShield/nat-tcp-v4 \
    --p7=/users/yangzhou/NFShield/acl-fw \
    --p8=/users/yangzhou/NFShield/lpm \
    --p9=/users/yangzhou/NFShield/nat-tcp-v4 \
    --p10=/users/yangzhou/NFShield/maglev \
    --p11=/users/yangzhou/NFShield/lpm \
    --p12=/users/yangzhou/NFShield/lpm \
    --p13=/users/yangzhou/NFShield/nat-tcp-v4 \
    --p14=/users/yangzhou/NFShield/maglev \
    --p15=/users/yangzhou/NFShield/monitoring \
    > /users/yangzhou/GEM5_DRAMSim2/sgx_nic/results/stdout_detailed_monitoring.dpi.lpm.maglev.monitoring.monitoring.nat-tcp-v4.acl-fw.lpm.nat-tcp-v4.maglev.lpm.lpm.nat-tcp-v4.maglev.monitoring_4MB_tp.out \
    2> /users/yangzhou/GEM5_DRAMSim2/sgx_nic/stderr/stderr_detailed_monitoring.dpi.lpm.maglev.monitoring.monitoring.nat-tcp-v4.acl-fw.lpm.nat-tcp-v4.maglev.lpm.lpm.nat-tcp-v4.maglev.monitoring_4MB_tp.out
