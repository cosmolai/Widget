
#include <stdio.h>
#include <stdlib.h>

unsigned char Buffer[0x2000000] = {0};

void main ()
{
  FILE *file;
  unsigned int count;
  unsigned char c;
  unsigned int filesize;
  unsigned int baseaddress;

  file = NULL;
  file = fopen ("IclSystemFwMono_406291.Cap", "rb");

  if (file == NULL) {
    printf ("Open file fails.\n");
    return;
  }
  count = 0;
  while (1) {
    c = fgetc (file);
    if (feof (file)) {
      break;
    }
    Buffer[count++] = c;
  }
  fclose (file);
  filesize = count;
  baseaddress = (unsigned int)Buffer;

  printf ("File Size: %X\n", filesize);

  {
    unsigned int Index;
    unsigned int CkSum;
    CkSum = 0;
    for (Index = 0; Index + 3 < filesize; Index += 4) {
      CkSum += *(unsigned int *)(baseaddress + Index);
    }
    printf ("Buffer checksum = %X\n", CkSum);
  }

  {
    unsigned int padding;
    file = fopen ("outimage.bin", "wb");
    if (file == NULL) {
      printf ("Open file fails.\n");
      return;
    }
    padding = (filesize + 0xFFF) & 0xFFFFF000;
    printf ("padding: %X\n", padding);
    for (count = 0; count < padding; count++) {
      fputc (Buffer[count], file);
    }
    fclose (file);
  }
}