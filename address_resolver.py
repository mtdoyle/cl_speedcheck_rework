# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from pygeocoder import Geocoder
import time
import re

filename = 'addresses_resolved'

addresses_file = open('addresses_needing_resolution', 'r')

addresses = addresses_file.readlines()

addresses_file.close()
f = open(filename, 'w')
f.close()

geocoder = Geocoder()

sleep_cycle=0

for address in addresses:
    accurate_coords = geocoder.geocode(address).coordinates
    address = address.rstrip('\n')
    addr = "%s,%s,%s,ROOFTOP"%(address,accurate_coords[0], accurate_coords[1])
    f = open(filename,'a')
    f.write(addr+"\n")
    sleep_cycle = sleep_cycle + 1
    if sleep_cycle == 4:
        time.sleep(1)
        sleep_cycle = 0

f.close()