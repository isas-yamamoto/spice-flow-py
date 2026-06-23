import numpy as np
import spiceypy as spice

from .compat import apply_pyrender_compat

apply_pyrender_compat()
import pyrender
import trimesh
from PIL import Image, ImageOps
from .render_util import bg_color_rgba
from .star import star_texture


def render_solar_object(solar_object, wireframe):
    if "model" not in solar_object:
        return None

    model = solar_object["model"]
    mesh = None
    if model["type"] == "texture-body":
        sphere = trimesh.creation.uv_sphere(radius=solar_object["radius"][0])
        vs = trimesh.creation.uv_sphere().vertices
        uv = []
        for v in vs:
            _r, lon, lat = spice.reclat(np.array(v))
            u = (lon + np.pi) / (2.0 * np.pi)
            v_coord = (np.pi / 2.0 - lat) / np.pi
            uv.append([u, v_coord])
        uv = np.array(uv)
        im = Image.open(model["file"])
        sphere.visual = trimesh.visual.TextureVisuals(
            uv=uv,
            image=ImageOps.flip(im),
        )
        mesh = pyrender.Mesh.from_trimesh(
            mesh=sphere, smooth=True, wireframe=wireframe
        )
    elif model["type"] == "model":
        polygon = trimesh.load(model["file"])
        mesh = pyrender.Mesh.from_trimesh(mesh=polygon)
    else:
        return None

    pose = np.identity(4)
    pose[0:3, 0:3] = solar_object["rotation"]
    pose[0:3, 3] = solar_object["position"]
    return mesh, pose


def render_star(star, width, height):
    pos = star["image_pos"]
    return star_texture(
        pos[0], pos[1], star["visual_magnitude"], star["color"], width, height
    )


def _directional_light_pose(light_direction):
    norm = np.linalg.norm(light_direction)
    if norm > 0:
        light_direction = light_direction / norm
    else:
        light_direction = np.array([0.0, 0.0, -1.0])

    z_axis = -light_direction
    up_vector = np.array([0.0, 1.0, 0.0])
    x_axis = np.cross(up_vector, z_axis)
    x_norm = np.linalg.norm(x_axis)
    if x_norm > 0:
        x_axis = x_axis / x_norm
    else:
        x_axis = np.array([1.0, 0.0, 0.0])
    y_axis = np.cross(z_axis, x_axis)
    light_pose = np.eye(4)
    light_pose[:3, 0] = x_axis
    light_pose[:3, 1] = y_axis
    light_pose[:3, 2] = z_axis
    return light_pose


def render(obsinfo, bg_color=None, wireframe=False, intensity=10.0):
    rgba = bg_color_rgba(bg_color)
    scene = pyrender.Scene(bg_color=list(rgba[:3]))
    camera = pyrender.PerspectiveCamera(
        yfov=np.radians(obsinfo.fov.fovy), aspectRatio=obsinfo.fov.aspect
    )

    # rot_z(180) . rot_y(180)
    camera_pose = np.array(
        [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]],
        dtype=np.float64,
    )
    scene.add(camera, pose=camera_pose)

    star_image = np.zeros(shape=(obsinfo.height, obsinfo.width, 4), dtype=np.uint8)

    for star in obsinfo.stars:
        star_image += render_star(star, obsinfo.width, obsinfo.height)

    for solar_object in obsinfo.solar_objects:
        rendered = render_solar_object(solar_object, wireframe)
        if rendered is None:
            continue
        mesh, pose = rendered
        scene.add(mesh, pose=pose)

    light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=intensity)
    scene.add(light, pose=_directional_light_pose(obsinfo.pos))

    # Render the scene
    r = pyrender.OffscreenRenderer(obsinfo.width, obsinfo.height)
    flags = pyrender.RenderFlags.RGBA | pyrender.RenderFlags.SHADOWS_DIRECTIONAL
    foreground, _ = r.render(scene, flags=flags)

    # background layer: star_image, foreground layer:foreground
    bg_color_int = (np.array(rgba) * 255).astype(int)
    return np.where(
        foreground != bg_color_int,
        foreground,
        np.where(star_image != [0, 0, 0, 0], star_image, bg_color_int),
    )
