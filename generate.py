#!/usr/bin/env python


import math
import os
from subprocess import *

p_path = "./src/channel-model"


##########################################
##########################################
##########################################
def friis_gnuplot_template():
    return """
    set term postscript eps enhanced color "Times" 30
    set output "friis.eps"

    set size 2

    set key spacing 1.2
    set grid xtics ytics mytics

    set title "Friis Path Loss Behaviour"
    set xlabel "Node Distance [meter]"
    set ylabel "RX Power [dbm]"

    set yrange[-150:20]

    set style line 1 linetype 1 linecolor rgb "#3e6694" lw 15

    plot "friis.dat" using 1:2 title "Friis" with points ls 1
    !epstopdf --outfile=friis.pdf friis.eps
    !rm -rf friis.eps
    """


def friis():

    # first of all open gnuplot template file
    f = open('friis.gpi', 'w')
    f.write(friis_gnuplot_template())
    f.close()

    # open  data file
    fdat = open('friis.dat', 'w')

    for i in range(1, 500):
        f = float(i)
        output = Popen([p_path,
            "--algorithm", "friis",
            "--distance", "%f" % f],
            stdout=PIPE).communicate()[0]
        fdat.write("%f %s\n" % (f, output.rstrip('\n')))

    fdat.close()

    # execute gnuplot
    p = Popen("gnuplot" + " friis.gpi", shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv friis.pdf latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)



##########################################
##########################################
##########################################
def trg_gnuplot_template():
    return """
    set term postscript eps enhanced color "Times" 30
    set output "trg.eps"
    set size 2

    set key spacing 1.2
    set grid xtics ytics mytics

    set title "Two Ray Ground Path Loss Behaviour"
    set xlabel "Node Distance [meter]"
    set ylabel "RX Power [dbm]"

    set yrange[-150:20]

    set style line 1 linetype 1 linecolor rgb "#3e6694" lw 15

    plot "trg.dat" using 1:2 title "Two Ray Ground" with points ls 1
    !epstopdf --outfile=trg.pdf trg.eps
    !rm -rf trg.eps
    """


def trg():

    # first of all open gnuplot template file
    f = open('trg.gpi', 'w')
    f.write(trg_gnuplot_template())
    f.close()

    # open  data file
    fdat = open('trg.dat', 'w')

    for i in range(1, 500):
        f = float(i)
        output = Popen([p_path,
            "--algorithm", "tworayground",
            "--distance", "%f" % f],
            stdout=PIPE).communicate()[0]
        fdat.write("%f %s\n" % (f, output.rstrip('\n')))

    fdat.close()

    # execute gnuplot
    p = Popen("gnuplot" + " trg.gpi", shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv trg.pdf latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)

##########################################
##########################################
##########################################
def trg_vanilla_gnuplot_template():
    return """
    set term postscript eps enhanced color "Times" 30
    set output "trg_vanilla.eps"
    set size 2

    set key spacing 1.2
    set grid xtics ytics mytics

    set title "Two Ray Ground Path Loss Behaviour"
    set xlabel "Node Distance [meter]"
    set ylabel "RX Power [dbm]"

    set yrange[-150:20]

    set style line 1 linetype 1 linecolor rgb "#3e6694" lw 15

    plot "trg_vanilla.dat" using 1:2 title "Two Ray Ground" with points ls 1
    !epstopdf --outfile=trg_vanilla.pdf trg_vanilla.eps
    !rm -rf trg_vanilla.eps
    """


def trg_vanilla():

    prefix = "trg_vanilla"

    # first of all open gnuplot template file
    f = open(prefix + ".gpi", 'w')
    f.write(trg_vanilla_gnuplot_template())
    f.close()

    # open  data file
    fdat = open(prefix + ".dat", 'w')

    for i in range(1, 500):
        f = float(i)
        output = Popen([p_path,
            "--algorithm", "tworaygroundvanilla",
            "--distance", "%f" % f],
            stdout=PIPE).communicate()[0]
        fdat.write("%f %s\n" % (f, output.rstrip('\n')))

    fdat.close()

    # execute gnuplot
    p = Popen("gnuplot" + " " + prefix + ".gpi", shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + prefix + ".pdf latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)

friis()
trg()
trg_vanilla()
