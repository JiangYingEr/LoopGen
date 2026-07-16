# LoopGen

Address learning is a fundamental SDN service that maintains a dynamic mapping from host addresses to switch ports, supporting many critical network applications. However, the address learning's core position makes it an attractive attack target. Meanwhile, unfortunately, it lacks security protection from a global view, resulting in the fact that individual, normal events can collectively cause damage. Based on it, this paper proposes LoopGen, a new attack targeting the address learning mechanism. LoopGen shows that adversaries who compromised hosts can induce the controller to create a data-plane forwarding loop by only sending crafted packets in a specific order. This loop makes LoopGen a cost-effective DoS amplifier that can be combined with different DoS attacks. We conduct extensive experiments, evaluating LoopGen using diverse real-world topologies, different open-source controllers, and heterogeneous switches. The results show that LoopGen has non-trivial feasibility, significant amplification effect, low attack cost, and high stealthiness under existing defenses. Finally, we propose two countermeasures to mitigate this attack.

# How to run


We provided a VM image to help quickly reproduce our experiments. All codes and dependencies have been installed on the VM. All your need is to follows the instructions in `Experiment`.



### 1. Please install [VirtualBox](https://www.virtualbox.org/) on your machine

### 2. Please [download our VM](https://zenodo.org/records/21307319) and open it using VirtualBox. The `.ova` file is the VM.

[Here is an example about how to import ova using Virtualbox](https://ubuntu.com/docs/public-images/public-images-how-to/run-an-ova-using-virtualbox/)

Login in via the `p4` username, the password is
```
p4
```

![](login.png)

Then, for the experiment you want to try, please directly read the `readme.md` in the corresponding directory in `Experiment`.

If you want to build the entire environment from scratch, please see `BuildFromScratch.md`.


## Claims and Corresponding Experiments
This paper has the following five main claims. We list the corresponding experiment directories below. To conduct a concrete experiment, please directly read the corresponding `readme.md`.

### `C1` Feasibility: 
- `Experiment/Feasibility/Prerequisite/readme.md`
- `Experiment/Feasibility/AcrossController/Ryu/README.md`
- `Experiment/Feasibility/AcrossController/POX/l2/README.md`
- `Experiment/Feasibility/AcrossController/ONOS/README.md`
- `Experiment/Feasibility/AcrossSwitch/readme.md`.

### `C2` Amplification effect: 
- `Experiment/AmplificationEffect/readme.md`.

### `C3` Low cost:
-  `Experiment/Cost/readme.md`.

### `C4` Stealthiness under existing defenses: 
- `Experiment/Stealthiness/IdentityVerification/readme.md`
-  `Experiment/Stealthiness/EventScope/README.md`
-  `Experiment/Stealthiness/SVHunter/README.md`
-  `Experiment/Stealthiness/Lemon/readme.md`
-  `Experiment/Stealthiness/SISTAR/readme.md`.

### `C5` Controller-side defenses: 
- `Experiment/defense/readme.md`.


