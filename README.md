# PV_crawler

This project include two parts.

1. procBoot (a wrapper and management tool of `procServ`)
2. pvCrawler (a tool getting all the PV from EPICS IOC `st.cmd` file) 

## procBoot

see procServ. [https://github.com/ralphlange/procServ](https://github.com/ralphlange/procServ)

### Usage
`python3 proBoot.py [start|stop|restart|status|detail] [options] configFile`

## pvCrawler

### Requirement

- Elastic Search
- MSI (EPICS Extensions)
- Python > 3.7
- Python `elasticsearch` module

### Usage

1. prepare a `tbl` file with all the IOCs info, see below.

2. modify the file `pvCrawler/epics.config`

3. run `python3 maintask.py`

### IOCs

Since we are using procServ (procBoot) managing all the IOCs. 
It is possible to collect all ioc inforamtion into one file. format is like:

```
! IOCNAME----IOCHOST----IOCPORT----IOCPATH
BPM_SYNC	host1	30000	 /epics/BPMSync/iocBoot/iocBPMsyncApp/BPMSync.cmd
BPM_SYNCSHM	host2	30001	 /epics/BPMSync/iocBoot/iocBPMsyncApp/BPMSyncSHM.cmd
```
### EPICS db

> Using `Macro Substitution and Include Tool`

1. epics extension: [msi: Macro Substitution and Include Tool](https://epics.anl.gov/EpicsDocumentation/ExtensionsManuals/msi/msi.html)

2. alternatively [pymsi - a msi alternative written in python](https://www-csr.bessy.de/control/pymsi/) 

search the `st.cmd` or similar file for two functions:

- `dbLoadRecords()`
- `dbLoadTemplate()`

expand macro to get real PV Name, record type etc.
Using EPICS extensions: `msi` to expand.

Command is like:

`./msi -M "SYS=LIiEV,D=evg0,EVG=SKBEVG0" -o result.log ../SKBEVG-config.db`

`./msi -V -o outfile -I dir -M subs -S subfile template`
 
Note: EPICS PV name must be composed out of the following characters:

`a-z A-Z 0-9 _ - + : [ ] < > ;`

**!!! can not recognize correctly if several fields are in the same line (though allowed by EPICS IOC)**

### Insert PVs to Elastic Search

Using `Kibana` to check the result.

If successful, use this project to search PV on webpage [https://github.com/Insomnia1437/pvSearch-vue-node-es](https://github.com/Insomnia1437/pvSearch-vue-node-es) 
