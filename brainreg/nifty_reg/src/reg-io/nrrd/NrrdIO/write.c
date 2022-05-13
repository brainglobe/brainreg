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
#include "privateNrrd.h"

/*
  #include <sys/types.h>
  #include <unistd.h>
*/

int
nrrdIoStateSet(NrrdIoState *nio, int parm, int value) {
  static const char me[]="nrrdIoStateSet";
  

  if (!nio) {
    biffAddf(NRRD, "%s: got NULL pointer", me);
    return 1;
  }
  if (!( AIR_IN_OP(nrrdIoStateUnknown, parm, nrrdIoStateLast) )) {
    biffAddf(NRRD, "%s: identifier %d not in valid range [%d,%d]", me,
             parm, nrrdIoStateUnknown+1, nrrdIoStateLast-1);
    return 1;
  }
  switch (parm) {
  case nrrdIoStateDetachedHeader:
    nio->detachedHeader = !!value;
    break;
  case nrrdIoStateBareText:
    nio->bareText = !!value;
    break;
  case nrrdIoStateCharsPerLine:
    if (value < 40) {
      biffAddf(NRRD, "%s: %d charsPerLine is awfully small", me, value);
      return 1;
    }
    nio->charsPerLine = value;
    break;
  case nrrdIoStateValsPerLine:
    if (value < 4) {
      biffAddf(NRRD, "%s: %d valsPerLine is awfully small", me, value);
      return 1;
    }
    nio->valsPerLine = value;
    break;
  case nrrdIoStateSkipData:
    nio->skipData = !!value;
    break;
  case nrrdIoStateKeepNrrdDataFileOpen:
    nio->keepNrrdDataFileOpen = !!value;
    break;
  case nrrdIoStateZlibLevel:
    if (!( AIR_IN_CL(-1, value, 9) )) {
      biffAddf(NRRD, "%s: zlibLevel %d invalid", me, value);
      return 1;
    }
    nio->zlibLevel = value;
    break;
  case nrrdIoStateZlibStrategy:
    if (!( AIR_IN_OP(nrrdZlibStrategyUnknown, value, nrrdZlibStrategyLast) )) {
      biffAddf(NRRD, "%s: zlibStrategy %d invalid", me, value);
      return 1;
    }
    nio->zlibStrategy = value;
    break;
  case nrrdIoStateBzip2BlockSize:
    if (!( AIR_IN_CL(-1, value, 9) )) {
      biffAddf(NRRD, "%s: bzip2BlockSize %d invalid", me, value);
      return 1;
    }
    nio->bzip2BlockSize = value;
    break;
  default:
    fprintf(stderr, "!%s: PANIC: didn't recognize parm %d\n", me, parm);
    exit(1);
  }
  return 0;
}

int
nrrdIoStateEncodingSet(NrrdIoState *nio, const NrrdEncoding *encoding) {
  static const char me[]="nrrdIoStateEncodingSet";

  if (!( nio && encoding )) {
    if (nio) {
      nio->encoding = nrrdEncodingUnknown;
    }
    biffAddf(NRRD, "%s: got NULL pointer", me);
    return 1;
  }
  if (!encoding->available()) {
    nio->encoding = nrrdEncodingUnknown;
    biffAddf(NRRD, "%s: %s encoding isn't actually available", me,
             encoding->name);
    return 1;
  }
  nio->encoding = encoding;
  return 0;
}

int
nrrdIoStateFormatSet(NrrdIoState *nio, const NrrdFormat *format) {
  static const char me[]="nrrdIoStateFormatSet";

  if (!( nio && format )) {
    if (nio) {
      nio->format = nrrdFormatUnknown;
    }
    biffAddf(NRRD, "%s: got NULL pointer", me);
    return 1;
  }
  if (!format->available()) {
    nio->format = nrrdFormatUnknown;
    biffAddf(NRRD, "%s: %s format isn't actually available", me,
             format->name);
    return 1;
  }
  nio->format = format;
  return 0;
}

/*
** no biff
*/
int
nrrdIoStateGet(NrrdIoState *nio, int parm) {
  static const char me[]="nrrdIoStateGet";
  int value;
  
  if (!nio) {
    /* got NULL pointer */
    return -1;
  }
  if (!( AIR_IN_OP(nrrdIoStateUnknown, parm, nrrdIoStateLast) )) {
    /* got bogus parameter identifier */
    return -1;
  }
  switch (parm) {
  case nrrdIoStateDetachedHeader:
    value = !!nio->detachedHeader;
    break;
  case nrrdIoStateBareText:
    value = !!nio->bareText;
    break;
  case nrrdIoStateCharsPerLine:
    value = nio->charsPerLine;
    break;
  case nrrdIoStateValsPerLine:
    value = nio->valsPerLine;
    break;
  case nrrdIoStateSkipData:
    value = !!nio->skipData;
    break;
  case nrrdIoStateKeepNrrdDataFileOpen:
    value = !!nio->keepNrrdDataFileOpen;
    break;
  case nrrdIoStateZlibLevel:
    value = nio->zlibLevel;
    break;
  case nrrdIoStateZlibStrategy:
    value = nio->zlibStrategy;
    break;
  case nrrdIoStateBzip2BlockSize:
    value = nio->bzip2BlockSize;
    break;
  default:
    fprintf(stderr, "!%s: PANIC: didn't recognize parm %d\n", me, parm);
    exit(1);
  }
  return value;
}

