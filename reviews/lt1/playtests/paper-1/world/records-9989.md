# World 9989: the records a player can read

The in-world documents of world 9989 for the paper playtests: the Courier's articles, posters, chatter at the Anchor and death notices, written from the engine's events (`fixtures/engine/understory-world-9989.json`, Understory `af02971`). Written 21 October 2026 for game masters, who hand a player only the record itself: never the italic event lines, a *Truth* or a GM note. Read `engine-rules.md` and `atlas-9989.md` first.

- **Dates.** Re-dated by −37: the engine's 2026 to 2036 is the town's 1989 to January 1999, and every year inside a quoted line is shifted too. The month is the engine's. **The day of the month and the weekday are authored**, because the engine has nothing finer than a month.
- **What is authored.** Bylines, headlines, wording, days, set lists, funeral arrangements and every quote are `authored`. The facts are engine facts with their event ids. Where a record is wrong or partial, a GM note says how, gives the truth, and labels the distortion.
- **Ids.** `C-` the Courier, `P-` posters, `A-` chatter at the Anchor, `D-` death notices. The index at the end lists them by date.
- **The kind of thing.** Every record here is perceived information (`CLAUDE.md`, the five kinds of thing on screen): a person's account or a record, which may be wrong. None of it is the game's verdict.

## 1. How the export shows telling, and who knew what

Checked before writing. The short answer: the export says who *could* have known an event, not who did, and it shows telling only in traces.

- **There is no witness list.** The engine's events carry "who knows it, marked as seen or heard" (`engine-rules.md`, What an event carries), but the export leaves it out (engine request 1, `eventsKnownBy`). The only field about knowing is `vis`: of 2,635 events, 1,271 are private, 1,203 local and 161 public. The `decision` field gives only the kind of decision (`withdrawal`, `anger`, `disclosure`...), with no options or odds.
- **Read `vis` through the witness rules** (`engine-rules.md`, Witnesses). *Public:* the whole town, faintly. *Local:* the people in `who`, their partners and coworkers, and by chance anyone whose work is with people: the Anchor, the clinic, the school and the Courier. *Private:* the people in `who`, and nobody else unless a later event shows it travelled.
- **Telling shows up in four traces, all indirect.**
  1. **A `belief` cause on a later act.** 99 events carry one; only 8 name a teller, worded "had heard from X that ...". Examples: Jonah Scott confides in John Holmes because he "had heard from Neil Lyons that John Holmes got the big order done with hours to spare (1987)" (e-6461); Edward Baker asks Mark Holmes for money having "heard from Steve Baker that Mark Holmes put a note in the hat for Susie Lyons, and not a small one" (e-6894); Ken Scott drags up Colin Berry's coin in the hat, "had heard from Toby Tanner" (e-8886); Gary Newman confides in Eddie Lane on Lynn Newman's word (e-8970). The other 91 beliefs come from the person's own experience ("Hannah Tanner came and put it right (1986)", e-6401).
  2. **A confidence passed on.** Four `tell` events with decision `disclosure`, all private: Harry Myers tells what Maisie confided (e-6431), John Holmes tells Jonah Scott's (e-6462), Terry Sutton tells Kate Holmes's (e-7884), Eddie Lane tells Gary Newman's (e-8971). Three get back to the one who confided, as local `betrayed` events: "It got back to Jonah Scott that John Holmes had been talking" (e-6463), and e-7885, e-8972.
  3. **Being found out.** Nine `caught` events (local) and one `scheme:found` (public: "It came out that John Holmes had been running Ivan Tanner down", e-7594). Being found out is how a private act becomes something the town can know.
  4. **Confiding.** 32 `confide` and 21 `keepsecret` events, private. The content is never given: "what had been kept back", "how bad things had got", "everything, the parts nobody else knew". By the engine's rule a holder confides their latest secret, so a game master may infer it from the confider's private acts, labelled `GM-inferred`.
