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

/* friis and two ray ground values */
#define	DEFAULT_FREQUENCY (2.4 * 1000 * 1000 * 1000) /* 2.4 GHz */
#define	DEFAULT_SYSTEM_LOSS 1.0
#define	DEFAULT_TX_POWER 0.1 /* Watt */
#define	DEFAULT_RX_ANTENNA_GAIN 1.0
#define	DEFAULT_TX_ANTENNA_GAIN 1.0
#define	DEFAULT_RX_ANTENNA_HEIGHT 1.5 /* meter */
#define	DEFAULT_TX_ANTENNA_HEIGHT 1.5 /* meter */

/* shadowing values */
#define	DEFAULT_SHADOWING_PATHLOSS_EXP 2.0
#define	DEFAULT_SHADOWING_STD_DB 4.0
#define	DEFAULT_SHADOWING_DISTANCE 1.0

/* nakagami values */
#define	DEFAULT_NAKAGAMI_M0 1.50
#define	DEFAULT_NAKAGAMI_M1 0.75
#define	DEFAULT_NAKAGAMI_M2 0.75

#define	DEFAULT_NAKAGAMI_D0_M  80
#define	DEFAULT_NAKAGAMI_D1_M 200
#define	DEFAULT_NAKAGAMI_USE_DIST 1 /* true */

/* log distance values */
#define	DEFAULT_LOG_DISTANCE_EXPONENT 3.0
#define	DEFAULT_LOG_DISTANCE_REFERENCE_DISTANCE 1.0

/* three log distance values */
#define	DEFAULT_THREE_LOG_DISTANCE_REFERENCE_DISTANCE_1 1.0
#define	DEFAULT_THREE_LOG_DISTANCE_EXPONENT_1 1.9
#define	DEFAULT_THREE_LOG_DISTANCE_REFERENCE_DISTANCE_2 200.0
#define	DEFAULT_THREE_LOG_DISTANCE_EXPONENT_2 3.8
#define	DEFAULT_THREE_LOG_DISTANCE_REFERENCE_DISTANCE_3 500.0
#define	DEFAULT_THREE_LOG_DISTANCE_EXPONENT_3 3.8
#define	DEFAULT_THREE_LOG_DISTANCE_REFERENCE_DISTANCE 1.0

#define SPEED_OF_LIGHT  299792458.0

/* 1 meter iteration steps from 1 meter node distance till 500 distance */
#define	DEFAULT_START 1
#define	DEFAULT_END 500.0
#define	DEFAULT_DELTA 1.0


enum algo {
	FRIIS = 1,
	TWO_RAY_GROUND,
	TWO_RAY_GROUND_VANILLA,
	SHADOWING,
	NAKAGAMI,
	LOG_DISTANCE,
	THREE_LOG_DISTANCE
};

enum modulation {
	QAM4 = 1,
};


struct opts {
	double start;
	double end;
	double delta;

	double frequency;
	double system_loss;
	double tx_power;
	double tx_antenna_gain;
	double rx_antenna_gain;
	double rx_antenna_height;
	double tx_antenna_height;

	struct {
		double shadowing_pathloss_exp;
		double shadowing_std_db;
		double shadowing_distance;
	} shadowing;

	struct {
		double m0;
		double m1;
		double m2;
		double d0_m;
		double d1_m;
		double use_dist;
	} nakagami;

	struct {
		double exponent;
		double reference_dist;
	} log_distance;

	struct {
		double distance_1;
		double distance_2;
		double distance_3;

		double exponent_1;
		double exponent_2;
		double exponent_3;

		double reference_distance;
	} three_log_distance;

};

#define	OPTS_THREE_LOG(opts) opts->three_log_distance
#define	OPTS_LOG_DISTANCE(opts) opts->log_distance
#define	OPTS_NAKAGAMI(opts) opts->nakagami
#define	OPTS_SHADOWING(opts) opts->shadowing

struct c_env {
	gsl_rng *rng;
	enum algo algo;
	double (*func)(const struct opts *, struct c_env *, const double);
	enum modulation modulation;
	double (*modulation_ber_func)(const struct opts *, struct c_env *, const double);
};

