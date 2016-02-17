#include "CustomSpice.h"

char* spkpos_custom(char* target, double et, char* ref, char* abcorr, char* observer, double starg[3], double* lt) {
    SpiceDouble lt_spice;
    spkpos_c(target, et, ref, abcorr, observer, starg, &lt_spice);
    CHECK_EXCEPTION
    *lt = (double) lt_spice;
    FINALIZE
}

char* spkezr_custom(char* target, double et, char* ref, char* abcorr, char* observer, double starg[6], double* lt) {
    //SpiceDouble* starg_spice = malloc(sizeof(SpiceDouble) * 6);
    SpiceDouble lt_spice;
    spkezr_c(target, et, ref, abcorr, observer, starg, &lt_spice);
    CHECK_EXCEPTION
    //*starg = (double) starg_spice;
    *lt = (double) lt_spice;
    FINALIZE
}

char* ckgp_custom(int spacecraft_id, int instrument_id, double et, double tol, char* ref, double cmat[3][3], double* clkout, int* found){
    /* convert Ephimeris Time to Space Craft Clock String */
    SpiceChar clk_str[30];
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

/* Calculate transform matrix between frames */
char* pxform_custom(char* from, char* to, double et, double rotate[3][3]) {
    pxform_c(from, to, et, rotate);
    CHECK_EXCEPTION
    FINALIZE
}

/* Get field of view (VOW) of an instrument */
char* getfov_custom(int instrument_id, char shape[16], char frame[64], double boresight[3], int* n, double bounds[8][3]) {
    getfov_c(instrument_id, 8, 16, 64, shape, frame, boresight, n, bounds);
    CHECK_EXCEPTION
    FINALIZE
}

char* fovtrg_custom(char* inst, char* target, char* tshape, char* tframe, char* abcorr, char* observer, double* et, int* visible) {
    fovtrg_c(inst, target, tshape, tframe, abcorr, observer, et, visible);
    CHECK_EXCEPTION
    FINALIZE
}
