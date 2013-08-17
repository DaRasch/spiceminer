#include "CustomSpice.h"

char* spkezr_custom(char* target, double et, char* ref, char* abcorr, char* observer, double starg[6], double* lt) {
    //SpiceDouble* starg_spice = malloc(sizeof(SpiceDouble) * 6);
    SpiceDouble lt_spice;
    spkezr_c(target, et, ref, abcorr, observer, starg, &lt_spice);
    CHECK_EXCEPTION
    //*starg = (double) starg_spice;
    *lt = (double) lt_spice;
    FINALIZE
}