/*
** no biff
*/
const NrrdEncoding *
nrrdIoStateEncodingGet(NrrdIoState *nio) {

  return nio ? nio->encoding : nrrdEncodingUnknown;
}

/*
** no biff
*/
const NrrdFormat *
nrrdIoStateFormatGet(NrrdIoState *nio) {

  return nio ? nio->format : nrrdFormatUnknown;
}

void
_nrrdStrcatSpaceVector(char *str, int spaceDim,
                       const double val[NRRD_SPACE_DIM_MAX]) {
  char buff[AIR_STRLEN_MED];  /* bad Gordon */
  int dd;

  if (AIR_EXISTS(val[0])) {
    strcat(str, "(");
    for (dd=0; dd<spaceDim; dd++) {
      strcpy(buff, "");
      airSinglePrintf(NULL, buff, "%.17g", val[dd]);
      strcat(str, buff);
      sprintf(buff, "%s", dd < spaceDim-1 ? "," : ")");
      strcat(str, buff);
    }
  } else {
    strcat(str, _nrrdNoSpaceVector);
  }
  return;
}

int
_nrrdFieldInteresting(const Nrrd *nrrd, NrrdIoState *nio, int field) {
  int ret;
  unsigned int ai;
  
  if (!( nrrd
         && AIR_IN_CL(1, nrrd->dim, NRRD_DIM_MAX)
         && nio
         && nio->encoding
         && AIR_IN_OP(nrrdField_unknown, field, nrrdField_last) )) {
    return 0;
  }

  ret = 0;
  switch (field) {
  case nrrdField_comment:
    /* comments and key/value pairs are always handled differently (by
       being printed explicity), so they are never "interesting" */
    break;
  case nrrdField_content:
    ret = !!(airStrlen(nrrd->content));
    break;
  case nrrdField_number:
    /* "number" is entirely redundant with "sizes", which is a
       required field.  Absolutely nothing is lost in eliding "number"
       from the header, so "number" is NEVER interesting.  Should this
       judgement later be found in error, this is the one place where
       the policy change can be implemented */
    break;
  case nrrdField_type:
    /* this is vital */
    ret = 1;
    break;
  case nrrdField_block_size:
    ret = (nrrdTypeBlock == nrrd->type);
    break;
  case nrrdField_dimension:
    /* this is vital */
    ret = 1;
    break;
  case nrrdField_space:
    /* its interesting if its known */
    ret = (nrrdSpaceUnknown != nrrd->space);
    break;
  case nrrdField_space_dimension:
    /* its interesting if its non-zero and if space is not known */
    ret = (nrrd->spaceDim > 0 && nrrdSpaceUnknown == nrrd->space);
    break;
  case nrrdField_sizes:
    /* this is vital */
    ret = 1;
    break;
  case nrrdField_spacings:
    for (ai=0; ai<nrrd->dim; ai++) {
      ret |= AIR_EXISTS(nrrd->axis[ai].spacing);
    }
    break;
  case nrrdField_thicknesses:
    for (ai=0; ai<nrrd->dim; ai++) {
      ret |= AIR_EXISTS(nrrd->axis[ai].thickness);
    }
    break;
  case nrrdField_axis_mins:
    for (ai=0; ai<nrrd->dim; ai++) {
      ret |= AIR_EXISTS(nrrd->axis[ai].min);
    }
    break;
  case nrrdField_axis_maxs:
    for (ai=0; ai<nrrd->dim; ai++) {
      ret |= AIR_EXISTS(nrrd->axis[ai].max);
    }
    break;
  case nrrdField_space_directions:
    ret = nrrd->spaceDim > 0;
    break;
  case nrrdField_centers:
    for (ai=0; ai<nrrd->dim; ai++) {
      ret |= (nrrdCenterUnknown != nrrd->axis[ai].center);
    }
    break;
  case nrrdField_kinds:
    for (ai=0; ai<nrrd->dim; ai++) {
      ret |= (nrrdKindUnknown != nrrd->axis[ai].kind);
    }
    break;
  case nrrdField_labels:
    for (ai=0; ai<nrrd->dim; ai++) {
      ret |= !!(airStrlen(nrrd->axis[ai].label));
    }
    break;
  case nrrdField_units:
    for (ai=0; ai<nrrd->dim; ai++) {
      ret |= !!(airStrlen(nrrd->axis[ai].units));
    }
    break;
  case nrrdField_min:
  case nrrdField_max:
    /* these no longer exist in the Nrrd struct; we never write them */
    ret = AIR_FALSE;
    break;
  case nrrdField_old_min:
    ret = AIR_EXISTS(nrrd->oldMin);
    break;
  case nrrdField_old_max:
    ret = AIR_EXISTS(nrrd->oldMax);
    break;
  case nrrdField_endian:
    ret = nio->encoding->endianMatters && 1 < nrrdElementSize(nrrd);
    break;
  case nrrdField_encoding:
    /* this is vital */
    ret = 1;
    break;
  case nrrdField_line_skip:
    ret = nio->lineSkip > 0;
    break;
  case nrrdField_byte_skip:
    ret = nio->byteSkip != 0;
    break;
  case nrrdField_keyvalue:
    /* comments and key/value pairs are always handled differently (by
       being printed explicity), so they are never "interesting" */
    break;
  case nrrdField_sample_units:
    ret = !!airStrlen(nrrd->sampleUnits);
    break;
  case nrrdField_space_units:
    for (ai=0; ai<nrrd->spaceDim; ai++) {
      ret |= !!(airStrlen(nrrd->spaceUnits[ai]));
    }
    break;
  case nrrdField_space_origin:
    /* we're trusting other validity checks to ensure that
       all the coeffs exist or not, together */
    ret = (nrrd->spaceDim > 0 
           && AIR_EXISTS(nrrd->spaceOrigin[0]));
    break;
  case nrrdField_measurement_frame:
    /* we're trusting other validity checks to ensure that
       all the coeffs exist or not, together */
    ret = (nrrd->spaceDim > 0 
           && AIR_EXISTS(nrrd->measurementFrame[0][0]));
    break;
  case nrrdField_data_file:
    /* detached header was either requested or is required */
    ret = (nio->detachedHeader 
           || nio->dataFNFormat
           || nio->dataFNArr->len > 1);
    break;
  }

  return ret;
}

