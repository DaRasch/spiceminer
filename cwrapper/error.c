#include "CustomSpice.h"

/* Get/set action to perform on error */
char* erract_custom(char* op, char* action) {
    erract_c(op, STR_LEN_MAX, action);
    /* If this method fails, it is irrelevant, that no errors are caught */
    FINALIZE
}

/* Get/set device to print error to */
char* errdev_custom(char* op, char* device) {
    errdev_c(op, STR_LEN_MAX, device);
    CHECK_EXCEPTION
    FINALIZE
}
