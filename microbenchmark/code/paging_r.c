#include <stdio.h>
#include <stdlib.h>

#include <unistd.h>
#include <sys/resource.h>
#include <sys/times.h>
#include <sys/types.h>
#include <time.h>
#include <limits.h>


double get_seconds () {         /* routine to read time */
    struct tms rusage;
    times(&rusage);             /* time in clock ticks */
    return (double) (rusage.tms_utime)/sysconf(_SC_CLK_TCK);
}


int main (int argc, char *argv[]) {

    //#define MB_COUNT (2048)
    unsigned long long MB_COUNT = (unsigned long long)atoi(argv[1]);
    #define MB_BYTE (1024 * 1024)

    /* 4bytes * 256 = 1KB */

    const unsigned long long byte_count = (unsigned long long)MB_BYTE * MB_COUNT;
    const unsigned long long max_idx = byte_count/sizeof(unsigned long long) - 1;
    unsigned long long *ptr_start = NULL;
    unsigned long long idx = 0;
    unsigned long long *ptr = NULL;
    double sec;
    unsigned long long tmp = 0;

    printf("Try to malloc %llu MB...\n", byte_count/MB_BYTE);
    ptr_start = ptr = (unsigned long long*) malloc(byte_count);

    if( ptr == NULL ) {
        printf("malloc %lluMB failed\n", byte_count/MB_COUNT);
    } else {
        printf("Ptr start = %p; addr = %p; max_idx=%llu\n", ptr_start, ptr, max_idx);
    }
    
    printf("unsigned long long siez:%d\n", sizeof(unsigned long long));

    sec = get_seconds();
    for (idx = 0; idx <= max_idx; idx++, ptr++) {
        tmp = *ptr;
    }
    sec = get_seconds() - sec;

    printf ("Sec = %6.3f \n", sec);
    printf("Write Only ");

    free(ptr_start);
    printf("Complete\n");
    return 0;
}
