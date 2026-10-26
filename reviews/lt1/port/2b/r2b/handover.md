# R2b handover (26 October)

The wall stone is done (`report.md`). Next is the step, beside reference 06, then the coping, by the same loop. After that comes one strict review of all three stones on Fable, from a short packet of the final sheets and the report's lines (Opus if Fable is out, noted as such); then `NOW.md`'s 2b line.

- **Render one still and its sheet** (Blender's Python has numpy; the system Python does not):

  ```
  /Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 tools/r2b_wall.py PANEL.bin
  python3 tools/unity_lock.py run --owner "R2b stones" --purpose ... -- .../Unity -batchmode -quit -projectPath $PWD/unity -executeMethod Overstory.EditorTools.LT1R2b.Still -mesh PANEL.bin -out reviews/lt1/port/2b/r2b/<stone>/roundN -moment 1300-drizzle -dry -normal -0.33,-0.95 -ref docs/references/stone/<ref>.jpg -crop x,y,w,h -logFile LOG
  ```

  - `-dry` gives 1300-drizzle's overcast with dry stone, as reference 10 has it.
  - The stand at 53,-1, facing -0.33,-0.95, looks along the open street.
- **Sets:** `-moment a,b` and `-mesh tag=path,...` take lists, and `-cams "tag:out,along,eye[,aimOut,aimAlong,aimUp];..."` takes a semicolon list. `-looks material` renders the material look alone.
  - `tools/r2b_switch.py OUT` compares the l0 and l1 frames.
  - `tools/r2b_sheet.py OUT LOOK moments cams` makes the contact sheet.
- **The step and coping** need their own part functions and a panel tool like `r2b_wall.py`. `LT1R2b` draws any triangle soup in the R2B2 format.
- **Lessons:**
  - Material colours are sRGB-authored, so the rubble's `_Stone` of 0.54 is about 0.25 linear. Only the lichen is pale.
  - The lichen's look is the shared growth layer's; leave it to its own job.
- **Don't commit:** the Heart scene, `M_Sky.mat` or the other untracked files in the tree. They are other sessions'.
