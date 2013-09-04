#include "CustomSpice.h"

char* bodc2n_custom(int code, char* name, int* found) {
    /* name = malloc(sizeof(char) * STR_LEN); */
    SpiceBoolean found_spice;
    bodc2n_c(code, STR_LEN, name, &found_spice);
    CHECK_EXCEPTION
    *found = (int)found_spice;
    FINALIZE
}

char* bodn2c_custom(char* name, int* code, int* found) {
    SpiceInt code_spice;
    SpiceBoolean found_spice;
    bodn2c_c(name, &code_spice, &found_spice);
    CHECK_EXCEPTION
    *code = (int)code_spice;
    *found = (int)found_spice;
    FINALIZE
}

char* namfrm_custom(char* name, int* code) {
    SpiceInt code_spice;
    namfrm_c(name, &code_spice);
    CHECK_EXCEPTION
    *code = (int)code_spice;
    FINALIZE
}
