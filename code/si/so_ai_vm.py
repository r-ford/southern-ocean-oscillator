#!/glade/u/apps/opt/conda/envs/npl/bin/python
#PBS -N so_vm
#PBS -A UALB0048
#PBS -j oe
#PBS -k oe 
#PBS -q main@desched1
#PBS -l walltime=8:00:00
#PBS -l select=1:ncpus=1:mpiprocs=128

# Calculate Atlantic--Indian sector SO vertical-mean of variable `var_name`

import glob, os
import numpy as np
import xarray as xr

def so_ai(da):
    region = da.where((da.TLAT <= -30) & ((da.TLONG >= 360-70) | (da.TLONG <= 80)), drop=True)
    return region

save_path = '/glade/derecho/scratch/rford2/ihesp-gn/'
hr_path = '/glade/campaign/collections/rda/data/d651029/B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02/ocn/proc/tseries/month_1/'

var_name = 'TEMP'

ds_list = []
for file in sorted(glob.glob(os.path.join(hr_path, 'B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02.pop.h.'+var_name+'.*'))):
    ds = xr.open_dataset(file)
    so_ai_vm = so_ai(ds[var_name]).isel(z_t=slice(0, 20)).mean(dim=['z_t'], skipna=True).compute()
    ds_list.append(so_ai_vm)
    ds.close()

ds_vm = xr.concat(ds_list, dim='time')
ds_vm.to_netcdf(save_path+'HRCESM-70W80ESO-0020VM'+var_name+'-full.nc')
