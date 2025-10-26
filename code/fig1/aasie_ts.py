#!/glade/u/apps/opt/conda/envs/npl/bin/python
#PBS -N aasie
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
hr_path = '/glade/campaign/collections/rda/data/d651029/B.E.13.B1850C5.ne120_t12.sehires38.003.sunway_02/ice/proc/tseries/month_1/'

aasie_list = []
for file in sorted(glob.glob(os.path.join(hr_path, '*.aice.*'))):
    ds = xr.open_dataset(file)
    aasie = ds.tarea.where((ds.TLAT < 0) & (ds.aice >= 15)).sum(dim=['ni', 'nj']).compute()
    aasie_list.append(aasie)
    ds.close()

aasie_full = xr.concat(aasie_list, dim='time')
aasie_full.to_netcdf(save_path+'HRCESM-AASIE-full.nc')