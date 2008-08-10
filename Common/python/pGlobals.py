
CLOCK_FREQUENCY	 	  = 20000000.0
CLOCK_TIC		  = 1.0/CLOCK_FREQUENCY
CLOCK_TIC_MILLISECONDS    = CLOCK_TIC*1000.0
CLOCK_ROLLOVER		  = 2**25
NUM_TOWERS                = 16
NUM_TKR_LAYERS_PER_TOWER  = 36
NUM_GTRC_PER_LAYER        = 2
NUM_GTFE_PER_LAYER        = 24
NUM_TKR_LAYERS            = NUM_TKR_LAYERS_PER_TOWER*NUM_TOWERS
NUM_TKR_GTRC              = NUM_TKR_LAYERS*NUM_GTRC_PER_LAYER
NUM_CAL_LAYERS_PER_TOWER  = 8
NUM_CAL_LAYERS            = NUM_CAL_LAYERS_PER_TOWER*NUM_TOWERS
NUM_CAL_COLUMNS_PER_TOWER = 12
NUM_ACD_CABLES            = 12
NUM_ACD_VETOES            = 128

# FASTMON special variables
FASTMON_DIR_VAR_NAME      = 'FAST_MON_DIR'
XML_CONFIG_DIR_VAR_NAME   = 'XML_CONFIG_DIR'

# ROOT related variables.
ROOT_BASKET_SIZE          = 1000000 

#PLUS_INFINITY = float('infinity')
#MINUS_INFINITY = float('-infinity')
PLUS_INFINITY = 1.e24
MINUS_INFINITY = -1.e24
NAN = float('nan')