/*
** _nrrdSprintFieldInfo
**
** this prints "<prefix><field>: <info>" into *strP (after allocating it for
** big enough, usually with a stupidly big margin of error), in a form
** suitable to be written to NRRD or other image headers.  This will always
** print something (for valid inputs), even stupid <info>s like
** "(unknown endian)".  It is up to the caller to decide which fields
** are worth writing, via _nrrdFieldInteresting().
**
** NOTE: some of these fields make sense in non-NRRD files (e.g. all
** the per-axis information), but many only make sense in NRRD files.
** This is just one example of NRRD-format-specific stuff that is not
** in formatNRRD.c
*/
void
_nrrdSprintFieldInfo(char **strP, const char *prefix,
                     const Nrrd *nrrd, NrrdIoState *nio, int field) {
  static const char me[]="_nrrdSprintFieldInfo";
  char buff[AIR_STRLEN_MED], *fnb;
  double colvec[NRRD_SPACE_DIM_MAX];
  const char *fs;
  unsigned int ii, dd,
    uintStrlen = 11,
    size_tStrlen = 33,
    doubleStrlen = 513;
  size_t fslen, fdlen, maxl;
  int endi;
  
  if (!( strP && prefix
         && nrrd 
         && AIR_IN_CL(1, nrrd->dim, NRRD_DIM_MAX)
         && AIR_IN_OP(nrrdField_unknown, field, nrrdField_last) )) {
    return;
  }
  if (!_nrrdFieldInteresting(nrrd, nio, field)) {
    *strP = airStrdup("");
  }
  
  fs = airEnumStr(nrrdField, field);
  fslen = strlen(prefix) + strlen(fs) + strlen(": ") + 1;
  switch (field) {
  case nrrdField_comment:
  case nrrdField_keyvalue:
    fprintf(stderr, "%s: CONFUSION: why are you calling me on \"%s\"?\n", me,
            airEnumStr(nrrdField, nrrdField_comment));
    *strP = airStrdup("");
    break;
  case nrrdField_content:
    airOneLinify(nrrd->content);
    *strP = (char *)calloc(fslen + strlen(nrrd->content), sizeof(char));
    sprintf(*strP, "%s%s: %s", prefix, fs, nrrd->content);
    break;
  case nrrdField_number:
    *strP = (char *)calloc(fslen + size_tStrlen, sizeof(char));
    sprintf(*strP, "%s%s: " _AIR_SIZE_T_CNV, prefix, fs, 
            nrrdElementNumber(nrrd));
    break;
  case nrrdField_type:
    *strP = (char *)calloc(fslen + strlen(airEnumStr(nrrdType, nrrd->type)),
                           sizeof(char));
    sprintf(*strP, "%s%s: %s", prefix, fs, airEnumStr(nrrdType, nrrd->type));
    break;
  case nrrdField_block_size:
    *strP = (char *)calloc(fslen + size_tStrlen, sizeof(char));
    sprintf(*strP, "%s%s: " _AIR_SIZE_T_CNV, prefix, fs, nrrd->blockSize);
    break;
  case nrrdField_dimension:
    *strP = (char *)calloc(fslen + uintStrlen, sizeof(char));
    sprintf(*strP, "%s%s: %d", prefix, fs, nrrd->dim);
    break;
  case nrrdField_space:
    *strP = (char *)calloc(fslen + strlen(airEnumStr(nrrdSpace, nrrd->space)),
                           sizeof(char));
    sprintf(*strP, "%s%s: %s", prefix, fs, airEnumStr(nrrdSpace, nrrd->space));
    break;
  case nrrdField_space_dimension:
    *strP = (char *)calloc(fslen + uintStrlen, sizeof(char));
    sprintf(*strP, "%s%s: %d", prefix, fs, nrrd->spaceDim);
    break;
    /* ---- begin per-axis fields ---- */
  case nrrdField_sizes:
    *strP = (char *)calloc(fslen + nrrd->dim*(size_tStrlen + 1), sizeof(char));
    sprintf(*strP, "%s%s:", prefix, fs);
    for (ii=0; ii<nrrd->dim; ii++) {
      sprintf(buff, " " _AIR_SIZE_T_CNV, nrrd->axis[ii].size);
      strcat(*strP, buff);
    }
    break;
  case nrrdField_spacings:
    *strP = (char *)calloc(fslen + nrrd->dim*(doubleStrlen + 1), sizeof(char));
    sprintf(*strP, "%s%s:", prefix, fs);
    for (ii=0; ii<nrrd->dim; ii++) {
      airSinglePrintf(NULL, buff, " %.17g", nrrd->axis[ii].spacing);
      strcat(*strP, buff);
    }
    break;
  case nrrdField_thicknesses:
    *strP = (char *)calloc(fslen + nrrd->dim*(doubleStrlen + 1), sizeof(char));
    sprintf(*strP, "%s%s:", prefix, fs);
    for (ii=0; ii<nrrd->dim; ii++) {
      airSinglePrintf(NULL, buff, " %.17g", nrrd->axis[ii].thickness);
      strcat(*strP, buff);
    }
    break;
  case nrrdField_axis_mins:
    *strP = (char *)calloc(fslen + nrrd->dim*(doubleStrlen + 1), sizeof(char));
    sprintf(*strP, "%s%s:", prefix, fs);
    for (ii=0; ii<nrrd->dim; ii++) {
      airSinglePrintf(NULL, buff, " %g", nrrd->axis[ii].min);
      strcat(*strP, buff);
    }
    break;
  case nrrdField_axis_maxs:
    *strP = (char *)calloc(fslen + nrrd->dim*(doubleStrlen + 1), sizeof(char));
    sprintf(*strP, "%s%s:", prefix, fs);
    for (ii=0; ii<nrrd->dim; ii++) {
      airSinglePrintf(NULL, buff, " %g", nrrd->axis[ii].max);
      strcat(*strP, buff);
    }
    break;
  case nrrdField_space_directions:
    *strP = (char *)calloc(fslen + 
                           nrrd->dim*nrrd->spaceDim*(doubleStrlen 
                                                     + strlen("(,) ")),
                           sizeof(char));
    sprintf(*strP, "%s%s: ", prefix, fs);
    for (ii=0; ii<nrrd->dim; ii++) {
      _nrrdStrcatSpaceVector(*strP, nrrd->spaceDim,
                             nrrd->axis[ii].spaceDirection);
      if (ii < nrrd->dim-1) {
        strcat(*strP, " ");
      }
    }
    break;
  case nrrdField_centers:
    fdlen = 0;
    for (ii=0; ii<nrrd->dim; ii++) {
      fdlen += 1 + airStrlen(nrrd->axis[ii].center 
                             ? airEnumStr(nrrdCenter, nrrd->axis[ii].center)
                             : NRRD_UNKNOWN);
    }
    *strP = (char *)calloc(fslen + fdlen, sizeof(char));
    sprintf(*strP, "%s%s:", prefix, fs);
    for (ii=0; ii<nrrd->dim; ii++) {
      sprintf(buff, " %s",
              (nrrd->axis[ii].center 
               ? airEnumStr(nrrdCenter, nrrd->axis[ii].center)
               : NRRD_UNKNOWN));
      strcat(*strP, buff);
    }
    break;
  case nrrdField_kinds:
    fdlen = 0;
    for (ii=0; ii<nrrd->dim; ii++) {
      fdlen += 1 + airStrlen(nrrd->axis[ii].kind
                             ? airEnumStr(nrrdKind, nrrd->axis[ii].kind)
                             : NRRD_UNKNOWN);
    }
    *strP = (char *)calloc(fslen + fdlen, sizeof(char));
    sprintf(*strP, "%s%s:", prefix, fs);
    for (ii=0; ii<nrrd->dim; ii++) {
      sprintf(buff, " %s",
              (nrrd->axis[ii].kind
               ? airEnumStr(nrrdKind, nrrd->axis[ii].kind)
               : NRRD_UNKNOWN));
      strcat(*strP, buff);
    }
    break;
  case nrrdField_labels:
    fdlen = 0;
    for (ii=0; ii<nrrd->dim; ii++) {
      fdlen += airStrlen(nrrd->axis[ii].label) + 4;
    }
    *strP = (char *)calloc(fslen + fdlen, sizeof(char));
    sprintf(*strP, "%s%s:", prefix, fs);
    for (ii=0; ii<nrrd->dim; ii++) {
      strcat(*strP, " \"");
      if (airStrlen(nrrd->axis[ii].label)) {
        strcat(*strP, nrrd->axis[ii].label);
      }
      strcat(*strP, "\"");
    }
    break;
  case nrrdField_units:
    fdlen = 0;
    for (ii=0; ii<nrrd->dim; ii++) {
      fdlen += airStrlen(nrrd->axis[ii].units) + 4;
    }
    *strP = (char *)calloc(fslen + fdlen, sizeof(char));
    sprintf(*strP, "%s%s:", prefix, fs);
    for (ii=0; ii<nrrd->dim; ii++) {
      strcat(*strP, " \"");
      if (airStrlen(nrrd->axis[ii].units)) {
        strcat(*strP, nrrd->axis[ii].units);
      }
      strcat(*strP, "\"");
    }
    break;
    /* ---- end per-axis fields ---- */
  case nrrdField_min:
  case nrrdField_max:
    /* we're basically a no-op, now that these fields became meaningless */
    *strP = (char *)calloc(fslen + doubleStrlen, sizeof(char));
    sprintf(*strP, "%s%s: 0.0", prefix, fs);
    strcat(*strP, buff);
    break;
  case nrrdField_old_min:
    *strP = (char *)calloc(fslen + doubleStrlen, sizeof(char));
    sprintf(*strP, "%s%s: ", prefix, fs);
    airSinglePrintf(NULL, buff, "%g", nrrd->oldMin);
    strcat(*strP, buff);
    break;
  case nrrdField_old_max:
    *strP = (char *)calloc(fslen + doubleStrlen, sizeof(char));
    sprintf(*strP, "%s%s: ", prefix, fs);
    airSinglePrintf(NULL, buff, "%g", nrrd->oldMax);
    strcat(*strP, buff);
    break;
  case nrrdField_endian:
    if (airEndianUnknown != nio->endian) {
      /* we know a specific endianness because either it was recorded as
         part of "unu make -h", or it was set (and data was possibly
         altered) as part of "unu save" */
      endi = nio->endian;
    } else {
      /* we record our current architecture's endian because we're
         going to writing out data */
      endi = AIR_ENDIAN;
    }
    *strP = (char *)calloc(fslen + strlen(airEnumStr(airEndian, endi)),
                           sizeof(char));
    sprintf(*strP, "%s%s: %s", prefix, fs, airEnumStr(airEndian, endi));
    break;
  case nrrdField_encoding:
    *strP = (char *)calloc(fslen + strlen(nio->encoding->name),
                           sizeof(char));
    sprintf(*strP, "%s%s: %s", prefix, fs, nio->encoding->name);
    break;
  case nrrdField_line_skip:
    *strP = (char *)calloc(fslen + uintStrlen, sizeof(char));
    sprintf(*strP, "%s%s: %d", prefix, fs, nio->lineSkip);
    break;
  case nrrdField_byte_skip:
    *strP = (char *)calloc(fslen + uintStrlen, sizeof(char));
    sprintf(*strP, "%s%s: %ld", prefix, fs, nio->byteSkip);
    break;
  case nrrdField_sample_units:
    airOneLinify(nrrd->sampleUnits);
    *strP = (char *)calloc(fslen + strlen(nrrd->sampleUnits), sizeof(char));
    sprintf(*strP, "%s%s: \"%s\"", prefix, fs, nrrd->sampleUnits);
    break;
  case nrrdField_space_units:
    fdlen = 0;
    for (ii=0; ii<nrrd->spaceDim; ii++) {
      fdlen += airStrlen(nrrd->spaceUnits[ii]) + 4;
    }
    *strP = (char *)calloc(fslen + fdlen, sizeof(char));
    sprintf(*strP, "%s%s:", prefix, fs);
    for (ii=0; ii<nrrd->spaceDim; ii++) {
      strcat(*strP, " \"");
      if (airStrlen(nrrd->spaceUnits[ii])) {
        strcat(*strP, nrrd->spaceUnits[ii]);
      }
      strcat(*strP, "\"");
    }
    break;
  case nrrdField_space_origin:
    *strP = (char *)calloc(fslen + nrrd->spaceDim*(doubleStrlen 
                                                   + strlen("(,) ")),
                           sizeof(char));
    sprintf(*strP, "%s%s: ", prefix, fs);
    _nrrdStrcatSpaceVector(*strP, nrrd->spaceDim, nrrd->spaceOrigin);
    break;
  case nrrdField_measurement_frame:
    *strP = (char *)calloc(fslen + (nrrd->spaceDim*
                                    nrrd->spaceDim*(doubleStrlen 
                                                    + strlen("(,) "))),
                           sizeof(char));
    sprintf(*strP, "%s%s: ", prefix, fs);
    for (dd=0; dd<nrrd->spaceDim; dd++) {
      for (ii=0; ii<nrrd->spaceDim; ii++) {
        colvec[ii] = nrrd->measurementFrame[dd][ii];
      }
      _nrrdStrcatSpaceVector(*strP, nrrd->spaceDim, colvec);
      if (dd < nrrd->spaceDim-1) {
        strcat(*strP, " ");
      }
    }
    break;
  case nrrdField_data_file:
    /* NOTE: this comes last (nrrdField_data_file is the highest-valued
       member of the nrrdField* enum) because the "LIST" form of the
       data file specification requires that the following lines be
       the filenames */
    /* error checking elsewhere: assumes there is data file info */
    if (nio->dataFNFormat) {
      *strP = (char *)calloc(fslen + strlen(nio->dataFNFormat) + 4*uintStrlen,
                             sizeof(char));
      if (nio->dataFileDim == nrrd->dim-1) {
        sprintf(*strP, "%s%s: %s %d %d %d", prefix, fs, nio->dataFNFormat, 
                nio->dataFNMin, nio->dataFNMax, nio->dataFNStep);
      } else {
        sprintf(*strP, "%s%s: %s %d %d %d %d", prefix, fs, nio->dataFNFormat, 
                nio->dataFNMin, nio->dataFNMax, nio->dataFNStep,
                nio->dataFileDim);
      }
    } else if (nio->dataFNArr->len > 1) {
      maxl = 0;
      for (ii=0; ii<nio->dataFNArr->len; ii++) {
        maxl = AIR_MAX(maxl, strlen(nio->dataFN[ii]));
      }
      *strP = (char *)calloc(fslen + strlen(NRRD_LIST_FLAG) 
                             + uintStrlen + nio->dataFNArr->len * (maxl + 1),
                             sizeof(char));
      fnb = (char *)calloc(fslen + strlen(NRRD_LIST_FLAG) 
                           + uintStrlen + maxl + 1,
                           sizeof(char));
      if (nio->dataFileDim == nrrd->dim-1) {
        sprintf(*strP, "%s%s: LIST\n", prefix, fs);
      } else {
        sprintf(*strP, "%s%s: LIST %d\n", prefix, fs, nio->dataFileDim);
      }
      for (ii=0; ii<nio->dataFNArr->len; ii++) {
        sprintf(fnb, "%s%s", nio->dataFN[ii], 
                ii<nio->dataFNArr->len-1 ? "\n" : "");
        strcat(*strP, fnb);
      }
      free(fnb);
    } else {
      /* there is some ambiguity between a "LIST" of length one,
         and a single explicit data filename, but that's harmless */
      *strP = (char *)calloc(fslen + strlen("./") 
                             + strlen(nio->dataFN[0]) + 1,
                             sizeof(char));
      sprintf(*strP, "%s%s: %s%s", prefix, fs, 
              /* this is a favor to older readers that can deal with
                 this NRRD file because its being saved in a NRRD0003
                 (or below) version, so we don't want to confuse them 
                 by not having the old explicit header-relative flag */
              (_nrrdFormatNRRD_whichVersion(nrrd, nio) < 4 ? "./" : ""),
              nio->dataFN[0]);
    }
    break;
  default:
    fprintf(stderr, "%s: CONFUSION: field %d unrecognized\n", me, field);
    break;
  }

  return;
}