/* al cheapo forward declarations */
static double calc_shadowing(const struct opts *, struct c_env *, const double);
static double calc_nakagami(const struct opts *, struct c_env *, const double);
static double calc_two_ray_ground_vanilla(const struct opts *, struct c_env *, const double);
static double calc_two_ray_ground(const struct opts *, struct c_env *, const double);
static double calc_friis(const struct opts *, struct c_env *, const double);
static double calc_log_distance(const struct opts *, struct c_env *, const double);
static double calc_three_log_distance(const struct opts *, struct c_env *, const double);

static double ber_qam4(const struct opts *, struct c_env *, const double);

struct algorithms {
	const char *name;
	enum algo algo;
	double (*func)(const struct opts *, struct c_env *, const double);
} algorithms[] = {
	{ "shadowing", SHADOWING,  calc_shadowing },
	{ "nakagami", NAKAGAMI, calc_nakagami },
	{ "tworaygroundvanilla", TWO_RAY_GROUND_VANILLA, calc_two_ray_ground_vanilla },
	{ "tworayground", TWO_RAY_GROUND, calc_two_ray_ground },
	{ "friis", FRIIS, calc_friis },
	{ "logdistance", LOG_DISTANCE, calc_log_distance },
	{ "threelogdistance", THREE_LOG_DISTANCE, calc_three_log_distance },
	{ NULL, 0, 0 }
};

struct modulations {
	const char *name;
	enum modulation modulation;
	double (*func)(const struct opts *, struct c_env *, const double);
} modulations[] = {
	{ "qam4", QAM4, ber_qam4 },
	{ NULL, 0, 0 }
};


/* calculate lambda */
static double
calc_wave_length(double frequency)
{
	return SPEED_OF_LIGHT / frequency;
}


static double
dbm_to_watt(double dbm)
{
	return (pow(10.0, dbm / 10.0)) / 1000.0;
}


static double
watt_to_dbm(double watt)
{
	return log10(watt * 1000.0) * 10.0;
}


static double
friis(double pt, double gt, double gr, double lambda, double l, double d)
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


static double
calc_crossover_distance(double height_tx, double height_rx, double lambda)
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


static double
two_ray_ground(double pt, double gt, double gr,
		       double ht, double hr, double l, double d)
{
        /*
         *	     Pt * Gt * Gr * (ht^2 * hr^2)
         *  Pr = ----------------------------
         *           d^4 * L
         *
         * The original equation in Rappaport's
		 * book assumes L = 1. To be consistant
		 * with the free space equation, L is
		 * added here.
         */
  return pt * gt * gr * (hr * hr * ht * ht) / (d * d * d * d * l);
}


static void
die(int exit_code, char *msg)
{
	fprintf(stderr, "%s\n", msg);
	exit(exit_code);
}


static void
print_usage(void)
{
	const char *name;
	int i = 0;

	fputs("./channel-mode <algo> <distance>\n", stderr);
	fputs("\tSupported algorithm are:\n", stderr);

	name = algorithms[i++].name;
	for (; name != NULL; name = algorithms[i++].name) {
		fprintf(stderr,"\t\to %s\n", name);
	}
}


