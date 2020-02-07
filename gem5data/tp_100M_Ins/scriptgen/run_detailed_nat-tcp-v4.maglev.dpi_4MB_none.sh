#!/bin/bash
build/ARM/gem5.fast \
    --remote-gdb-port=0 \
    --outdir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/m5out/detailed_nat-tcp-v4.maglev.dpi_4MB_none \
    --stats-file=detailed_nat-tcp-v4.maglev.dpi_4MB_none_stats.txt \
    configs/dramsim2/dramsim2_se.py \
    --cpu-type=detailed --clock=1.2GHz \
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
    --numpids=3 \
    --p0=/users/yangzhou/NF-GEM5/nat-tcp-v4 \
    --p1=/users/yangzhou/NF-GEM5/maglev \
    --p2=/users/yangzhou/NF-GEM5/dpi \
    > /users/yangzhou/GEM5_DRAMSim2/sgx_nic/results/stdout_detailed_nat-tcp-v4.maglev.dpi_4MB_none.out \
    2> /users/yangzhou/GEM5_DRAMSim2/sgx_nic/stderr/stderr_detailed_nat-tcp-v4.maglev.dpi_4MB_none.out
