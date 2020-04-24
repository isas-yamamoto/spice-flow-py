import xml.etree.ElementTree as ET
import spiceypy as spice

from .fov import Fov
from .solar_object import search_solar_objects
from .star import search_stars
from .transform import viewport_frustum
from .util import vec_padist
from .xml_util import get_view_xml, get_solar_xml, get_star_xml


class ObsInfo:
    MAX_ROOMS = 256

    def __init__(self, inst, et, abcorr, obsrvr, width, height, mag_limit):
        # input parameter
        self.inst = inst
        self.et = et
        self.abcorr = abcorr
        self.obsrvr = obsrvr
        self.width = width
        self.height = height

        # parameters equivalent to input parameter
        self.date = spice.et2utc(et, "ISOC", 3)
        self.inst_id = spice.bodn2c(inst)

        # Instrument FOV
        self.fov = Fov(self.inst_id)
        self.fov_in_degrees = self.fov.fovmax * 2.0 * spice.dpr()

        # geometry information
        self.pos, _ = spice.spkpos(obsrvr, et, self.fov.frame, abcorr, "SUN")
        self.obs2refmtx = spice.pxform(self.fov.frame, "J2000", et)
        self.ref2obsmtx = spice.pxform("J2000", self.fov.frame, et)

        # screen information
        pos_angle, angle_res, ra, dec = get_geometry_info(
            self.obs2refmtx, self.fov, width, height
        )

        self.center = self.fov.bounds_rect.center_vec
        self.pos_angle = pos_angle
        self.angle_res = angle_res
        self.ra = ra
        self.dec = dec

        # searched objects
        self.solar_objects = search_solar_objects(self)
        self.stars = search_stars(self, mag_limit)

    def set_obs_table(self, obs_table):
        for solar_object in self.solar_objects:
            if solar_object["name"] in obs_table:
                solar_object["model"] = obs_table[solar_object["name"]]
            elif solar_object["type"] == "PLANET":
                key = "{}.{}".format(
                    solar_object["type"], solar_object["name"]
                )
                solar_object["model"] = obs_table[key]

    def to_xml(self):
        sv_doc = ET.Element("svdoc")
        sv_frame = ET.SubElement(sv_doc, "frame")
        sv_frame.append(get_view_xml(self))
        for solar_object in self.solar_objects:
            sv_frame.append(get_solar_xml(solar_object))
        for star in self.stars:
            sv_frame.append(get_star_xml(star))
        return sv_doc


def get_geometry_info(obs2refmtx, fov, width, height):
    cvec = spice.vhat(fov.bounds_rect.center_vec)
    cvec_ref = spice.mxv(obs2refmtx, cvec)

    # Azimuth in the upward direction of the screen
    mvec = spice.vhat(fov.bounds_rect.top_vec)
    mvec_ref = spice.mxv(obs2refmtx, mvec)
    pa, dist = vec_padist(cvec_ref, mvec_ref)
    pos_angle = pa * spice.dpr()

    # Pixel resolution up to the center of the screen top edge
    vp = viewport_frustum(fov.bounds_rect, width, height, mvec)
    angle_res = dist / (height / 2.0 - vp[1]) * spice.dpr()
    _, ra, dec = spice.recrad(cvec_ref)

    return pos_angle, angle_res, ra * spice.dpr(), dec * spice.dpr()
