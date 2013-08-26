#include "CustomSpice.h"

/* Convert UTC string to ephimeris time (et) */
/* Unused and deprecated */
char* utc2et_custom(char* time_string, double* et) {
    SpiceDouble et_spice;
    utc2et_c(time_string, &et_spice);
    CHECK_EXCEPTION
    *et = (double) et_spice;
    FINALIZE
}

/* Convert seconds since 2000 to ephimeris time (et) */
char* deltet_custom(double epoch, char* eptype, double* delta) {
    SpiceDouble delta_spice;
    deltet_c(epoch, eptype, &delta_spice);
    CHECK_EXCEPTION
    *delta = (double) delta_spice;
    FINALIZE
}

/* Convert between time formats */
char* unitim_custom(double* et, char* insys, char* outsys) {
    SpiceDouble et_spice = unitim_c(*et, insys, outsys);
    CHECK_EXCEPTION
    *et = (double) et_spice;
    FINALIZE
}
