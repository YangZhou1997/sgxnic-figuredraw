# !/bin/bash

NIC=10.243.38.93
NIC_PATH=/usr/local/Cavium_Networks/OCTEON-SDK/examples/throughput-eva

NB=localhost
NB_PATH=/home/yangz/NetBricks/examples/throughput-eva

SB=localhost
SB_PATH=/home/yangz/SafeBricks/examples/throughput-eva

CG=10.243.38.86
CG_PATH=/home/yangz/NetBricks/examples/memory-profiling/cgroup-log

TWO=$NIC
TWO_PATH=/home/yangz/pktgen/dpdk_zeroloss_dyn_two_apps/*.dat

# scp yangz@$NIC:$NIC_PATH/* ./rawdata/nic/
# scp yangz@$NB:$NB_PATH/* ./rawdata/nb/
# scp yangz@$SB:$SB_PATH/* ./rawdata/sb/
# scp yangz@$CG:$CG_PATH/* ./rawdata/mem/
# scp yangz@$NIC:$NIC_PATH/* ./rawdata/dpi/
scp yangz@$TWO:$TWO_PATH ./rawdata/two_latency/
scp yangz@$NIC:$NIC_PATH/* ./rawdata/two_loss/

