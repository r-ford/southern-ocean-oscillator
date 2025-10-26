#!/glade/u/apps/opt/conda/envs/npl/bin/python
#PBS -N sosst
#PBS -A XXXX####
#PBS -j oe
#PBS -k eod
#PBS -q casper
#PBS -l walltime=01:00:00
#PBS -l select=1:ncpus=1:mpiprocs=128

import glob, os
import numpy as np
import xarray as xr

save_path = '/glade/u/home/rford2/ihesp/'
hr_path = '/glade/campaign/collections/rda/data/d651029/B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02/ocn/proc/tseries/month_1/'

sosst_list = []
for file in sorted(glob.glob(os.path.join(hr_path, 'B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02.pop.h.TEMP.*'))):
    ds = xr.open_dataset(file)
    sosst = ds.TEMP.isel(z_t=0).where(ds.TLAT <= -30.).weighted(ds.TAREA).mean(dim=['nlat', 'nlon'])
    sosst_list.append(sosst)

sosst_full = xr.concat(sosst_list, dim='time')
sosst_full.to_netcdf(save_path+'HRCESM-SOSST-full.nc')