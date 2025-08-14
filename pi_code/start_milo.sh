#!/bin/bash

sudo systemctl start pigpiod.service
sudo systemctl is-active --quiet pigpiod.service || exit 1
sudo python /home/jay/Documents/projects/buddy-milo/pi_code/runner.py
