<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
    <img alt="Shawn Liu - Applied AI engineer and published ML researcher. Reliable AI that ships." src="assets/banner-light.svg" width="100%">
  </picture>
</p>

<p align="center">
  <code>UC Irvine '26 → Columbia MSCS</code> · <code>Open to Applied-AI / ML / SWE</code> · <code>● loop-study.com is live</code>
</p>

<p align="center">
  <a href="https://shawnnnliu.github.io/">Portfolio</a> ·
  <a href="https://loop-study.com">Loop</a> ·
  <a href="https://openreview.net/profile?id=%7EXiangjian_Liu1">OpenReview</a> ·
  <a href="https://www.linkedin.com/in/xiangjian-shawn-liu/">LinkedIn</a> ·
  <a href="mailto:xl3704@columbia.edu">Email</a>
</p>

---

### Pick your path

| If you're a… | Start here | Why |
| :-- | :-- | :-- |
| **Recruiter / hiring manager** | [Receipts](#receipts) | Every claim below has a number and a link that proves it. |
| **Researcher** | [Research](#research) | Six papers, what I actually did on each, honest status labels. |
| **Engineer** | [Loop](#loop) | Why an LLM app has 5,135 tests. |

---

## The throughline

Most people read my profile as two unrelated people: an ML researcher who publishes on encrypted inference and neurosymbolic robustness, and a full-stack engineer who ships web products.
It's one idea.

My research is about systems that **degrade predictably**: how CKKS noise erodes a hypervector's similarity margin, how a classical-neural fusion loses accuracy gracefully under attack instead of falling off a cliff, how a beat-wise data split quietly manufactures a 98% accuracy that doesn't survive contact with a new patient.
My engineering is the same instinct pointed at production: validation layers, human approval gates, typed failure reasons, rollback paths.

I don't trust a model I can't bound.
That's the whole résumé.

---

## Loop

**LLMs propose. Deterministic infrastructure disposes.**

[Loop](https://loop-study.com) turns a career goal, your real weekly availability, and your progress signals into a validated study plan, then drafts it as an actual week on your Google Calendar.
I built it because I wanted it, and I use it daily.

Four LLM nodes write the plans and the prose.
Everything downstream of them is deterministic: five checks (schema, graph, coverage, user-fit, scheduling) sit between any proposal and your calendar, a failure goes *back* to the model as a typed repair message twice at most and then gives up honestly, and nothing is written until you approve it.
The write manager rechecks approval and payload hash, dry-runs, catches duplicates, verifies, and offers rollback.
The LLM SDK **cannot be imported** outside that first package; `import-linter` fails the build if you try.

- **5,135 tests** because the failure mode isn't "the model said something dumb," it's "the model said something dumb and it landed on your calendar at 8am Tuesday." The interesting tests are the boundary, not the model's outputs. One supervisor state machine owns every transition, every failure carries a typed reason code, and calendar sync is reconciliation-based, so external changes are adopted and deleted events don't resurrect.
- **Evals gate the prompts.** Every LLM call lands in a SQLite log with tokens, cost, and latency. Real model outputs are captured into committed recordings that CI re-grades offline, so live API calls never run in CI. Prompt bytes are version-pinned by hash, so an unmeasured prompt change fails the build. One fixture deliberately still fails, so I know the gate works.
- **Syllabi aren't generated from vibes.** 242 curated documents, 7,776 retrieval chunks, BM25-first with deterministic source-confidence scoring. Retrieval is code; the LLM only consumes what it's handed.
- **Deployment is deliberately boring.** One Docker image on Fly.io, a single uvicorn process on one always-on machine, because SQLite with WAL is a one-process store and no autoscaler should be fighting over the database. OAuth tokens are encrypted at rest, and Loop never stores raw calendar event titles or descriptions.

`Python 3.11` `FastAPI` `Pydantic v2` `SQLite + WAL` `React + TS + Vite` `Anthropic Messages API` `Google Calendar OAuth` `Docker` `Fly.io`

---

## Receipts

Everyone says "production-grade." Here's what I mean by it, with the number attached.

| Claim | The number | Where to check |
| :-- | :-- | :-- |
| LLM output never reaches your calendar unchecked | **5** deterministic validation checks, **≤2** typed repairs, then honest failure | [loop-study.com](https://loop-study.com) |
| Nothing writes without you | **1** human approval gate; the writer rechecks approval + payload hash, dry-runs, verifies, offers rollback | [case study](https://shawnnnliu.github.io/#loop) |
| Prompt changes ship measured, not vibed | **8** versioned eval sets; CI re-grades committed recordings; prompts pinned by hash | [Agentic-Calendar](https://github.com/ShawnnnLiu/Agentic-Calendar) |
| Tested like infrastructure | **4,822** backend + **313** frontend tests, green in CI | [Agentic-Calendar](https://github.com/ShawnnnLiu/Agentic-Calendar) |
| Cost is a design constraint, not a surprise | **$1.70**/user/month expected, worked out in a written axiom. Hard cap **$8** | [case study](https://shawnnnliu.github.io/#loop) |
| Plans cite their sources | **242** curated documents → **7,776** retrieval chunks, BM25-first | [loop-study.com](https://loop-study.com) |
| Decisions are written down before they're built | **23** axioms + **10** ADRs | [Agentic-Calendar](https://github.com/ShawnnnLiu/Agentic-Calendar) |
| A crash warning arrives early enough to matter | **3.05 s** mean time-to-accident, streaming at **408 fps** from a 2.95M-param student | [Crash-Anticipation](https://github.com/ShawnnnLiu/Crash-Anticipation) |
| Encrypted inference stays usable | **>90%** accuracy under CKKS-FHE at **4×** lower bootstrapping overhead | IEEE TAI (under review) |

---

## Research

Secure ML inference (FHE/CKKS), neurosymbolic AI, and hyperdimensional computing.
Six papers: four accepted or published, two under review, labelled honestly.

| Venue | Paper | My role | |
| :-- | :-- | :-- | :-- |
| **WACV 2026** | Cross-Modal Event Encoder: Bridging Image–Text Knowledge to Event Streams | lead + corresponding | [arXiv](https://arxiv.org/abs/2412.03093) |
| **NeurIPS 2025** · NeurReps | Geometric Priors for Generalizable World Models via VSA | co-author | [OpenReview](https://openreview.net/forum?id=0MJ1PW2vE8) |
| **ISLPED 2026** | Integrating Symbolic & Neural Mechanisms for Adversarially Robust HDC | co-author | `10.1145/3816440.3818596` |
| **Frontiers in AI** | Optimal Hyperdimensional Representation for Learning & Cognitive Computation | co-author | [Paper](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2026.1690492/full) |
| **IEEE TAI 2026** · *under review* | Robust Reasoning & Learning with Brain-Inspired Representations under FHE | lead + corresponding | *(preprint on request)* |
| **IEEE TAI 2026** · *under review* | HyperEncrypt: Homomorphic HDC for Efficient & Secure Learning | co-author | *(preprint on request)* |

The event encoder gets **+15.2 pts** zero-shot on unseen N-ImageNet classes by transferring CLIP's understanding to event streams alone.
The VSA world model learns grid-like state embeddings an MLP baseline never finds: **87.5%** zero-shot accuracy at **4×** noise robustness.

Grateful to research with **Prof. Mohsen Imani** (BiasLab @ UCI) and **Dr. Haleh Alimohamadi** (BioIntelligence Lab @ UCI).

---

## Shipped

| | What it is | The honest headline |
| :-- | :-- | :-- |
| 🛬 **Safe UAV Landing** <br> <sub>U.S. Navy collaboration</sub> | Pose estimation + symbolic reasoning replacing brittle fixed-pattern optical markers for autonomous carrier landing in bad weather. | A reasoning module that **holds the landing** whenever crew or obstacles are on the deck. CUI dataset, visuals restricted. |
| 🚗 **[Crash Anticipation](https://github.com/ShawnnnLiu/Crash-Anticipation)** <br> <sub>v0.3.0</sub> | Online crash-risk prediction from one dashcam. A neural model decides *whether* it's dangerous; a symbolic layer decides *what the threat is* and can always explain itself. | **3.05 s** mean warning at **408 fps**, from a distilled 2.95M-param student that beats its 21.88M teacher on lead time. And it's still image-space geometry, not spatial understanding, and [I say so out loud](https://shawnnnliu.github.io/#projects). |
| 🫀 **[Arrhythmia, Honestly Evaluated](https://github.com/ShawnnnLiu/Arrythmia_Classifier)** | Shows how beat-wise splits leak patient identity and inflate ECG accuracy, then searches for an optimal patient-wise split. | **98.4% → 89.7%.** The gap *is* the paper. |
| 🧬 **[Antimicrobial Peptides](https://github.com/ShawnnnLiu/Peptide-Anti-microbial-Properties-Prediction)** | Fuses biochemical descriptors with structure-aware features from ESMFold conformations across SVM / MLP / GNN. | Ongoing: isolating what 3D conformation actually contributes. |
| 🛒 **[AdamsFoods Wholesale](https://adamsfoodswholesale.com/)** <br> <sub>● live, solo build</sub> | React + Node/Express wholesale platform, signed-URL S3 media, JWT auth with role-guarded admin routes. | Real customers, today. |
| 🐾 **Feeding Pets of the Homeless** <br> <sub>CTC @ UCI</sub> | Donation-management platform for a national nonprofit, role-based across regional chapters. | Built and maintained free of charge. |

Also kicking around: **[Astrolabe](https://github.com/ShawnnnLiu/Astrolabe)** (LLM course-selection for Columbia, built by someone about to need it), **[Robust-NeRF](https://github.com/ShawnnnLiu/Robust-NeRF)**, and a [search engine over UCI](https://github.com/ShawnnnLiu/UCI-DIR-Search-Engine) with tf-idf scoring and an inverted index.

---

## Recent

<!-- NEWS:START -->
- **Jul 2026** · **Loop** is deployed live at [loop-study.com](https://loop-study.com): an LLM-powered interview-prep scheduler with deterministic validation, human approval gates, and a recordings-based eval harness. I built it for my own daily use. [[Case study]](https://shawnnnliu.github.io/#loop)
- **May 22, 2026** · **Integrating Symbolic and Neural Mechanisms for Adversarially Robust Hyperdimensional Computing** was accepted to *ISLPED 2026*.
- **Apr 5, 2026** · **Live Spotify Stats**: feel free to stalk my recent listening history and see how our music tastes match up :)
- **Jan 19, 2026** · **Optimal Hyperdimensional Representation for Learning and Cognitive Computation**: third author, accepted to *Frontiers in Artificial Intelligence*. [[Paper]](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2026.1690492/full)
<!-- NEWS:END -->

<sub>Auto-synced from <a href="https://shawnnnliu.github.io/#news">shawnnnliu.github.io</a>.</sub>

---

<p align="center">
  <b>Let's build something that ships.</b><br>
  <a href="mailto:xl3704@columbia.edu">xl3704@columbia.edu</a> ·
  <a href="https://shawnnnliu.github.io/assets/CV/Shawn_Liu_CV_Research.pdf">CV</a> ·
  <a href="https://www.linkedin.com/in/xiangjian-shawn-liu/">LinkedIn</a>
</p>

<p align="center">
  <sub>The news block above is rebuilt on a schedule by <a href=".github/workflows/update-readme.yml">a GitHub Action</a>.<br>
  Every link in this file is checked in CI, because a README with dead links is a README that lies.</sub>
</p>
