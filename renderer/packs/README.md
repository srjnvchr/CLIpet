# Packs

A pack is a folder here (`renderer/packs/<name>/`) holding a custom
scene and/or character made from your own artwork, instead of the
built-in `couch_desk` room or `bot` character. Generate one with:

```bash
python design/import_image.py room.png --as background --name myroom
python design/import_image.py cat.png  --as character --name myroom
```

then run the pet with `PET_SCENE=myroom PET_CHARACTER=myroom` (env
vars, see the main README's "Customizing" section). A pack only needs
whichever file you actually made art for - `PET_CHARACTER=myroom` works
fine even if `myroom/` has no `background.json`, as long as you pair it
with a scene that does (e.g. the built-in `couch_desk`).

## File format

Both files are plain JSON, read by `renderer/image_asset.py` with no
dependencies beyond the standard library - `design/import_image.py`
(which needs PIL) is just a convenient way to produce them from an
image; you can also hand-write or generate one yourself.

**`background.json`**
```jsonc
{
  "width": 72, "height": 64,
  // optional - defaults to a spot near the bottom-left/right quarters
  "spots": { "idle": [18, 51], "work": [54, 51] },
  "pixels": [[r, g, b], /* width*height entries, row-major */ ...]
}
```

**`character.json`**
```jsonc
{
  "width": 16, "height": 16,
  // optional - defaults to bottom-center; the pixel that lines up with
  // wherever the scene places the character
  "anchor": [8, 15],
  // width*height entries, row-major; null = transparent (scene shows through)
  "pixels": [[r, g, b], null, ...]
}
```