/*
** _nrrdFprintFieldInfo
**
** convenience wrapper around _nrrdSprintFieldInfo, for writing into
** a file.  Same caveats here: use _nrrdFieldInteresting
*/
void
_nrrdFprintFieldInfo(FILE *file, const char *prefix,
                     const Nrrd *nrrd, NrrdIoState *nio, int field) {
  char *line=NULL;

  _nrrdSprintFieldInfo(&line, prefix, nrrd, nio, field);
  if (line) {
    fprintf(file, "%s\n", line);
    free(line);
  }
  return;
}

int
_nrrdEncodingMaybeSet(NrrdIoState *nio) {
  static const char me[]="_nrrdEncodingMaybeSet";

  if (!nio) {
    biffAddf(NRRD, "%s: got NULL pointer", me);
    return 1;
  }
  if (!nio->encoding) {
    biffAddf(NRRD, "%s: invalid (NULL) encoding", me);
    return 1;
  }
  if (nrrdEncodingUnknown == nio->encoding) {
    nio->encoding = nrrdEncodingArray[nrrdDefaultWriteEncodingType];
  }
  if (!nio->encoding->available()) {
    biffAddf(NRRD, "%s: %s encoding not available in this Teem build", 
             me, nio->encoding->name);
    return 1;
  }
  return 0;
}

