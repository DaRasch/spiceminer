#include "CustomSpice.h"

char* deltet_custom(double epoch, char* eptype, double* delta) {
    SpiceDouble delta_spice;
    deltet_c(epoch, eptype, &delta_spice);
    CHECK_EXCEPTION
    *delta = (double) delta_spice;
    FINALIZE
}
