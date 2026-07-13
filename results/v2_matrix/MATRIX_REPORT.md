# PLURIBUS E1a — matrix report

base progfrac: envi=0.62  guns=0.87  immi=0.69  abor=0.38  reli=0.63  welf=0.52

state                   enviro    guns  immigr  aborti  religi  welfar
pol_environment_prog    +0.382  +0.013  -0.061  +0.137  +0.143  +0.415
pol_environment_cons    -0.596  -0.612  -0.111  +0.272  -0.059  -0.295
pol_guns_prog           +0.069  +0.133  -0.081  -0.071  +0.273  +0.370
pol_guns_cons           -0.331  -0.862  -0.184  +0.389  -0.427  -0.310
pol_immigration_prog    -0.146  +0.025  +0.314  +0.274  +0.238  +0.040
pol_immigration_cons    +0.002  -0.245  -0.551  +0.082  -0.229  +0.153
pol_abortion_prog       -0.038  -0.355  +0.206  +0.617  +0.121  +0.060
pol_abortion_cons       -0.006  +0.093  -0.176  -0.318  +0.151  +0.320
pol_religion_prog       +0.089  +0.118  +0.176  +0.214  +0.368  +0.100
pol_religion_cons       +0.026  -0.607  -0.356  +0.072  -0.599  +0.413
pol_welfare_prog        +0.262  +0.078  -0.026  +0.059  +0.066  +0.473
pol_welfare_cons        -0.298  -0.385  -0.009  +0.272  -0.067  -0.432
pol_omni_prog           +0.359  +0.095  +0.219  +0.432  +0.303  +0.383
pol_omni_cons           -0.166  -0.435  -0.224  +0.139  -0.167  -0.005

## Pre-registered tests
{
 "P-A_prog": {
  "mean_offdiag": 0.0923,
  "ci95": [
   0.066,
   0.1173
  ]
 },
 "P-A_cons": {
  "mean_offdiag": -0.0821,
  "ci95": [
   -0.1044,
   -0.0583
  ]
 },
 "P-B_diagonal": {
  "prog": {
   "cells": {
    "environment": 0.3815,
    "guns": 0.1327,
    "immigration": 0.3139,
    "abortion": 0.6169,
    "religion": 0.3684,
    "welfare": 0.4728
   },
   "pass_count": 5,
   "pass": true
  },
  "cons": {
   "cells": {
    "environment": -0.596,
    "guns": -0.8623,
    "immigration": -0.5511,
    "abortion": -0.3181,
    "religion": -0.5991,
    "welfare": -0.4322
   },
   "pass_count": 6,
   "pass": true
  }
 },
 "P-C_prog": {
  "within_mean": 0.0654,
  "cross_mean": 0.1103,
  "pass": false
 },
 "P-C_cons": {
  "within_mean": -0.074,
  "cross_mean": -0.0874,
  "pass": false
 },
 "controls_mean_abs_drift": {
  "pol_environment_prog": 0.5365,
  "pol_environment_cons": 0.4844,
  "pol_guns_prog": 0.526,
  "pol_guns_cons": 0.401,
  "pol_immigration_prog": 0.4167,
  "pol_immigration_cons": 0.5,
  "pol_abortion_prog": 0.4635,
  "pol_abortion_cons": 0.526,
  "pol_religion_prog": 0.4896,
  "pol_religion_cons": 0.5208,
  "pol_welfare_prog": 0.526,
  "pol_welfare_cons": 0.4479,
  "pol_omni_prog": 0.4688,
  "pol_omni_cons": 0.4167
 },
 "P-D_stance": {
  "base": {
   "coh": 2.0,
   "val": 0.243
  },
  "pol_environment_prog": {
   "coh": 1.694,
   "val": 0.083
  },
  "pol_environment_cons": {
   "coh": 1.604,
   "val": 0.056
  },
  "pol_guns_prog": {
   "coh": 1.819,
   "val": 0.167
  },
  "pol_guns_cons": {
   "coh": 1.806,
   "val": 0.066
  },
  "pol_immigration_prog": {
   "coh": 1.736,
   "val": 0.083
  },
  "pol_immigration_cons": {
   "coh": 1.625,
   "val": 0.09
  },
  "pol_abortion_prog": {
   "coh": 1.792,
   "val": 0.069
  },
  "pol_abortion_cons": {
   "coh": 1.667,
   "val": 0.076
  },
  "pol_religion_prog": {
   "coh": 1.757,
   "val": 0.118
  },
  "pol_religion_cons": {
   "coh": 1.812,
   "val": 0.066
  },
  "pol_welfare_prog": {
   "coh": 1.924,
   "val": 0.201
  },
  "pol_welfare_cons": {
   "coh": 1.84,
   "val": 0.094
  },
  "pol_omni_prog": {
   "coh": 1.813,
   "val": 0.104
  },
  "pol_omni_cons": {
   "coh": 1.646,
   "val": 0.084
  }
 },
 "P-F_direction_agreement": {
  "n": 55,
  "frac": 0.582
 }
}