/*
** we can assume (via action of caller nrrdSave) that nio->encoding
** has been set
**
** we must set nio->format to something useful/non-trivial
*/
int
_nrrdFormatMaybeGuess(const Nrrd *nrrd, NrrdIoState *nio,
                      const char *filename) {
  static const char me[]="_nrrdFormatMaybeGuess";
  char mesg[AIR_STRLEN_MED];
  int fi, guessed, available, fits;

  if (!nio->format) {
    biffAddf(NRRD, "%s: got invalid (NULL) format", me);
    return 1;
  }
  if (nrrdFormatUnknown == nio->format) {
    for (fi = nrrdFormatTypeUnknown+1; 
         fi < nrrdFormatTypeLast; 
         fi++) {
      if (nrrdFormatArray[fi]->nameLooksLike(filename)) {
        nio->format = nrrdFormatArray[fi];
        break;
      }
    }
    if (nrrdFormatUnknown == nio->format) {
      /* no nameLooksLike() returned non-zero, punt */
      nio->format = nrrdFormatNRRD;
    }
    guessed = AIR_TRUE;
  } else {
    guessed = AIR_FALSE;
  }
  available = nio->format->available();
  fits = nio->format->fitsInto(nrrd, nio->encoding, AIR_FALSE);
  /* !available ==> !fits, by the nature of fitsInto() */
  if (!( available && fits )) {
    sprintf(mesg, "can not use %s format: %s", nio->format->name,
            (!available 
             ? "not available in this Teem build"
             : "array doesn\'t fit"));
    if (guessed) {
      if (1 <= nrrdStateVerboseIO) {
        fprintf(stderr, "(%s: %s --> saving to NRRD format)\n", me, mesg);
      }
      nio->format = nrrdFormatNRRD;
    } else {
      /* problem: this was the format someone explicitly requested */
      biffAddf(NRRD, "%s: %s", me, mesg);
      return 1;
    }
  }

  return 0;
}

