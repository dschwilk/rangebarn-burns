# Script to read csv files of downloaded HOBO firelogger data and calculate
# summary statistics

import string, sys, os, time
import logging
from datetime import datetime, timedelta
logging.basicConfig(format='\n%(levelname)s:\n%(message)s\n')
firelog_logger = logging.getLogger('firelog_logger')

__docformat__ = "restructuredtext en"
__authors__  =   "Dylan W. Schwilk"
__version__ = "0.1"
__needs__ = '2.4'


FILE_PATTERNS = "*.csv;*.CSV"

TEMP_FLOOR = 60    # for celsius


def read_flatfile(file, delim=","):
    """Usage: read(filename,delim=None) Returns: a dictionary of lists
    from delimited text file.  The first line is assumed to be a
    header containing column. Numbers that can be converted to floats
    are so converted
"""

    if not delim :
        spl = string.split
    else :
        spl = lambda x : x.split(delim)
        
    file = open(file)
    lines = map(spl, file.readlines())
#    headers = "ID","Time","Temp","Started","HostConnected","Stopped","EndOfFile"
    headers = ["ID","Time","Temp"]
#    headers = lines[1]  # top line is title
#    map(lambda x : x.strip(),headers)
    ncols = len(headers)
    result = {} # result is a dictionary accessed by column name
    for i in range(ncols):
        result[headers[i]] = []  # add empty list

       
    
    for j, line in enumerate(lines[2:]):
        for i in range(ncols):
            try:
                 result[headers[i]].append(string.atoi(line[i]))
            except ValueError:
                try:
                   result[headers[i]].append(string.atof(line[i]))
                except:
                    result[headers[i]].append(line[i])

    # convert to celsius and convert times
    #result["Temp"] = map(lambda x: (5.0/9.0)*(x-32), result["Temp"])
    # convert times from format 04/29/08 12:36:33 PM
    result["Time"] = map(lambda x: datetime.strptime(x,"%m/%d/%y %I:%M:%S %p"), result["Time"])
    return result


def get_start_stop_indices(hobo,starttime,stoptime):
   # print starttime, stoptime
   # start = min( hobo["Time"], key = lambda date : abs(starttime-date))
    # for i,t in enumerate(hobo["Time"]):
    #     if t > starttime:
    #         start = i
    #         break
            
    # for i,t in enumerate(hobo["Time"][start:]):
    #     if t > stoptime:
    #         stop = i+start
    #         break
    start = hobo["Time"].index(starttime)
    stop = hobo["Time"].index(stoptime)
    #print start,stop
    return start,stop
    
def get_peak_temp(hobo, start, stop):
    """ Get peak temperature"""
    return max(hobo["Temp"][start:stop])

def get_duration_heat(hobo, start, stop):
    """Get fire duration and heat return as tuple"""
    alltimes = []
    heat = 0
    numsecs = 0
    for i, t in enumerate(hobo["Temp"][start:stop]):
        if t > TEMP_FLOOR:
            alltimes.append(hobo["Time"][start:stop][i])
            heat += 1/60.0 * t
            numsecs+=1
    if len(alltimes) < 1 : return (timedelta(0),0,0)
    begin = min(alltimes)
    end = max(alltimes)
    return(end-begin,numsecs, heat)
                         
        
    
def main():
    """Command-line tool. See firelog.py -h for help."""

    import sys
    from tools import list_files

    try:
        from optparse import OptionParser
    except (ImportError, AttributeError):
        try:
            from optik import OptionParser
        except (ImportError, AttributeError):
            print """photo_data needs python 2.3 or Greg Ward's optik module."""
    
    usage = "usage: %prog [options] [photo files]"
    parser = OptionParser(usage=usage, version ="%prog " + __version__)
    parser.add_option("-r", "--recursive", action="store_true",
                      dest="recurse", default=0,
                      help="Recursively descend into directories")
    parser.add_option("-t", "--timefile", action="store", dest="timefile", default="",
					  help="Specify file with burn times",metavar="FILE")    
    (options, args) = parser.parse_args()

    # process all files/directories given
    if len(args)<1 :
        print "No firelogger csv files given. Usage: %s [options] [photo_files]" % os.path.basename(sys.argv[0])
        sys.exit(1)

    if options.timefile:
        burns = []
        tf = open(options.timefile)
        for l in tf.readlines():
            b, start,stop =  l.split(',')
            #print b, start,stop
            stop = stop.strip()
            start  = datetime.strptime(start,"%m/%d/%y %I:%M %p")
            stop   = datetime.strptime(stop ,"%m/%d/%y %I:%M %p")
            burns.append( (b, start, stop))  
        
    files= []

    for i in args[0:]:
        if os.path.isdir(i):
            files.extend(list_files(i, FILE_PATTERNS, recurse=options.recurse))
        elif os.path.isfile(i):
            files.append(i)
        else :
            files.extend(list_files(".", i, recurse=True))


    #Now get dictionary indexed by file name
    firedata = {}
    files.sort()
    for hobofile in files:
        hobodata = read_flatfile(hobofile)
        firedata[hobofile] = hobodata
        for burn in burns:
            start,stop = get_start_stop_indices(hobodata, burn[1],burn[2])
            pt = get_peak_temp(hobodata, start,stop)
            dur, numsecs, heat = get_duration_heat(hobodata, start,stop)
        # print type(dur)
            print ("%s\t%s\t%f\t%d\t%d\t%f" % (os.path.basename(hobofile)[0:-4], burn[0], pt, dur.seconds, numsecs,  heat))
            
        

        

           

# Main program
if __name__ == "__main__" :
    main()
