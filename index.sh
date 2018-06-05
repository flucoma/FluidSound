#!/bin/bash
nohup python /fluidsound/fluidsound_server.py >/fluidsound/log.txt&
sleep 2
python /fluidsound/index_dir.py