static void
setup_defaults(struct opts *opts)
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
	OPTS_SHADOWING(opts).shadowing_pathloss_exp = DEFAULT_SHADOWING_PATHLOSS_EXP;
	OPTS_SHADOWING(opts).shadowing_std_db       = DEFAULT_SHADOWING_STD_DB;
	OPTS_SHADOWING(opts).shadowing_distance     = DEFAULT_SHADOWING_DISTANCE;

	/* nakagami setup */
	OPTS_NAKAGAMI(opts).m0 = DEFAULT_NAKAGAMI_M0;
	OPTS_NAKAGAMI(opts).m1 = DEFAULT_NAKAGAMI_M1;
	OPTS_NAKAGAMI(opts).m2 = DEFAULT_NAKAGAMI_M2;
	OPTS_NAKAGAMI(opts).d0_m = DEFAULT_NAKAGAMI_D0_M;
	OPTS_NAKAGAMI(opts).d1_m = DEFAULT_NAKAGAMI_D1_M;
	OPTS_NAKAGAMI(opts).use_dist = DEFAULT_NAKAGAMI_USE_DIST;

	/* log distance setup */
	OPTS_LOG_DISTANCE(opts).exponent = DEFAULT_LOG_DISTANCE_EXPONENT;
	OPTS_LOG_DISTANCE(opts).reference_dist = DEFAULT_LOG_DISTANCE_REFERENCE_DISTANCE;

	/* thre log distance setup */
	OPTS_THREE_LOG(opts).distance_1 = DEFAULT_THREE_LOG_DISTANCE_REFERENCE_DISTANCE_1;
	OPTS_THREE_LOG(opts).distance_2 = DEFAULT_THREE_LOG_DISTANCE_REFERENCE_DISTANCE_2;
	OPTS_THREE_LOG(opts).distance_3 = DEFAULT_THREE_LOG_DISTANCE_REFERENCE_DISTANCE_3;

	OPTS_THREE_LOG(opts).exponent_1 = DEFAULT_THREE_LOG_DISTANCE_EXPONENT_1;
	OPTS_THREE_LOG(opts).exponent_2 = DEFAULT_THREE_LOG_DISTANCE_EXPONENT_2;
	OPTS_THREE_LOG(opts).exponent_3 = DEFAULT_THREE_LOG_DISTANCE_EXPONENT_3;

	OPTS_THREE_LOG(opts).reference_distance = DEFAULT_THREE_LOG_DISTANCE_REFERENCE_DISTANCE;

	opts->start =  DEFAULT_START;
	opts->end =  DEFAULT_END;
	opts->delta = DEFAULT_DELTA;
}

static int
find_algorithm(const char *arg, struct c_env *c_env)
{
	const char *name;
	int i = 0;

	name = algorithms[i].name;
	for (; algorithms[i].name != NULL; name = algorithms[i++].name) {
		if (!(strcasecmp(arg, algorithms[i].name))) {
			c_env->func = algorithms[i].func;
			c_env->algo = algorithms[i].algo;
			return 1;
		}
	}

	return 0;
}


static int
find_modulation(const char *arg, struct c_env *c_env)
{
	const char *name;
	int i = 0;

	name = modulations[i].name;
	for (; modulations[i].name != NULL; name = modulations[i++].name) {
		if (!(strcasecmp(arg, modulations[i].name))) {
			c_env->modulation_ber_func = modulations[i].func;
			c_env->modulation          = modulations[i].modulation;
			return 1;
		}
	}
	return 0;
}

