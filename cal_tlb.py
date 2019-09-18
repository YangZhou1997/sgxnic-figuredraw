import sys
per_tlb_cost_core = [0.0112069, 0.00647285, 0.0149641, 0.008668506, 0.0407497, 0.02191868]
per_tlb_cost_accele = [0.00463727, 0.00232214, 0.00569684, 0.002770481, 0.00311821, 0.001437977]
per_tlb_cost_pktio = [0.00311821, 0.001437977]
per_tlb_cost_pagesize = [0.0112069, 0.00647285, 0.00445464, 0.002214057, 0.00311821, 0.001437977]

def multi_float(time, per_tlb_core): 
    temp = list(map(lambda x: "{:.3f} & ".format(x * time), per_tlb_core))
    for item in temp:
        sys.stdout.write(item)        
    print()

multi_float(8, per_tlb_cost_core)
multi_float(16, per_tlb_cost_core)
multi_float(48, per_tlb_cost_core)

multi_float(16, per_tlb_cost_accele)
multi_float(8, per_tlb_cost_accele)
multi_float(4, per_tlb_cost_accele)

multi_float(12, per_tlb_cost_pktio)
multi_float(6, per_tlb_cost_pktio)
multi_float(3, per_tlb_cost_pktio)

multi_float(48, per_tlb_cost_pagesize)
