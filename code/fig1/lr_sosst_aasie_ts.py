#!/glade/u/apps/opt/conda/envs/npl/bin/python
#PBS -N lr_ts
#PBS -A XXXX####
#PBS -j oe
#PBS -k eod
#PBS -q main@desched1
#PBS -l walltime=02:00:00
#PBS -l select=1:ncpus=128:mpiprocs=128

import glob, os
import numpy as np
import xarray as xr

save_path = '/glade/u/home/rford2/ihesp/'
lr_ocn_path = '/glade/campaign/collections/rda/data/d651030/PIcntl/B.E.13.B1850C5.ne30_g16.sehires38.003.sunway/ocn/proc/tseries/month_1/'
lr_ice_path = '/glade/campaign/collections/rda/data/d651030/PIcntl/B.E.13.B1850C5.ne30_g16.sehires38.003.sunway/ice/proc/tseries/month_1/'

sosst_list = []
for file in sorted(glob.glob(os.path.join(lr_ocn_path, '*.TEMP.*'))):
    dso = xr.open_dataset(file)
    sosst = dso.TEMP.isel(z_t=0).where(dso.TLAT <= -30.).weighted(dso.TAREA).mean(dim=['nlat', 'nlon']).compute()
    sosst_list.append(sosst)
    dso.close()

aasie_list = []
for file in sorted(glob.glob(os.path.join(lr_ice_path, '*.aice.*'))):
    dsi = xr.open_dataset(file)
    aasie = dsi.tarea.where((dsi.TLAT < 0) & (dsi.aice >= 15)).sum(dim=['ni', 'nj']).compute()
    aasie_list.append(aasie)
    dsi.close()
    
sosst_full = xr.concat(sosst_list, dim='time')
sosst_full.to_netcdf(save_path+'LRCESM-SOSST-full.nc')

aasie_full = xr.concat(aasie_list, dim='time')
aasie_full.to_netcdf(save_path+'LRCESM-AASIE-full.nc')