#include "CustomSpice.h"

char* bodn2c_custom(char* name, int* code, int* found) {
    SpiceInt code_spice;
    SpiceBoolean found_spice;
    bodn2c_c(name, &code_spice, &found_spice);
    CHECK_EXCEPTION
    *code = (int)code_spice;
    *found = (int)found_spice;
    FINALIZE
}
