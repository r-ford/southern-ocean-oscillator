#!/glade/u/apps/opt/conda/envs/npl/bin/python
#PBS -N wgkp
#PBS -A XXXX####
#PBS -j oe
#PBS -k eod
#PBS -q main@desched1
#PBS -l walltime=12:00:00
#PBS -l select=1:ncpus=1:mpiprocs=128

# Calculate variable over WGKP region

import glob, os
import numpy as np
import xarray as xr

def wgkp(da):
    region = da.where((da.TLAT <= -50) & (da.TLAT >= -70) & ((da.TLONG >= 360-40) | (da.TLONG <= 80)), drop=False)
    return region

save_path = '/glade/u/home/rford2/ihesp/data/'
hr_path = '/glade/campaign/collections/rda/data/d651029/B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02/ocn/proc/tseries/month_1/'

var = 'ROFF_F'

cr_list = []
for file in sorted(glob.glob(os.path.join(hr_path, 'B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02.pop.h.'+var+'.*'))):
    ds = xr.open_dataset(file)
    cr = wgkp(ds[var]).weighted(ds.TAREA).mean(dim=['nlat', 'nlon'], skipna=True).compute()
    cr_list.append(cr)
    ds.close()

cr_full = xr.concat(cr_list, dim='time')
cr_full.to_netcdf(save_path+'HRCESM-WGKP'+var+'.nc')
