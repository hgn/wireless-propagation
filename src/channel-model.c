#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <getopt.h>
#include <time.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <gsl/gsl_math.h>
#include <gsl/gsl_rng.h>
#include <gsl/gsl_randist.h>

#define	SEED_DEVICE "/dev/urandom"

#define	DEFAULT_FREQUENCY (2.4 * 1000 * 1000 * 1000) /* 2.4 GHz */
#define	DEFAULT_SYSTEM_LOSS 1.0
#define	DEFAULT_TX_POWER 0.1 /* Watt */
#define	DEFAULT_RX_ANTENNA_GAIN 1.0
#define	DEFAULT_TX_ANTENNA_GAIN 1.0
#define	DEFAULT_RX_ANTENNA_HEIGHT 1.5 /* meter */
#define	DEFAULT_TX_ANTENNA_HEIGHT 1.5 /* meter */

/* shadowing model */
#define	DEFAULT_SHADOWING_PATHLOSS_EXP 2.0
#define	DEFAULT_SHADOWING_STD_DB 4.0
#define	DEFAULT_SHADOWING_DISTANCE 1.0

#define SPEED_OF_LIGHT  299792458.0

enum algo {
	FRIIS = 1,
	TWO_RAY_GROUND,
	TWO_RAY_GROUND_VANILLA,
	SHADOWING,
};

struct opts {
	enum algo algo;
	double node_distance;
	double frequency;
	double system_loss;
	double tx_power;
	double tx_antenna_gain;
	double rx_antenna_gain;
	double rx_antenna_height;
	double tx_antenna_height;
	double shadowing_pathloss_exp;
	double shadowing_std_db;
	double shadowing_distance;
};

struct c_env {
	gsl_rng *rng;
};


/* calculate lambda */
static double calc_wave_length(double frequency)
{
	return SPEED_OF_LIGHT / frequency;
}

static double dbm_to_watt(double dbm)
{
	return (pow(10.0, dbm / 10.0)) / 1000.0;
}

static double watt_to_dbm(double watt)
{
	return log10(watt * 1000.0) * 10.0;
}

double friis(double pt, double gt, double gr, double lambda, double l, double d)
{
        /*
         * Friis free space equation:
         *
         *       Pt * Gt * Gr * (lambda^2)
         *   P = --------------------------
         *       (4 * pi * d)^2 * L
         */
  double m = lambda / (4 * M_PI * d);
  return (pt * gt * gr * (m * m)) / l;
}

double calc_crossover_distance(double height_tx, double height_rx, double lambda)
{
	/*
	         4 * PI * hr * ht
	 d = ----------------------------
	             lambda

	* At the crossover distance, the received power predicted by the two-ray
	* ground model equals to that predicted by the Friis equation.
    */

	return (4 * M_PI * height_tx * height_rx) / lambda;
}

double two_ray_ground(double pt, double gt, double gr, double ht, double hr, double l, double d)
{
        /*
         *  Two-ray ground reflection model.
         *
         *	     Pt * Gt * Gr * (ht^2 * hr^2)
         *  Pr = ----------------------------
         *           d^4 * L
         *
         * The original equation in Rappaport's book assumes L = 1.
         * To be consistant with the free space equation, L is added here.
         */
  return pt * gt * gr * (hr * hr * ht * ht) / (d * d * d * d * l);
}

static void die(int exit_code, char *msg)
{
	fprintf(stderr, "%s\n", msg);
	exit(exit_code);
}

static void print_usage(void)
{
	fputs("./channel-mode <algo> <distance>\n", stderr);
}

static void setup_defaults(struct opts *opts)
{
	/* standard values */
	opts->frequency         = DEFAULT_FREQUENCY;
	opts->system_loss       = DEFAULT_SYSTEM_LOSS;
	opts->tx_power          = DEFAULT_TX_POWER;
	opts->rx_antenna_gain   = DEFAULT_RX_ANTENNA_GAIN;
	opts->tx_antenna_gain   = DEFAULT_TX_ANTENNA_GAIN;
	opts->tx_antenna_height = DEFAULT_TX_ANTENNA_HEIGHT;
	opts->rx_antenna_height = DEFAULT_RX_ANTENNA_HEIGHT;

	/* shadowing related values*/
	opts->shadowing_pathloss_exp = DEFAULT_SHADOWING_PATHLOSS_EXP;
	opts->shadowing_std_db       = DEFAULT_SHADOWING_STD_DB;
	opts->shadowing_distance     = DEFAULT_SHADOWING_DISTANCE;

	opts->node_distance = -1.0;
}

