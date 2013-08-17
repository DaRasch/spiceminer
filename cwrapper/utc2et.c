#include "CustomSpice.h"

char* utc2et_custom(char* time_string, double* et) {
    SpiceDouble et_spice;
    utc2et_c(time_string, &et_spice);
    CHECK_EXCEPTION
    *et = (double) et_spice;
    FINALIZE
}
