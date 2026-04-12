# Bovine VNS — Technical & Strategic Dossier
**Bluesky Hackathon 2026 | April 2026**

> An instrumented ear tag delivering electrical stimulation to the auricular branch of the vagus nerve in cattle, targeting BRD reduction and dark-cutting prevention. This document presents the evidence base honestly, including the substantial gaps.

---

## Contents

1. [The Two Problems](#1-the-two-problems)
2. [The Auricular VNS Concept](#2-the-auricular-vns-concept)
3. [What the Evidence Actually Shows — Honest Assessment](#3-what-the-evidence-actually-shows--honest-assessment)
4. [The Full Data Gap Map](#4-the-full-data-gap-map)
5. [Delivery Approach Comparison](#5-delivery-approach-comparison)
6. [V2a — Poll/Parotid Injectrode](#6-v2a--pollparotid-injectrode)
7. [Device Specification — V1 Ear Tag](#7-device-specification--v1-ear-tag)
8. [Validation Experiment Sequence](#8-validation-experiment-sequence)
9. [Simulation Work for Hackathon](#9-simulation-work-for-hackathon)
10. [Competitive Landscape](#10-competitive-landscape)
11. [Messaging Framework](#11-messaging-framework)
12. [Farmer Validation Calls](#12-farmer-validation-calls)
13. [Academic Contacts](#13-academic-contacts)
14. [Risk Register](#14-risk-register)
15. [Development Roadmap](#15-development-roadmap)

---

## 1. The Two Problems

### 1.1 Bovine Respiratory Disease (BRD)

BRD is an infectious respiratory disease caused by bacteria and viruses attacking the lungs, primarily in the first weeks after feedlot arrival when cattle are stressed from transport and commingling. It is the single largest disease burden in the US beef industry.

| Metric | Value |
|--------|-------|
| US annual industry cost | $800M–$1B+ |
| Cattle affected per year | 16–21% of placed feedlot cattle |
| Cost per treatment episode | $38–230 all-in (drugs, labor, performance loss) |
| Standard response | Prophylactic antibiotics — under pressure from WHO, FDA GFI #213, consumer backlash |

**Biological mechanism:** Vagal stimulation activates the cholinergic anti-inflammatory pathway via the splenic nerve, suppressing TNF-alpha, IL-1beta, and IL-6 through alpha7 nicotinic acetylcholine receptor (alpha7nAChR) signalling on macrophages. This specific pathway is FDA-validated in humans: SetPoint Medical received PMA approval (P240039) on August 6, 2025, for vagal nerve stimulation in rheumatoid arthritis via this exact mechanism (RESET-RA trial, n=242).

### 1.2 Dark Cutting Beef

Dark cutting is a meat quality defect caused by pre-slaughter stress — a completely separate mechanism from BRD.

**Causal chain:** Stress → cortisol surge → glycogen depletion from muscle tissue → no lactic acid post-mortem → pH does not fall → dark, sticky, dry meat.

| Metric | Value |
|--------|-------|
| US annual cost | $288M (National Beef Quality Audit 2022) |
| Incidence | 1.8% of cattle |
| Packer discount | $38.75/cwt carcass weight (20–40% price reduction) |
| VNS mechanism | Parasympathetic shift reduces cortisol, preserving glycogen for normal post-mortem acidification |

> **KEY DISTINCTION:** BRD and dark cutting are caused by different mechanisms — immune dysregulation vs. autonomic stress response — but both involve the vagal pathway. The same device can address both with different stimulation protocols at different points in the production calendar.

---

## 2. The Auricular VNS Concept

### 2.1 The Human ABVN — What Is Known

The auricular branch of the vagus nerve (ABVN) leaves the cervical vagus at the jugular ganglion just outside the cranium and innervates specific regions of the outer ear. In humans this branch is well-characterised from cadaver dissection and fMRI:

- Cymba concha: innervated by ABVN in ~100% of cadaver studies
- Cavum concha: ABVN present in ~45% of cases
- Tragus: partial ABVN innervation (~45% of cases)
- Earlobe: no ABVN innervation (standard sham site in human taVNS trials)

Critically: **nerve fibres in the human auricle sit in a 1–1.5 mm gap between the auricular cartilage and the skin.** This is the accessible depth in humans. Bovine ear cartilage and skin are substantially thicker — the equivalent depth in cattle is unknown.

### 2.2 Human taVNS Evidence

Transcutaneous auricular VNS is well-validated in humans across multiple RCTs:

- Anti-inflammatory efficacy confirmed: reduces TNF-alpha, IL-1beta, IL-6, IL-17a; increases IL-4 and IL-10
- 2025 NUVISTA stroke RCT: significant reduction in IL-6 and cytokine score over 7 days
- Anti-inflammatory effects blocked by alpha7nAChR antagonist (methyllycaconitine), confirming the cholinergic anti-inflammatory pathway as the operative mechanism — identical to cervical VNS
- Stimulation parameters across studies: 10–30 Hz, pulse width 0.1–0.5 ms, amplitude under 4 mA, duration 20–60 min per session
- Cymba concha produces strongest NTS/locus coeruleus activation vs. other auricular sites (fMRI-verified)
- Safety profile: minimal side effects in pooled analysis of 488 participants

> **Note on parameter consensus:** There is no agreed optimal parameter set for human taVNS. Different conditions use different parameters (e.g. 10 Hz for cardiac effects, 25 Hz for epilepsy, 15 Hz found superior for anti-inflammatory in mouse LPS model). Translating any of these to cattle requires independent validation.

---

## 3. What the Evidence Actually Shows — Honest Assessment

This section deliberately separates what is proven from what is assumed.

### 3.1 The Mastitis Paper — What It Does and Does Not Show

**The paper:** Journal of Dairy Research 2022, n=85 dairy cows, subclinical mastitis. Auriculotherapy (AT) using procaine hydrochloride injection (0.4ml, 2% solution) at the ear tag position on the bovine ear. Outcome: significant reduction in quarter somatic cell count (QSCC), a direct marker of udder inflammation.

**What this proves:**
- The bovine auricular region near the ear tag position has connections to systemic inflammatory pathways
- Stimulating this area by chemical means (procaine nerve block) produces measurable anti-inflammatory effects in cattle
- The ABVN is accessible in the bovine ear at or near the standard ear tag location

**What this does NOT prove — and these gaps are substantial:**

1. **Electrical vs. chemical stimulation are fundamentally different.** Procaine is a local anaesthetic that blocks nerve conduction by inhibiting sodium channels. It floods the tissue around the nerve and affects all fibres indiscriminately. Electrical stimulation requires precise charge delivery to specific fibre types at specific parameters. The mechanisms are not directly comparable.

2. **No electrical parameter validation in cattle.** The 15 Hz / 250–500 µs / sub-4 mA parameters used in human taVNS are derived from human ABVN fibre diameters and human ear tissue impedance. Bovine ABVN fibre composition, myelination density, and ear tissue impedance are all unmeasured. Whether any human-derived electrical parameter actually recruits bovine ABVN fibres at practical amplitudes is unknown.

3. **The paper's own authors flag the anatomy problem.** The mastitis paper explicitly states: *"anatomical structures appear to be too different from humans to transfer AAP directly to bovine"* (citing Artmeier and König 1978; Kothbauer 1986). This is the closest thing to a bovine auricular VNS paper, and its authors acknowledge that the bovine ear doesn't map cleanly onto the human model.

4. **Bovine ear geometry and tissue thickness.** Bovine ear cartilage is substantially thicker and differently structured than human ear cartilage. The 1987 New Zealand Veterinary Journal paper on ruminant auricular conchae (Rashid et al.) described the nerve and vessel arrangement in cattle, sheep, and deer — but provided no quantitative measurements of nerve depth, fibre density, or tissue impedance. The ABVN in cattle may sit deeper than the 1–1.5 mm gap seen in humans, requiring higher amplitudes that may cause pain or tissue damage.

5. **Effect size and clinical relevance.** The mastitis paper showed a significant reduction in QSCC on days 2, 4, and 6 post-treatment. The absolute magnitude of this reduction and its biological relevance for BRD-type inflammation (a systemically distinct condition involving lung-targeted pathogens and a different cytokine profile) has not been established.

6. **Ear tag position ≠ optimal ABVN stimulation site.** Standard ear tags are positioned in the centre of the ear for practical reasons (tissue thickness, attachment security). This may or may not correspond to the location of highest ABVN fibre density in cattle. The mastitis paper used ear tag position 10 (a bovine auricular acupuncture point) based on the Kothbauer bovine ear chart — a system developed from traditional veterinary acupuncture, not from anatomical nerve mapping.

### 3.2 The Honest Ranking of Evidence

| Claim | Evidence quality | Verdict |
|-------|-----------------|---------|
| Vagal stimulation suppresses inflammation via cholinergic anti-inflammatory pathway | Strong (FDA-validated in humans, SetPoint PMA 2025) | Robust |
| ABVN stimulation activates cholinergic anti-inflammatory pathway in humans | Strong (multiple RCTs, mechanism confirmed with alpha7nAChR antagonist) | Robust |
| Bovine ABVN exists and is accessible at the ear tag region | Weak (one anatomy paper 1987, one procaine injection study 2022) | Suggestive only |
| Electrical stimulation of bovine ABVN produces anti-inflammatory effect | **Zero evidence** | Unproven |
| Human taVNS parameters translate to cattle | **Zero evidence** | Assumed, not established |
| BRD morbidity reduced by auricular VNS in cattle | **Zero evidence** | Entirely speculative |
| Dark cutting prevented by auricular VNS in cattle | **Zero evidence** | Entirely speculative |

> **The ear tag is a well-reasoned hypothesis supported by mechanism analogies and one suggestive (but chemically different) bovine study. It is not supported by direct evidence for the specific application.**

This is the honest starting position. The scientific case for funding Experiment 1 is reasonable. The scientific case for claiming efficacy is not yet there.

---

## 4. The Full Data Gap Map

### 4.1 Gaps Specific to V1 (Ear Tag / Auricular Approach)

| Gap | Severity | Path to resolution | Cost estimate |
|-----|----------|--------------------|---------------|
| Bovine ABVN fibre density and myelination at ear | **Blocking for efficacy claims** | Histology: abattoir ear tissue, anti-neurofilament IHC, confocal imaging. 4–6 weeks. | ~$15k |
| Bovine ear tissue impedance vs. human | **Blocking for parameter selection** | Ex vivo impedance spectroscopy (1 Hz–100 kHz) through ear tissue layers. Days. | ~$5k |
| Whether electrical stimulation recruits bovine ABVN at practical amplitudes | **Blocking for all efficacy** | Dose titration in calves: heart rate change as surrogate for NTS activation (same validation used in human taVNS). 2–3 months. | ~$75k |
| Bovine auricular anatomy mapping (ABVN location relative to ear tag) | **Important but not immediately blocking** | Dissection + histological cross-sectioning of bovine concha. Rashid et al. 1987 provides partial roadmap. | ~$20k |
| Anti-inflammatory effect magnitude via bovine auricular electrical stimulation | **Blocking for BRD claim** | LPS challenge model in calves, active vs sham, measure cytokine panel. 6–12 months. | ~$200k |
| BRD morbidity reduction in field conditions | **Blocking for commercial claim** | Randomised pen trial, 200 cattle, 150-day finishing period. | ~$750k |
| Dark cutting prevention efficacy | **Blocking for that specific claim** | Cortisol measurement + muscle pH study under simulated transport stress. | ~$150k |

### 4.2 Gaps Specific to V2a (Poll/Parotid Injectrode)

| Gap | Severity | Path to resolution | Cost estimate |
|-----|----------|--------------------|---------------|
| Bovine vagus morphometry at juguloparotid level | **Blocking before safe deployment** | Abattoir tissue: Masson's trichrome + anti-claudin-1 IHC, digital morphometry. Pelot et al. 2020 protocol. 3 months. | ~$75k |
| Safe stimulation parameters at this level | **Blocking** | In vivo safety titration with continuous cardiac and GI monitoring. | ~$150k |
| Injectrode not yet commercial product | **Time constraint** | Neuronoff Inc. commercialisation timeline. Not in team's control. | — |

### 4.3 Gaps That Cannot Be Resolved at the Hackathon

None of these gaps can be closed in 48 hours. What can be done is:
- Characterise exactly how big the gaps are (species morphometry visualisation)
- Show the simulation work that would guide the experiments that close them
- Demonstrate understanding of what must be true for the device to work
- Build the economic case that justifies funding the experiments

---

## 5. Delivery Approach Comparison

Eight variables evaluated across three approaches.

| Variable | V1 — Ear tag (ABVN) | V2a — Poll/parotid Injectrode | V2b — Mid-cervical cuff |
|----------|--------------------|-----------------------------|------------------------|
| **Method / material** | ✅ Resolved. Surface electrode on tag inner face. Standard conductive materials. ISO 10993 electrode coating only. | ⚠️ Conditional. Injectrode: silicone + Ag nanoparticles at 65 wt%. Pig-validated. ISO 10993 in bovine tissue needed. | ⚠️ Conditional. Pt-Ir cuff — established material. Same ISO 10993 requirement. |
| **Surgery / injection** | ✅ Resolved. Standard ear tag applicator. 5 seconds. Zero labour cost. | ⚠️ Conditional. Ultrasound-guided percutaneous needle. 5–10 min by trained technician. $20–40/head labour. On-site ultrasound needed. | ❌ Blocking. Surgical dissection through carotid sheath. Sedation, sterile field, vet required. $80–220/head. Economically non-viable. |
| **Target area** | ⚠️ Conditional. ABVN: afferent only. Drives NTS brainstem reflex. Bovine anatomy not quantified. Procaine study is only cattle evidence. | ⚠️ Conditional. Main vagal trunk below jugular ganglion. Both afferent and efferent. Full cervical potency. Morphometry needed. | ❌ Blocking. Mid-cervical trunk. GI motor efferents fully present. Full organotopic map required before safe deployment. |
| **Edible region?** | ✅ Resolved. Ear entirely discarded at slaughter. USDA explicitly excludes ear from meat definition. | ✅ Resolved. Head removed entirely at first slaughter cut. Parotid/poll is head tissue — discarded. | ❌ Blocking. Mid-cervical tissue enters ground beef. Novel regulatory negotiation required. |
| **FDA / regulatory** | ✅ Resolved. No CVM pre-market approval. ISO 10993 electrode only. Analogous to Revalor ear implant. Budget ~$200–500k. | ⚠️ Conditional. Head placement sidesteps food additive concern. ISO 10993 for Injectrode polymer. Pre-submission meeting with CVM. Budget ~$200–500k. | ❌ Blocking. FDA CVM + FSIS + possibly CVB. Zero precedent for active therapeutic implant in edible-tissue region. Budget $2–10M, 2–4 years. |
| **Nerve mapping needed** | ⚠️ Needed but not launch-blocking. Bovine ABVN not quantified. Ear tag position anatomically fixed. Systematic characterisation is priority research, not hard prerequisite. | ❌ Blocking before safe use. Bovine vagus morphometry at juguloparotid level absent. 3-month abattoir study resolves this. Ultrasound placement partially compensates. | ❌ Blocking. Full fascicular organotopic map. Must locate GI motor efferents. 12–24 months, multiple labs. |
| **Off-target risks** | ✅ Low. ABVN is afferent sensory only. No motor efferents to forestomach. Bloat risk essentially zero. Worst case: local skin irritation. | ⚠️ Manageable. Juguloparotid level is above GI motor efferent branching point. Primary risk: cardiac (bradycardia). Monitorable and reversible. Safety titration required. | ❌ High. Mid-cervical level: GI motor efferents present. Unselective stimulation → Hoflund syndrome (rumen stasis, bloat, potential death). Non-negotiable safety prerequisite: fascicular selectivity. |
| **Cost per head** | ✅ Viable. BOM $10–24, placement ~$0. Net margin $5–39 conservative. | ⚠️ Tight. BOM $20–40, placement $20–40. Total $40–80 vs $29–63 value. Viable at scale. | ❌ Not viable. Surgery $80–220. Total $110–280 vs $29–63 value. Negative margin in most scenarios. |

**Conclusion:** V2b (mid-cervical) is not a viable commercial product on any near-term timeline. It is research infrastructure. V1 (ear tag) is the right first device — low risk, lowest cost, zero edible tissue concern — but carries the most scientific uncertainty about whether it actually works electrically. V2a (poll/parotid Injectrode) is the right V2 device once the V1 mechanism is validated and Injectrode matures commercially.

---

## 6. V2a — Poll/Parotid Injectrode

### 6.1 The Injectrode

Published: Trevathan, Ludwig et al., *Advanced Healthcare Materials*, 2019. Commercialised through Neuronoff Inc., currently in clinical trials for DRG stimulation.

**Material:** Silicone base + silver nanoparticles at 65 wt% (the percolation threshold). Liquid before injection, cures in vivo around the nerve.

**Key properties:**
- Young's Modulus <100 kPa (orders of magnitude less stiff than conventional cuffs — matches tissue mechanics)
- Stretchable 150–200% without loss of conductivity
- Impedance 360 Ω vs. 1350 Ω for LivaNova clinical cuff (lower = better power efficiency)
- Validated in pig vagus nerve: heart rate changes produced on dose-titration vs. LivaNova cuff
- Required higher current than LivaNova for equivalent response — due to larger electrode contact geometry, not poorer conductivity. Soluble engineering issue.
- FDA preclinical testing completed

### 6.2 Why Poll/Parotid Is the Right Anatomical Target

The cervical vagus is most superficial just below the jugular ganglion in the retromandibular/parotid fossa — approximately 2–3 cm deep, covered by the parotid salivary gland. Advantages:

- **Shallowest accessible point:** compared to mid-cervical depth of 4–6 cm through muscle layers
- **Excellent ultrasound landmark:** internal jugular vein runs immediately adjacent, easily visualised; standard jugular venipuncture site in cattle — every large animal vet can find it in seconds
- **Non-edible tissue:** entire head (including parotid/poll region) removed at first slaughter cut and discarded
- **Above GI motor branching:** at the juguloparotid level, the vagus is above the point where GI motor efferents to the rumen and reticulum diverge caudally. Primary off-target risk shifts from Hoflund syndrome (bloat) to cardiac (bradycardia) — a far more manageable and reversible effect

### 6.3 Selectivity: Why Injectrode Achieves Sufficient Precision

Two distinct selectivity problems must be separated:

**Fibre-type selectivity** (achievable with Injectrode in current bipolar form): activating small-diameter B-fibres (anti-inflammatory efferents) while avoiding Aα motor fibres (the Hoflund risk). This is parameter-based — using the strength-duration curve difference between fibre types. The PyFibers simulation defines this safe operating window. Conformal, low-impedance contact enables precise delivery. No spatial electrode steering required.

**Organ selectivity** (not required for this application): spatially targeting the splenic immune fascicle specifically. The Injectrode in bipolar form cannot do this. However, the anti-inflammatory pathway works via broad afferent activation triggering a brainstem reflex — unmyelinated C-fibre afferents are distributed across all fascicles, not concentrated in a specific organ-targeted group. You are driving a central reflex arc, not targeting a peripheral organ directly.

> **Summary:** With bovine vagus morphometry at the juguloparotid level, you know where to inject. With stimulation parameters from the PyFibers simulation, you know what to deliver. The Injectrode's conformal contact means spatial steering is not needed — you are driving a brainstem reflex, not targeting a specific fascicle. The Hoflund risk is managed through fibre-type selectivity, not organ selectivity.

### 6.4 Procedure in Practice

1. Animal enters chute during normal processing
2. Technician applies ultrasound probe to parotid region behind jaw
3. Identifies vagal trunk adjacent to jugular vein (~2–3 cm depth)
4. Inserts needle percutaneously to perivagal fascial plane
5. Injects Injectrode polymer — flows conformally, cures in ~5 minutes
6. Places small IPG subcutaneously in poll region with second needle pass
7. Attaches external collar/patch providing wireless power

**Total estimated procedure time:** 5–10 minutes. No surgical field, no sterile drape, no sedation beyond chute restraint.

**At slaughter:** head removal cut made at standard location. Entire device (electrode, lead, IPG) removed with the head. Nothing enters the carcass.

---

## 7. Device Specification — V1 Ear Tag

### 7.1 Hardware

| Component | Specification | BOM at 100k units |
|-----------|--------------|-------------------|
| Microcontroller | Nordic nRF52840. BLE 5.0, 64 MHz ARM Cortex-M4, 1 MB flash | $1.50–2.50 |
| Battery | Primary lithium cell (CR2450 equivalent), 620 mAh. Non-rechargeable for 150-day finishing period | $0.50–2.00 |
| Electrode array | Two platinum or silver-coated contacts on inner face. Biphasic charge-balanced delivery. Hydrogel coupling layer. | $3.00–8.00 |
| PCB and passives | Custom rigid PCB, stimulation driver IC, filtering capacitors | $1.00–2.50 |
| Encapsulation | Food-grade silicone overmould. ISO 10993 compliant. UV stabilised. | $2.00–5.00 |
| Assembly and test | Automated SMT. Functional test: stimulation output verification, BLE connectivity | $2.00–4.00 |
| **Total BOM** | | **$10–24** |

### 7.2 Stimulation Protocols

Two programmable protocols, preloaded at manufacture and triggered by real-time clock:

| Protocol | When | Parameters | Target |
|----------|------|-----------|--------|
| Anti-inflammatory | Weeks 1–4 post-arrival (BRD high-risk window) | 15 Hz, 250–500 µs pulse, biphasic, charge-balanced, sub-4 mA **(pending bovine dose titration — these are human-derived starting estimates only)** | Suppress cytokine cascade during immune stress |
| Calming / autonomic | 48–72 hours before scheduled slaughter | 10 Hz, 500 µs pulse, biphasic, charge-balanced | Shift autonomic balance parasympathetic. Preserve glycogen. Prevent dark cutting. |

> **These parameters are educated starting estimates derived from human taVNS literature. They have not been validated in cattle and may require substantial revision after Experiment 2 (dose titration in calves).**

### 7.3 Unit Economics

| Value stream | Per head (conservative) |
|-------------|------------------------|
| BRD reduction (25% relative morbidity) | $4–15 |
| Dark cutting prevention | $0.75–3 |
| Feed efficiency (3% FCR improvement, moderate evidence) | $19–25 |
| Antibiotic reduction premium | $5–20 |
| **Total value** | **$29–63** |

| Cost stream | Per head |
|------------|----------|
| Device BOM at 100k units | $10–24 |
| Placement labor | ~$0 |
| **Net margin** | **$5–39 conservative** |

---

## 8. Validation Experiment Sequence

These experiments must happen in order. Each gates the next. None can be skipped.

### Experiment 1 — Bovine ear tissue characterisation
**Timeline:** Months 1–2  
**Cost:** ~$20k  
**What:** Collect bovine ear samples from abattoir. Measure impedance spectrum (1 Hz–100 kHz) through different tissue layers at the ear tag insertion zone. Map ABVN histologically with anti-neurofilament antibody and confocal imaging. Compare tissue depth to human 1–1.5 mm reference.  
**Gates:** Determines whether electrical stimulation at practical amplitudes (sub-4 mA) can reach the ABVN through bovine ear tissue. If impedance is prohibitively high or nerve depth is too great, the ear tag concept may need fundamental redesign or replacement with an intranasal/tragal approach.

### Experiment 2 — Dose titration in calves
**Timeline:** Months 3–6  
**Cost:** ~$75k  
**What:** Instrumented ear tag with variable parameters (frequency, pulse width, amplitude). Primary outcome: heart rate change (bradycardia) as surrogate for NTS activation — identical validation approach used in human taVNS trials. Secondary: tolerability, local tissue response, adverse events.  
**Gates:** Identifies the effective parameter window for bovine ABVN electrical stimulation. If no heart rate response is observed at any tested parameter within the safe range, the fundamental premise of auricular electrical stimulation in cattle is not supported.

### Experiment 3 — LPS inflammation model
**Timeline:** Months 6–12  
**Cost:** ~$200k  
**What:** Calves challenged with BRD-relevant endotoxin (LPS). Active vs. sham ear tag stimulation using parameters from Experiment 2. Measure cytokine panel (TNF-alpha, IL-1beta, IL-6) at 2h, 6h, 24h. Include alpha7nAChR antagonist group to confirm mechanism.  
**Gates:** First direct evidence that bovine auricular electrical stimulation suppresses the inflammatory response relevant to BRD. Must show statistically significant, biologically meaningful cytokine reduction vs. sham.

### Experiment 4 — Field pen trial
**Timeline:** Months 12–24  
**Cost:** ~$750k  
**What:** Randomised pen trial. 200 feedlot cattle across 2 matched pens, active vs. sham ear tags. Track BRD morbidity/mortality over 150-day finishing period. Secondary outcomes: dark cutting incidence, packer grading, growth performance. University partnership required (KSU, TAMU, or CSU).  
**Gates:** Commercial proof-of-concept data. This is what you take to feedlot operators and investors.

**Total to commercial proof of concept: ~$1M, 18–24 months.**

---

## 9. Simulation Work for Hackathon

### 9.1 Tools

| Tool | Purpose | Setup time | Key requirement |
|------|---------|-----------|----------------|
| PyFibers (`pip install pyfibers`) | Fibre activation thresholds, strength-duration curves, safe parameter window | 10 minutes | Python, NEURON (free) |
| axonml (Zenodo 10.5281/zenodo.12752386) | GPU-accelerated population selectivity maps (~90,000x speedup) | 30–60 minutes | NVIDIA GPU, CUDA 11.7+, PyTorch 2.0+ |
| NRV framework (Docker) | Full FEM pipeline, no COMSOL | 1 hour | Docker, FEniCSx+Gmsh bundled |
| ASCENT (wmglab-duke/ascent) | Gold standard + Mock Morphology Generator | 4–8 hours | COMSOL or o2S2PARC (free via osparc.io) |

### 9.2 Demo Deliverables — Priority Order

**Demo 1 (Hours 0–4): The species morphometry gap.**
Four-panel figure: human vagus cross-section (SPARC portal), pig (~47 fascicles), sheep (~6 fascicles), **empty "BOVINE: ?" panel**. Also add a fifth panel showing bovine ear cross-section with "ABVN location: unknown." This is the IP wedge made visual. The data gap that whoever fills first owns the electrode design space.

**Demo 2 (Hours 4–12): Fibre selectivity simulation.**
PyFibers with analytical point-source potentials on a synthetic bovine vagus cross-section scaled from pig morphometry. Activation thresholds across fibre types: Aα motor (danger zone), Aβ sensory, B autonomic (target), C unmyelinated. Output: heatmap showing safe operating window between B-fibre activation and Aα activation. Include a deliberate "wrong parameters" failure case showing Aα activation — demonstrates understanding of the safety constraint.

**Demo 3 (Hours 12–18): Strength-duration curves.**
For each fibre type, show how activation threshold varies with pulse width. Identify the optimal pulse width for B-fibre selectivity. Annotate with the human taVNS parameter range and the question mark: *"Do these parameters translate to cattle? This is Experiment 2."*

**Demo 4 (Hours 18–22): Unit economics calculator.**
Interactive widget. Inputs: feed price, BRD incidence, dark cutting incidence, carbon credit price, device cost. Outputs: per-head ROI and payback. Comparison vs. Bovaer, ArkeaBio, seaweed.

**Demo 5 (Hours 22–30): Integrated dashboard.**
Streamlit or Jupyter app combining morphometry panel, selectivity heatmap, strength-duration curves, and economics calculator. Add bovine auricular anatomy diagram showing ABVN location relative to standard ear tag position.

---

## 10. Competitive Landscape

### 10.1 Direct Competitors

**None.** No company, academic group, or funded research programme anywhere in the world is applying bioelectronic medicine or implantable neurostimulation to livestock for production enhancement. USDA NIFA has no bioelectronic livestock projects. DARPA's ElectRx focused entirely on human applications. This white space is confirmed by exhaustive search.

### 10.2 Adjacent Players

| Company | KPI addressed | Limitation | Our differentiation |
|---------|-------------|-----------|---------------------|
| Bovaer (DSM-Firmenich/Elanco) | Methane only | ~30% reduction, dairy only, daily TMR mixing, ~$75/head, cannot reach pasture cattle | Multi-KPI. Works on all cattle. |
| Rumin8 | Methane only | 86–95% claimed, ~2027 launch, water dosing still requires daily infrastructure | Available before 2027. Multi-KPI. |
| ArkeaBio | Methane only | 10–15% reduction, vaccine mechanism, years from commercial | Larger effect, sooner, more KPIs. |
| Halter ($1B valuation 2025) | Monitoring/behaviour only | GPS collar, no therapeutic intervention | Therapeutic not just monitoring. Complementary. |
| smaXtec / Allflex | Health monitoring | Rumen bolus sensors, diagnostic only | Treat, not just detect. |
| Revalor / Synovex | Growth only | Welfare-negative framing, single mechanism | Welfare-positive, multi-KPI. Same placement infrastructure. |

### 10.3 The Data Flywheel

At 1% US market penetration (~100k cattle): continuous vagal nerve recording logs → world's current chronic vagal dataset across all species is a few thousand animal-hours → **1,000x the world's dataset within 3 years of commercial launch.**

Uses: product optimisation; licensing to human VNS companies (SetPoint, LivaNova, Inspire Medical) whose devices would benefit from larger vagal response datasets; research dataset licensing to pharma.

> **Reframe for SF/NYC investor audiences:** "We are not a cow startup. We are an AI company that uses cows as the data source."

---

## 11. Messaging Framework

### 11.1 Core Pitch

> "We made the ear tag do something useful."

### 11.2 What to Say / Not Say

| Say this | Not this |
|----------|---------|
| "We made the ear tag do something useful" | "Bioelectronic medicine for livestock" |
| "The same thing good stockmanship does, but automated and measurable" | "Neural implant" |
| "An alternative to prophylactic antibiotics, backed by FDA-validated human science" | "Breakthrough neurotech" |
| "Building on 60 years of Revalor ear implant practice" | "We are applying SetPoint's VNS to cows" |
| "Automated stockmanship" | "Revolutionary neural modulation platform" |
| "Welfare + profit — stress reduction before slaughter improves meat quality" | "Neural enhancement for production efficiency" |

### 11.3 The Three-Minute Pitch Video Structure

- **0:00–0:20 — Hook.** One of these three options:
  - *Option A (economic):* "Last year, American beef farmers left $1.1 billion on the table — from sick animals and stressed ones. We know exactly why both happen. We built a $15 device that addresses both."
  - *Option B (absurdity):* "There are 87 million cattle in America. Every single one already gets an ear tag. That ear tag does one thing: it holds a number. We made it do something useful."
  - *Option C (contrast):* "In August 2025, the FDA approved a device that reduces inflammation by stimulating a nerve in the neck. It costs $30,000 and it's for humans. The same nerve runs through the ear of every cow in America. We put the relevant part in a $15 ear tag."

- **0:20–0:45 — The problem made real.** Two numbers, two sentences. BRD: $1B/year. Dark cutting: $288M/year.

- **0:45–1:00 — The insight.** "The vagus nerve regulates both immune response and stress. It has a branch in the ear. We stimulate it." Pause two seconds.

- **1:00–1:20 — Why now.** SetPoint FDA approval (mechanism validated). Bovine mastitis study (ABVN accessible in cattle). Electronics miniaturisation. Three convergences.

- **1:20–1:50 — Show the simulation.** Fibre selectivity heatmap. Species morphometry gap panel. The empty bovine panel is the IP moat.

- **1:50–2:10 — The numbers.** Conservative value stack. $29–63/head. $15 device cost. Zero placement labour.

- **2:10–2:25 — Format is the message.** Same applicator gun. Five seconds per animal. The farmer changes nothing.

- **2:25–2:40 — The data flywheel.** 1,000x the world's vagal dataset. "We're not a cow startup."

- **2:40–3:00 — The ask.** V1 ear tag validates mechanism. V2 poll Injectrode maximises value. The experiment sequence is fundable. The white space is total.

### 11.4 The Comparable Company

**Loyal** (dog longevity): serious science (mTOR, GH/IGF-1 pathways targeting the hallmarks of large-dog aging), pitched as "more years with your dog." The mechanism is the product. The outcome is the pitch. Same playbook: sophisticated mechanism, accessible emotional outcome, farmer/owner as the advocate, not the engineer.

---

## 12. Farmer Validation Calls

**Goal:** Answer three questions — is the problem real and expensive, does ear tag format feel approachable, who do they trust?

**Opening:**
> "Hi, I'm part of a student team at a neurotech hackathon working on a device concept for feedlot health. We're not selling anything — we want 10 minutes to understand whether the problem we're trying to solve is actually painful from your perspective."

**Questions:**
1. What percentage of your placed cattle do you treat for BRD per year, and what does a treatment episode actually cost you all-in — drugs, labor, and the performance hit?
2. Have you had a dark-cutting problem? What was the packer discount and what caused it?
3. You already tag every animal's ear. If a modified ear tag could reduce your BRD treatment rate by 25%, what would that be worth per head, and what would make you sceptical?
4. When you see something new for feedlot health, who do you trust to tell you it works — university trial, neighbour producer, your vet, or your packer?
5. What would a pilot look like that you'd actually agree to run?

**Listen for:** Specific dollar amounts validating dossier numbers. Whether dark cutting is real to their specific operation. Whether "ear tag format" immediately reduces resistance. The trust hierarchy — because that person is your pilot partner. Anything that kills the idea.

**Contacts:**
- Texas Cattle Feeders Association: 806-358-3681
- Kansas Livestock Association: 785-273-5115
- Nebraska Cattlemen: 402-475-2333
- County extension beef cattle specialists via tamu.edu/extension or ksu.edu/extension
- LinkedIn: search "feedlot veterinarian" or "bovine veterinarian"
- Reddit: r/Ranching, r/Farming

---

## 13. Academic Contacts

| Contact | Institution | Relevance | Contact |
|---------|------------|-----------|---------|
| **Stavros Zanos** | Feinstein Institutes | HIGHEST PRIORITY. Large-animal (pig) VNS, fascicular selectivity, organ-selective stimulation, imec ASIC collaboration. $3M NIH grant. | szanos@northwell.edu |
| **Nicole Pelot** | Duke University | ASCENT pipeline, cross-species vagus morphometry, SPARC portal. Essential for bovine morphometry study design. | nikki.pelot@duke.edu |
| **Kip Ludwig** | University of Wisconsin-Madison | Injectrode inventor, pig vagus organotopy, NIH SPARC architect. The person to call about minimally invasive bovine VNS. | Via UW-Madison BME |
| UCL Centre for Nerve Engineering | University College London | VNS in pigs and sheep, EIT-based real-time fascicular imaging. Closest large-animal VNS data to cattle. | David Holder, Kirill Aristovich |
| Bionics Institute / UNSW Australia | Melbourne / Sydney | Chronic VNS in awake freely-moving sheep, 3 months stable. Best chronic large-animal VNS precedent available. | Payne et al. |

---

## 14. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Bovine ABVN not electrically accessible at practical amplitudes through ear tissue** | Medium | Critical | This is what Experiment 1 tests. If tissue impedance is too high, redesign electrode or move to tragal/ear canal placement. V2a poll Injectrode is the fallback if auricular approach fails entirely. |
| **15 Hz / human parameters don't recruit bovine ABVN fibres** | Medium | High | Experiment 2 (dose titration) establishes the actual effective window. Parameters may be significantly different from human. Design ear tag electronics with wide parameter adjustment range. |
| **Anti-inflammatory effect via auricular route insufficient for BRD** | Medium | High | Establishes the case for V2a (poll Injectrode) which provides full cervical trunk potency. V1 ear tag then becomes a welfare/stress device and dark cutting prevention tool rather than the BRD primary. |
| **Bovine auricular anatomy doesn't map to human ABVN location** | Medium | High | The mastitis paper's own authors flagged this risk (Artmeier and König 1978). Experiment 1 histology will determine actual nerve location in bovine ear. Electrode array can be repositioned based on findings. |
| **Welfare perception — rBST precedent** | Medium | High | Lead with antibiotic replacement framing from day one. Never say "neural implant." Engage welfare scientists pre-launch. Partner with certified humane programmes. |
| **FDA CVM food additive classification for V1 ear tag** | Low | Low | Ear is entirely discarded at slaughter. USDA explicitly excludes ear tissue from meat definition. Pre-submission CVM meeting in Year 1 to confirm pathway formally. |
| **Cardiac adverse effects from V2a poll Injectrode** | Low | High | Safety titration study with continuous cardiac monitoring before routine deployment. Start at sub-therapeutic amplitudes. Bradycardia is monitorable and reversible; far less severe than Hoflund syndrome. |
| **Injectrode not commercially available in time for V2a** | Low | Medium | V1 ear tag generates revenue and data independently of Injectrode. V2a timeline allows 3–5 years for Neuronoff to mature. Alternative: collab with Ludwig lab for research-grade deployment. |
| **Competition emerges** | Low | High | White space currently confirmed as total. Bovine morphometry dataset and regulatory precedent create durable first-mover moat once established. |

---

## 15. Development Roadmap

| Phase | Timeline | Milestone | Deliverable |
|-------|---------|-----------|------------|
| Founding science | Months 1–2 | Bovine ear tissue characterisation | Impedance profile, ABVN histology, nerve depth vs. human. Informs electrode design. |
| Founding science | Months 3–6 | Dose titration in calves | Effective electrical parameter range for bovine ABVN. V1 prototype in-animal. |
| Founding science (parallel) | Months 1–4 | Bovine vagus morphometry, juguloparotid | First-ever quantified bovine vagus dataset. IP moat. ~$75k. |
| V1 commercial science | Months 6–12 | LPS inflammation model | Proof of anti-inflammatory effect via bovine auricular electrical stimulation. |
| V1 commercial science | Months 12–24 | Field pen trial (200 cattle) | BRD morbidity, dark cutting incidence, growth performance vs. sham. Commercial proof-of-concept. |
| V1 commercial | Year 2–3 | Pilot feedlot partnerships | 3–5 feedlot operators. Device supply. Farmer testimonials. Revenue begins. |
| V2a science | Year 1–2 (parallel) | Juguloparotid safety titration | Safe parameter range for poll Injectrode. Cardiac monitoring. |
| V2a launch | Year 3–4 | Poll/parotid Injectrode pilot | Higher potency cervical VNS. Non-edible placement. Full value stack. |
| Data platform | Year 3+ | 1% market penetration (~100k cattle) | 1,000x world's vagal dataset. Data licensing. AI company reframe. |

---

*Bovine Auricular VNS Technical & Strategic Dossier | Bluesky Hackathon 2026*  
*This document presents the evidence base including its substantial gaps. The ear tag is a well-reasoned hypothesis. It is not yet a validated product.*