static struct opts* parse_opts(int ac, char **av)
{
	int c;
	struct opts *opts;

	opts = malloc(sizeof(*opts));
	if (!opts)
		die(EXIT_FAILURE, "Out of memory");
	memset(opts, 0, sizeof(*opts));

	setup_defaults(opts);

	while (1) {
		int option_index = 0;
		static struct option long_options[] = {

			/* standard values */
			{"algorithm",       1, 0, 'a'},
			{"distance",        1, 0, 'd'},
			{"frequency",       1, 0, 'f'},
			{"systemloss",      1, 0, 'l'},
			{"txpower",         1, 0, 'p'},
			{"rxantennagain",   1, 0, 'r'},
			{"txantennagain",   1, 0, 't'},
			{"rxantennaheight", 1, 0, 'u'},
			{"txantennaheight", 1, 0, 'i'},

			/* shadowing values */
			{"shadowingpathlossexp", 1, 0, 'g'},
			{"shadowingstddb",       1, 0, 'h'},
			{"shadowingdistance",    1, 0, 'j'},

			{0, 0, 0, 0}
		};

		c = getopt_long(ac, av, "a:d:f:l:p:r:t:u:i:g:h:j:",
				long_options, &option_index);
		if (c == -1)
			break;

		switch (c) {
			case 'a':
				if (!strcasecmp(optarg, "friis")) {
					opts->algo = FRIIS;
				} else if (!strcasecmp(optarg, "tworayground")) {
					opts->algo = TWO_RAY_GROUND;
				} else if (!strcasecmp(optarg, "tworaygroundvanilla")) {
					opts->algo = TWO_RAY_GROUND_VANILLA;
				} else if (!strcasecmp(optarg, "shadowing")) {
					opts->algo = SHADOWING;
				} else {
					fprintf(stderr, "Algorithm \"%s\" not supported!\n",
							av[1]);
					print_usage();
					exit(EXIT_FAILURE);
				}
				break;

			case 'd':
				opts->node_distance = strtod(optarg, NULL);
				break;

			case 'f':
				opts->frequency = strtod(optarg, NULL);
				break;

			case 'p':
				opts->tx_power = strtod(optarg, NULL);
				break;

			case 'l':
				opts->system_loss = strtod(optarg, NULL);
				break;

			case 'r':
				opts->rx_antenna_gain = strtod(optarg, NULL);
				break;

			case 't':
				opts->tx_antenna_gain = strtod(optarg, NULL);
				break;

			case 'u':
				opts->rx_antenna_height = strtod(optarg, NULL);
				break;

			case 'i':
				opts->tx_antenna_height = strtod(optarg, NULL);
				break;

			case 'g':
				opts->shadowing_pathloss_exp = strtod(optarg, NULL);
				break;

			case 'h':
				opts->shadowing_std_db = strtod(optarg, NULL);
				break;

			case 'j':
				opts->shadowing_distance = strtod(optarg, NULL);
				break;

			case '?':
				break;

			default:
				printf("?? getopt returned character code 0%o ??\n", c);
		}
	}

	if (!opts->algo)
		die(EXIT_FAILURE, "No algorithm given");

	if (opts->node_distance < 0)
		die(EXIT_FAILURE, "No valid distance given (> 0m)");

	return opts;
}

static void calc_friis(const struct opts *opts)
{
	double dbm;
	double wave_length = calc_wave_length(opts->frequency);

	double rx_power = friis(opts->tx_power,
							opts->tx_antenna_gain,
							opts->rx_antenna_gain,
							wave_length,
							opts->system_loss,
							opts->node_distance);

	dbm = watt_to_dbm(rx_power);

	fprintf(stdout, "%lf\n", dbm);
}

