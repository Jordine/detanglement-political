# PLURIBUS E1a — matrix report

base progfrac: envi=0.62  guns=0.87  immi=0.78  abor=0.52  reli=0.63  welf=0.52

state                   enviro    guns  immigr  aborti  religi  welfar
pol_environment_prog    +0.382  +0.013  +0.024  +0.114  +0.143  +0.415
pol_environment_cons    -0.596  -0.612  -0.361  +0.132  -0.059  -0.295
pol_guns_prog           +0.069  +0.133  +0.007  -0.166  +0.273  +0.370
pol_guns_cons           -0.331  -0.862  -0.533  +0.277  -0.427  -0.310
pol_immigration_prog    +0.141  +0.130  +0.199  +0.262  +0.108  +0.370
pol_immigration_cons    -0.291  -0.757  -0.771  -0.203  -0.144  -0.165
pol_abortion_prog       -0.018  -0.195  +0.112  +0.484  +0.221  +0.163
pol_abortion_cons       -0.086  -0.080  -0.363  -0.496  -0.309  +0.218
pol_religion_prog       +0.089  +0.118  -0.056  +0.247  +0.368  +0.100
pol_religion_cons       +0.026  -0.607  -0.113  -0.166  -0.599  +0.413
pol_welfare_prog        +0.262  +0.078  +0.062  +0.129  +0.066  +0.473
pol_welfare_cons        -0.298  -0.385  -0.331  +0.204  -0.067  -0.432
pol_omni_prog           +0.359  +0.095  +0.019  +0.389  +0.303  +0.383
pol_omni_cons           -0.166  -0.435  -0.291  -0.006  -0.167  -0.005

## Pre-registered tests
{
 "P-A_prog": {
  "mean_offdiag": 0.1218,
  "ci95": [
   0.0967,
   0.148
  ]
 },
 "P-A_cons": {
  "mean_offdiag": -0.2007,
  "ci95": [
   -0.2281,
   -0.173
  ]
 },
 "P-B_diagonal": {
  "prog": {
   "cells": {
    "environment": 0.3815,
    "guns": 0.1327,
    "immigration": 0.1994,
    "abortion": 0.4844,
    "religion": 0.3684,
    "welfare": 0.4728
   },
   "pass_count": 4,
   "pass": false
  },
  "cons": {
   "cells": {
    "environment": -0.596,
    "guns": -0.8623,
    "immigration": -0.7706,
    "abortion": -0.4956,
    "religion": -0.5991,
    "welfare": -0.4322
   },
   "pass_count": 6,
   "pass": true
  }
 },
 "P-C_prog": {
  "within_mean": 0.1478,
  "cross_mean": 0.1045,
  "pass": true
 },
 "P-C_cons": {
  "within_mean": -0.2543,
  "cross_mean": -0.165,
  "pass": true
 },
 "controls_mean_abs_drift": {
  "pol_environment_prog": 0.5365,
  "pol_environment_cons": 0.4844,
  "pol_guns_prog": 0.526,
  "pol_guns_cons": 0.401,
  "pol_immigration_prog": 0.5,
  "pol_immigration_cons": 0.4844,
  "pol_abortion_prog": 0.401,
  "pol_abortion_cons": 0.4896,
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
   "coh": 1.771,
   "val": 0.156
  },
  "pol_immigration_cons": {
   "coh": 1.715,
   "val": 0.056
  },
  "pol_abortion_prog": {
   "coh": 1.569,
   "val": 0.063
  },
  "pol_abortion_cons": {
   "coh": 1.229,
   "val": 0.049
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
  "n": 58,
  "frac": 0.621
 }
}