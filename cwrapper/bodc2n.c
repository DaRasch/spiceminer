#include "CustomSpice.h"

char* bodc2n_custom(int code, char* name, int* found) {
    name = malloc(sizeof(char) * STR_LEN);
    SpiceBoolean found_spice;
    bodc2n_c(code, STR_LEN, name, &found_spice);
    CHECK_EXCEPTION
    *found = (int)found_spice;
    FINALIZE
}