static void calc_two_ray_ground(const struct opts *opts)
{
	double dbm, rx_power;
	double wave_length = calc_wave_length(opts->frequency);

	double x_border = calc_crossover_distance(opts->tx_antenna_height,
			                                  opts->rx_antenna_height,
											  wave_length);


	if (opts->node_distance < x_border) {
		/* friis */
		rx_power = friis(opts->tx_power,
							opts->tx_antenna_gain,
							opts->rx_antenna_gain,
							wave_length,
							opts->system_loss,
							opts->node_distance);
	} else {
		/* two ray ground */
		rx_power = two_ray_ground(opts->tx_power,
							opts->tx_antenna_gain,
							opts->rx_antenna_gain,
							opts->tx_antenna_height,
							opts->rx_antenna_height,
							opts->system_loss,
							opts->node_distance);
	}

	dbm = watt_to_dbm(rx_power);

	fprintf(stdout, "%lf\n", dbm);
}

static void calc_two_ray_ground_vanilla(const struct opts *opts)
{
	double dbm, rx_power;

	rx_power = two_ray_ground(opts->tx_power,
						opts->tx_antenna_gain,
						opts->rx_antenna_gain,
						opts->tx_antenna_height,
						opts->rx_antenna_height,
						opts->system_loss,
						opts->node_distance);

	dbm = watt_to_dbm(rx_power);

	fprintf(stdout, "%lf\n", dbm);
}

static void calc_shadowing(const struct opts *opts, struct c_env *c_env)
{
	double dbm, avg_db, pr, power_loss_db;
	double wave_length = calc_wave_length(opts->frequency);

	double rx_power = friis(opts->tx_power,
							opts->tx_antenna_gain,
							opts->rx_antenna_gain,
							wave_length,
							opts->system_loss,
							opts->node_distance);

	if (opts->node_distance > opts->shadowing_distance) {
		avg_db = -10.0 * opts->shadowing_pathloss_exp *
			log10(opts->node_distance/opts->shadowing_distance);
	} else {
		avg_db = 0.0;
	}

	power_loss_db = avg_db + gsl_ran_gaussian(c_env->rng, opts->shadowing_std_db);

	pr = rx_power * pow(10.0, (power_loss_db / 10.0));

	dbm = watt_to_dbm(pr);

	fprintf(stdout, "%lf\n", dbm);
}

static struct c_env* init_env(void)
{
	struct c_env *ret;
	int fd;
	unsigned long rtn;
	char *crypt_device;

	gsl_rng_env_setup();

	ret = malloc(sizeof(*ret));
	if (!ret)
		die(EXIT_FAILURE, "Out of memory");

	memset(ret, 0, sizeof(*ret));

	/* take the mersenne twister as default prng one */
	ret->rng = gsl_rng_alloc(gsl_rng_mt19937);
	if (!ret->rng) {
		/* fall back to the dafault */
		ret->rng = gsl_rng_alloc(gsl_rng_default);
		if (!ret->rng)
			die(EXIT_FAILURE, "Cannot initialize random number generator\n");

		/* seems to work ... */
	}

	/* set seed */
	crypt_device = SEED_DEVICE;
	if ( (fd = open(crypt_device, O_RDONLY)) < 0 ) {
		rtn = (long) time(NULL);
	} else {
		if ( (read(fd, &rtn, sizeof(long))) < (int)sizeof(long)) {
			rtn = (long) time(NULL);
		}
	}
	gsl_rng_set(ret->rng, rtn);

	return ret;
}

static void finit_env(struct c_env *c_env)
{
	gsl_rng_free(c_env->rng);
	free(c_env);
}

int main(int ac, char **av)
{
	struct opts *opts;
	struct c_env *c_env;

	opts = parse_opts(ac, av);
	c_env = init_env();


	switch (opts->algo) {
		case FRIIS:
			calc_friis(opts);
			break;
		case TWO_RAY_GROUND:
			calc_two_ray_ground(opts);
			break;
		case TWO_RAY_GROUND_VANILLA:
			calc_two_ray_ground_vanilla(opts);
			break;
		case SHADOWING:
			calc_shadowing(opts, c_env);
			break;
		default:
			fprintf(stderr, "Programmed error in switch/case statement: %s:%d\n",
					__FILE__, __LINE__);
			exit(EXIT_FAILURE);
	}

	finit_env(c_env);

	free(opts);

	return 0;
}
