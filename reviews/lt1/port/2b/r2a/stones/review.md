# R2a stones: the strict review

23 October 2026. A fresh reviewer read `review-packet.md`, then the sheets, `counts.json` and the references, and only then `report.md`. This ran on Opus 5.5, not Fable, because Fable can't use the credits now. The reviewer re-rendered nothing and edited nothing. `tools/check.py` does not exist, so nothing here passed it. Saved as the reviewer wrote it. How the report answers it is in `report.md`, The review.

## 1. Verdict

**Pass with conditions.** R2a asked three things. It answered two of them honestly, and the answer is mostly no.

- **SN7 in context: no.** The wall stone reads as orange tiles in a near-black grid beside 10. Its chamfer is 1 px at 8 m, and SN4 asks for 2. The step and the coping have rims and dark lines.
- **The switch: no.** L1 does not pass for L0 on the wall stone in any light.

A rung that found that out is done.

**The third question was not answered.** The A/B over the patch ran on a patch that is nearly empty. So the "done" line "the A/B gives evidence for SN7's number" is not met. Close that question as "not answered, carried to R2b", not as support for proposal 1.

Nothing needs re-running to close R2a, once the report is corrected (section 3). Two things must run before anything is decided on them: the step's switch at 8 m, and patch-off at the wall stone's sun stand.

## 2. Proposals

**Proposal 1, SN7 at about 2 L* with the patches as built: reject as written.**
- The patch is nearly empty. In raking light, `patch-split-0.png` shows one lamina line.
- Its normals are almost flat: mean length 0.9989 as built, 0.9991 minor off, 0.9986 facets ×2. Its fade at 1 m moves at most 0.66 L* p99.
- The report says it too: the patch draws under 1 L*, and the spread comes from light across the planes.
- Minor off did reach the shader: slice 0's normal hash changes (9b4c50bdabd0 against ea0f8971cb13). The ledges just carry almost nothing.
- The test lights could not show the patch even if it held something. The sun is 8° up and the shade is soft, so neither rakes horizontal laminae.
- Patch off was run only at the foot, in drizzle and blue hour, never at the wall stone's sun stand.

So 1.68 under 2 L* only shows that an empty patch is quiet. Change it to: SN7's number stays open. R2b gives the stone its block-scale form and gives the patch content, then the A/B runs again in a raking light.

I am wrong if a raking frame, or patch off at the sun stand, shows the as-built patch reading as split stone at 1 m.

**Proposal 2, one switch rule (switch ≤ motion + 2 L*), with L1's outline at the fill line.** Take the rule, with changes:
- Motion p99 ranges from 0.2 to 5.0 L* across lights and distances. Where motion is 5, a 7 L* pop passes.
- The baseline depends on a dolly speed chosen without reason (about 23 mm a frame). Write a fixed speed into the rule.
- Add an absolute cap, a floor on the baseline, and an area or connected-region term, so a pop shaped like a joint counts for more than scattered pixels.

Its parts:
- **Coping at 12 m:** take.
- **Step at 8 m:** only after a re-run. In sun, in grey, it gets worse with distance (+3.4, +3.5, +4.2), so no distance passes yet.
- **Wall stone, L1's outline at the fill line (option 1):** change it. L1 at 8 m has joints of 4.2–9.5 mm, inside SN5's 4–12 mm. L0's visible joint is 13.7–24.4 mm, outside it. Copying L0 into L1 copies the wrong level and locks in the brick-and-mortar look. First settle SN4 against SN5: a 10–12 mm chamfer and a 4–12 mm joint can't both show. Then, by default, fix L0. I am wrong if 10 shows joints of 15–25 mm at that scale.
- **Visible joint error replacing the fixed 9 mm:** take.
- **No switch at 18 m:** take.

**Proposal 3, the soil to the pack after a diagnosis: take it, but after the form work.**
- Face to joint is 3.8× in sun and about 18× in shade, against 2.7× in the albedo. The extra dark is in the ambient term (occlusion or sky light). It is a lighting fault before it is a pack value.
- Calibrate the pack value on 10, where the joints are dark but don't read as a grid.
- A clamp on the joint's floor is not the fix. Lighter joints between rectangles read as tiles in grey grout.

