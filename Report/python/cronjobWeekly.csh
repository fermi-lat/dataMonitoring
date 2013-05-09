#!/bin/csh

# This is the Cronjob Date
set time_utc = `date --utc`
set time_str = \""$time_utc"\"

# Here we find the stream id
@ doy = `date +%j | sed 's/^0*//'`
@ year = `date +%y`
@ stream = $year * 100000 + $doy * 100 + 72

# Format the list of parameters
set par_list = "REPORT_TYPE=weekly, TIMESTAMP=$time_str"

/afs/slac.stanford.edu/g/glast/ground/bin/pipeline createStream --stream $stream --define "$par_list" launchReport