- **Most `tell` events are not telling.** Of 112, 105 are local "tells": a state let slip or plainly seen, each naming its own witness ("Eddie Lane has stopped coming out; saving, he says", e-6436; "Sarah Lane has been practising every night; the neighbours can hear", e-7922). They make good chatter as they stand.
- **Belief labels use the engine's short form of an act.** Evan Newman's belief "Peter Scott found out lying (1989)" (e-6739) stands for letting Olive Shaw take the blame (e-6446, e-6447). Harry Myers's belief "Gary Myers found out taking from the till (1995)" (e-8450) stands for the trip money (e-7880). Treat these as how a teller would put it, not as a second fact.
- **Bent accounts are almost absent.** The engine bends telling (softened by a teller who likes the person, hardened by one who doesn't, the wrong person named 15% of the time by an insincere teller), but the export keeps no bent version. The one trace is "though Mark Holmes made light of it" inside a belief (e-7106). So **every wrong or partial record below is GM-simulated or authored**, built on telling's shape (`engine-rules.md`, rule 3: it starts with someone who saw or was wronged, goes to one close hearer, may pass once more, and bends with liking), and labelled in its GM note.

**How game masters use this.**
1. Before a character says something, or the Courier prints it, check the event's `vis` and whether that person could have seen it or been told under the rules above. If not, they don't know it.
2. Let a record be wrong only in ways the record makes natural: a private cause the speaker can't know and fills in, the teller's liking or dislike, second-hand wording, the paper's own ties. Never with a new fact about what happened.
3. Never let a record reveal, or hint at, a private act nobody found out. Among them: Harry Myers's trip money (e-6385, e-6913), Susie Lyons's expenses at the Courier itself (e-6445), Eddie Lane's till (e-6609), Eric Lane's catch (e-7425, e-7726), the timber account at the sawmill (Sid Tanner e-8392, Sarah Lane e-8488, Leo Holmes e-8675), and Gary Newman's till (e-8795; see A-32).
4. When a player's misreading comes from one of these records, score its cause as "a wrong record" (`method.md`, Scoring). Log every record you hand over by id and date.

## 2. The Courier

The town's weekly, out on Thursdays (authored). Its people in the record: Ken Scott, at the Courier since 1976 and its lead (the editor); Toby Tanner, reporter since 1987; Susie Lyons until January 1991 (e-6838); Colin Berry from October 1991 (e-7050) until he walked out in October 1998 (e-8905); Vera Holmes from November 1998 (e-8940). Ken Scott's ties shape the paper: his partner Sylvia Waller (married July 1992, e-7305) and her parents Toby and Grace Waller; his brother Jonah Scott and their mother Audrey Scott; Thea Waller, Sylvia's sister, married to Colin Berry.

### C-01 · Thursday 15 June 1989
**Harbour day goes off well enough**
*By Toby Tanner*

Saturday's harbour day went off well enough, by most accounts, and the town was out on the quay for it. Audrey Scott, 67, took the day on in May when nobody else would and saw it through from the first table to the last. The Courier thanks her and everyone who lent a hand.

*Events: e-6432 (took it on, local), e-6444 (went off well enough, public).*

### C-02 · Thursday 22 June 1989
**A new clerk for the council office**
*By Susie Lyons*

Lily Lyons, 32, has moved to the town to take up a post at the council office, which has been a clerk short for eleven months. She starts this week. Chief officer Terry Sutton said the office had been waiting a long time for her.

**Born.** To Alex and Lisa Myers, a son, Colin: a brother for Tom.

*Events: e-6442, e-6458.*

### C-03 · Thursday 14 December 1989 · wrong
**Festival on the quay "the best night in years"**
*By Susie Lyons*

Terry Sutton has done it again. Saturday's festival on the quay was, in the words of more than one person walking home, the best night the town has had in years. Mr Sutton, 62, of the council office, first spoke of it in May, and by September he had his helpers: Larry Baker, Toby Waller, Jonah Scott, Kate Holmes, Molly Scott and Mona Sayer. "Every one of them pulled their weight," he told the Courier, "and it showed." Kate Holmes was up all night before it finishing her part. It is Mr Sutton's eleventh festival on the quay since 1963, and he says it will not be his last.

*Events: e-6437, e-6438, e-6450, e-6451, e-6492, e-6510, e-6511, e-6580, e-6583; venture v-20.*

> **GM note.** Wrong: not every helper pulled their weight. Molly Scott "missed the deadline on her part of the summer festival and the whole place paid for it" (e-6581, local), and the engine's reason for the night counts "1 of the helpers let it down" (cause of e-6583). Jonah Scott nearly missed his doing it twice (e-6579). Right: the best night in years (e-6583, public), Kate Holmes's all-nighter (e-6580, local), the helpers (v-20), eleven festivals (v-3, v-7, v-9, v-10, v-12, v-15 to v-20). Mechanism: `GM-simulated` softening; the source is the organiser, who would not shame a helper in print, and the quote is `authored`. The engine's "summer festival" falls in December (see P-01).

### C-04 · Thursday 21 December 1989
**Agnes Fielding, 1886 to 1989**
*By Ken Scott*

Agnes Fielding, the oldest person in the town, died last week after a long illness. She was 103. Born here in August 1886, she was the widow of Colin Eden, who died in 1969. She had her two pints at the Anchor most evenings into her hundreds, was there every Friday without fail, walked the shore of an evening, and past a hundred took up a garden, out in it every morning from spring to autumn. She had a second heart attack in November. Few in the town can remember it without her.

*Events: e-6527, e-6557. Her habits and marriage are from her record (p-36).*

### C-05 · Thursday 21 June 1990
**Thirty-four years under the bonnet**
*By Toby Tanner*

Trevor Lane, 63, has retired as head mechanic at the garage after thirty-four years, as he said last September he would. His place goes to Sally Baker, 39, who came to the town in April for a job at the garage, bringing her husband, Terry Baker, and the children. Terry Baker has started at the clinic. Mr Lane says he will not miss the cold mornings.

*Events: e-6508, e-6641, e-6642, e-6689, e-6690. Not printed: Gary Hughes was passed over for the job (e-6692, local) and walked out in July (e-6720).*

### C-06 · Thursday 28 June 1990
**Harbour day "like clockwork"**
*By Susie Lyons*

Harry Myers of the school took on the harbour day in May, and it ran like clockwork. Mr Myers, 43, had a list for everything, and the quay was cleared by dark. He has offered to keep the lists for whoever does it next year.

*Events: e-6676, e-6701. The offer in the last line is authored colour.*

### C-07 · Thursday 10 January 1991
**Susie Lyons says goodbye; a new band at the Anchor**
*By Ken Scott*

Susie Lyons, 66, has retired after five years at the Courier. Readers will know her name from the harbour days, the festivals and a good many notices. We shall miss her at the desk by the window.

**Driftwood.** Oliver Brook, who skippers for the harbour fleet, and Peter Lane of the Old Bank Café have started a band. They call it Driftwood, and Andy Shaw, 77, has joined them.

*Events: e-6826, e-6828, e-6838.*

### C-08 · Thursday 14 February 1991
**Married**

Thea Waller, 33, who runs the clinic, and Colin Berry, 42, also of the clinic, were married on Saturday.

*Events: e-6885. Not printed: their son Andy was born in November 1989 (e-6555, public).*

### C-09 · Thursday 23 May 1991
**Driftwood's first night**
*By Toby Tanner*

Driftwood played the Anchor for the first time on Friday and did well. Oliver Brook, Peter Lane and Andy Shaw kept the room for two sets. The best received was "Coming Home on a Sunday", the first song Peter Lane has ever written. They will be back.

*Events: e-6934 (the song, local), e-6954 (public).*

### C-10 · Thursday 17 October 1991
**Best night in years, again**
*By Colin Berry*

Terry Sutton's twelfth festival on the quay was, by common consent, the best night the town has had in years: two in a row. His helpers were Larry Baker, Toby Waller, Jonah Scott, Kate Holmes and, for the first time, Sam Brook, who sat up all night to finish his part. One stall was not ready on time, and nobody minded by nine o'clock.

*Events: e-6830, e-6831, e-6832, e-6861, e-6875, e-6910, e-7060 to e-7065; venture v-21. The stall that was late is Kate Holmes's part (e-7063, local); the paper names nobody. Right.*

### C-11 · Thursday 28 November 1991 · wrong
**Changes at the garage**
*By Colin Berry*

Gary Newman, 32, who came to the town in July with his wife Lynn for a job at the garage, is the new head mechanic. He takes over from Sally Baker, who has moved to the clinic after eighteen months at the garage. Mrs Baker said she wanted a fresh start, and she leaves the garage on the best of terms with her successor. Lynn Newman has worked at the garage since August.

*Events: e-6986, e-7006, e-7048, e-7073.*

> **GM note.** Wrong: "on the best of terms". Sally Baker let Gary Newman take the blame for a mistake at work (e-7011, private), was found out (e-7012, local), and Gary took her aside and said exactly what he thought (e-7029, private; he "can't stand Sally Baker"). She walked out of the garage (e-7032, local) and started at the clinic (e-7073). Gary Newman also froze at his first staff meeting (e-7049, local). Right: "a fresh start" is how a startover would be told. Mechanism: `GM-simulated`; the paper had the public moves and Sally's own account, and the writer added a gloss. Colin Berry had walked out of the clinic in July himself (e-6989).

### C-12 · Thursday 13 February 1992
**Married**

Olive Shaw, 61, of the Anchor, and Ben Reed, 51, of the Night Shift, were married on Saturday. They have been seeing each other for two years.

*Events: e-6628, e-7178.*

### C-13 · Thursday 9 April 1992 · wrong
**A new owner at the Old Bank Café**
*By Toby Tanner*

Lisa Myers, 40, is the new owner of the Old Bank Café. She takes over from Peter Lane, 34, who said last March he would step down after thirteen years. Sean Hale has joined the staff from the Anchor. Eddie Lane, who worked alongside Mrs Myers, has moved on to the garage this month: a change, we understand, he had been wanting for some time.

*Events: e-6908, e-7137, e-7138, e-7144, e-7198.*

> **GM note.** Wrong: the change Eddie Lane wanted was the café. He and Lisa Myers had both been after the owner's job since 1989 (e-6522, e-6546, e-6547), both first in and last out to show it (e-6788, e-6860). He was passed over (e-7142, local: "Lisa Myers had the stronger record"), what he had wanted for two years was gone (e-7141), he took Lisa aside and said exactly what he thought (e-7143), and walked out (e-7184, private). Mechanism: `GM-simulated`; the paper fills in a cause for a public move. The engine words Peter Lane's stepping down as "retired after 13 years" at 34 (e-7137); the article says "step down". Not printed: Lisa froze at her first staff meeting (e-7140, local).

### C-14 · Thursday 21 May 1992 · wrong and partial
**Terry Sutton retires; newcomer to lead the council office**
*By Ken Scott*

After thirty-four years at the council office, Terry Sutton, 65, has retired as chief officer. The town knows him best for the festival on the quay, which he has put on twelve times. His place goes to Lily Lyons, 35, who came to the town only three years ago. It is no secret that many in the office had hoped the post would go to someone who knows the town better, and that Sylvia Waller was widely expected to be put forward. We wish Mrs Lyons well.

*Events: e-6935, e-7224, e-7225.*

> **GM note.** Wrong: Sylvia Waller herself told Lily Lyons the job should go to Lily (e-7038, local, September 1991), after Lily picked holes in her work in front of everyone (e-7023); Jonah Scott conceded twice (e-6961, e-6962, e-7215). The office's rivalry was real (e-6957, e-6959, e-6960) but its end was not as printed. Partial: Terry Sutton was found out taking from the expense claims in 1990 (e-6702, e-6703, local), and Lily dragged it up in front of everyone at the office (e-6869); the paper prints none of it. Mechanism: `GM-simulated`, hardened by the editor's ties: Sylvia is his partner (married two months later, e-7305), and he kept Lily Lyons at arm's length (e-6464).

### C-15 · Thursday 18 June 1992
**Eddie Lane's list**
*By Colin Berry*

The harbour day ran like clockwork on Saturday, and Eddie Lane, 45, who took it on in May when nobody else would, had a list for everything. Asked how he found the time in his first months at the garage, he said he had found it.

*Events: e-7237, e-7268. The answer is authored.*

### C-16 · Thursday 23 July 1992
**Editor weds**
*By Toby Tanner*

Ken Scott, 34, who has been at the Courier since 1976, married Sylvia Waller, 29, of the council office, on Saturday. Her father Toby Waller gave a speech that will not be printed here.

*Events: e-7305. The speech is authored colour.*

### C-17 · Thursday 21 January 1993 · wrong
**Correction**

In last week's Courier the clinic's winter opening hours were printed wrongly. The correct hours are on the clinic door. The error was made by our reporter Toby Tanner, who apologises to readers and to the clinic. — *Ed.*

*Events: e-7401.*

> **GM note.** Wrong: the mistake was Colin Berry's; he "let Toby Tanner take the blame for a mistake at work" (e-7401, private). Toby sulked about it for months (e-7423). By September he knew, and dragged it up in front of everyone at the Courier (e-7558, local; its belief cause shows he knew). In October Colin did it again (e-7579) and that time was found out (e-7580, local). The nature of the error (the clinic's hours) and the notice are `authored`; who carried the blame is engine. Not printed, ever: Colin Berry was found out taking from the Courier's expenses in May and June 1992 (e-7233, e-7272) and again in March 1997 (e-8490).

