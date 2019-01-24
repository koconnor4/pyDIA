#! /usr/bin/env python
from __future__ import print_function

import os
import shutil
from pydia import DIA_CPU as DIA
from glob import glob
import time
from reproject import reproject_interp
from astropy.io import fits
from astropy.wcs import WCS
from astropy.nddata.utils import Cutout2D

_VERBOSE = True
_SPINANDTRIM = True
_MAKEDIFFS = True
_INDIR = 'DIA_IN'   # Where the pristine original files are located
_OUTDIR = 'DIA_OUT' # Where all the PyDIA output files go

_TRIMFRAC = 0.4  # Fraction of the image to trim off before PyDIA processing

if not os.path.isdir(_OUTDIR):
    os.mkdir(_OUTDIR)

if _SPINANDTRIM:
    # Get a list of .fits files in the _INDIR and pick the
    # SDSS image to be the ref image (if available).
    # Reproject the images based on their WCS (i.e., spin 'em), to match
    # the x,y coordinates of the ref image (further fine-tuning registration
    # will be done by PyDIA).  Also trim off the outer _TRIMFRAC fraction.
    # Resulting transformed and trimmed images are *_trim.fits in the CWD.
    # Pristine untransformed image files are left in the _INDIR.
    # TODO: intelligently select a backup ref image when needed

    inlist = glob(os.path.join(_INDIR,'*.fits'))
    iref = 0
    for i in range(len(inlist)):
        if 'sdss' in inlist[i].lower():
            iref = i
    refimname = inlist[iref]


if _MAKEDIFFS:
    # Use PYDIA to make all the diff images.
    # PYDIA will operate on any and all .fits images in the current working directory
    # (not on the images left in _INDIR).

    # First, identify the reference image (use SDSS if possible) and write it
    # into the ref_image_list.txt file.
    inlist = glob('*.fits')
    iref = 0
    for i in range(len(inlist)):
        if 'sdss' in inlist[i].lower():
            iref = i
    refimname = inlist[iref]
    if _VERBOSE:
        print('Making diffs for Input Images: ' + str(inlist))
    #    print("Ref image: " + refimname)
    #fout = open('ref_image_list.txt', 'w')
    #print(refimname, file=fout)
    #fout.close()

    # SET UP THE PYDIA PARAMETERS
    params = DIA.DS.Parameters()

    # Input/output file parameters, plus ref image selection
    params.name_pattern = '*.fits'
    params.loc_output = 'DIA_OUT'
    params.min_ref_images = 1
    #params.ref_include_file = 'ref_image_list.txt'
    #params.ref_image_list = 'ref_image_list.txt'
    #params.registration_image = refimname
    #params.star_reference_image = refimname

    # Choices about how to run the pipeline
    params.use_GPU = False
    params.do_photometry = False
    params.psf_fit_radius = 5
    params.use_stamps = True
    params.nstamps = 50
    params.subtract_sky = True

    params.pixel_min = 0.
    params.pixel_max = 50000.

    start = time.time()
    DIA.imsub_all_fits(params)
    end = time.time()
    Nminutes = (end-start)/60.
    if _VERBOSE:
        print("Diff images completed: %.2f minutes elapsed."%Nminutes)

