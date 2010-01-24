#!/usr/bin/env python


import math
import os
from subprocess import *
import tempfile

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

def lines_gnuplot_template_n(alg, y_min = -150, y_max = 20, linewidth = 4, datafiles=[]):

    if len(datafiles) == 0:
        raise NameError, 'No file names given for datafile'

    gnuplot_str = """
    set term postscript eps enhanced color "Times" 30
    set output "%s.eps"

    set size 2

    set key spacing 1.2
    set grid xtics ytics mytics

    set title "%s Path Loss Model"
    set xlabel "Node Distance [meter]"
    set ylabel "RX Power [dbm]"

    for datafile in datafiles


    set yrange[%d:%d]

    set style line 1 linetype 1 linecolor rgb "#3e6694" lw %d
    plot "%s" using 1:2 title "%s" with lines ls 1
    """ % (alg, alg, y_min, y_max, linewidth, datafiles[0])

    for i in range(len(datafiles) - 1):
        gnuplot_str += """
         "%s" using 1:2 title "" with lines ls 1
        """ % (alg, datafiles[i])

    gnuplot_str += """
    !epstopdf --outfile=%s.pdf %s.eps
    !rm -rf %s.eps
    """ % (alg, alg, alg)


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
def nakagami_m0_distribution(m_val = 0.15):

    algorithm = "nakagami"
    name        = "nakagami" + str(m_val) + "_distribution"
    gnuplotname = name + ".gpi"
    delta       = 0.52
    iterations  = 60
    datafile    = name + ".dat"
    pdfname     = name + ".pdf"

    gpi_src = """
    set term postscript eps enhanced color "Times" 30
    set output "%s.eps"

    set size 2

    set key spacing 1.2
    set grid xtics ytics mytics

    set title "%s Path Loss Model"
    set xlabel "Node Distance [meter]"
    set ylabel "RX Power [dbm]"

    set yrange[-120:20]

    set style line 1 linetype 2 linecolor rgb "#3e6694" lw 5

    plot "%s" using 1:2 title "%s" with dots ls 1
    !epstopdf --outfile=%s.pdf %s.eps
    !rm -rf %s.eps
    """ %(name, "Nakagami Distribution", datafile, "Nakagami Dispersion (m = " + str(m_val) + ")", name, name, name)

    # first of all open gnuplot template file
    f = open(gnuplotname, 'w')
    f.write(gpi_src)
    f.close()

    # open  data file
    fdat = open(datafile, 'a')

    for i in range(iterations):
        output = Popen([p_path,
            "--delta", str(delta),
            "--m0", str(m_val),
            "--m1", str(m_val),
            "--m2", str(m_val),
            "--algorithm", algorithm ],
            stdout=PIPE).communicate()[0]
        fdat.write("%s\n" % (output))

    fdat.close()

    # execute gnuplot
    p = Popen("gnuplot" + " " + gnuplotname, shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + pdfname + " latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)

##########################################
##########################################
##########################################
def nakagami_m0_variances():

    algorithm = "nakagami"
    name        = "nakagami" + "_m0_variances"
    gnuplotname = name + ".gpi"
    datafile1  = tempfile.NamedTemporaryFile()
    datafile2  = tempfile.NamedTemporaryFile()
    datafile3  = tempfile.NamedTemporaryFile()
    datafile4  = tempfile.NamedTemporaryFile()
    datafile5  = tempfile.NamedTemporaryFile()
    pdfname    = name + ".pdf"

    gpi_src = """
    set term postscript eps enhanced color "Times" 25
    set output "%s.eps"

    set size 2

    set key spacing 1.2
    set grid xtics ytics mytics

    set title "%s Path Loss Model"
    set xlabel "Node Distance [meter]"
    set ylabel "RX Power [dbm]"

    set yrange[-100:0]
    set xrange[0:200]

    set style line 1 linetype 1 linecolor rgb "#3e6694" lw 3
    set style line 2 linetype 1 linecolor rgb "#ff0000" lw 3
    set style line 3 linetype 1 linecolor rgb "#00ff00" lw 3
    set style line 4 linetype 1 linecolor rgb "#00ffff" lw 3
    set style line 5 linetype 1 linecolor rgb "#0000ff" lw 3

    plot "%s" using 1:2 title "m0 = 0.25" with lines ls 1, \
         "%s" using 1:2 title "m0 = 1.0" with lines ls 2, \
         "%s" using 1:2 title "m0 = 1.5 (default)" with lines ls 3, \
         "%s" using 1:2 title "m0 = 2.0" with lines ls 4, \
         "%s" using 1:2 title "m0 = 5.0" with lines ls 5
    !epstopdf --outfile=%s.pdf %s.eps
    !rm -rf %s.eps
    """ %(name, "Nakagami M0 Effects (d0m = 80)",
            datafile1.name, datafile2.name, datafile3.name, datafile4.name, datafile5.name,
            name, name, name)

    # first of all open gnuplot template file
    f = open(gnuplotname, 'w')
    f.write(gpi_src)
    f.close()

    # open  data file
    fdat = datafile1
    output = Popen([p_path,
        "--m0", "0.25",
        "--algorithm", algorithm ],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))

    fdat = datafile2
    output = Popen([p_path,
        "--m0", "1.0",
        "--algorithm", algorithm ],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))

    fdat = datafile3
    output = Popen([p_path,
        "--m0", "1.5",
        "--algorithm", algorithm ],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))

    fdat = datafile4
    output = Popen([p_path,
        "--m0", "2.0",
        "--algorithm", algorithm ],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))

    fdat = datafile5
    output = Popen([p_path,
        "--m0", "5.0",
        "--algorithm", algorithm ],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))

    # execute gnuplot
    p = Popen("gnuplot" + " " + gnuplotname, shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + pdfname + " latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)

    datafile1.close()
    datafile2.close()
    datafile3.close()
    datafile4.close()
    datafile5.close()

##########################################
##########################################
##########################################
def nakagami_m0_variance_distribution():

    algorithm   = "nakagami"
    name        = "nakagami" + "_m0_variance_distribution"
    iterations  = 100
    delta       = 0.2
    gnuplotname = name + ".gpi"
    datafile1   = tempfile.NamedTemporaryFile(mode = 'a')
    datafile2   = tempfile.NamedTemporaryFile(mode = 'a')
    datafile3   = tempfile.NamedTemporaryFile(mode = 'a')
    datafile4   = tempfile.NamedTemporaryFile(mode = 'a')
    datafile5   = tempfile.NamedTemporaryFile(mode = 'a')
    pdfname     = name + ".pdf"

    gpi_src = """
    set term postscript eps enhanced color "Times" 30
    set output "%s.eps"

    set size 2

    set key spacing 1.2
    set grid xtics ytics mytics

    set title "%s Path Loss Model"
    set xlabel "Node Distance [meter]"
    set ylabel "RX Power [dbm]"

    set yrange[-100:0]
    set xrange[0:80]

    set style line 1 linetype 3 linecolor rgb "#3e6694" lw 6
    set style line 2 linetype 3 linecolor rgb "#ff0000" lw 6
    set style line 3 linetype 3 linecolor rgb "#00ff00" lw 6
    set style line 4 linetype 3 linecolor rgb "#00ffff" lw 6
    set style line 5 linetype 3 linecolor rgb "#0000ff" lw 6

    plot "%s" using 1:2 title "m0 = 0.25" with dots ls 1, \
            "%s" using 1:2 title "m0 = 1.0" with dots ls 2, \
            "%s" using 1:2 title "m0 = 1.5 (default)" with dots ls 3, \
            "%s" using 1:2 title "m0 = 2.0" with dots ls 4, \
            "%s" using 1:2 title "m0 = 5.0" with dots ls 5
    !epstopdf --outfile=%s.pdf %s.eps
    !rm -rf %s.eps
    """ %(name, "Nakagami M0 Effects (d0m = 80)",
            datafile1.name, datafile2.name, datafile3.name, datafile4.name, datafile5.name,
            name, name, name)

    # first of all open gnuplot template file
    f = open(gnuplotname, 'w')
    f.write(gpi_src)
    f.close()

    # open  data file
    fdat = datafile1
    for i in range(iterations):
        output = Popen([p_path,
            "--delta", str(delta),
            "--m0", "0.25",
            "--algorithm", algorithm ],
            stdout=PIPE).communicate()[0]
        fdat.write("%s\n" % (output))

    fdat = datafile2
    for i in range(iterations):
        output = Popen([p_path,
            "--delta", str(delta),
            "--m0", "1.0",
            "--algorithm", algorithm ],
            stdout=PIPE).communicate()[0]
        fdat.write("%s\n" % (output))

    fdat = datafile3
    for i in range(iterations):
        output = Popen([p_path,
            "--delta", str(delta),
            "--m0", "1.5",
            "--algorithm", algorithm ],
            stdout=PIPE).communicate()[0]
        fdat.write("%s\n" % (output))

    fdat = datafile4
    for i in range(iterations):
        output = Popen([p_path,
            "--delta", str(delta),
            "--m0", "2.0",
            "--algorithm", algorithm ],
            stdout=PIPE).communicate()[0]
        fdat.write("%s\n" % (output))

    fdat = datafile5
    for i in range(iterations):
        output = Popen([p_path,
            "--delta", str(delta),
            "--m0", "5.0",
            "--algorithm", algorithm ],
            stdout=PIPE).communicate()[0]
        fdat.write("%s\n" % (output))

    # execute gnuplot
    p = Popen("gnuplot" + " " + gnuplotname, shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + pdfname + " latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)

    datafile1.close()
    datafile2.close()
    datafile3.close()
    datafile4.close()
    datafile5.close()

##########################################
##########################################
##########################################
def nakagami_distribution():

    algorithm = "nakagami"
    name        = "nakagami" + "_distribution"
    gnuplotname = name + ".gpi"
    datafile    = name + ".dat"
    pdfname     = name + ".pdf"

    gpi_src = """
    set term postscript eps enhanced color "Times" 30
    set output "%s.eps"

    set size 2

    set key spacing 1.2
    set grid xtics ytics mytics

    set title "%s Path Loss Model"
    set xlabel "Node Distance [meter]"
    set ylabel "RX Power [dbm]"

    set yrange[-120:20]

    set style line 1 linetype 2 linecolor rgb "#3e6694" lw 5

    plot "%s" using 1:2 title "%s" with dots ls 1
    !epstopdf --outfile=%s.pdf %s.eps
    !rm -rf %s.eps
    """ %(name, "Nakagami Dispersion", datafile, "Nakagami Dispersion", name, name, name)

    # first of all open gnuplot template file
    f = open(gnuplotname, 'w')
    f.write(gpi_src)
    f.close()

    # open  data file
    fdat = open(datafile, 'a')

    for i in range(30):
        output = Popen([p_path,
            "--algorithm", algorithm ],
            stdout=PIPE).communicate()[0]
        fdat.write("%s\n" % (output))

    fdat.close()

    # execute gnuplot
    p = Popen("gnuplot" + " " + gnuplotname, shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + pdfname + " latex/images", shell=True)
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
##########################################
def ber():

    name        = "ber" 
    pdfname    = name + ".pdf"
    gnuplotname = name + ".gpi"

    algorithm1 = "bpsk"
    datafile1  = tempfile.NamedTemporaryFile()
    algorithm2 = "qam4"
    datafile2  = tempfile.NamedTemporaryFile()
    algorithm3 = "4pam"
    datafile3  = tempfile.NamedTemporaryFile()
    algorithm4 = "qam16"
    datafile4  = tempfile.NamedTemporaryFile()
    algorithm5 = "16psk"
    datafile5  = tempfile.NamedTemporaryFile()


    gpi_src = """
    set term postscript eps enhanced color "Times" 30
    set output "%s.eps"

    set key left bottom

    set size 2

    set key spacing 1.2
    set grid 

    set title "Symbol error probability curve for various modulation schemes"
    set xlabel "Es/No [dB]"
    set ylabel "Symbol Error Rate [%%]"

    set log y

    #set yrange[-100:0]
    #set xrange[0:200]

    set style line 1 linetype 1 linecolor rgb "#3e6694" lw 5
    set style line 2 linetype 1 linecolor rgb "#ff0000" lw 5
    set style line 3 linetype 1 linecolor rgb "#00ff00" lw 5
    set style line 4 linetype 1 linecolor rgb "#00ffff" lw 5
    set style line 5 linetype 1 linecolor rgb "#0000ff" lw 5

    plot "%s" using 2:1 title "BPSK"  with linespoints ls 1, \
         "%s" using 2:1 title "QAM4"  with linespoints ls 2, \
         "%s" using 2:1 title "4PAM"  with linespoints ls 3, \
         "%s" using 2:1 title "QAM16" with linespoints ls 4, \
         "%s" using 2:1 title "16PSK" with linespoints ls 5
    !epstopdf --outfile=%s.pdf %s.eps
    !rm -rf %s.eps
    """ %(name, datafile1.name, datafile2.name, datafile3.name,
            datafile4.name, datafile5.name,
            name, name, name)

    # first of all open gnuplot template file
    f = open(gnuplotname, 'w')
    f.write(gpi_src)
    f.close()

    # open  data file
    fdat = datafile1
    alg  = algorithm1
    output = Popen([p_path, "--modulation", alg, "-b"],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))
    fdat.flush()

    # open  data file
    fdat = datafile2
    alg  = algorithm2
    output = Popen([p_path, "--modulation", alg, "-b"],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))
    fdat.flush()

    fdat = datafile3
    alg  = algorithm3
    output = Popen([p_path, "--modulation", alg, "-b"],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))
    fdat.flush()

    fdat = datafile4
    alg  = algorithm4
    output = Popen([p_path, "--modulation", alg, "-b"],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))
    fdat.flush()

    fdat = datafile5
    alg  = algorithm5
    output = Popen([p_path, "--modulation", alg, "-b"],
        stdout=PIPE).communicate()[0]
    fdat.write("%s\n" % (output))
    fdat.flush()

    # execute gnuplot
    p = Popen("gnuplot" + " " + gnuplotname, shell=True)
    sts = os.waitpid(p.pid, 0)

    # move image in tex directory
    p = Popen("mv " + pdfname + " latex/images", shell=True)
    sts = os.waitpid(p.pid, 0)

    datafile1.close()
    datafile2.close()
    datafile3.close()
    datafile4.close()
    datafile5.close()



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
nakagami_distribution()
nakagami_m0_variances()
nakagami_m0_variance_distribution()
nakagami_m0_distribution(0.15)
nakagami_m0_distribution(0.25)
nakagami_m0_distribution(1.0)
nakagami_m0_distribution(1.5)
nakagami_m0_distribution(2.0)
nakagami_m0_distribution(5.0)
ber()