### C-18 · Thursday 11 February 1993
**Council says yes to the festival**
*By Colin Berry*

The council has said yes to Terry Sutton's festival on the quay, his thirteenth and his first since retiring from the council office. Six people are behind it: Toby Waller, Larry Baker, Kate Holmes, Sam Brook, Sylvia Waller and Jonah Scott.

*Events: e-7301, e-7302, e-7311, e-7312, e-7331, e-7348, e-7349, e-7435; venture v-22.*

### C-19 · Thursday 15 April 1993
**Home, and new faces**
*By Toby Tanner*

Alice Tanner, 23, daughter of Ivan Tanner and Molly Scott, is home after five years away, and has started at the sawmill. Agnes Tanner, 25, has come to the town to work at the Anchor, which has been a pair of hands short for sixteen months. (The two are no relation.) At the harbour fleet Steve Baker, 66, has retired after six years.

*Events: e-7440, e-7453, e-7454, e-7455.*

### C-20 · Thursday 27 May 1993 · partial
**A washout**
*By Ken Scott*

Not every year can be the best night in years. Saturday's festival on the quay was a washout, and nobody will pretend otherwise. Some of the work was not ready on the night, and what was ready could not carry it. Terry Sutton has given the town thirteen festivals, and his helpers give their own time. The Courier will not go looking for someone to blame.

*Events: e-7499.*

> **GM note.** Partial: the public record names two helpers: "The summer festival that Terry Sutton put on was a washout; Toby Waller and Sylvia Waller never did their part" (e-7499). The editor is Sylvia's husband and Toby's son-in-law (e-7305). The local detail is milder than the public line: Sylvia missed her deadline (e-7497) and Toby's part went out rough and someone else had to fix it (e-7493). Larry Baker and Kate Holmes delivered (e-7494, e-7495), Sam Brook sat up all night (e-7496) and Jonah Scott did his twice (e-7498). Mechanism: `GM-simulated` omission, bent by the editor's ties. A player who reads only the Courier will not learn whose parts failed; anyone who was on the quay will.

### C-21 · Thursday 27 May 1993 · wrong
**Comings and goings**
*By Colin Berry*

Maisie Myers, 42, has left the town for a post in the city. She has worked at the school, the sawmill and, since last summer, the council office. Harry Myers stays on at the school. Jonah Scott, 44, has left the council office for a start at the harbour fleet. Mr Scott, who has always loved the water, says the change has been a long time coming.

*Events: e-6411, e-7285, e-7478, e-7483.*

> **GM note.** Wrong on Jonah Scott: his move follows Lily Lyons's promotion (the cause of e-7478 is e-7225). He had wanted the chief officer's job (e-6434, e-6955, e-7128), conceded it (e-6961, e-6962, e-7215), and started looking for work elsewhere once she had it (e-7468, local). "Always loved the water" is the paper's own. Mechanism: `GM-simulated`, softened: Jonah is the editor's brother (both sons of Tom Vaughan and Audrey Scott). Partial on Maisie Myers: the public line ends "Harry Myers stayed, and that was the end of the marriage" (e-7483); the paper keeps to the job, as a paper of its time would (`authored`).

### C-22 · Thursday 26 August 1993
**Barman buys a boat**
*By Toby Tanner*

Peter Scott, 41, of the Anchor, has bought a boat of his own after four years of wanting one. Regulars will know he took on extra work last year and has been putting every spare penny aside. Where he will find the time to sail it is another matter.

*Events: e-7189, e-7327 (local), e-7542, e-7544.*

### C-23 · Thursday 16 June 1994
**Peter Lane leaves; Driftwood plays on**
*By Colin Berry*

Peter Lane, 36, has left the town for a job in the city. He has talked about the city for as long as anyone can remember, and now he has gone. Driftwood, the band he started with Oliver Brook, will go on without him, with Andy Shaw and Edward Baker.

**Harbour day.** Harry Myers ran it again, and again it ran like clockwork.

*Events: e-7729, e-7747, e-7748, e-7749, e-7750 (local), e-7761.*

### C-24 · Thursday 21 July 1994
**Father and son at the open night**
*By Toby Tanner*

The Anchor's open night on Friday had Sam Brook, 68, and his son Oliver Brook, 37, on the same bill, and both did well. Two of the Night Shift, Ben Reed and John Holmes, were in the room and could not be drawn up. Perhaps next time.

*Events: e-7769, e-7770, e-7771, e-7772, e-7773, e-7777.*

### C-25 · Thursday 15 September 1994
**Married**

Jonah Scott, 45, of the harbour fleet, and Vera Holmes, 46, daughter of Kate Holmes and Mark Holmes, were married on Saturday.

*Events: e-6968, e-7818.*

### C-26 · Thursday 16 March 1995 · wrong
**Driftwood called back twice**
*By Toby Tanner*

Friday's crowd at the Anchor would not let Driftwood go. "The Fence at the Clinic", Andy Shaw's song from last winter, had them called back twice, and the room sang the last chorus without them. Of the newer songs, "Christmas Fence" owes its best lines to Edward Baker, and it shows. Oliver Brook, Andy Shaw and Edward Baker have played together since Peter Lane left, and they have never sounded better.

*Events: e-7659, e-7868, e-7869, e-7952.*

> **GM note.** Wrong: "Christmas Fence" is Andy Shaw's (e-7868). "Edward Baker let people think the best of Andy Shaw's song was Edward Baker's" (e-7869, local), Andy found out (e-7870), sulked for months (e-7878) and stayed in the band for the others' sake (e-7890). Right: "The Fence at the Clinic" is Andy's and got them called back twice (e-7659, e-7952). "Never sounded better" is the writer's; that October "Andy Shaw and Edward Baker never once looked at each other" (e-8105, public). Mechanism: `GM-simulated`; Edward's claim reached the paper as he told it (the claimant is the source). The set list is `authored`.

### C-27 · Thursday 21 September 1995
**Open night; a goodbye**
*By Colin Berry*

