#include "CustomSpice.h"

char* errdev_custom(char* op, char* device) {
    errdev_c(op, 2000, device);
    CHECK_EXCEPTION
    FINALIZE
}
