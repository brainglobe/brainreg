/*
  NrrdIO: stand-alone code for basic nrrd functionality
  Copyright (C) 2008, 2007, 2006, 2005  Gordon Kindlmann
  Copyright (C) 2004, 2003, 2002, 2001, 2000, 1999, 1998  University of Utah
 
  This software is provided 'as-is', without any express or implied
  warranty.  In no event will the authors be held liable for any
  damages arising from the use of this software.
 
  Permission is granted to anyone to use this software for any
  purpose, including commercial applications, and to alter it and
  redistribute it freely, subject to the following restrictions:
 
  1. The origin of this software must not be misrepresented; you must
     not claim that you wrote the original software. If you use this
     software in a product, an acknowledgment in the product
     documentation would be appreciated but is not required.
 
  2. Altered source versions must be plainly marked as such, and must
     not be misrepresented as being the original software.
 
  3. This notice may not be removed or altered from any source distribution.
*/

#include "NrrdIO.h"

void
demoIO(char *filename) {
  char me[]="demoIO", newname[]="foo.nrrd", *err, *key, *val;
  int kvn, kvi;
  Nrrd *nin;

  /* create a nrrd; at this point this is just an empty container */
  nin = nrrdNew();

  /* read in the nrrd from file */
  if (nrrdLoad(nin, filename, NULL)) {
    err = biffGetDone(NRRD);
    fprintf(stderr, "%s: trouble reading \"%s\":\n%s", me, filename, err);
    free(err);
    return;
  }

  /* say something about the array */
  printf("%s: \"%s\" is a %d-dimensional nrrd of type %d (%s)\n", 
         me, filename, nin->dim, nin->type,
         airEnumStr(nrrdType, nin->type));
  printf("%s: the array contains %d elements, each %d bytes in size\n",
         me, (int)nrrdElementNumber(nin), (int)nrrdElementSize(nin));

  /* print out the key/value pairs present */
  kvn = nrrdKeyValueSize(nin);
  if (kvn) {
    for (kvi=0; kvi<kvn; kvi++) {
      nrrdKeyValueIndex(nin, &key, &val, kvi);
      printf("%s: key:value %d = %s:%s\n", me, kvi, key, val);
      free(key); free(val);
      key = val = NULL;
    }
  }

  /* modify key/value pairs, and write out the nrrd to a different file */
  nrrdKeyValueClear(nin);
  nrrdKeyValueAdd(nin, "new key", "precious value");
  if (nrrdSave(newname, nin, NULL)) {
    err = biffGetDone(NRRD);
    fprintf(stderr, "%s: trouble writing \"%s\":\n%s", me, newname, err);
    free(err);
    return;
  }

  /* blow away both the Nrrd struct *and* the memory at nin->data
     (nrrdNix() frees the struct but not the data,
     nrrdEmpty() frees the data but not the struct) */
  nrrdNuke(nin);

  return;
}

int
main(int argc, char **argv) {
  char *err;

  fprintf(stderr, "(from Teem %s, %s)\n", 
          airTeemVersion, airTeemReleaseDate);

  if (!nrrdSanity()) {
    fprintf(stderr, "\n");
    fprintf(stderr, "!!! nrrd sanity check FAILED: fix and re-compile\n");
    err = biffGet(NRRD);
    fprintf(stderr, "%s\n", err);
    free(err); 
    return 1;
  } else {
    fprintf(stderr, "(nrrdSanity check passed)\n\n");
  }

  if (2 != argc) {
    fprintf(stderr, "usage: demoIO <filename>\n");
    return 1;
  }

  demoIO(argv[1]);

  return 0;
}
