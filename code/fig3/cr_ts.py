#!/glade/u/apps/opt/conda/envs/npl/bin/python
#PBS -N cr
#PBS -A XXXX####
#PBS -j oe
#PBS -k eod
#PBS -q main@desched1
#PBS -l walltime=12:00:00
#PBS -l select=1:ncpus=1:mpiprocs=128

# Calculate variable over convective region (CONV)

import glob, os
import numpy as np
import xarray as xr

save_path = '/glade/u/home/rford2/ihesp/data/'
hr_path = '/glade/campaign/collections/rda/data/d651029/B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02/ocn/proc/tseries/month_1/'

crmask_ds = xr.open_dataset(save_path+'HRCESM-CRMASK.nc')
crmask = crmask_ds.conv_region

var = 'SALT'

cr_list = []
for file in sorted(glob.glob(os.path.join(hr_path, 'B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02.pop.h.'+var+'.*'))):
    ds = xr.open_dataset(file)
    cr = ds[var].isel(z_t=slice(0, 10)).mean(dim='z_t').where(crmask).weighted(ds.TAREA).mean(dim=['nlat', 'nlon'], skipna=True).compute()
    cr_list.append(cr)
    ds.close()

cr_full = xr.concat(cr_list, dim='time')
cr_full.to_netcdf(save_path+'HRCESM-CR'+var+'100m.nc')