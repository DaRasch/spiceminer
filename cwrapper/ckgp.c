#include "SpiceUsr.h"

void ckgp_c2(int spacecraft_id, int instrument_id, double et, double tol, char* ref, double cmat[3][3], double* clkout, int* found){
    /* convert Ephimeris Time to Space Craft Clock String */
    SpiceChar* clk_str = 0;
    sce2s_c(spacecraft_id, et, 30, clk_str);
    /* convert Space Craft Clock String to double */
    SpiceDouble clk_double;
    scencd_c(spacecraft_id, clk_str, &clk_double);
    /* get matrix */
    SpiceDouble clkout_spice;
    SpiceBoolean found_spice;
    ckgp_c(instrument_id, clk_double, tol, ref, cmat, &clkout_spice, &found_spice);
    /* Convert back to sane formats */
    *clkout = (double) clkout_spice;
    *found = (int) found_spice;
    /* XXX: errors on failure or not found? */
}
