#!/bin/bash
build/ARM/gem5.fast \
    --remote-gdb-port=0 \
    --outdir=/users/yangzhou/gem5/sgx_nic/m5out/TimingSimpleCPU_dpi-queue.nat-tcp-v4.lpm.monitoring_4MB \
    --stats-file=TimingSimpleCPU_dpi-queue.nat-tcp-v4.lpm.monitoring_4MB_stats.txt \
    configs/example/se_nic.py \
    --interp-dir /usr/aarch64-linux-gnu \
    --redirects /lib=/usr/aarch64-linux-gnu/lib \
    -c "dpi-queue;nat-tcp-v4;lpm;monitoring" \
    --cpu-type=TimingSimpleCPU --cpu-clock=2.4GHz --asic-clock=0.56GHz \
    --cacheline_size=128 \
    --caches --l2cache \
    --l2_size=4MB --l2_assoc=16 \
    --mem-size=192GB --mem-type=DDR3_1600_8x8 --mem-channels=2 --mem-ranks=2 \
    --fast-forward=2000000000 \
    --rel-max-tick=2000000000000 \
    > /users/yangzhou/gem5/sgx_nic/results/stdout_TimingSimpleCPU_dpi-queue.nat-tcp-v4.lpm.monitoring_4MB.out \
    2> /users/yangzhou/gem5/sgx_nic/stderr/stderr_TimingSimpleCPU_dpi-queue.nat-tcp-v4.lpm.monitoring_4MB.out