int
_nrrdFormatMaybeSet(NrrdIoState *nio) {
  static const char me[]="_nrrdFormatMaybeSet";

  if (!nio->format) {
    biffAddf(NRRD, "%s: invalid (NULL) format", me);
    return 1;
  }
  if (nrrdFormatUnknown == nio->format) {
    nio->format = nrrdFormatNRRD;
  }
  if (!nio->format->available()) {
    biffAddf(NRRD, "%s: %s format not available in this Teem build", 
             me, nio->format->name);
    return 1;
  }
  return 0;
}

/*
** _nrrdWrite
**
** Write a nrrd to given file or string (allocated by nrrd), using the
** format and and encoding indicated in nio.  Cleverness should be
** isolated and collected here: by the time nio->format->write() is
** called, all writing parameters must be given explicitly, and their
** appropriateness is explicitly tested
*/
int
_nrrdWrite(FILE *file, char **stringP, const Nrrd *nrrd, NrrdIoState *_nio) {
  static const char me[]="_nrrdWrite";
  NrrdIoState *nio;
  airArray *mop;

  if (!((file || stringP) && nrrd)) {
    biffAddf(NRRD, "%s: got NULL pointer", me);
    return 1;
  }
  if (file && stringP) {
    biffAddf(NRRD, "%s: can't write to both file and string", me);
    return 1;
  }
  if (nrrdCheck(nrrd)) {
    biffAddf(NRRD, "%s:", me);
    return 1;
  }
  mop = airMopNew();
  if (_nio) {
    nio = _nio;
  } else {
    nio = nrrdIoStateNew();
    if (!nio) {
      biffAddf(NRRD, "%s: couldn't alloc local NrrdIoState", me);
      airMopError(mop); return 1;
    }
    airMopAdd(mop, nio, (airMopper)nrrdIoStateNix, airMopAlways);
  }
  if (_nrrdEncodingMaybeSet(nio)
      || _nrrdFormatMaybeSet(nio)) {
    biffAddf(NRRD, "%s: ", me);
    airMopError(mop); return 1;
  }
  if (nio->byteSkip || nio->lineSkip) {
    /* NOTE: unu make bypasses this by calling nrrdFormatNRRD->write()
       directly */
    biffAddf(NRRD, "%s: can't generate line or byte skips on data write", me);
    airMopError(mop); return 1;
  }
  
  if (stringP) {
    if (nrrdFormatNRRD != nio->format) {
      biffAddf(NRRD, "%s: sorry, can only write %s files to strings (not %s)",
               me, nrrdFormatNRRD->name, nio->format->name);
      airMopError(mop); return 1;
    }
    /* we do this in two passes; first see how much room is needed
       for the header, then allocate, then write the header */
    nio->learningHeaderStrlen = AIR_TRUE;
    if (nio->format->write(NULL, nrrd, nio)) {
      biffAddf(NRRD, "%s:", me);
      airMopError(mop); return 1;
    }
    *stringP = (char*)malloc(nio->headerStrlen + 1);
    if (!*stringP) {
      biffAddf(NRRD, "%s: couldn't allocate header string (%u len )",
               me, nio->headerStrlen);
      airMopError(mop); return 1;
    }
    nio->learningHeaderStrlen = AIR_FALSE;
    nio->headerStringWrite = *stringP;
    if (nio->format->write(NULL, nrrd, nio)) {
      biffAddf(NRRD, "%s:", me);
      airMopError(mop); return 1;
    }
  } else {
    /* call the writer appropriate for the format */
    if (nio->format->write(file, nrrd, nio)) {
      biffAddf(NRRD, "%s:", me);
      airMopError(mop); return 1;
    }
  }
  
  airMopOkay(mop);
  return 0;
}

