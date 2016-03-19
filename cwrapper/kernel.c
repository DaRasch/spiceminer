#include "CustomSpice.h"

/* Get kernel architecture and type */
char* getfat_custom(char* path, int arclen, int typlen, char* arch, char* type) {
    getfat_c(path, arclen, typlen, arch, type);
    CHECK_EXCEPTION
    FINALIZE
}

/* Load kernel */
char* furnsh_custom(char* path) {
    furnsh_c(path);
    CHECK_EXCEPTION
    FINALIZE
}

/* Unload kernel */
char* unload_custom(char* path) {
    unload_c(path);
    CHECK_EXCEPTION
    FINALIZE
}

/* Find all IDs in a spk file */
char* spkobj_custom(char* path, SpiceCell* ids) {
    spkobj_c(path, ids);
    CHECK_EXCEPTION
    FINALIZE
}

/* Get coverage window for an object in a spk file */
char* spkcov_custom(char* path, int idcode, SpiceCell* cover) {
    spkcov_c(path, idcode, cover);
    CHECK_EXCEPTION
    FINALIZE
}

/* Find all IDs in a ck file */
char* ckobj_custom(char* path, SpiceCell* ids) {
    ckobj_c(path, ids);
    CHECK_EXCEPTION
    FINALIZE
}

/* Get coverage window for an object in a ck file */
char* ckcov_custom(char* path, int idcode, SpiceCell* cover) {
    ckcov_c(path, idcode, SPICEFALSE, "SEGMENT", 0.0, "TDB", cover);
    CHECK_EXCEPTION
    FINALIZE
}

/* Find all frames in a spk file */
char* pckfrm_custom(char* path, SpiceCell* ids) {
    pckfrm_c(path, ids);
    CHECK_EXCEPTION
    FINALIZE
}

/* Get coverage window for an object in a spk file */
char* pckcov_custom(char* path, int idcode, SpiceCell* cover) {
    pckcov_c(path, idcode, cover);
    CHECK_EXCEPTION
    FINALIZE
}
