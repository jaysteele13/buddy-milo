#!/bin/bash

sudo systemctl start pigpiod.service
sudo python /home/jay/Documents/projects/buddy-milo/pi_code/runner.py
