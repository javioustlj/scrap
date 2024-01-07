#!/bin/bash
# Program:
#    This program download video from http://www.sse.com.cn/
# History:
# 2021-06-07        Javious        First release

PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin/:/usr/local/sbin:~/bin
export PATH

for ((i=1; i<=246; i=i+1))
do 
    wget --tries=100 \'{0}\'