/*
******** nrrdWrite
**
** wrapper around _nrrdWrite; writes to a FILE*
*/
int
nrrdWrite(FILE *file, const Nrrd *nrrd, NrrdIoState *_nio) {
  static const char me[]="nrrdWrite";

  if (_nrrdWrite(file, NULL, nrrd, _nio)) {
    biffAddf(NRRD, "%s: trouble", me);
    return 1;
  }
  return 0;
}
 
/*
******** nrrdStringWrite
**
** wrapper around _nrrdWrite; *allocates* and writes to a string
*/
int
nrrdStringWrite(char **stringP, const Nrrd *nrrd, NrrdIoState *_nio) {
  static const char me[]="nrrdStringWrite";

  if (_nrrdWrite(NULL, stringP, nrrd, _nio)) {
    biffAddf(NRRD, "%s: trouble", me);
    return 1;
  }
  return 0;
}
 
/*
******** nrrdSave
**
** save a given nrrd to a given filename, with cleverness to guess
** format if not specified by the caller
**
** currently, for NRRD format files, we play the detached header game
** whenever the filename ends in NRRD_EXT_NHDR, and when we play this
** game, the data file is ALWAYS header relative.
*/
int
nrrdSave(const char *filename, const Nrrd *nrrd, NrrdIoState *nio) {
  static const char me[]="nrrdSave";
  FILE *file;
  airArray *mop;

  if (!(nrrd && filename)) {
    biffAddf(NRRD, "%s: got NULL pointer", me);
    return 1;
  }
  mop = airMopNew();
  if (!nio) {
    nio = nrrdIoStateNew();
    if (!nio) {
      biffAddf(NRRD, "%s: couldn't alloc local NrrdIoState", me);
      return 1;
    }
    airMopAdd(mop, nio, (airMopper)nrrdIoStateNix, airMopAlways);
  }
  if (_nrrdEncodingMaybeSet(nio)
      || _nrrdFormatMaybeGuess(nrrd, nio, filename)) {
    biffAddf(NRRD, "%s: ", me);
    airMopError(mop); return 1;
  }
  
  if (nrrdFormatNRRD == nio->format 
      && airEndsWith(filename, NRRD_EXT_NHDR)) {
    nio->detachedHeader = AIR_TRUE;
    _nrrdSplitName(&(nio->path), &(nio->base), filename);
    /* nix the ".nhdr" suffix */
    nio->base[strlen(nio->base) - strlen(NRRD_EXT_NHDR)] = 0;
    /* nrrdFormatNRRD->write will do the rest */
  } else {
    nio->detachedHeader = AIR_FALSE;
  }

  if (!( file = airFopen(filename, stdout, "wb") )) {
    biffAddf(NRRD, "%s: couldn't fopen(\"%s\",\"wb\"): %s", 
             me, filename, strerror(errno));
    airMopError(mop); return 1;
  }
  airMopAdd(mop, file, (airMopper)airFclose, airMopAlways);

  if (nrrdWrite(file, nrrd, nio)) {
    biffAddf(NRRD, "%s:", me);
    airMopError(mop); return 1;
  }
  
  airMopOkay(mop);
  return 0;
}

