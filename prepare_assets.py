from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
source = Image.open(ROOT / "logo.jpg").convert("RGB")

# Remove the large white margins from the full wordmark for a crisp UI header.
white = Image.new("RGB", source.size, "white")
diff = ImageChops.difference(source, white).convert("L")
bbox = diff.point(lambda value: 255 if value > 18 else 0).getbbox()
if not bbox:
    raise RuntimeError("The uploaded ARJSOFT logo appears to be blank.")
left, top, right, bottom = bbox
pad_x = int((right - left) * 0.035)
pad_y = int((bottom - top) * 0.06)
header = source.crop((max(0, left-pad_x), max(0, top-pad_y),
                      min(source.width, right+pad_x),
                      min(source.height, bottom+pad_y)))
header.save(ASSETS / "arjsoft-logo.png", "PNG", optimize=True)

# The top mark is the ARJ monogram. Isolate it from the wordmark and
# center it on a square canvas for Windows, taskbar and shortcut icons.
mark_area = source.crop((0, 0, source.width, int(source.height * 0.50)))
mark_diff = ImageChops.difference(mark_area, Image.new("RGB", mark_area.size, "white")).convert("L")
mark_bbox = mark_diff.point(lambda value: 255 if value > 18 else 0).getbbox()
if not mark_bbox:
    raise RuntimeError("Could not isolate the ARJSOFT monogram from logo.jpg.")
mark = mark_area.crop(mark_bbox)
side = max(mark.size)
padding = int(side * 0.12)
canvas_side = side + padding * 2
canvas = Image.new("RGB", (canvas_side, canvas_side), "white")
mark.thumbnail((side, side), Image.Resampling.LANCZOS)
canvas.paste(mark, ((canvas_side-mark.width)//2, (canvas_side-mark.height)//2))
icon = canvas.resize((256, 256), Image.Resampling.LANCZOS)
icon.save(ASSETS / "arjsoft-icon.ico", format="ICO",
          sizes=[(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)])
print("Prepared high-resolution ARJSOFT logo and Windows icon.")
