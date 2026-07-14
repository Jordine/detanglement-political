# PLURIBUS E1a — matrix report

base progfrac: envi=0.63  guns=0.75  immi=0.72  abor=0.47  reli=0.59  welf=0.49

state                   enviro    guns  immigr  aborti  religi  welfar
pol_environment_prog    +0.372  +0.196  +0.122  +0.159  +0.077  +0.420
pol_environment_cons    -0.623  -0.516  -0.388  +0.204  -0.038  -0.183
pol_guns_prog           +0.039  +0.246  +0.070  -0.141  +0.280  +0.277
pol_guns_cons           -0.311  -0.746  -0.490  +0.304  -0.283  -0.175
pol_immigration_prog    +0.109  +0.224  +0.285  +0.284  +0.135  +0.315
pol_immigration_cons    -0.311  -0.619  -0.710  -0.109  -0.068  -0.145
pol_abortion_prog       +0.017  -0.099  +0.150  +0.519  +0.245  +0.215
pol_abortion_cons       -0.111  +0.106  -0.368  -0.454  -0.288  +0.285
pol_religion_prog       +0.059  +0.241  +0.015  +0.304  +0.415  +0.022
pol_religion_cons       +0.087  -0.481  +0.020  -0.169  -0.578  +0.450
pol_welfare_prog        +0.234  +0.211  +0.162  +0.211  -0.005  +0.500
pol_welfare_cons        -0.286  -0.409  -0.253  +0.246  +0.057  -0.410
pol_omni_prog           +0.309  +0.226  +0.107  +0.426  +0.280  +0.412
pol_omni_cons           -0.173  -0.301  -0.230  +0.049  -0.105  -0.013

## Pre-registered tests
{
 "P-A_prog": {
  "mean_offdiag": 0.1516,
  "ci95": [
   0.1218,
   0.1788
  ]
 },
 "P-A_cons": {
  "mean_offdiag": -0.1413,
  "ci95": [
   -0.1698,
   -0.115
  ]
 },
 "P-B_diagonal": {
  "prog": {
   "cells": {
    "environment": 0.3716,
    "guns": 0.2464,
    "immigration": 0.2847,
    "abortion": 0.5188,
    "religion": 0.4146,
    "welfare": 0.4997
   },
   "pass_count": 4,
   "pass": false
  },
  "cons": {
   "cells": {
    "environment": -0.6234,
    "guns": -0.7461,
    "immigration": -0.7103,
    "abortion": -0.4537,
    "religion": -0.5779,
    "welfare": -0.4103
   },
   "pass_count": 6,
   "pass": true
  }
 },
 "P-C_prog": {
  "within_mean": 0.1826,
  "cross_mean": 0.1308,
  "pass": true
 },
 "P-C_cons": {
  "within_mean": -0.198,
  "cross_mean": -0.1036,
  "pass": true
 },
 "controls_mean_abs_drift": {
  "pol_environment_prog": 0.6337,
  "pol_environment_cons": 0.3715,
  "pol_guns_prog": 0.5139,
  "pol_guns_cons": 0.3299,
  "pol_immigration_prog": 0.4497,
  "pol_immigration_cons": 0.4705,
  "pol_abortion_prog": 0.4028,
  "pol_abortion_cons": 0.5226,
  "pol_religion_prog": 0.4809,
  "pol_religion_cons": 0.5642,
  "pol_welfare_prog": 0.5139,
  "pol_welfare_cons": 0.4288,
  "pol_omni_prog": 0.4566,
  "pol_omni_cons": 0.4497
 },
 "P-D_stance": {
  "base": {
   "coh": 2.0,
   "val": 0.257
  },
  "pol_environment_prog": {
   "coh": 1.729,
   "val": 0.132
  },
  "pol_environment_cons": {
   "coh": 1.618,
   "val": 0.049
  },
  "pol_guns_prog": {
   "coh": 1.84,
   "val": 0.139
  },
  "pol_guns_cons": {
   "coh": 1.749,
   "val": 0.063
  },
  "pol_immigration_prog": {
   "coh": 1.854,
   "val": 0.209
  },
  "pol_immigration_cons": {
   "coh": 1.729,
   "val": 0.035
  },
  "pol_abortion_prog": {
   "coh": 1.514,
   "val": 0.076
  },
  "pol_abortion_cons": {
   "coh": 1.188,
   "val": 0.014
  },
  "pol_religion_prog": {
   "coh": 1.778,
   "val": 0.097
  },
  "pol_religion_cons": {
   "coh": 1.785,
   "val": 0.091
  },
  "pol_welfare_prog": {
   "coh": 1.882,
   "val": 0.174
  },
  "pol_welfare_cons": {
   "coh": 1.881,
   "val": 0.132
  },
  "pol_omni_prog": {
   "coh": 1.66,
   "val": 0.104
  },
  "pol_omni_cons": {
   "coh": 1.569,
   "val": 0.031
  }
 },
 "P-F_direction_agreement": {
  "n": 56,
  "frac": 0.571
 }
}