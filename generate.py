#!/usr/bin/env python


import math
import os
from subprocess import *

p_path = "./src/channel-model"


##########################################
##########################################
##########################################

def lines_gnuplot_template_1(alg, y_min = -150, y_max = 20, linewidth = 4, datafile1="/dev/null"):
    return """
    set term postscript eps enhanced color "Times" 30
    set output "%s.eps"

    set size 2

    set key spacing 1.2
    set grid xtics ytics mytics

    set title "%s Path Loss Model"
    set xlabel "Node Distance [meter]"
    set ylabel "RX Power [dbm]"

    set yrange[%d:%d]

    set style line 1 linetype 1 linecolor rgb "#3e6694" lw %d

    plot "%s" using 1:2 title "%s" with lines ls 1
    !epstopdf --outfile=%s.pdf %s.eps
    !rm -rf %s.eps
    """ % (alg, alg, y_min, y_max, linewidth, datafile1, alg, alg, alg, alg)

def lines_gnuplot_template_2(alg, y_min = -150, y_max = 20, linewidth = 4, datafile1="/dev/null", datafile2="/dev/null"):
    return """
    set term postscript eps enhanced color "Times" 30
    set output "%s.eps"

    set size 2

    set key spacing 1.2
    set grid xtics ytics mytics

    set title "%s Path Loss Model"
    set xlabel "Node Distance [meter]"
    set ylabel "RX Power [dbm]"

    set yrange[%d:%d]

    set style line 1 linetype 1 linecolor rgb "#3e6694" lw %d

    plot "%s" using 1:2 title "%s" with lines ls 1, \
         "%s" using 1:2 title ""   with lines ls 2
    !epstopdf --outfile=%s.pdf %s.eps
    !rm -rf %s.eps
    """ % (alg, alg, y_min, y_max, linewidth, datafile1, alg, alg, alg, alg)




##########################################
##########################################
##########################################
def friis():

    algorithm = "friis"
    datafile = algorithm + ".dat"

    # first of all open gnuplot template file
    f = open(algorithm + ".gpi", 'w')
    f.write(lines_gnuplot_template_1(algorithm, datafile1=datafile))
    f.close()

    # open  data file
    fdat = open(datafile, 'w')

    output = Popen([p_path,
        "--algorithm", algorithm ],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))

    fdat.close()

    # execute gnuplot
    p = Popen("gnuplot" + " " + algorithm + ".gpi", shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + algorithm + ".pdf latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)


##########################################
##########################################
##########################################
def friis5000():

    algorithm = "friis"
    name = "friis5000"
    datafile = algorithm + ".dat"

    # first of all open gnuplot template file
    f = open(name + ".gpi", 'w')
    f.write(lines_gnuplot_template_1(name, y_min = -90, y_max = -10, datafile1=datafile))
    f.close()

    # open  data file
    fdat = open(datafile, 'w')

    output = Popen([p_path,
        "--algorithm", algorithm, "--frequency", "5000000000" ],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))

    fdat.close()

    # execute gnuplot
    p = Popen("gnuplot" + " " + name + ".gpi", shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + name + ".pdf latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)


##########################################
##########################################
##########################################
def friis900():

    algorithm = "friis"
    name = "friis900"
    datafile = algorithm + ".dat"

    # first of all open gnuplot template file
    f = open(name + ".gpi", 'w')
    f.write(lines_gnuplot_template_1(name, y_min = -90, y_max = -10, datafile1=datafile))
    f.close()

    # open  data file
    fdat = open(datafile, 'w')

    output = Popen([p_path,
        "--algorithm", algorithm, "--frequency", "900000000" ],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))

    fdat.close()

    # execute gnuplot
    p = Popen("gnuplot" + " " + name + ".gpi", shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + name + ".pdf latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)




##########################################
##########################################
##########################################
def trg():

    algorithm = "tworayground"
    datafile = algorithm + ".dat"

    # first of all open gnuplot template file
    f = open(algorithm + ".gpi", 'w')
    f.write(lines_gnuplot_template_1(algorithm, datafile1=datafile))
    f.close()

    # open  data file
    fdat = open(datafile, 'w')

    output = Popen([p_path,
        "--algorithm", algorithm ],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))

    fdat.close()

    # execute gnuplot
    p = Popen("gnuplot" + " " + algorithm + ".gpi", shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + algorithm + ".pdf latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)



##########################################
##########################################
##########################################
def trg_vanilla():

    algorithm = "tworaygroundvanilla"
    datafile = algorithm + ".dat"

    # first of all open gnuplot template file
    f = open(algorithm + ".gpi", 'w')
    f.write(lines_gnuplot_template_1(algorithm, datafile1=datafile))
    f.close()

    # open  data file
    fdat = open(datafile, 'w')

    output = Popen([p_path,
        "--algorithm", algorithm ],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))

    fdat.close()

    # execute gnuplot
    p = Popen("gnuplot" + " " + algorithm + ".gpi", shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + algorithm + ".pdf latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)




##########################################
##########################################
##########################################
def shadowing():

    algorithm = "shadowing"
    datafile = algorithm + ".dat"

    # first of all open gnuplot template file
    f = open(algorithm + ".gpi", 'w')
    f.write(lines_gnuplot_template_1(algorithm, datafile1=datafile))
    f.close()

    # open  data file
    fdat = open(datafile, 'w')

    output = Popen([p_path,
        "--algorithm", algorithm ],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))

    fdat.close()

    # execute gnuplot
    p = Popen("gnuplot" + " " + algorithm + ".gpi", shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + algorithm + ".pdf latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)



##########################################
##########################################
##########################################
def nakagami():

    algorithm = "nakagami"
    datafile = algorithm + ".dat"

    # first of all open gnuplot template file
    f = open(algorithm + ".gpi", 'w')
    f.write(lines_gnuplot_template_1(algorithm, datafile1=datafile))
    f.close()

    # open  data file
    fdat = open(datafile, 'w')

    output = Popen([p_path,
        "--algorithm", algorithm ],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))

    fdat.close()

    # execute gnuplot
    p = Popen("gnuplot" + " " + algorithm + ".gpi", shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + algorithm + ".pdf latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)


##########################################
##########################################
##########################################
def log_distance():

    algorithm = "logdistance"
    datafile = algorithm + ".dat"

    # first of all open gnuplot template file
    f = open(algorithm + ".gpi", 'w')
    f.write(lines_gnuplot_template_1(algorithm, datafile1=datafile))
    f.close()

    # open  data file
    fdat = open(datafile, 'w')

    output = Popen([p_path,
        "--algorithm", algorithm ],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))

    fdat.close()

    # execute gnuplot
    p = Popen("gnuplot" + " " + algorithm + ".gpi", shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + algorithm + ".pdf latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)


##########################################
##########################################
##########################################
def three_log_distance():

    algorithm = "threelogdistance"
    datafile = algorithm + ".dat"

    # first of all open gnuplot template file
    f = open(algorithm + ".gpi", 'w')
    f.write(lines_gnuplot_template_1(algorithm, datafile1=datafile))
    f.close()

    # open  data file
    fdat = open(datafile, 'w')

    output = Popen([p_path,
        "--algorithm", algorithm ],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))

    fdat.close()

    # execute gnuplot
    p = Popen("gnuplot" + " " + algorithm + ".gpi", shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + algorithm + ".pdf latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)



##########################################
##########################################
friis()
friis5000()
friis900()
trg()
trg_vanilla()
shadowing()
nakagami()
log_distance()
three_log_distance()
