import xml.etree.ElementTree as ET


def add_value(element, value, value_format=".6f"):
    str_format = "{:" + value_format + "}"
    element.text = str_format.format(value)


def add_xy_element(parent, xy, value_format=".6f"):
    add_value(ET.SubElement(parent, "x"), xy[0], value_format)
    add_value(ET.SubElement(parent, "y"), xy[1], value_format)


def add_xyz_element(parent, xyz, value_format=".6f"):
    add_value(ET.SubElement(parent, "x"), xyz[0], value_format)
    add_value(ET.SubElement(parent, "y"), xyz[1], value_format)
    add_value(ET.SubElement(parent, "z"), xyz[2], value_format)


def add_model(parent, model):
    if model["type"] == "model":
        # 3D polygon
        tag_model = ET.SubElement(parent, "model")
        tag_src = ET.SubElement(tag_model, "src")
        tag_src.attrib["type"] = "file"
        tag_src.text = model["file"]

        tag_scale = ET.SubElement(tag_model, "scale")
        add_value(tag_scale, model["scale"], "f")

        tag_color = ET.SubElement(tag_model, "color")
        tag_color.text = ",".join(map(str, model["color"]))

        tag_format = ET.SubElement(tag_model, "format")
        tag_format.text = model["format"]
    elif model["type"] in ("texture-body", "texture-ring"):
        tag_texture = ET.SubElement(parent, "texture")
        tag_texture.attrib["component"] = model["type"][8:]
        tag_src = ET.SubElement(tag_texture, "src")
        tag_src.attrib["type"] = "file"
        tag_src.text = model["file"]


def get_view_xml(obsinfo):
    tag_view = ET.Element("view")
    tag_date = ET.SubElement(tag_view, "date")
    tag_date.text = obsinfo.date

    #
    tag_location = ET.SubElement(tag_view, "location")
    add_xyz_element(tag_location, obsinfo.pos)

    #
    tag_boresight = ET.SubElement(tag_view, "boresight")
    add_xyz_element(tag_boresight, obsinfo.fov.boresight)

    #
    tag_bounds = ET.SubElement(tag_view, "bounds")
    for bound in obsinfo.fov.bounds:
        tag_point = ET.SubElement(tag_bounds, "point")
        add_xyz_element(tag_point, bound)

    #
    tag_fov = ET.SubElement(tag_view, "fov")
    add_value(tag_fov, obsinfo.fov_in_degrees)

    #
    tag_pos_angle = ET.SubElement(tag_view, "pos_angle")
    add_value(tag_pos_angle, obsinfo.pos_angle)

    tag_angle_res = ET.SubElement(tag_view, "angle_res")
    add_value(tag_angle_res, obsinfo.angle_res, ".6e")

    #
    tag_shape = ET.SubElement(tag_view, "shape")
    tag_shape.text = obsinfo.fov.shape

    #
    tag_center = ET.SubElement(tag_view, "center")
    tag_ra = ET.SubElement(tag_center, "ra")
    add_value(tag_ra, obsinfo.ra)
    tag_dec = ET.SubElement(tag_center, "dec")
    add_value(tag_dec, obsinfo.dec)

    #
    tag_image_size = ET.SubElement(tag_view, "image_size")
    tag_width = ET.SubElement(tag_image_size, "width")
    tag_width.text = str(obsinfo.width)
    tag_height = ET.SubElement(tag_image_size, "height")
    tag_height.text = str(obsinfo.height)

    return tag_view


def get_solar_xml(solar_object):
    tag_object = ET.Element("object")
    if solar_object["type"] == "PLANET":
        tag_object.attrib["type"] = "solar"
        tag_object.attrib["id"] = "PLANET.{}".format(solar_object["name"])
    else:
        tag_object.attrib["type"] = "solar"
        tag_object.attrib["id"] = "{}".format(solar_object["name"])
    #
    tag_name = ET.SubElement(tag_object, "name")
    tag_name.text = solar_object["name"]
    #
    tag_position = ET.SubElement(tag_object, "position")
    add_xyz_element(tag_position, solar_object["position"])
    #
    tag_magnitude = ET.SubElement(tag_object, "magnitude")
    if solar_object["magnitude"] is not None:
        add_value(tag_magnitude, solar_object["magnitude"], ".2f")
    else:
        add_value(tag_magnitude, 0.0, ".2f")
    #
    tag_distance = ET.SubElement(tag_object, "distance")
    add_value(tag_distance, solar_object["distance"])
    #
    if "model" in solar_object:
        models = solar_object["model"]

        if type(models) == list:
            for model in models:
                add_model(tag_object, model)
        else:
            add_model(tag_object, models)
    #
    tag_image_pos = ET.SubElement(tag_object, "image_pos")
    add_xy_element(tag_image_pos, solar_object["image_pos"], ".0f")
    #
    tag_radius = ET.SubElement(tag_object, "radius")
    add_xyz_element(tag_radius, solar_object["radius"])
    #
    tag_rotation = ET.SubElement(tag_object, "rotation")
    for i in range(3):
        tag_a3 = ET.SubElement(tag_rotation, "A3")
        tag_a3.text = "{:.10f}, {:.10f}, {:.10f}".format(
            *solar_object["rotation"][i]
        )

    return tag_object


def get_star_xml(star):
    tag_object = ET.Element("object")
    tag_object.attrib["type"] = "star"
    tag_object.attrib["id"] = "STAR.HIPPARCOS.{}".format(star["hip_id"])
    #
    tag_name = ET.SubElement(tag_object, "name")
    add_value(tag_name, star["hip_id"], "d")
    #
    tag_position = ET.SubElement(tag_object, "position")
    add_xyz_element(tag_position, star["position"])
    #
    tag_magnitude = ET.SubElement(tag_object, "magnitude")
    add_value(tag_magnitude, star["visual_magnitude"], ".2f")
    #
    tag_distance = ET.SubElement(tag_object, "distance")
    add_value(tag_distance, star["distance"], ".6e")
    #
    tag_image_pos = ET.SubElement(tag_object, "image_pos")
    add_xy_element(tag_image_pos, star["image_pos"], ".0f")
    #
    tag_spectral = ET.SubElement(tag_object, "spectral")
    tag_spectral.text = star["spectral_type"]
    #
    tag_color = ET.SubElement(tag_object, "color")
    tag_color.text = "{},{},{}".format(*star["color"])

    return tag_object
