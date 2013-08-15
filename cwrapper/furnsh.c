#include "CustomSpice.h"

char* furnsh_custom(char* path) {
    furnsh_c(path);
    CHECK_EXCEPTION
    FINALIZE
}