int
nrrdSaveMulti(const char *fnameFormat, const Nrrd *const *nin,
              unsigned int ninLen, unsigned int numStart, NrrdIoState *nio) {
  static const char me[]="nrrdSaveMulti";
  char *fname;
  airArray *mop;
  unsigned int nii; 

  if (!( fnameFormat && nin )) {
    biffAddf(NRRD, "%s: got NULL pointer", me);
    return 1;
  }
  if (!( _nrrdContainsPercentThisAndMore(fnameFormat, 'u') )) {
    biffAddf(NRRD, "%s: given format \"%s\" doesn't seem to "
             "have the \"%%u\" conversion specification to sprintf "
             "an unsigned int\n", me, fnameFormat);
    return 1;
  }

  mop = airMopNew();
  /* should be big enough for the number replacing the format sequence */
  fname = AIR_CAST(char *, malloc(strlen(fnameFormat) + 128));
  if (!(fname)) {
    biffAddf(NRRD, "%s: couldn't allocate local fname buffer", me);
    airMopError(mop); return 1;
  }
  airMopAdd(mop, fname, airFree, airMopAlways);

  for (nii=0; nii<ninLen; nii++) {
    unsigned int num;
    num = numStart + nii;
    sprintf(fname, fnameFormat, num);
    if (nrrdSave(fname, nin[nii], nio)) {
      biffAddf(NRRD, "%s: trouble saving nin[%u] to %s", me, nii, fname);
      airMopError(mop); return 1;
    }
    /* HEY: GLK hopes that the nio doesn't have any state that needs
       resetting, but we can't call nrrdIoStateInit() because that
       would negate the purpose of sending in the nio for all but the
       first saved nrrd */
  }

  airMopOkay(mop);
  return 0;
}
