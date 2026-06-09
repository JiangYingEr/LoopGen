## Explanation

- For RTT, the ping command can **directly** output the min, avg, max, and dev, so the ***.ipynb file(s)** directly contain the raw data.
- For throughput, the Iperf command also directly output the final evaluated throughput, so the ***.ipynb file(s)** directly contain the raw data.

## Correspondence

**Figure 6: Latency caused by LoopGen (IP packets)** in the paper:

- latencyhibercanada.ipynb
- latencynettrial.ipynb
- latencysprint.ipynb
- latencybtasiapac.ipynb

**Figure 7: Latency caused by LoopGen (ARP packets)** in the paper:

- latencyhibercanadaARP.ipynb
- latencynettrialARP.ipynb
- latencysprintARP.ipynb
- latencybtasiapacARP.ipynb

**Figure 8: TCP Bandwidth caused by LoopGen** in the paper:

- BWIP.ipynb
- BWARP.ipynb

**Figure 9: UDP Bandwidth caused by LoopGen** in the paper:

- BWIPUDP.ipynb
- BWARPUDP.ipynb

**Figure 10: Loss rate when evaluating UDP bandwidth** in the paper:

- LOSSARPUDP.ipynb
- LOSSIPUDP.ipynb