static struct opts*
parse_opts(int ac, char **av, struct c_env *c_env)
{
	int c, ret;
	struct opts *opts;

	opts = malloc(sizeof(*opts));
	if (!opts)
		die(EXIT_FAILURE, "Out of memory");
	memset(opts, 0, sizeof(*opts));

	setup_defaults(opts);

	while (1) {
		int option_index = 0;
		static struct option long_options[] = {

			/* basic simulation setup */
			{"algorithm",       1, 0, 'a'},
			{"start",           1, 0, 's'},
			{"end",             1, 0, 'e'},
			{"delta",           1, 0, 'd'},

			/* standard values */
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

			/* log distance values */
			{"logdistanceexponent", 1, 0, 'P'},
			{"logdistancereferencedistance", 1, 0, 'O'},

			/* three log distance values */
			{"threelogexponent1", 1, 0, 'Q'},
			{"threelogexponent2", 1, 0, 'W'},
			{"threelogexponent3", 1, 0, 'E'},
			{"threelogdistance1", 1, 0, 'R'},
			{"threelogdistance2", 1, 0, 'T'},
			{"threelogdistance3", 1, 0, 'Y'},
			{"threelogreferencedistance", 1, 0, 'U'},

			/* nakagami values */
			{"m0", 1, 0, 'A'},
			{"m1", 1, 0, 'S'},
			{"m2", 1, 0, 'D'},
			{"d0m", 1, 0, 'F'},
			{"d1m", 1, 0, 'G'},
			{"usedistance", 1, 0, 'H'},

			{"modulation", 1, 0, 'm'},

			{0, 0, 0, 0}
		};

		c = getopt_long(ac, av, "a:s:e:d:f:l:p:r:t:u:i:g:h:j:P:O:Q:W:E:R:T:Y:U:A:S:D:F:G:H:m:",
				long_options, &option_index);
		if (c == -1)
			break;

		switch (c) {
		case 'a':
			ret = find_algorithm(optarg, c_env);
			if (!ret) {
				fprintf(stderr, "Algorithm \"%s\" not supported!\n",
						optarg);
				print_usage();
				exit(EXIT_FAILURE);
			}
			break;

		/* test case values */
		case 's':
			opts->start = strtod(optarg, NULL);
			break;
		case 'e':
			opts->end = strtod(optarg, NULL);
			break;
		case 'd':
			opts->delta = strtod(optarg, NULL);
			break;

		/* standard system values */
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

		/* shadowing values */
		case 'g':
			OPTS_SHADOWING(opts).shadowing_pathloss_exp = strtod(optarg, NULL);
			break;
		case 'h':
			OPTS_SHADOWING(opts).shadowing_std_db = strtod(optarg, NULL);
			break;
		case 'j':
			OPTS_SHADOWING(opts).shadowing_distance = strtod(optarg, NULL);
			break;

		/* log distance model values */
		case 'P':
			OPTS_LOG_DISTANCE(opts).exponent = strtod(optarg, NULL);
			break;
		case 'O':
			OPTS_LOG_DISTANCE(opts).reference_dist = strtod(optarg, NULL);
			break;

		/* three log distance model */
		case 'Q':
			OPTS_THREE_LOG(opts).exponent_1 = strtod(optarg, NULL);
			break;
		case 'W':
			OPTS_THREE_LOG(opts).exponent_2 = strtod(optarg, NULL);
			break;
		case 'E':
			OPTS_THREE_LOG(opts).exponent_3 = strtod(optarg, NULL);
			break;

		case 'R':
			OPTS_THREE_LOG(opts).distance_1 = strtod(optarg, NULL);
			break;
		case 'T':
			OPTS_THREE_LOG(opts).distance_2 = strtod(optarg, NULL);
			break;
		case 'Y':
			OPTS_THREE_LOG(opts).distance_3 = strtod(optarg, NULL);
			break;

		case 'U':
			OPTS_THREE_LOG(opts).reference_distance = strtod(optarg, NULL);
			break;

		/* nakagami values */
		case 'A':
			OPTS_NAKAGAMI(opts).m0 = strtod(optarg, NULL);
			break;
		case 'S':
			OPTS_NAKAGAMI(opts).m1 = strtod(optarg, NULL);
			break;
		case 'D':
			OPTS_NAKAGAMI(opts).m2 = strtod(optarg, NULL);
			break;
		case 'F':
			OPTS_NAKAGAMI(opts).d0_m = strtod(optarg, NULL);
			break;
		case 'G':
			OPTS_NAKAGAMI(opts).d1_m = strtod(optarg, NULL);
			break;
		case 'H':
			if (!strcasecmp(optarg, "yes")) {
				OPTS_NAKAGAMI(opts).use_dist = 1;
			} else if (!strcasecmp(optarg, "no")){
				OPTS_NAKAGAMI(opts).use_dist = 0;
			} else {
				die(EXIT_FAILURE, "Only yes or no allowed for nakagami \"usedistance\"");
			}
			break;

		/* modulation and BER specific code */
		case 'm':
			ret = find_modulation(optarg, c_env);
			if (!ret) {
				fprintf(stderr, "Modulation \"%s\" not supported!\n",
						optarg);
				print_usage();
				exit(EXIT_FAILURE);
			}
			break;

		case '?':
			break;

		default:
			printf("?? getopt returned character code 0%o ??\n", c);
		}
	}

	if (c_env->algo == 0) {
		fprintf(stderr, "No algorithn given\n");
		print_usage();
		exit(EXIT_FAILURE);
	}

	if (c_env->modulation == 0) {
		/* no modulation given - working in SNR threshold mode */
	}

	if (opts->start < 0.0)
		die(EXIT_FAILURE, "No valid distance given (must > 0m)");

	if (opts->delta < 0.0)
		die(EXIT_FAILURE, "No valid delta given (must > 0)");

	return opts;
}

/* returns the Bit Error Rate for a given SNR */
static double
ber_qam4(const struct opts *opts, struct c_env *c_env, const double snr)
{
	(void) opts;
	(void) c_env;
	(void) snr;

	return 0.0;
}


