from p4utils.mininetlib.cli import P4CLI
c = P4CLI(9090)
c.do_p4switch_reboot("s1")
