# Bovine Auricular Vagus Nerve Stimulation — Hackathon Build

## One-line pitch
An instrumented ear tag that delivers low-level electrical stimulation to the auricular branch of the vagus nerve in cattle, reducing systemic inflammation during the BRD-risk window and cortisol-driven stress before slaughter — replacing prophylactic antibiotics and preventing dark-cutting beef, with a data flywheel as the long-term moat.

---

## The two problems being solved (separate mechanisms, same device)

### Problem 1 — BRD (Bovine Respiratory Disease)
- Affects 16-21% of placed cattle in feedlots
- Single treatment episode costs $38-230 all-in (drugs, labor, performance loss)
- $800M-$1B/year industry cost in the US
- Standard response is prophylactic antibiotics — under pressure from WHO, FDA GFI #213, consumer backlash
- Mechanism: vagal stimulation activates the cholinergic anti-inflammatory pathway -> splenic nerve -> alpha7nAChR macrophage signalling -> suppresses TNF-alpha, IL-1beta, IL-6
- This pathway is FDA-validated in humans (SetPoint Medical PMA approved August 6, 2025, P240039, for rheumatoid arthritis, RESET-RA trial n=242)

### Problem 2 — Dark cutting beef
- Caused by pre-slaughter stress -> cortisol surge -> glycogen depletion -> no post-mortem pH drop -> dark, sticky, dry meat
- Packer discount: $38.75/cwt carcass weight (20-40% price reduction)
- Industry cost: $288M/year in the US
- Incidence: 1.8% of cattle (2022 National Beef Quality Audit)
- Mechanism: VNS shifts autonomic balance parasympathetic -> less cortisol -> glycogen preserved -> normal meat pH
- This is a welfare AND profit argument

These are two separate mechanisms (immune vs. autonomic/stress) that both use the same vagal pathway, addressable by the same device with different stimulation protocols at different points in the production cycle.

---

## The ear tag — core technical insight

The auricular branch of the vagus nerve (ABVN) leaves the cervical vagus trunk at the jugular ganglion just outside the cranium and innervates the central regions of the outer ear — specifically the cymba concha (100% of cadaver studies) and cavum concha (45%).

In humans, electrically stimulating this branch at the concha produces the same systemic anti-inflammatory effect as cervical trunk VNS, via the nucleus tractus solitarius -> dorsal motor nucleus -> efferent fibres to the spleen.

A bovine ear chart with 27 auricular acupuncture points exists for cattle (Kothbauer 1999).

### Why ear tag and not cervical implant (for V1)
- Cervical VNS requires surgical dissection, sterile field, sedation, trained veterinarian
- 20-45 minutes per animal = $33-150 in labor alone at feedlot scale
- Places implanted material in edible neck tissue -> FDA food safety question
- Economically prohibitive as Version 1
- Ear tag: zero new behavior from farmer, ear discarded at slaughter, 5 seconds per animal, ABVN runs through the ear tag position
- Cultural precedent: Revalor hormone implants used in 94% of US feedlot cattle for 60 years

Roadmap: ear tag (V1) generates proof-of-concept data and revenue -> cervical VNS via Injectrode (V2) maximises potency once mechanism is validated.

---

## Key Published Evidence: Winkler et al. 2021

**Paper:** "A potential treatment approach for subclinical mastitis in dairy cows: auriculotherapy of the auricular branch of the vagus nerve." Journal of Dairy Research, Volume 88, Issue 4, November 2021, pp. 407-412. DOI: 10.1017/S002202992100087X. Open Access (CC BY-NC-ND 4.0).

### Study design
- 85 clinically healthy dairy cows from nine dairy farms in Lower Austria
- Randomized: 45 treated (TRE), 40 control (CON)
- 784 total quarter somatic cell counts analysed (399 TRE, 385 CON)
- Inclusion: cows with individual composite SCC > 200,000 cells/ml; quarters with QSCC > 100,000 cells/ml on d0
- Ethics approved by University of Veterinary Medicine, Vienna

