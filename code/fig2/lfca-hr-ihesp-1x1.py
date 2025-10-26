#!/glade/u/apps/opt/conda/envs/npl/bin/python
#PBS -N lfca
#PBS -A XXXX####
#PBS -j oe
#PBS -k eod
#PBS -q main@desched1
#PBS -l walltime=12:00:00
#PBS -l select=1:ncpus=128:mpiprocs=128

import sys
sys.path.append('/glade/u/home/rford2/ihesp')

import numpy as np
import xarray as xr
import pandas as pd
from signal_processing import lfca # This file can be downloaded at https://github.com/rcjwills/lfca

save_path = '/glade/derecho/scratch/rford2/'

#############
# Functions #
#############

def detrend_dim(da, dim, deg=1):
    p = da.polyfit(dim=dim, deg=deg)
    fit = xr.polyval(da[dim], p.polyfit_coefficients)
    return da - fit

######################
# Load and prep data #
######################

ds1 = xr.open_dataset('/glade/derecho/scratch/rford2/ihesp-regrid/HR-SST/iHESP-HR.PICTRL.SST.1x1.150-520.nc').rename({'nlat': 'lat', 'nlon': 'lon'}).set_index(lat='lat', lon='lon')
ds2 = xr.open_dataset('/glade/derecho/scratch/rford2/ihesp-regrid/HR-SSS/iHESP-HR.PICTRL.SSS.1x1.150-520.nc').rename({'nlat': 'lat', 'nlon': 'lon'}).set_index(lat='lat', lon='lon')

t = ds1.TEMP.isel(z_t=0).squeeze()
s = ds2.SALT.isel(z_t=0).squeeze()
t_clim = t.groupby('time.month')
ta_full = t_clim - t_clim.mean(dim='time')
ta_full = detrend_dim(ta_full, 'time', deg=1)
# ta_full = ta_full.coarsen(lat=2, lon=2).mean()

s_clim = s.groupby('time.month')
sa_full = s_clim - s_clim.mean(dim='time')
sa_full = detrend_dim(sa_full, 'time', deg=1)
# sa_full = sa_full.coarsen(lat=2, lon=2).mean()

# ta_eq = ta_full.where((ta_full.lat < 30) & (ta_full.lat > -30), drop=True) # Tropics
ta_se = ta_full.where(ta_full.lat < -30, drop=True) # SH extratropics
# ta_nne = ta_full.where(ta_full.lat < 30, drop=True) # Not NH extratropics (i.e. se + eq)
# ta_nse = ta_full.where(ta_full.lat > -30, drop=True) # Not SH extratropics

# sa_eq = sa_full.where((sa_full.lat < 30) & (sa_full.lat > -30), drop=True)
sa_se = sa_full.where(sa_full.lat < -30, drop=True)
# sa_nne = sa_full.where(sa_full.lat < 30, drop=True)
# sa_nse = sa_full.where(sa_full.lat > -30, drop=True)

# Choose domain
ta = ta_se
sa = sa_se

# Normalize
ta = ta/ta.std()
sa = sa/sa.std()

# Flatten
ta_stack = ta.stack(loc=('lat', 'lon'), create_index=False).load()
sa_stack = sa.stack(loc=('lat', 'lon'), create_index=False).load()
# Joint anomalies
ja_stack = xr.concat([ta_stack, sa_stack], dim='loc')

# To reconstruct lat/lon structure after analysis
ta_stack_multiindex = ta.stack(loc=('lat', 'lon'))
sa_stack_multiindex = sa.stack(loc=('lat', 'lon'))
ja_stack_multiindex = xr.concat([ta_stack_multiindex, sa_stack_multiindex], dim='loc')

# Remove NaNs corresponding to land regions (this is the final processed data)
ja_proc = ja_stack.dropna(dim='loc', how='any')
ja_proc_mi = ja_stack_multiindex.dropna(dim='loc', how='any')

# Weights
coslat = np.cos(np.deg2rad(ja_proc.lat))
normvec = coslat/coslat.sum()
scale = np.sqrt(normvec)
scale = np.reshape(scale.values, (scale.values.size, 1))

############
# Analysis #
############

cutoff = 120 # months, i.e., 10 years
truncation = 30 # modes to keep

lfcs, lfps, weights, r, pvar, pcs, eofs, ntr, pvar_slow, pvar_lfc, r_eofs, pvar_slow_eofs = lfca(ja_proc.values, cutoff, truncation, scale)

############################
# Reshape and save results #
############################

nloc = ja_proc_mi.sizes['loc']
half_nloc = nloc // 2

ta_proc_ds = ja_proc_mi.isel(loc=slice(0, half_nloc)).to_dataset(name='SSTA')
sa_proc_ds = ja_proc_mi.isel(loc=slice(half_nloc, nloc)).to_dataset(name='SSSA')

ta_proc_ds['LFP'] = (['mode', 'loc'], np.real(lfps[:, 0:half_nloc]))
ta_proc_ds['EOF'] = (['mode', 'loc'], np.real(eofs[0:30, 0:half_nloc]))
ta_proc_ds['LFC'] = (['time', 'mode'], np.real(lfcs))
ta_proc_ds['PC'] = (['time', 'mode'], np.real(pcs[:, 0:30]))
ta_proc_ds['LFC_ETV'] = (['mode'], np.real(pvar_lfc))
ta_proc_ds['LFC_ESV'] = (['mode'], np.real(pvar_slow))
ta_proc_ds['EOF_ETV'] = (['mode'], np.real(pvar[0:30]))
ta_proc_ds['EOF_ESV'] = (['mode'], np.real(pvar_slow_eofs[0:30]))

sa_proc_ds['LFP'] = (['mode', 'loc'], np.real(lfps[:, half_nloc:nloc]))
sa_proc_ds['EOF'] = (['mode', 'loc'], np.real(eofs[0:30, half_nloc:nloc]))
sa_proc_ds['LFC'] = (['time', 'mode'], np.real(lfcs))
sa_proc_ds['PC'] = (['time', 'mode'], np.real(pcs[:, 0:30]))
sa_proc_ds['LFC_ETV'] = (['mode'], np.real(pvar_lfc))
sa_proc_ds['LFC_ESV'] = (['mode'], np.real(pvar_slow))
sa_proc_ds['EOF_ETV'] = (['mode'], np.real(pvar[0:30]))
sa_proc_ds['EOF_ESV'] = (['mode'], np.real(pvar_slow_eofs[0:30]))

ta_lfca = ta_proc_ds.unstack()
sa_lfca = sa_proc_ds.unstack()

_full_lfca_ds = xr.concat([ta_lfca, sa_lfca], pd.Index(['SST', 'SSS'], name='var')).drop_vars(['SSTA', 'month', 'z_t'])
_full_lfca_ds['SSTA'] = ta_lfca.SSTA
_full_lfca_ds['SSSA'] = sa_lfca.SSSA
full_lfca_ds = _full_lfca_ds.drop_vars(['month', 'z_t'])

full_lfca_ds.to_netcdf(save_path+'iHESP-HR.PICTRL.NSO-JLFCA.1x1.nc')