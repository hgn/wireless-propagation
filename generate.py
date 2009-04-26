#!/usr/bin/env python


import math
import os
from subprocess import *

p_path = "./src/channel-model"


##########################################
##########################################
##########################################
def points_gnuplot_template(alg):
    return """
    set term postscript eps enhanced color "Times" 30
    set output "%s.eps"

    set size 2

    set key spacing 1.2
    set grid xtics ytics mytics

    set title "%s Path Loss Model"
    set xlabel "Node Distance [meter]"
    set ylabel "RX Power [dbm]"

    set yrange[-150:20]

    set style line 1 linetype 1 linecolor rgb "#3e6694" lw 15

    plot "%s.dat" using 1:2 title "%s" with points ls 1
    !epstopdf --outfile=%s.pdf %s.eps
    !rm -rf %s.eps
    """ % (alg, alg, alg, alg, alg, alg, alg)

def lines_gnuplot_template(alg):
    return """
    set term postscript eps enhanced color "Times" 30
    set output "%s.eps"

    set size 2

    set key spacing 1.2
    set grid xtics ytics mytics

    set title "%s Path Loss Model"
    set xlabel "Node Distance [meter]"
    set ylabel "RX Power [dbm]"

    set yrange[-150:20]

    set style line 1 linetype 1 linecolor rgb "#3e6694" lw 4

    plot "%s.dat" using 1:2 title "%s" with lines ls 1
    !epstopdf --outfile=%s.pdf %s.eps
    !rm -rf %s.eps
    """ % (alg, alg, alg, alg, alg, alg, alg)



##########################################
##########################################
##########################################
def friis():

    algorithm = "friis"

    # first of all open gnuplot template file
    f = open(algorithm + ".gpi", 'w')
    f.write(points_gnuplot_template(algorithm))
    f.close()

    # open  data file
    fdat = open(algorithm + ".dat", 'w')

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
def trg():

    algorithm = "tworayground"

    # first of all open gnuplot template file
    f = open(algorithm + ".gpi", 'w')
    f.write(points_gnuplot_template(algorithm))
    f.close()

    # open  data file
    fdat = open(algorithm + ".dat", 'w')

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

    # first of all open gnuplot template file
    f = open(algorithm + ".gpi", 'w')
    f.write(points_gnuplot_template(algorithm))
    f.close()

    # open  data file
    fdat = open(algorithm + ".dat", 'w')

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

    # first of all open gnuplot template file
    f = open(algorithm + ".gpi", 'w')
    f.write(lines_gnuplot_template(algorithm))
    f.close()

    # open  data file
    fdat = open(algorithm + ".dat", 'w')

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

    # first of all open gnuplot template file
    f = open(algorithm + ".gpi", 'w')
    f.write(lines_gnuplot_template(algorithm))
    f.close()

    # open  data file
    fdat = open(algorithm + ".dat", 'w')

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

    # first of all open gnuplot template file
    f = open(algorithm + ".gpi", 'w')
    f.write(points_gnuplot_template(algorithm))
    f.close()

    # open  data file
    fdat = open(algorithm + ".dat", 'w')

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
trg()
trg_vanilla()
shadowing()
nakagami()
log_distance()