static double
calc_friis(const struct opts *opts, struct c_env *c_env, const double node_distance)
{
	double dbm;
	double wave_length;

	(void)c_env; /* not required here */

	wave_length = calc_wave_length(opts->frequency);

	double rx_power = friis(opts->tx_power,
							opts->tx_antenna_gain,
							opts->rx_antenna_gain,
							wave_length,
							opts->system_loss,
							node_distance);

	dbm = watt_to_dbm(rx_power);

	return dbm;
}


static double
calc_two_ray_ground(const struct opts *opts, struct c_env *c_env, const double node_distance)
{
	double dbm, rx_power;
	double wave_length;

	(void) c_env;

	wave_length = calc_wave_length(opts->frequency);

	double x_border = calc_crossover_distance(opts->tx_antenna_height,
			                                  opts->rx_antenna_height,
											  wave_length);


	if (node_distance < x_border) {
		/* friis */
		rx_power = friis(opts->tx_power,
							opts->tx_antenna_gain,
							opts->rx_antenna_gain,
							wave_length,
							opts->system_loss,
							node_distance);
	} else {
		/* two ray ground */
		rx_power = two_ray_ground(opts->tx_power,
							opts->tx_antenna_gain,
							opts->rx_antenna_gain,
							opts->tx_antenna_height,
							opts->rx_antenna_height,
							opts->system_loss,
							node_distance);
	}

	dbm = watt_to_dbm(rx_power);

	return dbm;
}

static double
calc_two_ray_ground_vanilla(const struct opts *opts, struct c_env *c_env, const double node_distance)
{
	double dbm, rx_power;

	(void)c_env; /* not required for two ray ground */

	rx_power = two_ray_ground(opts->tx_power,
						opts->tx_antenna_gain,
						opts->rx_antenna_gain,
						opts->tx_antenna_height,
						opts->rx_antenna_height,
						opts->system_loss,
						node_distance);

	dbm = watt_to_dbm(rx_power);

	return dbm;
}


static double
calc_shadowing(const struct opts *opts, struct c_env *c_env, const double node_distance)
{
	double dbm, avg_db, pr, power_loss_db;
	double wave_length = calc_wave_length(opts->frequency);

	double rx_power = friis(opts->tx_power,
							opts->tx_antenna_gain,
							opts->rx_antenna_gain,
							wave_length,
							opts->system_loss,
							node_distance);

	if (node_distance > OPTS_SHADOWING(opts).shadowing_distance) {
		avg_db = -10.0 * OPTS_SHADOWING(opts).shadowing_pathloss_exp *
			log10(node_distance / OPTS_SHADOWING(opts).shadowing_distance);
	} else {
		avg_db = 0.0;
	}

	power_loss_db = avg_db + gsl_ran_gaussian(c_env->rng, OPTS_SHADOWING(opts).shadowing_std_db);

	pr = rx_power * pow(10.0, (power_loss_db / 10.0));

	dbm = watt_to_dbm(pr);

	return dbm;
}

static double
calc_log_distance(const struct opts *opts, struct c_env *c_env, const double node_distance)
{
	double rx_power_dbm;
	double path_loss_db, wave_length;
	double rxc, reference_lost;

	(void) c_env;

	wave_length = calc_wave_length(opts->frequency);

	rx_power_dbm = friis(opts->tx_power,
					opts->tx_antenna_gain,
					opts->rx_antenna_gain,
					wave_length,
					opts->system_loss,
					node_distance);

	if (node_distance < OPTS_LOG_DISTANCE(opts).reference_dist) {
		return rx_power_dbm;
	}

	/* calculate reference lost */
	reference_lost = friis(opts->tx_power,
					opts->tx_antenna_gain,
					opts->rx_antenna_gain,
					wave_length,
					opts->system_loss,
					OPTS_LOG_DISTANCE(opts).reference_dist);

	path_loss_db =
		10 * OPTS_LOG_DISTANCE(opts).exponent *
			log10(node_distance / OPTS_LOG_DISTANCE(opts).reference_dist);


	rxc = - reference_lost - path_loss_db;

	return rx_power_dbm + rxc;
}

