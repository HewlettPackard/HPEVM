#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#define handle_error(msg) \
    do { perror(msg); exit(EXIT_FAILURE); } while (0)
int
main(int argc, char *argv[])
{
    char *addr;
    int fd;
    struct stat sb;
    off_t offset, pa_offset;
    size_t length;
    ssize_t s;

    if (argc != 2) {
        fprintf(stderr, "%s file \n", argv[0]);
        exit(EXIT_FAILURE);
    }

    fd = open("/proc/sys/vm/drop_caches", O_RDWR);
    if (fd == -1)
        handle_error("open");
    if (fstat(fd, &sb) == -1)           /* To obtain file size */
        handle_error("fstat");
    sync();
    write(fd, "1", 1);


    fd = open(argv[1], O_RDONLY);
    if (fd == -1)
        handle_error("open");
    if (fstat(fd, &sb) == -1)           /* To obtain file size */
        handle_error("fstat");
    
    offset = 0;
    length = sb.st_size;

    addr = mmap(NULL, length, PROT_READ,
                MAP_PRIVATE, fd, pa_offset);
    if (addr == MAP_FAILED)
        handle_error("mmap");
    s = write(STDOUT_FILENO, addr, length);

    if (s != length) {
        if (s == -1)
            handle_error("write");
        fprintf(stderr, "partial write");
        exit(EXIT_FAILURE);
    }
    exit(EXIT_SUCCESS);
}
