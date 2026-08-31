import io
import os

import resvg_py
from env import GridWorldEnv
from PIL import Image
from renderer import RichGridWorldRenderer


def create_gif(
    images: list[str],
    output_dir: str,
    env: GridWorldEnv,
    renderer: RichGridWorldRenderer,
):
    """
    Transform the input images and exports the gif into the output folder
    Args:
        images: all the images that are needed to gen the gif
        output_dir: the output dir to be exported on
        env: the current env config
    Returns:
        None
    """

    config = [
        f"width={env.width}",
        f"height={env.height}",
        f"has_key={env.has_key}",
        f"door_open={env.door_open}",
    ]

    title = f"{' '.join(config)}.gif"

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, title)

    frames = []
    total = len(images)
    for i, image in enumerate(images, start=1):
        renderer.print_message(f"Renderizando frame {i}/{total}...")
        with open(image, "r", encoding="utf-8") as f:
            svg_string = f.read()

        png_bytes = bytes(resvg_py.svg_to_bytes(svg_string=svg_string))
        frames.append(Image.open(io.BytesIO(png_bytes)).convert("RGBA"))

    max_width = max(frame.width for frame in frames)
    max_height = max(frame.height for frame in frames)

    padded_frames = []
    for frame in frames:
        canvas = Image.new("RGBA", (max_width, max_height), (0, 0, 0, 255))
        x = (max_width - frame.width) // 2
        y = (max_height - frame.height) // 2
        canvas.paste(frame, (x, y), frame)
        padded_frames.append(canvas)

    first_frame = padded_frames[0]
    first_frame.save(
        output_path,
        format="GIF",
        append_images=padded_frames[1:],
        save_all=True,
        duration=1000,
        loop=0,
    )
    renderer.print_message(f"GIF successfully saved at: {output_path}")