I am wrong if fixing the joint's darkness alone makes the wall read as stone.

## 3. Claims to attack

The report is mostly honest, and its table carries every light. But it flatters in places and misses others.

- **"Passed" in its In short flatters.**
  - The grey joints pass by construction: grey fill on grey faces.
  - The thin share passes pooled (7.3%) only because the wall stones are at 0%, and R2b's new form will take that away.
  - The off-state was proven in one frame, in one light. The wet branch was never tried.
- **The packet gives the wall stone's switch in sun only.** It fails at every light and stand measured:

  | Light, stand | Grey (8 / 10 / 12 m) | Material (8 / 10 / 12 m) |
  | --- | --- | --- |
  | Drizzle | +5.8 / +4.6 / +4.0 | +10.2 / +9.8 / +7.9 |
  | Low sun, foot | | +6.4 / +5.9 / +4.0 |
  | Blue hour | | +3.3 / +3.2 / +2.0 |

- **"The step's joint within 2.2 L* in grey" is false for its bottom joint.** `joint_off` flags it against a 6 L* tolerance:
  - in grey, −25.7 in sun, +18.4 in drizzle and +12.2 in blue hour;
  - in material, −45.7 in sun.

  That joint is 34.5 mm wide.
- **The step's right rim is missing from the rim faults:** +32.8 in sun at 1 m, +14.1 in drizzle, +9.6 in blue hour.
- **The line counter misses wide dark lines at 1 m.** The wall stone's left rim is −36.3 L* at 1 m in sun, and the counter reads "dark 0". Every "no dark line" at 1 m is unproven.
- **Thin triangles are gated only face-on.** From eye height at 12 m:
  - the step's L1 is 18–28% thin (median altitude 2.3–3.1 px), and its L0 33–39%;
  - the coping's L1 is 20% thin.

  The coping's L0 has 4 of 11 triangles thin even at 1 m (slivers of 0.26–0.33 mm), and its top is a fan from one corner. The "median 10 px" was read as area, which is lenient.
- **Proposal 1 builds a number on a patch the report itself says draws nothing.**

## 4. What no one said

- **The wall stones have no value spread.** Neighbours sit within 0.3–1.2 L*: material medians 61.2–62.4 at 12 m in sun, grey 72.2–72.5. SN7 asks for 1–6 L*. Nobody measured it, and it fails the low end. One flat face, four straight edges, even courses and one value: that is why the wall reads as brick. In 05 and 10, stones differ from their neighbours by far more.
- **The grey rig is not neutral.** The grey frames have an orange sun, saturated blue on up-facing faces and a near-black foot. "Judge form in grey light" was not met.
- **The coping's smudge and its dark edge lines may share one cause.** The smudge is at the left end, and the lines are 16–64 px. L1 casts the shadows, has no chamfers and stands about 9 mm proud, so L0's chamfers may sit in L1's shadow. The step's dark nosing line survived both L1-noline and L0-flat, which doesn't rule this out. A cheap test: one frame with L0 casting its own shadow.
- **One overview frame is useless.** The foot-oblique view is framed through roofs and shows nothing.
- **There is one bright speck on the block at 12 m in sun,** probably a mote in the scene. Motes spoil the speck counts.

## 5. Must-fix before R2b, ranked

1. **Wall stone form.** Give it a block-scale outline (more than four edges, irregular courses) and a neighbour value spread of 1–6 L*, measured.
2. **SN4 against SN5.** Settle them in writing. Then fix L0's joint and L1's outline to match, and re-run the dolly in all three lights at both stands.
3. **The measuring tools.**
   - Make the line counter catch wide dark lines at 1 m.
   - Make the report treat `joint_off` as a fail.
   - Gate the thin share per kind and at eye height.
   - Use a neutral grey rig and a fixed dolly speed.
4. **The step.** Fix L1's nosing facets, the right rim and the bottom joint.
5. **The coping.** Remove the slivers and the corner fan. Diagnose the smudge, including the L1-shadow test.
6. **The soil.** Diagnose the ambient term, then move the value to the pack, calibrated on 10.
7. **The proofs still missing.**
   - The off-state in all three lights and on the wet branch.
   - Patch off at the wall stone's sun stand, in a raking light.