At Friday's open night Matt Sayer, 71, played and did well. Andy Shaw, 82, of Driftwood, took a spot and had a night to forget. Gary Hughes, 43, has left for a job in the city. He came to the town in 1990 for the garage, worked at the sawmill, and bought a house of his own only last October.

*Events: e-6603, e-6941, e-7830, e-8066, e-8067 to e-8070. The engine says Andy Shaw "fell apart" (e-8068).*

### C-28 · Thursday 18 April 1996
**Twenty-nine years at the clinic**
*By Toby Tanner*

Toby Waller, 67, has retired after twenty-nine years at the clinic. Jonah Scott has taken a job in the city, and Vera Holmes has gone with him.

*Events: e-8231, e-8247.*

### C-29 · Thursday 18 July 1996
**Harbour day: where were the tables?**
*By Colin Berry*

Saturday's harbour day was chaos. Nobody knew where the tables were, and Steve Baker, 69, who took the day on in June when nobody else would, was nowhere to be found. Those who came made the best of it.

*Events: e-8279, e-8300, e-8327.*

### C-30 · Thursday 19 September 1996 · wrong
**Driftwood calls it a day**
*By Colin Berry*

Driftwood have split up after six years. People still talk about the night the room went quiet. It has been a hard year for Andy Shaw, who has been unwell since the spring, and the band has not been the same without him at his best. Sarah Lane, who joined in January, and Oliver Brook are expected to go on playing.

*Events: e-8185, e-8229 (local), e-8374.*

> **GM note.** Wrong: the split is not about Andy Shaw's illness. The record's reasons: "they want it to sound like different things", and "Oliver Brook, Edward Baker and Sarah Lane each need to be the one who matters" (e-8374). Andy's cancer (e-8229, April) is true but not a cause. "Expected to go on playing" is the writer's guess; Oliver Brook's next band is Pirate Radio, in 1998 (e-8752). Not printed: in August Oliver played Andy's song "Behind the Clinic" as if it were his own (e-8356, local). Mechanism: `GM-simulated`; the writer joins two true facts with a cause the record lacks.

### C-31 · Thursday 26 September 1996
**Ellie Eden's festival**
*By Toby Tanner*

The council said yes this month, and on Saturday the festival on the quay was the best night the town has had in years. It was put on by Ellie Eden, 42, who came to the town last year and works at the Old Bank Café, with Sean Hale, Tess Lane and Neil Lyons. Terry Sutton was seen enjoying himself on the other side of a stall.

*Events: e-7875, e-8190, e-8203, e-8258, e-8357, e-8375, e-8376, e-8380; venture v-23. Two helpers let it down (e-8377, e-8378, local); the paper does not say otherwise. Terry Sutton at a stall is authored colour.*

### C-32 · Thursday 20 February 1997
**Mary Tanner**
*By Toby Tanner*

Mary Tanner died suddenly last week of a heart attack. She was 77. She married Mark Holmes in 1981. She had her own boat from 1962 and was out on it every weekend, kept a shed she was seldom out of, played cards at the Anchor on Tuesdays for twenty-five years, and did an impression of Mona Sayer that the whole of the Anchor used to ask for. She had two strokes, in 1989 and 1991, and came through both.

*Events: e-6556, e-6970, e-7168 (local), e-8459. Her habits and marriage are from her record (p-22).*

### C-33 · Thursday 26 March 1998
**A washout, a new band and a retirement**
*By Colin Berry*

Saturday's festival on the quay, Ellie Eden's second, was a washout; Molly Scott never did her part. The council had said yes in December. On a better note, Neil Lyons, Oliver Brook and Sean Hale have started a band and call it Pirate Radio. And Olive Shaw, 67, has retired after ten years behind the bar at the Anchor.

*Events: e-8552, e-8682, e-8736, e-8752, e-8758; venture v-24. Right: the public line names Molly Scott (e-8758).*

### C-34 · Thursday 25 June 1998
**The room went quiet**
*By Toby Tanner*

At Friday's open night John Holmes, 52, of the Night Shift, played on his own, and the room went quiet. Oliver Brook did well after him. Pirate Radio have a new member: Andy Shaw, 84, last seen with Driftwood.

*Events: e-8807 to e-8810, e-8830. Not printed: Alice Tanner and Sarah Lane were both passed over for the place and went at Andy in front of everyone at the Anchor (e-8831 to e-8834, local). See A-28.*

### C-35 · Thursday 22 October 1998 · wrong
**Andy Shaw, 1913 to 1998**
*By Toby Tanner*

Andy Shaw died last week after a long illness. He was 85. Born in the town in 1913, he married Stella Shaw in 1957 and lost her in 1978. For twenty-six years he swam in the harbour every morning, whatever the weather, until illness kept him from the water. He sang with the choir on Thursdays for twenty-two years. In 1971 he tried to open a café in the old bank, and the council said no. In his late seventies he joined Driftwood and wrote some of the best songs this town has heard: "March Light", "The Fence at the Clinic", "No Ferry Tonight". In September he played the Anchor with Pirate Radio. Pirate Radio will go on without him.

*Events: e-6593, e-6828, e-7022, e-7659, e-8157, e-8229, e-8892, e-8899, e-8928; venture v-8.*

> **GM note.** Wrong: Andy Shaw stopped swimming in January 1990, and "it just lapsed" (e-6593, private). His cancer was diagnosed in April 1996 (e-8229), more than six years later. Right: the swimming began in 1964 and ran twenty-six years; the rest is true. Mechanism: `GM-simulated`; the writer joins two true facts with the cause a reader expects (`docs/ideas/stories-in-the-world.md`, Andy Shaw, "Where they mislead"). Not printed: "Christmas Fence" (see C-26), the row with Edward Baker (e-7870), the money friends gave him (e-7613, e-8093, e-8493, e-8677, private), and that Karen Holmes made peace with him in July, "27 years after the café" (e-8858, local).

### C-36 · Thursday 19 November 1998 · partial
**Changes at the Courier**
*By Ken Scott*

Colin Berry has left the Courier after seven years. We thank him for his work and wish him well. Vera Holmes, 50, joins us this month. She and Jonah Scott came home in October after three years in the city.

*Events: e-8905, e-8939, e-8940.*

> **GM note.** Partial: Colin Berry walked out (e-8905, local) after Ken Scott dragged up in front of everyone at the Courier what Colin did last year (e-8886): Ken "had heard from Toby Tanner that Colin Berry put in the smallest coin he could find when the hat went round for Molly Scott" (e-8743). Behind it: Colin was found out taking from the expenses three times (e-7233, e-7272, e-8490) and letting Toby Tanner take the blame (e-7580). Also unsaid: Vera Holmes is the editor's sister-in-law. Mechanism: `authored` omission by the editor.

## 3. Posters

Posters are records with a maker, a date and a claim, and a credit on one can be wrong. Days and small print are `authored`; the months are the engine's.

**On the festival months.** The engine calls every festival on the quay a "summer festival", but its nights fall when the venture ends: December 1989, October 1991, May 1993, September 1996 and March 1998. The posters carry the engine's month. If a concept needs a summer night, re-dating it is `GM-simulated` and logged once.

### P-01 · for Saturday 9 December 1989
> **SUMMER FESTIVAL ON THE QUAY**
> Saturday 9 December · from four o'clock
> Put on by Terry Sutton, with Larry Baker, Toby Waller, Jonah Scott, Kate Holmes, Molly Scott and Mona Sayer
> Stalls · music · something hot to drink
> *Wrap up warm. Everyone welcome.*

*Events: e-6437, e-6438, e-6450, e-6451, e-6492, e-6510, e-6511, e-6583; v-20.*

