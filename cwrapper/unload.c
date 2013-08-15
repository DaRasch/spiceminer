#include "CustomSpice.h"

char* unload_custom(char* path) {
    unload_c(path);
    CHECK_EXCEPTION
    FINALIZE
}
