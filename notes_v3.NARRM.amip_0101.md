
# v3.NARRM.amip_0101

```shell
# HPSS path for data
/home/t/tang30/E3SMv3/RRM/v3.NARRM.amip_0101

# examine zstash archive
zstash ls --hpss=/home/t/tang30/E3SMv3/RRM/v3.NARRM.amip_0101 "archive/atm/hist/*eam.h0.1985*"

# zstash command to extract
cd /global/cfs/cdirs/m4310/data/sims/v3.NARRM.amip_0101
zstash extract --hpss=/home/t/tang30/E3SMv3/RRM/v3.NARRM.amip_0101 "archive/atm/hist/*eam.h0.*"
```

```shell
zstash ls --hpss=/home/t/tang30/E3SMv3/RRM/v3.NARRM.amip_0101 "archive/rest/*198*"

zstash extract --hpss=/home/t/tang30/E3SMv3/RRM/v3.NARRM.amip_0101 "archive/rest/1985-01-01-00000/*"
```