### P-02 · for Friday 19 October 1990
> **THE NIGHT SHIFT**
> at the Anchor · Friday 19 October · eight o'clock
> John Holmes · Kate Holmes · Ben Reed · Sam Brook
> "Your Father's Boat" · and new: "After Christmas", "Walking Out (the Clinic)", "A Shore for Four in the Morning"

*Events: e-6406, e-6506, e-6598, e-6750, e-6787 ("Your Father's Boat" got them called back twice). The engine does not say who wrote "Your Father's Boat": it was written before 1989. The poster credits nobody.*

### P-03 · for Friday 17 May 1991
> **DRIFTWOOD**
> first night · the Anchor · Friday 17 May
> Oliver Brook · Peter Lane · Andy Shaw
> with "Coming Home on a Sunday"

*Events: e-6826, e-6828, e-6934, e-6954.*

### P-04 · for Saturday 12 October 1991
> **SUMMER FESTIVAL ON THE QUAY**
> Saturday 12 October
> Terry Sutton · Larry Baker · Toby Waller · Jonah Scott · Kate Holmes · Sam Brook
> *Last time was the best night in years. Come and see if we can do it again.*

*Events: e-6830, e-6831, e-6832, e-6861, e-6875, e-6910, e-7065; v-21.*

### P-05 · for Saturday 13 June 1992
> **HARBOUR DAY**
> Saturday 13 June · on the quay from ten
> Organised by Eddie Lane
> *Stallholders: tell Eddie by Thursday where you want your table.*

*Events: e-7237, e-7268 (it ran like clockwork).*

### P-06 · for Saturday 22 May 1993
> **SUMMER FESTIVAL ON THE QUAY**
> Saturday 22 May · approved by the council
> Terry Sutton, with Toby Waller, Larry Baker, Kate Holmes, Sam Brook, Sylvia Waller and Jonah Scott

*Events: e-7301, e-7302, e-7311, e-7312, e-7331, e-7348, e-7349, e-7435, e-7499 (the washout); v-22. A poster that survives the night names the two whose parts failed alongside everyone else.*

### P-07 · for Friday 15 July 1994
> **OPEN NIGHT AT THE ANCHOR**
> Friday 15 July
> *Anyone can play. Put your name down at the bar.*

*Events: e-7769 to e-7777. Who keeps the list is authored; Evan Newman is the one people ask about the open night (e-7161, e-8283, e-8871).*

### P-08 · for Friday 10 March 1995 · wrong credit
> **DRIFTWOOD**
> at the Anchor · Friday 10 March
> Oliver Brook · Andy Shaw · Edward Baker
> "The Fence at the Clinic" (Shaw) · "Christmas Fence" (Shaw / Baker) · "March Winter" (Shaw) · "Saturday Fence" (Shaw)

*Events: e-7433, e-7659, e-7786, e-7868, e-7869, e-7952.*

> **GM note.** Wrong credit: "Christmas Fence" is Andy Shaw's alone (e-7868). The shared credit follows Edward Baker's claim (e-7869, local), which Andy found out about (e-7870). Mechanism: `GM-simulated`; whoever made the poster took the claim as told. "Saturday Fence" is also one Edward "would not play the way it was written" (e-7434).

### P-09 · for Friday 15 March 1996
> **DRIFTWOOD**
> with Sarah Lane · the Anchor · Friday 15 March
> Oliver Brook · Andy Shaw · Edward Baker · Sarah Lane
> "No Ferry Tonight" · "The Fence at the Clinic"

*Events: e-8157, e-8158, e-8185, e-8219. Sarah Lane joined in January (e-8185). Edward Baker "would not play Andy Shaw's song the way it was written" when Andy brought "No Ferry Tonight" (e-8158).*

### P-10 · for Saturday 13 July 1996
> **HARBOUR DAY**
> Saturday 13 July · on the quay
> Organised by Steve Baker
> *Tables and stalls: see Steve.*

*Events: e-8300, e-8327 ("nobody knew where the tables were, and Steve Baker was nowhere to be found"). The small print is authored, and a player who has it after the day holds a small irony.*

### P-11 · for Saturday 14 September 1996
> **SUMMER FESTIVAL ON THE QUAY**
> Saturday 14 September · approved by the council
> Put on by Ellie Eden, with Sean Hale, Tess Lane and Neil Lyons

*Events: e-8203, e-8258, e-8357, e-8375, e-8376, e-8380; v-23.*

### P-12 · for Saturday 21 March 1998
> **SUMMER FESTIVAL ON THE QUAY**
> Saturday 21 March · approved by the council
> Ellie Eden, with Lisa Myers, Sean Hale, Neil Lyons, Molly Scott and Harry Myers

*Events: e-8552, e-8610, e-8626, e-8627, e-8648, e-8660, e-8682, e-8758 (the washout); v-24.*

### P-13 · for Friday 18 September 1998
> **PIRATE RADIO**
> first night at the Anchor · Friday 18 September
> Neil Lyons · Oliver Brook · Sean Hale · Andy Shaw
> with "Letting Go on a Monday"

*Events: e-8752, e-8830, e-8891, e-8892 (did well). Andy Shaw died the next month (e-8899); a poster still on the wall in November names a dead man.*

## 4. Chatter at the Anchor

What is said at the bar, with who says it and the truth behind it. Hand a player only the quoted line; the *Truth* is for game masters and may look ahead of the line's date. Every speaker is alive, in town and at the Anchor at the date: a regular by habit (Friday, Tuesday cards, two pints most evenings) or one of the staff. Bar staff are the likeliest to have heard local news, since the Anchor is one of the places where local news arrives by chance. The words are `authored`; *right*, *partial* or *wrong* is judged against the engine.

**A-01 · July 1989 · Evan Newman, behind the bar.** "Olive carried the can for that last month, and it was Peter's mistake all along. Came out in the end."
*Truth:* right. Peter Scott let Olive Shaw take the blame for a mistake at work (e-6446, private) and was found out the same month (e-6447, local); all three work at the Anchor. A year later Evan dragged it up in front of everyone (e-6739).

**A-02 · August 1989 · Larry Baker, two pints.** "Eddie Lane's stopped coming out. Saving, he says. For what, I'd like to know."
*Truth:* right, from Eddie's own account (e-6436). He had wanted a house of his own since 1983 and bought one in October (e-6520, e-6521).

**A-03 · November 1989 · Mona Sayer, Tuesday cards.** "Molly's stopped coming in Fridays. That's Terry's festival; he's had her running about since September."
*Truth:* wrong. Molly Scott's Fridays "just lapsed" (e-6519). She had signed up for the festival in September (e-6510) but went on to miss her deadline (e-6581). Mona is Terry Sutton's wife (h-12) and a helper herself (e-6511); she reads her husband's festival into an absence that has no cause. Mechanism: `GM-simulated`, a link the speaker supplies.

**A-04 · January 1990 · Evan Newman.** "Hannah hasn't been in of a Friday since Agnes went. Nor has Olive, unless she's working."
*Truth:* right as seen. Both stopped their Fridays after Agnes Fielding's death, "it hit hard" (e-6589, e-6590). The engine marks it private; the bar staff seeing empty seats is `GM-simulated` observation. Hannah was back by February 1991 (e-6871).

**A-05 · February 1990 · Toby Waller, Friday (he swims off the harbour steps himself).** "Andy Shaw's not been down the steps since New Year. Twenty-odd years, every morning. He'll be poorly, I'd say."
*Truth:* the absence is right, the guess wrong. Andy's swimming "just lapsed" in January 1990 (e-6593, private); he was not ill until the cancer of April 1996 (e-8229). Seeing it is `GM-simulated` observation by a fellow swimmer; the guess is the speaker's. This is the trap C-35 falls into eight years later.

