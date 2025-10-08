import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import patches
from astropy.table import Table


from astroquery.gaia import Gaia
Gaia.MAIN_GAIA_TABLE = "gaiadr.gaia_source"  # Select Data Release 

# Define and execute the ADQL query to crossmatch with 2MASS
query = f"""
SELECT gaia.source_id, gaia.ra AS g_ra, gaia.dec AS g_dec, gaia.parallax, gaia.pmra, gaia.pmdec, tmass.*
FROM gaiadr3.gaia_source AS gaia
JOIN gaiadr3.tmass_psc_xsc_best_neighbour AS xmatch USING (source_id)
JOIN gaiadr3.tmass_psc_xsc_join AS xjoin USING (clean_tmass_psc_xsc_oid)
JOIN gaiadr1.tmass_original_valid AS tmass ON
   xjoin.original_psc_source_id = tmass.designation
WHERE DISTANCE(289.074, -16.323, gaia.ra, gaia.dec) < 1.
AND phot_g_mean_mag < 14
"""

job = Gaia.launch_job(query)
gaiadr_match = job.get_results()
print(f"Number of matched sources: {len(gaiadr_match)}")
# Save the results to a file
gaiadr_match.write("gaiadr3_2mass_crossmatch.fits", format="fits", overwrite=True)

bad_pho =[] #create placeholder list for source_id with bad photometric quality

for i in range(len(gaiadr_match)):
    if gaiadr_match['ph_qual'][i] != 'AAA':
        bad_pho.append(gaiadr_match['source_id'][i]) #loop to find bad photometric quality source_id

print(bad_pho)

neg_par = [] #create placeholder list for source_id with non-positive parallax

for i in range(len(gaiadr_match)):
    if gaiadr_match['parallax'][i] <= 0:
        neg_par.append(gaiadr_match['source_id'][i]) #loop to find non-positive parallax source_id

print(neg_par)

mask = ~np.isin(gaiadr_match['source_id'], bad_pho) #create mask to filter out bad photometric quality source_id

stage_1_filter = gaiadr_match[mask] #cutting bad photometric quality stars from table

mask2 = mask = ~np.isin(stage_1_filter['source_id'], neg_par) #create mask to filter out non-positive parallax source_id

filtered_result = stage_1_filter[mask2] #cutting non-positive parallax stars from table

print(f"Number of stars after cutting: {len(filtered_result)}")
