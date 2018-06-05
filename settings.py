import os
INDEX_DIR                   = '/fluidsound/index/'
INDEX_NAME                  = 'fs_index'
INDEXING_SERVER_INDEX_NAME = INDEX_NAME # used in Freesound for offline indexing, not used here
SIMILARITY_MINIMUM_POINTS   = 20
PCA_DIMENSIONS              = 100
PCA_DESCRIPTORS             = [
                                 "*lowlevel*mean",
                                 "*lowlevel*dmean",
                                 "*lowlevel*dmean2",
                                 "*lowlevel*var",
                                 "*lowlevel*dvar",
                                 "*lowlevel*dvar2"
                              ]
PORT                         = 8008
N_RESULTS                    = 10
BAD_REQUEST_CODE             = 400
SERVER_ERROR_CODE            = 500
NOT_FOUND_CODE               = 404
FILENAME_INDEX               = "/fluidsound/filenames.pickle"
PRESETS                      = ['lowlevel', 'pca']
PRESET_DIR                   = '/fluidsound/presets/'
DEFAULT_PRESET               = 'pca'