### Intervention
- **NOT electrical stimulation** — pharmacological auriculotherapy
- Three repeated intracutaneous infiltrations of 0.4 ml procaine hydrochloride 2% (8.0 mg per treatment)
- Injected at four points (12, 3, 6, 9 o'clock) around the ear tag scar on the LEFT ear only
- Treatments on d0, d2, d4; sampling on d0, d2, d4, d6
- Controls handled identically but without injection

### Key results
- Significant reduction of QSCC in TRE from d0 to d6 (P < 0.01) after three treatments
- No significant change in CON over the same period (P > 0.05)
- Effect was bilateral — left ear treatment reduced SCC in BOTH left and right udder quarters
- Effect was independent of bacteriological culture results (worked in both positive and negative samples)
- Bacteriological cure rate was NOT affected (27.5% CON vs. 20.3% TRE, P = 0.38)
- Strongest effect at ear tag position 10 (the standard ear tag location, corresponding to udder AAP)
- ~70% of ear tags were already at position 10 by default

### Critical finding for the project
The bovine ABVN functional zone is at position 10 (mid-ear, standard ear tag location) — NOT at position 9 (auditory meatus, where human taVNS targets). The paper states: "the area of vagal innervation at the cow's ears is different compared with humans." This means the default ear tag placement is already the optimal stimulation location in cattle.

### What this proves
- The bovine ABVN is accessible at the standard ear tag position
- Stimulating it produces measurable systemic anti-inflammatory response
- The effect is vagal-pathway-mediated (bilateral response from unilateral treatment)
- The response is immune modulation, not direct antimicrobial (no bacterial cure rate change)

### What this does NOT prove
- That electrical stimulation at this location works in cattle (procaine blocks conduction; taVNS activates fibres — mechanistically opposite)
- That the cholinergic anti-inflammatory pathway specifically is the mechanism
- Any dose-response relationship for electrical parameters
- Long-term efficacy beyond 6 days

---

## The Efficacy Gap: Honest Assessment of Auricular Stimulation

### Why ear stimulation may not be strong enough

**1. Human taVNS vs. cervical VNS effect sizes are not comparable.**
SetPoint's PMA is for cervical VNS — a cuff directly on the nerve trunk, activating both afferent AND efferent fibres, including direct efferent drive to the spleen. Auricular VNS is afferent-only — sensory fibres project to NTS, relying on the central reflex arc to drive efferent output back down. That's a two-synapse relay with signal attenuation at every step. Human taVNS studies show statistically significant but modest cytokine reductions compared to cervical VNS.

**2. The Winkler paper used procaine, not electricity.**
Even with direct intracutaneous injection, the study showed SCC reduction only after three treatments over six days. A surface electrode on a tag, through keratinized ear skin, with no conductive gel, has far worse neural coupling than a needle delivering drug directly to tissue.

**3. Surface electrode coupling through an ear tag is the weakest possible delivery.**
Human taVNS devices use conductive gel, clip electrodes pressed firmly into the concha, and 1-4 hour supervised sessions. An ear tag electrode sits against a cartilage punch wound that scars over, in an animal that rubs its ears against fences. Impedance will be high and inconsistent. The fraction of delivered current reaching ABVN fibres through scarred tissue and cartilage is genuinely uncertain.

**4. Zero dose-response data for electrical taVNS in any ruminant.**
The extrapolation chain: human -> bovine (species), pharmacological -> electrical (modality), intradermal injection -> surface electrode (delivery method). Three compounding unknowns.

### Strategic implications
The ear tag is strongest as a **monitoring and data platform first, with experimental stimulation as the research bet.** The cervical VNS (V2) is where the therapeutic effect size lives. The ear tag gets us into the barn and generates the world's first bovine vagal dataset.

---

## The Vagus Nerve Selectivity Problem

### The core problem: the vagus nerve is not a single wire

The cervical vagus contains thousands of fibres serving completely different functions — heart rate, breathing, laryngeal muscles, gut motility, immune modulation, sensory feedback from every thoracic and abdominal organ. When you stimulate the whole nerve with a simple cuff electrode, you activate all of them indiscriminately.

For cattle specifically, the dangerous off-target effect is **vagal indigestion (Hoflund syndrome)** — unselective stimulation of motor fibres to the forestomach causes the reticulum and rumen to stop contracting, gas accumulates, the animal bloats, and in severe cases dies. Fascicular selectivity is not a nice-to-have but a **hard safety requirement** for any cervical VNS in cattle.

### Fibre type selectivity vs. organ selectivity — two separate problems

**Fibre type selectivity** = activating small-diameter B-fibres (autonomic, anti-inflammatory) without activating large-diameter A-alpha fibres (motor, including forestomach). Achieved through stimulation parameters (pulse width, amplitude). Large myelinated A-alpha fibres have lower activation thresholds at short pulse widths, but the relationship inverts at longer pulse widths. The strength-duration curve for each fibre type is different. **This is what the PyFibers simulation produces — the safe operating window between B-fibre activation and A-alpha activation.** Parameter-based selectivity; doesn't require knowing spatial fascicular layout.

**Organ selectivity** = steering current spatially to the fascicle containing splenic/immune fibres rather than laryngeal or forestomach fibres. Requires the organotopic map and a multi-contact electrode. A 2025 Nature Communications paper showed that even with interferential current stimulation, almost no electrode configuration achieved perfect selectivity because BP and recurrent laryngeal fibres are mixed within the same fascicles — fundamental anatomical limits on surface electrode selectivity.

### What's been proven in pigs (the closest large-animal data)

**Organotopy demonstrated (2023):** The porcine mid-cervical vagus nerve is organised organotopically. Using electrical impedance tomography and selective stimulation in four pigs, researchers identified consistent spatially separated fascicular regions for cardiac, pulmonary, and recurrent laryngeal function, verified by microCT tracing.

**Fascicle-selective VNS achieved (2023):** A multi-contact helix cuff electrode with 8 platinum-iridium contacts delivered fascicle-selective VNS in both anaesthetised and chronically implanted awake swine. Compound action potentials and physiological responses from different organs were elicited in a radially asymmetric manner matching documented fascicular organisation.

### For the ear tag (V1): safety margin is wide
The auricular branch contains predominantly afferent sensory fibres, not motor fibres to the forestomach. Vagal indigestion risk via auricular stimulation is essentially zero. The fibre type selectivity question still applies (activate afferent NTS-projecting fibres, not pain fibres) but the safety margin is much wider than cervical.

### For cervical VNS (V2): three critical unknowns

**Gap 1: Bovine vagus morphometry — completely absent.** No quantified bovine cervical vagus dataset exists. Unknown: nerve diameter, fascicle count, fascicular organisation, perineurium thickness, fibre diameter distributions. Human and pig cervical vagus ~2mm diameter. Cattle estimated 3-5mm from body mass scaling. Pig has ~47 fascicles, sheep ~6. Bovine is unknown. **Addressable: 3-month abattoir experiment, $50-100k. Whoever does this first owns the only bovine vagus morphometry dataset in existence.**

**Gap 2: Bovine organotopy — completely unknown.** Even in pigs the map only covers cardiac, pulmonary, and laryngeal function. Splenic/immune fibres have not been mapped to a specific fascicular location in any species at the cervical level.

**Gap 3: GI motor fibre location — the safety-critical unknown.** Motor efferents to rumen and reticulum cause Hoflund syndrome if activated. Where they sit in the bovine cervical vagus cross-section is not mapped.

---

## Hardware Design

### Ear tag (V1)
- Small electrode array on inner face, positioned against the cymba concha
- Microcontroller: nRF52840 (~$1.50-2.50 at volume)
- Primary lithium cell battery (~$0.50-2.00)
- Biphasic stimulation circuitry
- BLE for data logging
- BOM at 100k volume: ~$10-24 total

### Stimulation parameters (from human taVNS literature)
- 15 Hz (outperforms 25 Hz for anti-inflammatory effect in mouse LPS model)
- Biphasic charge-balanced waveform
- Cymba and cavum concha bilateral stimulation
- Two programmable protocols:
  - Anti-inflammatory: weeks 1-4 post-arrival (BRD high-risk window)
  - Calming: 48-72 hours before scheduled slaughter (dark cutting prevention)

### Battery life
150-day feedlot finishing period achievable at these duty cycles on a primary lithium cell.

### Cervical VNS (V2) — cost estimate
- Sedation + local anesthesia: $15-40
- Veterinarian time (30-60 min at $150-300/hr): $75-300
- Surgical supplies: $20-50
- Implant device: $200-500 prototype, $50-150 at scale
- Post-op monitoring: $30-80
- **Total per head: ~$360-970 early stage, $190-420 at scale**
- **Throughput killer:** 30-60 min/animal vs. 5 seconds for ear tag. A feedlot processing 200-500 head on arrival day would need 12-60 vet-days per cohort.
- **Solution for V2:** Injectrode (injectable polymer electrode, Kip Ludwig lab) — injected through a needle in ~30 seconds, cures in place around the nerve, $5-20 materials cost. Eliminates the surgical bottleneck.

---

## Recommended Pitch Framing

Given the efficacy gap in auricular stimulation, the strongest position is:

**"The ear tag gets us into the barn. The cervical device is where the therapeutic value lives."**

- V1 ear tag = monitoring/data platform + experimental stimulation as controlled research
- V1 generates the world's first bovine vagal dataset (HRV, skin conductance, temperature, activity)
- V1 stimulation runs as a controlled trial during first 10,000 head deployed
- V2 cervical VNS via Injectrode = full therapeutic effect, enabled by morphometry data from V1
- Founding experiment (bovine vagus morphometry from abattoir tissue) = 3 months, $50-100k, de-risks V2

### What to say
- "We made the ear tag do something useful"
- "The same thing good stockmanship does, but automated and measurable"
- "An alternative to prophylactic antibiotics, backed by FDA-validated human science"
- "We're building on 60 years of Revalor ear implant practice"

### What not to say
- "Bioelectronic medicine for livestock"
- "Neural implant"
- "Breakthrough neurotech"
- "We're applying SetPoint's VNS to cows"

Lead with: welfare + profit. Dark cutting stat opens the pitch. BRD antibiotic replacement is the WHO-aligned tailwind. Data flywheel is the investor unlock for tech audiences.

---

## The Data Flywheel (long-term moat)

At 1% US market penetration: ~100k instrumented cattle x continuous vagal recording.
World's current chronic vagal recording dataset across all species: a few thousand animal-hours.
This would be 1000x the world's data within 3 years of commercial launch.

Uses:
- Own product optimisation (parameter refinement, responder prediction)
- Sale to human VNS device companies (cervical vagus morphometry and response data is directly translatable)
- Foundation model for bovine neural activity
- Reframes company from "cow startup" to "AI/data company that uses cows as the data source"

---

## Competitive Landscape

No direct competitors. Every competitor solves one KPI:

| Company | Mechanism | KPI | Limitation |
|---------|-----------|-----|------------|
| Bovaer (DSM/Elanco) | 3-NOP feed additive | ~30% methane | Dairy only, daily TMR mixing, ~$75/head |
| Rumin8 | Synthetic bromoform | Methane (86-95%) | ~2027 commercial launch |
| ArkeaBio | Methane vaccine | 10-15% methane | ~$45.5M raised, years from commercial |
| smaXtec/Allflex/Halter | Sensors | Monitoring only | No therapeutic intervention |
| Revalor/Synovex | Hormone implant | Growth | Welfare-negative framing |
| Nofence/Halter/Vence | GPS collar | Virtual fencing | No health intervention |

The ear tag VNS is the only multi-KPI platform: BRD + dark cutting + feed efficiency + antibiotic replacement + data, in one device.

---

## Unit Economics Per Head

### Value stack (conservative)
- BRD reduction (25% relative): $4-15/head
- Dark cutting prevention: $0.75-3/head
- Feed efficiency (3% improvement): $19-25/head*
- Antibiotic reduction premium: $5-20/head
- **Total: $29-63/head conservative**

*Feed efficiency is the weakest claim — no direct evidence for VNS -> feed efficiency in ruminants. Extrapolated from stress reduction -> better intake -> better FCR. Soft-pedal or asterisk this number.

### Device cost at scale
- BOM at 100k units: $10-24
- Placement labor: ~$0 (existing ear tag workflow)
- Net margin: $5-39/head conservative

### Market size
- US feedlot cattle: ~10M head at any time
- US TAM at $50/head net: ~$500M
- Global beef + dairy: $20B+

---

## Regulatory Picture

FDA CVM does not require pre-market approval (PMA, 510(k)) for veterinary devices.

**Ear tag (V1):** Ear is entirely discarded at slaughter — zero food safety concern. Modified ear tag with surface electrodes requires ISO biocompatibility data for electrode materials + standard FSIS notification. Budget: $200-500k. Much simpler than cervical.

**Cervical implant (V2):** Would require negotiation with FDA CVM + FSIS + potentially CVB across three agencies with zero precedent. Budget: $2-10M.

**Regulatory anchor:** Revalor hormone implants (NADA 138-612, approved 1987) — placed subcutaneously in the ear, 94% adoption rate, no food safety issues.

---

## Key Academic Contacts

- **Stavros Zanos** (Feinstein Institutes) — large-animal pig VNS, fascicular selectivity, imec ASIC. szanos@northwell.edu. Highest priority.
- **Warren Grill and Nicole Pelot** (Duke) — ASCENT pipeline, cross-species VNS parameter scaling. nikki.pelot@duke.edu
- **Kip Ludwig** (Wisconsin-Madison) — pig vagus organotopy, Injectrode inventor, NIH SPARC architect.
- **UCL Centre for Nerve Engineering** (Holder, Aristovich) — VNS in pigs and sheep, EIT-based fascicular imaging.
- **Bionics Institute / UNSW Australia** (Payne et al.) — chronic VNS in awake freely-moving sheep, up to 3 months stable recordings.

---

## Simulation Work (Hackathon Deliverables)

### Primary tools
- **PyFibers** (pip install pyfibers) — 10 min setup, 11 validated fiber models including MRG myelinated and unmyelinated, built-in analytical point-source extracellular potentials, threshold search. No COMSOL needed.
- **axonml** — ~90,000x speedup surrogate model, requires PyTorch 2.0+ and NVIDIA GPU with CUDA 11.7+. Pre-trained MRG model included. Zenodo DOI: 10.5281/zenodo.12752386
- **NRV framework** (nrv-framework/NRV) — fully open-source, Python-based, uses FEniCSx for FEM and Gmsh for meshing. Docker image available.
- **ASCENT** (wmglab-duke/ascent) — gold standard but requires COMSOL ($5-10k/year). Free via o2S2PARC cloud (osparc.io) with NIH SPARC portal access.

### Simulation deliverables
1. **Species morphometry gap visualisation** — quantified vagus cross-sections for human, pig, rat (SPARC portal data) with empty "BOVINE: ?" panel. The IP wedge made visual.
2. **Synthetic bovine vagus cross-section** using ASCENT Mock Morphology Generator — extrapolating from pig (~47 fascicles) and sheep (~6 fascicles) via body mass scaling.
3. **Fibre selectivity maps** — activation thresholds across fibre types (A-alpha motor, A-beta sensory, B autonomic, C unmyelinated) showing the parameter space where B-fibre activation occurs without A-alpha activation. **This is the core safety window demonstration.**
4. **Auricular branch-specific model** — simplified nerve cross-section at cymba concha showing activation at ear tag-appropriate amplitudes.
5. **"Wrong parameters" failure case** — what happens with overstimulation (A-alpha activation -> vagal indigestion risk).

### Recommended approach
PyFibers + analytical point-source potentials for main demo. axonml for GPU-accelerated population selectivity maps if GPU available. Build Streamlit or Jupyter interactive dashboard.

---

## 48-Hour Build Plan

**Hours 0-6:** Install PyFibers + axonml. Build species morphometry gap visualisation. Create synthetic bovine vagus cross-section.

**Hours 6-16:** Core simulation — fibre selectivity maps, B-fibre vs A-alpha threshold separation, safety window demo, failure case. axonml for GPU-accelerated population maps. Build Streamlit/Jupyter interactive demo.

**Hours 16-22:** Unit economics calculator (interactive: input feed price, BRD incidence, dark cutting rate -> output per-head ROI and breakeven). Value stack comparison chart vs. competitors.

**Hours 22-30:** Dashboard integration — morphometry panel, selectivity maps, economics calculator, auricular anatomy diagram showing ABVN location relative to ear tag placement.

**Hours 30-42:** Pitch deck. Three-minute video script. Q&A prep document.

**Hours 42-48:** Rehearse, record backup screen recordings, final polish.

---

## Three-Minute Pitch Video Structure

- 0:00-0:30 — Dark-cutting stat and BRD cost. No jargon. Pure farmer economic pain.
- 0:30-0:50 — The ear tag concept. "We modified something farmers already use."
- 0:50-1:10 — Mechanism in one sentence. "The outer ear has a branch of the vagus nerve. Stimulating it reduces inflammation. A 2022 cattle study showed this works for mastitis."
- 1:10-1:40 — Show the simulation. PyFibers/axonml selectivity demo.
- 1:40-2:00 — Stack the value. BRD, dark cutting, feed efficiency, antibiotic replacement. $29-63/head.
- 2:00-2:20 — Data flywheel. "Every device generates longitudinal vagal nerve data that doesn't exist anywhere. 1000x the world's dataset within 3 years."
- 2:20-2:50 — Roadmap. Ear tag V1 generates proof. Cervical VNS V2 maximises value.
- 2:50-3:00 — The ask.

---

## Expert Validation — Dr. Ronald Tessman, DVM PhD

**Background:** Beef Cattle Technical Consultant at Elanco Animal Health. 17 years across Bayer, Merial, and Elanco overseeing clinical efficacy studies for feedlot products.

### Key confirmations:

**Mechanism validated:** "Runaway immune response associated with neutrophilia in the lung" — confirmed host inflammatory response is a major driver of BRD damage, not just bacteria. This is the biological basis for VNS intervention.

**No internal measurement exists:** The single biggest industry problem. Pen riders, ear tags, rumen boluses, whisper technology, ultrasound — none are great. A nerve cuff that can both sense inflammatory signals AND stimulate to modulate the response is exactly the internal measurement + intervention system he described as missing. An adjunctive diagnostic would be "tremendous."

**Diagnostic imprecision is enormous:** Animals get treated that don't have BRD. Animals that do have BRD never get treated and show up with lung lesions at slaughter. Even in FDA licensure studies, saline placebo animals sometimes recover — that's how imprecise clinical diagnosis is.

**Economics from Tessman:**
- Treatment cost: ~$50/head
- Diagnostic device threshold: ~$20/animal (must be cheaper than the treatment it helps avoid)
- If device can sense AND stimulate: value could double
- Pricing envelope: $20-50 diagnosis only, up to $100 with therapeutic effect
- Reusable device across multiple animals improves economics

**Biomarker reality check:**
- No well-correlated biomarker is currently predictive for BRD
- Field uses: cell counts (WBC differential, neutrophils), rectal temperature, blood glucose as stress proxies
- Rectal temp and blood glucose effectively replace cortisol measurement (reflect stress quickly)
- Has not looked at interleukins in BRD response
- Our closed-loop biomarker panel is ahead of where the field currently operates — opportunity to prove novel correlations, but must validate ourselves since nobody has done it in cattle BRD

---

## Farmer Validation Call Guide

### Who to call
- Texas Cattle Feeders Association: 806-358-3681
- Kansas Livestock Association: 785-273-5115
- Nebraska Cattlemen: 402-475-2333
- County extension beef cattle specialists (tamu.edu/extension, ksu.edu/extension)
- Feedlot veterinarians on LinkedIn
- r/Ranching and r/Farming

### Opening script
"Hi, I'm part of a student team at a neurotech hackathon working on a device concept for feedlot health. We're not selling anything — we want 10 minutes to understand whether the problem we're solving is actually painful from your perspective."

### Questions
1. What % of placed cattle do you treat for BRD per year, and what does a treatment episode cost all-in?
2. Have you had a dark-cutting problem — discount amount, what caused it?
3. If a modified ear tag reduced BRD treatment rate 25%, what is that worth per head, and what makes you sceptical?
4. Who do you trust to tell you something new works — university trial, neighbour, vet, or packer?
5. What would a pilot look like you'd actually agree to run?

Listen for: specific dollar amounts, whether dark cutting is real to their operation, reaction to "ear tag format," trust hierarchy, anything that kills the idea.