**A-06 · February 1990 · Ivan Tanner, Friday.** "The hat went round for Mary Tanner and Terry Sutton never put in a penny. Eric Lane emptied his wallet. Olive put a note in. John Holmes too. Not Terry."
*Truth:* wrong about Terry. He "slipped a folded note into the hat for Mary Tanner when nobody was looking" (e-6618, local). The rest is right (e-6615, e-6616, e-6617). Mechanism: the speaker saw only what was meant to be seen.

**A-07 · June 1990 · Sam Brook, Friday.** "John Holmes has let Greta go from the sawmill. After all those years."
*Truth:* right (e-6688, local). Greta Brook is the mother of Sam's son Oliver. What it led to was private: she started drinking that month (e-6699) and stopped in March 1992 (e-7197, local).

**A-08 · July 1990 · Toby Waller, Friday.** "They're making a lot of a few pounds on Terry's claims. Thirty-odd years he's given that office. They'd hang a man for less up there."
*Truth:* partial, softened. Terry Sutton took from the expense claims and was found out (e-6702, private; e-6703, local). Toby "thinks the world of Terry Sutton" (the bond in e-6450); "a few pounds" and "making a lot of it" are his. Mechanism: `GM-simulated` softening by liking. Toby works at the clinic, where local news can reach him.

**A-09 · September 1990 · Evan Newman.** "Matt Sayer's off the drink. He was in here every night after Olive finished with him. Now it's lemonade."
*Truth:* right. Matt took up two pints at the Anchor most evenings after he and Olive Shaw split (e-6379, public; e-6384) and started drinking more than was good for him (e-6383, private). He stopped in May (e-6687, local). The bar is where the start could be seen.

**A-10 · August 1991 · Mona Sayer, Tuesday cards.** "Lily Lyons picked Sylvia Waller's work to pieces in front of the whole office. Over the chief officer's job, if you ask me."
*Truth:* right (e-7023, local; e-6960). Mona's husband Terry Sutton runs that office, so she hears it as family of a coworker. A month later Sylvia told Lily the job should go to her (e-7038).

**A-11 · February 1992 · Tess Lane, Friday.** "Eddie was first in and last out at that café for a year and a half, and they gave it to Lisa Myers. Peter Lane promised it to her years ago."
*Truth:* partial. Both were first in and last out (e-6788, e-6860; e-6744). Peter Lane told Lisa the job "would be hers to win when it came up" (e-6545, local): an opening, not a promise. Lisa got it on "the stronger record" (e-7142). Tess is Eddie's wife (h-31). Mechanism: `GM-simulated` hardening by a partner.

**A-12 · February 1992 · Olive Shaw, behind the bar.** "Andy went to Karen Holmes again to put it behind them. She won't hear it. Not after the café, she says. That was 1971."
*Truth:* right (e-7165, e-7166). Karen Holmes opposed all six café plans for the old bank, Andy's in 1971 (v-8) and Olive's own in 1960 (v-1).

**A-13 · March 1992 · Oliver Brook, two pints.** "Mum's off the drink. Don't make a thing of it."
*Truth:* right. Greta Brook stopped drinking, "frightened by their own health" (e-7197, local; her cancer came back in October 1991, e-7047). That she started in 1990 was private (e-6699); Oliver had been at her side within the hour when she was ill (e-6608, e-7105).

**A-14 · July 1992 · Olive Shaw.** "The hat went round for John Holmes, for his mother. Toby Waller had left his wallet at home. That's twice he's done that."
*Truth:* right as far as she saw (e-7293; and for Greta Brook in 1990, e-6647). Olive emptied her own wallet (e-7294). She did not see Matt Sayer slip a folded note in when nobody was looking (e-7292).

**A-15 · October 1993 · Ivan Tanner, Tuesday cards.** "It's out now. John Holmes has been running me down to anyone who'd listen. Sixteen years, since they gave me the skipper's job and not him."
*Truth:* right. "It came out that John Holmes had been running Ivan Tanner down" (e-7594, public); the cause is "still sore about the skipper's job (1977)" (e-7593). Ivan confronted him in front of everyone at the harbour fleet the next month (e-7608), and they have refused each other's peace offers since (e-7449, e-7956, e-7990).

**A-16 · November 1993 · Neil Lyons, Friday.** "Toby Tanner's been at Colin over some mix-up at the paper. Six of one, if you ask me. Colin's all right."
*Truth:* partial, softened. Colin Berry let Toby Tanner take the blame for a mistake at work, twice (e-7401, e-7579), and was found out (e-7580, local); Toby had dragged it up in September (e-7558). Neil and Colin are friends (e-7356). Mechanism: `GM-simulated` softening by liking.

**A-17 · January 1995 · Larry Baker, two pints.** "Kate's not speaking to Terry Sutton. She told him something and it got round. Don't ask me what."
*Truth:* right. Kate Holmes confided in Terry (e-7883), he told people (e-7884, private), and it got back to her (e-7885, local). What she confided is not in the export. Larry is Kate's husband (h-10).

**A-18 · January 1995 · Olive Shaw.** "Edward wrote the best of that Christmas song, whatever Andy says. He's earned a bit of credit, Edward."
*Truth:* wrong. "Christmas Fence" is Andy Shaw's (e-7868); Edward let people think the best of it was his (e-7869), and Andy found out (e-7870). Olive has given Edward money each time he asked (e-7107, e-7752, e-8638). Mechanism: `GM-simulated`; the claim, passed on by someone who likes the claimant.

**A-19 · February 1995 · Tess Lane, Friday.** "Our Sarah plays every night once the house has gone quiet. The neighbours can tell you."
*Truth:* right (e-7922; e-7781). Sarah Lane is Tess's daughter. She fell apart at her first open night a year later (e-8249).

**A-20 · March 1995 · Neil Lyons, Friday.** "Called back twice. That's Andy's song, 'The Fence at the Clinic'. Never mind what anybody's saying about the other one."
*Truth:* right (e-7659, e-7952; on the other song, e-7869, e-7870). Neil has not missed a Night Shift night since 1993 (e-7512) and is teaching himself guitar (e-6638).

**A-21 · September 1995 · Mark Holmes, two pints.** "Gary Myers has bought himself a house. Eight months after they caught him at the trip money. Draw your own conclusions."
*Truth:* wrong. Gary Myers was found out taking from the trip money in January (e-7880, local), "a little" (e-7879). The house is "turned fifty; had the money put by" (e-8076), and he had talked about one "the way other people talk about the weather" (e-8034). Mechanism: two true facts joined by the speaker (`docs/ideas/stories-in-the-world.md`, the misleading shape).

**A-22 · August 1996 · Gary Myers, Friday.** "Oliver and Eric went out in that storm. The other three stayed tied up because they were frightened, and that's the truth of it."
*Truth:* partly wrong. Eric Lane and Oliver Brook went out (e-8339, e-8340); Bert Kemp, Oscar Ash and Maisie Baker hung back (e-8341, e-8342, e-8343). Only Oscar "was afraid of getting hurt"; Bert and Maisie "thought it through first" and could afford to wait. Gary, second hand, hardens it; he is himself one who "would not go out on the water when the wind was up" (e-6823). Mechanism: `GM-simulated`.

**A-23 · August 1996 · Oliver Brook, two pints.** "Bert had the sense to wait. He'd thought it through, and he could afford to. I couldn't, so I went."
*Truth:* right on Bert (e-8341). His own reason is his account; the record says he "is not one to hang back" and "did not stop to think", "though money has never meant much to him" (e-8340). Set A-22 beside it: two accounts of one night.

**A-24 · January 1997 · Tara Myers, Friday.** "Harry Myers brought up our Gary's business again, in front of the whole school. Two years ago, that was."
*Truth:* right (e-8450, local; e-7880). Tara is Gary Myers's mother. Gary dragged something back up about Harry in May (e-8527).
> **GM note.** Harry Myers himself took from the trip money in 1989 and 1991 (e-6385, e-6913, private, never found out). No record, line or hint may point at it.

