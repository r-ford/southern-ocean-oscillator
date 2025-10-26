#!/glade/u/apps/opt/conda/envs/npl/bin/python
#PBS -N so_zm
#PBS -A UALB0048
#PBS -j oe
#PBS -k oe 
#PBS -q main@desched1
#PBS -l walltime=4:00:00
#PBS -l select=1:ncpus=1:mpiprocs=128

# Calculate Atlantic--Indian sector SO zonal-mean of variable `var_name`

import glob, os
import numpy as np
import xarray as xr

def region(da):
    region = da.where((da.TLAT <= -30) & ((da.TLONG >= 360-60) | (da.TLONG <= 60)), drop=True)
    return region
    
save_path = '/glade/derecho/scratch/rford2/ihesp-gn/'
hr_path = '/glade/campaign/collections/rda/data/d651029/B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02/ocn/proc/tseries/month_1/'

var_name = 'TEMP'

ds_list = []
for file in sorted(glob.glob(os.path.join(hr_path, 'B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02.pop.h.'+var_name+'.*'))):
    ds = xr.open_dataset(file)
    region_zm = region(ds[var_name]).mean(dim=['nlon'], skipna=True)
    ds_list.append(region_zm)
    ds.close()

ds_zm = xr.concat(ds_list, dim='time')
ds_zm.to_netcdf(save_path+'HRCESM-60W60ESO-ZM'+var_name+'-full.nc')