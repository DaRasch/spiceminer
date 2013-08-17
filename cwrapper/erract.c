#include "CustomSpice.h"

char* erract_custom(char* op, char* action) {
    erract_c(op, STR_LEN_MAX, action);
    /* If this method fails, it is irrelevant, that no errors are catched */
    FINALIZE
}