**A-25 · March 1997 · Evan Newman.** "The hat for Mark Holmes. Greta put in more than anyone. Una Waller found the smallest coin in her purse again. She does it every time."
*Truth:* right (e-8495, e-8496). "Every time" stands so far on her coin for Greta Brook in 1990 (e-6648); she does it again for Ivan Tanner in 1998 (e-8747), and in the run she never puts in more.

**A-26 · July 1997 · Larry Baker, two pints.** "Edward emptied his wallet into the hat for Andy. After all that business with the song. And Colin Berry put in the smallest coin he could find."
*Truth:* right (e-8565, e-8566; also e-8563, e-8564). Larry Baker and Edward Baker are no relation.

**A-27 · March 1998 · Terry Sutton, Friday.** "Two of them put in the smallest coin they could find for Molly: Colin Berry and Eddie Lane. Molly, of all people."
*Truth:* right (e-8742, e-8743). Terry slipped in a folded note himself, unseen (e-8746). Toby Tanner passed Colin's coin on to Ken Scott (the belief in e-8886), which cost Colin his place at the Courier (e-8905).

**A-28 · June 1998 · Agnes Tanner, behind the bar.** "Two of them went at Andy Shaw in here in one week, over a place in a band. Alice Tanner had it out with him, and then Sarah Lane shouted at him in front of everyone. He's eighty-four."
*Truth:* right (e-8831 to e-8834, local). Andy "took it, and kept his head down" both times (e-8841, e-8842).

**A-29 · July 1998 · Mona Sayer, Tuesday cards.** "Karen Holmes went to Andy, if you can believe it, and they've buried the hatchet. Twenty-seven years after the café."
*Truth:* right (e-8857, e-8858). Andy dies three months later (e-8899).

**A-30 · November 1998 · Trevor Lane, Friday.** "First Friday I've come in for years. Andy would have laughed at me."
*Truth:* right. Trevor took up the Anchor on Fridays after Andy Shaw's death, "it hit hard" (e-8943). They had been friends again since 1995 (e-8135), and Andy took him to the choir in 1992 (e-7343).

**A-31 · January 1999 · Eve Vaughan, Tuesday cards.** "Neil's left the sawmill. He wanted a change. Twenty years is long enough in one place."
*Truth:* wrong. Neil Lyons lied to cover a mistake at work (e-8968, private), was found out (e-8969, local) and walked out "to start again somewhere else" (e-8982). Eve is his wife (h-25). Mechanism: `GM-simulated` softening by a partner; the length of his time at the sawmill is not in the export and is hers.

**A-32 · January 1999 · Agnes Tanner, behind the bar.** "Gary Newman's not speaking to Eddie Lane. Something Gary told him in confidence, and Eddie's been telling it round."
*Truth:* partial. Gary confided in Eddie (e-8970), Eddie told people (e-8971, private), it got back to Gary (e-8972, local), and Gary took him aside (e-8981). Agnes and Gary work together at the Anchor.
> **GM note.** What Gary confided is not in the export. By the engine's rule a holder confides their latest secret, which for Gary is taking a little from the Anchor's till (e-8795, May 1998). That inference is `GM-inferred`. If a player asks Agnes what it was, she doesn't know.

## 5. Death notices

The family's notice, as printed in the Courier. The family named is only who the record names. Funeral arrangements are `authored` (the setting has no religion, so no church is named).

### D-01 · Agnes Fielding · Courier, Thursday 21 December 1989

> **FIELDING, Agnes.** Died after a long illness, aged 103. Widow of Colin Eden. Born in the town in August 1886. The funeral is on Friday at eleven; friends are asked to come back to the Anchor afterwards.

*Events: e-6527, e-6557.*

> **GM note.** No relatives in the record: she had no children, and Colin Eden died in 1969. Who placed the notice is `authored`; her friends in the record are Hannah Tanner and Olive Shaw, who visited her weekly in her last illness (e-6531, e-6532, private), while Mark Holmes "found reasons to be busy" (e-6533). **What followed:** Hannah Tanner and Olive Shaw both stopped going to the Anchor on Fridays, "it hit hard" (e-6589, e-6590); Hannah was back by February 1991 (e-6871). In August 1989 Agnes had kept a promise to put in a word for Olive (e-6484). Nothing else in the run is caused by her death. The atlas casts her as the last owner of the corner's house E, which stands empty from 1990 (`atlas-9989.md`, Casting; `authored`).

### D-02 · Ellie Holmes · Courier, Thursday 18 June 1992

> **HOLMES, Ellie.** Died suddenly, of a heart attack, aged 76. Mother of John. The funeral is on Monday at two. Afterwards at the Anchor.

*Events: e-7261.*

> **GM note.** Her only child is John Holmes, foreman at the sawmill; his father, Edward Baker, was never her partner (p-19, p-20). Four months before she died she "had the whole of the church hill laughing about the time the first-aid bag went over the side" (e-7167, local); she had her own boat from 1965 and was out on it every weekend. **What followed:** John Holmes started drinking more than was good for him (e-7264, private) and took to the Anchor every Friday (e-7288). Mary Tanner came to see him weekly, Kate Holmes most days, Sean Hale weekly (e-7265 to e-7267, private). The hat went round for him: Olive Shaw emptied her wallet, Matt Sayer slipped a folded note in unseen, Toby Waller had left his wallet at home (e-7292 to e-7294). He dropped his Tuesday cards in February 1993 (e-7430) and stopped drinking in November 1993 (e-7630). The atlas does not cast her to a house: her only heir, John, wants "a house of his own" from 1995 and never goes after it (e-8180, e-8990), so giving him hers would make a false mystery (`atlas-9989.md`, Casting).

### D-03 · Mary Tanner · Courier, Thursday 13 February 1997

> **TANNER, Mary.** Died suddenly, of a heart attack, aged 77. Wife of Mark Holmes. The funeral is on Wednesday at eleven. No flowers; Mary would have said so herself.

*Events: e-8459.*

> **GM note.** Husband Mark Holmes (married 1981); no children of her own. Mark's daughter Vera Holmes is in the city in February 1997 (e-8247) and is not named in the notice (`authored`). The marriage had been cool for years: "Mary Tanner and Mark Holmes had stopped talking about anything that mattered" (e-7598, local), she had wondered whether to stay (e-7192, private), and in her strokes he "found reasons to be busy" (e-6562, e-6978). The last line of the notice is `authored`. **What followed:** Mark started drinking more than was good for him (e-8461, private). Larry Baker kept turning up at his door (e-8462); Edward Baker and Steve Baker found reasons to be busy (e-8463, e-8464). Toby Waller, her friend since 1989 (e-6477), took up the garden every morning (e-8486). The hat went round for Mark: Greta Brook put in more than anyone, Una Waller the smallest coin, Leo Lyons had left his wallet at home (e-8494 to e-8496).

### D-04 · Andy Shaw · Courier, Thursday 22 October 1998

> **SHAW, Andy.** Died after a long illness, aged 85. Husband of the late Stella. The funeral is on Tuesday at two. Pirate Radio will play at the Anchor afterwards, as he asked.

*Events: e-8899.*

> **GM note.** No children; his wife Stella Shaw died in 1978. Who placed the notice, and "as he asked", are `authored`; if a concept needs to know who placed it, his friends in the record are Ben Reed, Trevor Lane and Oliver Brook, who visited him through his illness (e-8540 to e-8542, e-8881 to e-8883). Ben Reed is the one he told "everything, the parts nobody else knew" (e-8539, e-8880, private), and Ben and Oliver had given him money (e-7613, e-8093, e-8493, e-8677, private). **What followed:** Pirate Radio "had to go on without him" (e-8928). Trevor Lane took up the Anchor on Fridays (e-8943); Ben Reed now reads late every night (e-8944). Ben brought the Night Shift a song that month, "Grey Road", and John Holmes was the first to call it their best (e-8926, e-8927). **Beware:** the engine records "Oliver Brook and Andy Shaw became friends" in the month of his death, after it (e-8901). Treat it as a friendship that was already true, not a new one.

