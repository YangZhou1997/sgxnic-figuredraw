#!/bin/bash
build/ARM/gem5.fast \
    --remote-gdb-port=0 \
    --outdir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/m5out/detailed_nat-tcp-v4.lpm.acl-fw.monitoring.lpm.dpi.maglev.lpm.lpm.nat-tcp-v4.lpm.acl-fw.dpi.acl-fw.nat-tcp-v4.dpi_4MB_tp \
    --stats-file=detailed_nat-tcp-v4.lpm.acl-fw.monitoring.lpm.dpi.maglev.lpm.lpm.nat-tcp-v4.lpm.acl-fw.dpi.acl-fw.nat-tcp-v4.dpi_4MB_tp_stats.txt \
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
    --maxinsts=100000000\
    --maxtick=2000000000000 \
    --numpids=16 \
    --p0=/users/yangzhou/NFShield/nat-tcp-v4 \
    --p1=/users/yangzhou/NFShield/lpm \
    --p2=/users/yangzhou/NFShield/acl-fw \
    --p3=/users/yangzhou/NFShield/monitoring \
    --p4=/users/yangzhou/NFShield/lpm \
    --p5=/users/yangzhou/NFShield/dpi \
    --p6=/users/yangzhou/NFShield/maglev \
    --p7=/users/yangzhou/NFShield/lpm \
    --p8=/users/yangzhou/NFShield/lpm \
    --p9=/users/yangzhou/NFShield/nat-tcp-v4 \
    --p10=/users/yangzhou/NFShield/lpm \
    --p11=/users/yangzhou/NFShield/acl-fw \
    --p12=/users/yangzhou/NFShield/dpi \
    --p13=/users/yangzhou/NFShield/acl-fw \
    --p14=/users/yangzhou/NFShield/nat-tcp-v4 \
    --p15=/users/yangzhou/NFShield/dpi \
    > /users/yangzhou/GEM5_DRAMSim2/sgx_nic/results/stdout_detailed_nat-tcp-v4.lpm.acl-fw.monitoring.lpm.dpi.maglev.lpm.lpm.nat-tcp-v4.lpm.acl-fw.dpi.acl-fw.nat-tcp-v4.dpi_4MB_tp.out \
    2> /users/yangzhou/GEM5_DRAMSim2/sgx_nic/stderr/stderr_detailed_nat-tcp-v4.lpm.acl-fw.monitoring.lpm.dpi.maglev.lpm.lpm.nat-tcp-v4.lpm.acl-fw.dpi.acl-fw.nat-tcp-v4.dpi_4MB_tp.out
