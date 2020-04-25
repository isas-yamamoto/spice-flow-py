from .obs_info import ObsInfo


def simulate(inst, et, abcorr, obsrvr, width, height, mag_limit):
    return ObsInfo(inst, et, abcorr, obsrvr, width, height, mag_limit)
