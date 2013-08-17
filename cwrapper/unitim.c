#include "CustomSpice.h"

char* unitim_custom(double* et, char* insys, char* outsys) {
    SpiceDouble et_spice = unitim_c(*et, insys, outsys);
    CHECK_EXCEPTION
    *et = (double) et_spice;
    FINALIZE
}