static double
calc_three_log_distance(const struct opts *opts, struct c_env *c_env, const double node_distance)
{
	double rx_power_dbm;
	double path_loss_db, wave_length;
	double rxc, reference_lost;

	(void) c_env;

	wave_length = calc_wave_length(opts->frequency);

	rx_power_dbm = friis(opts->tx_power,
					opts->tx_antenna_gain,
					opts->rx_antenna_gain,
					wave_length,
					opts->system_loss,
					node_distance);

	if (node_distance < OPTS_THREE_LOG(opts).distance_1) {
		return rx_power_dbm;
	}

	/* calculate reference lost */
	reference_lost = friis(opts->tx_power,
					opts->tx_antenna_gain,
					opts->rx_antenna_gain,
					wave_length,
					opts->system_loss,
					OPTS_THREE_LOG(opts).reference_distance);

	if (node_distance < OPTS_THREE_LOG(opts).distance_2) {

		path_loss_db =
			10 * OPTS_THREE_LOG(opts).exponent_1 *
				log10(node_distance / OPTS_THREE_LOG(opts).distance_1);

	} else if (node_distance < OPTS_THREE_LOG(opts).distance_3) {

		path_loss_db =
			10 * OPTS_THREE_LOG(opts).exponent_1 *
				log10(OPTS_THREE_LOG(opts).distance_2 / OPTS_THREE_LOG(opts).distance_1) +
			10 * OPTS_THREE_LOG(opts).exponent_2 *
				log10(node_distance /  OPTS_THREE_LOG(opts).distance_2);

	} else { /* broader away then distance_3 */
		path_loss_db =
			10 * OPTS_THREE_LOG(opts).exponent_1 *
				log10(OPTS_THREE_LOG(opts).distance_2 / OPTS_THREE_LOG(opts).distance_1) +
			10 * OPTS_THREE_LOG(opts).exponent_2 *
				log10(OPTS_THREE_LOG(opts).distance_3 /  OPTS_THREE_LOG(opts).distance_2) +
			10 * OPTS_THREE_LOG(opts).exponent_3 *
				log10(node_distance /  OPTS_THREE_LOG(opts).distance_3);
	}

	rxc = - reference_lost - path_loss_db;

	return rx_power_dbm + rxc;
}


static double
calc_nakagami(const struct opts *opts, struct c_env *c_env, const double node_distance)
{
	double rx_power, pr_0, pr_1;

	pr_0 = calc_three_log_distance(opts, c_env, node_distance);

	pr_1 = dbm_to_watt(pr_0);

	if (OPTS_NAKAGAMI(opts).use_dist == 0) {
		return watt_to_dbm(pr_1);
	} else {
		double m;

		if (node_distance <= OPTS_NAKAGAMI(opts).d0_m)
			m = OPTS_NAKAGAMI(opts).m0;
		else if (node_distance <= OPTS_NAKAGAMI(opts).d1_m)
			m = OPTS_NAKAGAMI(opts).m1;
		else
			m = OPTS_NAKAGAMI(opts).m2;

		rx_power = gsl_ran_gamma(c_env->rng, m, pr_1 / m);
	}

	return watt_to_dbm(rx_power);
}


static struct c_env*
init_env(void)
{
	struct c_env *ret;
	int fd;
	unsigned long rtn = 0;
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
		rtn = (long) time(NULL) ^ getpid();
	} else {
		if ( (read(fd, &rtn, sizeof(rtn))) < (int)sizeof(rtn)) {
			rtn = (long) time(NULL) ^ getpid();
		}
	}
	gsl_rng_set(ret->rng, rtn);

	return ret;
}


static void
finit_env(struct c_env *c_env)
{
	gsl_rng_free(c_env->rng);
	free(c_env);
}


int
main(int ac, char **av)
{
	struct opts *opts;
	struct c_env *c_env;
	double rx_power_dbm;
	double node_distance;

	c_env = init_env();
	opts = parse_opts(ac, av, c_env);

	for (node_distance = opts->start;
		 node_distance <= opts->end;
		 node_distance += opts->delta) {

		/* func point to the particular function */
		rx_power_dbm = c_env->func(opts, c_env, node_distance);

		fprintf(stdout, "%lf %lf\n", node_distance, rx_power_dbm);
	}

	finit_env(c_env);
	free(opts);

	return EXIT_SUCCESS;
}

/* vim:set ts=4 sw=4 tw=78 noet: */
