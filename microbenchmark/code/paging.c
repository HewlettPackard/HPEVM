#include <stdio.h>
#include <stdlib.h>

int main (int argc, char *argv[]) {

    //#define MB_COUNT (2048)
    unsigned int MB_COUNT = atoi(argv[1]);
    #define MB_BYTE (1024 * 1024)

    /* 4bytes * 256 = 1KB */

    const unsigned int byte_count = (unsigned int)MB_BYTE * (unsigned int)MB_COUNT; //10MB
    const unsigned int max_idx = byte_count/sizeof(unsigned int) - 1;
    unsigned int *ptr_start = NULL;
    unsigned int idx = 0;
    unsigned int *ptr = NULL;

    printf("Try to malloc %u MB...\n", byte_count/MB_BYTE);
    ptr_start = ptr = (unsigned int*) malloc(byte_count);

    if( ptr == NULL ) {
        printf("malloc %uMB failed\n", byte_count/MB_COUNT);
    } else {
        printf("Ptr start = %p; addr = %p; max_idx=%u\n", ptr_start, ptr, max_idx);
    }


    for (idx = 0; idx <= max_idx; idx++, ptr++) {
        *ptr = idx;
    }

    printf("Reset addr %p to start = %p; \n", ptr, ptr_start);
    ptr = ptr_start;

    for (idx = 0; idx <= max_idx; idx++, ptr++) {
        if (idx != *ptr) {
            printf("Ptr addr = %p, value = %u; idx = %u\n", ptr, *ptr, idx);
        }

        if (idx == max_idx) {
            printf("The last Ptr addr = %p, value = %u\n", ptr, *ptr);
        }
    }

    free(ptr_start);
    printf("Complete\n");
    return 0;
}