## 6. Index

| Id | Date | Kind | Events |
| --- | --- | --- | --- |
| C-01 | 1989-06 | harbour day | e-6432, e-6444 |
| C-02 | 1989-06 | arrival; birth | e-6442, e-6458 |
| C-03 | 1989-12 | festival · wrong | e-6437, e-6581, e-6583; v-20 |
| C-04 | 1989-12 | obituary | e-6527, e-6557 |
| C-05 | 1990-06 | garage | e-6508, e-6641, e-6642, e-6689, e-6690 |
| C-06 | 1990-06 | harbour day | e-6676, e-6701 |
| C-07 | 1991-01 | Courier; Driftwood | e-6826, e-6828, e-6838 |
| C-08 | 1991-02 | marriage | e-6885 |
| C-09 | 1991-05 | Driftwood | e-6934, e-6954 |
| C-10 | 1991-10 | festival | e-6830, e-7063, e-7064, e-7065; v-21 |
| C-11 | 1991-11 | garage · wrong | e-7011, e-7012, e-7029, e-7032, e-7048, e-7073 |
| C-12 | 1992-02 | marriage | e-6628, e-7178 |
| C-13 | 1992-04 | Old Bank Café · wrong | e-7137, e-7138, e-7141 to e-7144, e-7184, e-7198 |
| C-14 | 1992-05 | council · wrong, partial | e-6703, e-7023, e-7038, e-7224, e-7225 |
| C-15 | 1992-06 | harbour day | e-7237, e-7268 |
| C-16 | 1992-07 | marriage | e-7305 |
| C-17 | 1993-01 | correction · wrong | e-7401, e-7558, e-7579, e-7580 |
| C-18 | 1993-02 | council; festival | e-7301, e-7435; v-22 |
| C-19 | 1993-04 | arrivals | e-7440, e-7453, e-7454, e-7455 |
| C-20 | 1993-05 | festival · partial | e-7493, e-7497, e-7499 |
| C-21 | 1993-05 | departures · wrong | e-7225, e-7468, e-7478, e-7483 |
| C-22 | 1993-08 | purchase | e-7189, e-7327, e-7542, e-7544 |
| C-23 | 1994-06 | departure; harbour day | e-7747, e-7749, e-7761 |
| C-24 | 1994-07 | open night | e-7769 to e-7777 |
| C-25 | 1994-09 | marriage | e-7818 |
| C-26 | 1995-03 | Driftwood · wrong | e-7659, e-7868, e-7869, e-7870, e-7952 |
| C-27 | 1995-09 | open night; departure | e-8066, e-8068, e-8070 |
| C-28 | 1996-04 | retirement; departure | e-8231, e-8247 |
| C-29 | 1996-07 | harbour day | e-8300, e-8327 |
| C-30 | 1996-09 | Driftwood · wrong | e-8229, e-8356, e-8374 |
| C-31 | 1996-09 | festival | e-8376, e-8380; v-23 |
| C-32 | 1997-02 | obituary | e-8459 |
| C-33 | 1998-03 | festival; band; retirement | e-8736, e-8752, e-8758; v-24 |
| C-34 | 1998-06 | open night; band | e-8808, e-8810, e-8830 |
| C-35 | 1998-10 | obituary · wrong | e-6593, e-8229, e-8899 |
| C-36 | 1998-11 | Courier · partial | e-8490, e-8886, e-8905, e-8939, e-8940 |
| P-01 | 1989-12 | festival poster | e-6437, e-6583; v-20 |
| P-02 | 1990-10 | the Night Shift | e-6598, e-6750, e-6787 |
| P-03 | 1991-05 | Driftwood | e-6826, e-6828, e-6954 |
| P-04 | 1991-10 | festival poster | e-6830, e-7065; v-21 |
| P-05 | 1992-06 | harbour day | e-7237, e-7268 |
| P-06 | 1993-05 | festival poster | e-7301, e-7435, e-7499; v-22 |
| P-07 | 1994-07 | open night | e-7769 to e-7777 |
| P-08 | 1995-03 | Driftwood · wrong credit | e-7868, e-7869, e-7952 |
| P-09 | 1996-03 | Driftwood | e-8185, e-8219 |
| P-10 | 1996-07 | harbour day | e-8300, e-8327 |
| P-11 | 1996-09 | festival poster | e-8203, e-8380; v-23 |
| P-12 | 1998-03 | festival poster | e-8552, e-8758; v-24 |
| P-13 | 1998-09 | Pirate Radio | e-8752, e-8830, e-8892 |
| A-01 | 1989-07 | Evan Newman · right | e-6446, e-6447 |
| A-02 | 1989-08 | Larry Baker · right | e-6436, e-6520 |
| A-03 | 1989-11 | Mona Sayer · wrong | e-6519, e-6510 |
| A-04 | 1990-01 | Evan Newman · right | e-6589, e-6590 |
| A-05 | 1990-02 | Toby Waller · wrong guess | e-6593, e-8229 |
| A-06 | 1990-02 | Ivan Tanner · wrong | e-6615 to e-6618 |
| A-07 | 1990-06 | Sam Brook · right | e-6688 |
| A-08 | 1990-07 | Toby Waller · partial | e-6702, e-6703 |
| A-09 | 1990-09 | Evan Newman · right | e-6383, e-6384, e-6687 |
| A-10 | 1991-08 | Mona Sayer · right | e-7023 |
| A-11 | 1992-02 | Tess Lane · partial | e-6545, e-7142 |
| A-12 | 1992-02 | Olive Shaw · right | e-7165, e-7166 |
| A-13 | 1992-03 | Oliver Brook · right | e-7197 |
| A-14 | 1992-07 | Olive Shaw · right, partial | e-7292 to e-7294 |
| A-15 | 1993-10 | Ivan Tanner · right | e-7593, e-7594 |
| A-16 | 1993-11 | Neil Lyons · partial | e-7579, e-7580 |
| A-17 | 1995-01 | Larry Baker · right | e-7883 to e-7885 |
| A-18 | 1995-01 | Olive Shaw · wrong | e-7868, e-7869 |
| A-19 | 1995-02 | Tess Lane · right | e-7922 |
| A-20 | 1995-03 | Neil Lyons · right | e-7659, e-7952 |
| A-21 | 1995-09 | Mark Holmes · wrong | e-7880, e-8076 |
| A-22 | 1996-08 | Gary Myers · partly wrong | e-8339 to e-8343 |
| A-23 | 1996-08 | Oliver Brook · right | e-8340, e-8341 |
| A-24 | 1997-01 | Tara Myers · right | e-8450 |
| A-25 | 1997-03 | Evan Newman · right | e-8495, e-8496 |
| A-26 | 1997-07 | Larry Baker · right | e-8565, e-8566 |
| A-27 | 1998-03 | Terry Sutton · right | e-8742, e-8743 |
| A-28 | 1998-06 | Agnes Tanner · right | e-8831 to e-8834 |
| A-29 | 1998-07 | Mona Sayer · right | e-8857, e-8858 |
| A-30 | 1998-11 | Trevor Lane · right | e-8943 |
| A-31 | 1999-01 | Eve Vaughan · wrong | e-8968, e-8969, e-8982 |
| A-32 | 1999-01 | Agnes Tanner · partial | e-8970 to e-8972 |
| D-01 | 1989-12 | Agnes Fielding | e-6557 |
| D-02 | 1992-06 | Ellie Holmes | e-7261 |
| D-03 | 1997-02 | Mary Tanner | e-8459 |
| D-04 | 1998-10 | Andy Shaw | e-8899 |
