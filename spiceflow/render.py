import numpy as np
import spiceypy as spice
import pyrender
import trimesh
from PIL import Image, ImageOps
from .star import star_texture


def render_solar_object(solar_object, wireframe):
    if "model" in solar_object:
        model = solar_object["model"]
        if model["type"] == "texture-body":
            sphere = trimesh.creation.uv_sphere(
                radius=solar_object["radius"][0]
            )
            vs = trimesh.creation.uv_sphere().vertices
            uv = []
            for v in vs:
                r, lon, lat = spice.reclat(np.array(v))
                u = (lon + np.pi) / (2.0 * np.pi)
                v = (np.pi / 2.0 - lat) / np.pi
                uv.append([u, v])
            uv = np.array(uv)
            im = Image.open(model["file"])
            sphere.visual = trimesh.visual.TextureVisuals(
                uv=uv, image=ImageOps.flip(im),
            )
            mesh = pyrender.Mesh.from_trimesh(
                mesh=sphere, smooth=True, wireframe=wireframe
            )
        elif model["type"] == "model":
            polygon = trimesh.load(model["file"])
            mesh = pyrender.Mesh.from_trimesh(mesh=polygon)
        pose = np.identity(4)
        pose[0:3, 0:3] = solar_object["rotation"]
        pose[0:3, 3] = solar_object["position"]
        return mesh, pose


def render_star(star, width, height):
    pos = star["image_pos"]
    return star_texture(
        pos[0], pos[1], star["visual_magnitude"], star["color"], width, height
    )


def render(obsinfo, bg_color=[0.0, 0.0, 0.0], wireframe=False):
    scene = pyrender.Scene(bg_color=bg_color)
    camera = pyrender.PerspectiveCamera(
        yfov=np.radians(obsinfo.fov.fovy), aspectRatio=obsinfo.fov.aspect
    )

    # rot_z(180) . rot_y(180)
    camera_pose = np.array(
        [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]],
        dtype=np.float64,
    )
    scene.add(camera, pose=camera_pose)

    star_image = np.zeros(
        shape=(obsinfo.height, obsinfo.width, 4), dtype=np.uint8
    )

    for star in obsinfo.stars:
        star_image += render_star(star, obsinfo.width, obsinfo.height)

    for solar_object in obsinfo.solar_objects:
        mesh, pose = render_solar_object(solar_object, wireframe)
        scene.add(mesh, pose=pose)

    # light = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=3.8e27)
    light = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=3.8e17)
    pose = np.identity(4)
    pose[0:3, 3] = -obsinfo.pos
    scene.add(light, pose=pose)

    # Render the scene
    r = pyrender.OffscreenRenderer(obsinfo.width, obsinfo.height)
    flags = (
        pyrender.RenderFlags.RGBA | pyrender.RenderFlags.SHADOWS_DIRECTIONAL
    )
    color, _ = r.render(scene, flags=flags)
    color += star_image
    return color
