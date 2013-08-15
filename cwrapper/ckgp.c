#include "CustomSpice.h"

char* ckgp_custom(int spacecraft_id, int instrument_id, double et, double tol, char* ref, double cmat[3][3], double* clkout, int* found){
    /* convert Ephimeris Time to Space Craft Clock String */
    SpiceChar* clk_str = malloc(sizeof(char) * 30);
    sce2s_c(spacecraft_id, et, 30, clk_str);
    CHECK_EXCEPTION
    /* convert Space Craft Clock String to double */
    SpiceDouble clk_double;
    scencd_c(spacecraft_id, clk_str, &clk_double);
    CHECK_EXCEPTION
    /* get matrix */
    SpiceDouble clkout_spice;
    SpiceBoolean found_spice;
    ckgp_c(instrument_id, clk_double, tol, ref, cmat, &clkout_spice, &found_spice);
    CHECK_EXCEPTION
    /* Convert back to sane formats */
    *clkout = (double) clkout_spice;
    *found = (int) found_spice;
    FINALIZE
}
