#include "SpiceUsr.h"
#include <stdlib.h>

/* constants */
#define STR_LEN 256
#define ERROR_LEN 26
#define STR_LEN_MAX 2000


/* Every function MUST return the error message */

#define CHECK_EXCEPTION {\
    if(failed_c()) {\
        char* message = malloc(sizeof(char) * ERROR_LEN);\
        getmsg_c("short", ERROR_LEN, message);\
        reset_c();\
        return message;\
    }\
}

#define FINALIZE {\
    return NULL;\
}
