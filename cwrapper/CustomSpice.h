#include "SpiceUsr.h"
#include <stdlib.h>

/* constants */
#define STR_LEN 256
#define STR_LEN_MAX 2048
#define ERROR_LEN 26


/* Every function MUST return the error message */

#define CHECK_EXCEPTION {\
    if(failed_c()) {\
        char* message = malloc(sizeof(char) * STR_LEN_MAX);\
        getmsg_c("LONG", STR_LEN_MAX, message);\
        reset_c();\
        return message;\
    }\
}

#define FINALIZE {\
    return NULL;\
}
