#include "CustomSpice.h"

char* spkezr_custom(char* target, double et, char* ref, char* abcorr, char* observer, double* starg, double* lt) {
    SpiceDouble[6] starg_spice;
    SpiceDouble* lt_spice;
    spkezr_c(target, et, ref, abcorr, observer, starg_spice, lt_spice);
    CHECK_EXCEPTION
    *starg = (double) starg_spice;
    *lt = (double) lt_spice;
    FINALIZE
}
