import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { ShieldOff, FlaskConical, Thermometer, Pill, Users, ShieldCheck, DollarSign, Beaker, Cpu, Activity } from 'lucide-react'
import './App.css'

const TOTAL = 13

function Reveal({ children, delay = 0, y = 20 }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-40px' })
  return (
    <motion.div ref={ref} initial={{ opacity: 0, y }} animate={inView ? { opacity: 1, y: 0 } : {}} transition={{ duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] }}>
      {children}
    </motion.div>
  )
}

function ScaleIn({ children, delay = 0, className = '' }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-40px' })
  return (
    <motion.div ref={ref} className={className} initial={{ opacity: 0, scale: 0.7 }} animate={inView ? { opacity: 1, scale: 1 } : {}} transition={{ duration: 0.6, delay, ease: [0.34, 1.56, 0.64, 1] }}>
      {children}
    </motion.div>
  )
}

function SlideLogo() {
  return <img src="/logo.png" alt="BoVa" className="slide-logo" />
}

function Circles({ config }) {
  return config.map((c, i) => (
    <div key={i} className={`deco-circle ${c.type || 'solid'}`} style={{ width: c.size, height: c.size, top: c.top, bottom: c.bottom, left: c.left, right: c.right }} />
  ))
}

/* ═══ S1 — HOOK ═══ */
function S1() {
  return (
    <div className="slide bg-img bg-clear" id="slide-0">
      <SlideLogo />
      <Circles config={[
        { size: 500, top: '-15%', right: '-10%', type: 'ring' },
        { size: 200, bottom: '10%', left: '5%', type: 'ring' },
      ]} />
      <div className="slide-inner">
        <div className="hero-wrap">
          <div className="hero-left">
            <Reveal><img src="/logo.png" alt="BoVa" className="logo" /></Reveal>
            <Reveal delay={0.1}><div className="hero-tagline">$1.3 billion lost every year.</div></Reveal>
            <Reveal delay={0.2}><div className="hero-tagline-sub">Same nerve. Different animal.</div></Reveal>
          </div>
          <div className="hero-right">
            <ScaleIn delay={0.3}>
              <div className="hero-circle-outer">
                <div className="hero-circle-inner">
                  <div className="hero-number">$1.3B</div>
                  <div className="hero-number-label">Lost yearly</div>
                </div>
              </div>
            </ScaleIn>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ═══ S2 — FARMING HASN'T CHANGED ═══ */
function S2() {
  return (
    <div className="slide bg-img bg-cattle" id="slide-1">
      <SlideLogo />
      <Circles config={[
        { size: 400, top: '-10%', left: '-8%', type: 'ring' },
        { size: 160, bottom: '15%', right: '8%', type: 'ring' },
      ]} />
      <div className="slide-inner" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Reveal><div className="label">The Problem</div></Reveal>
        <Reveal delay={0.1}>
          <div className="title" style={{ textAlign: 'center' }}>Farming hasn't changed.</div>
          <div className="subtitle" style={{ textAlign: 'center', margin: '0 auto' }}>
            Cows are farmed the same way we've done it for thousands of years.
          </div>
        </Reveal>
        <div className="context-grid">
          {[
            { icon: <ShieldOff size={24} />, text: 'Consumers reject antibiotics, hormones, GMOs', delay: 0.2 },
            { icon: <FlaskConical size={24} />, text: 'Lab-grown meat is 20 years away', delay: 0.3 },
            { icon: <Thermometer size={24} />, text: 'Methane emissions still unsolved', delay: 0.4 },
            { icon: <Pill size={24} />, text: 'Prophylactic antibiotics under regulatory pressure', delay: 0.5 },
          ].map((item, i) => (
            <ScaleIn key={i} delay={item.delay} className="context-card">
              <div className="context-icon">{item.icon}</div>
              <div className="context-text">{item.text}</div>
            </ScaleIn>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ═══ S3 — BRD ═══ */
function S3() {
  return (
    <div className="slide" id="slide-2">
      <SlideLogo />
      <Circles config={[
        { size: 350, bottom: '-12%', right: '-8%', type: 'solid' },
        { size: 100, top: '30%', right: '5%', type: 'ring' },
      ]} />
      <div className="slide-inner">
        <Reveal><div className="problem-pill red">Problem 1</div></Reveal>
        <Reveal delay={0.1}>
          <div className="title">Bovine Respiratory Disease</div>
          <div className="subtitle">The #1 disease cost in US beef. Current answer: mass antibiotics.</div>
        </Reveal>
        <div className="stat-circles" style={{ marginTop: 40, justifyContent: 'flex-start' }}>
          {[
            { num: '$1B', label: 'Annual cost', delay: 0.2 },
            { num: '16.2%', label: 'Cattle affected', delay: 0.3 },
            { num: '$80-200', label: 'True cost/case', delay: 0.4 },
            { num: '97%', label: 'Feedlots hit', delay: 0.5 },
          ].map((s) => (
            <ScaleIn key={s.label} delay={s.delay} className="stat-circle">
              <div className="stat-circle-ring red"><div className="stat-num red">{s.num}</div></div>
              <div className="stat-unit">{s.label}</div>
            </ScaleIn>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ═══ S4 — DARK CUTTING ═══ */
function S4() {
  return (
    <div className="slide sage" id="slide-3">
      <SlideLogo />
      <Circles config={[
        { size: 300, top: '5%', right: '-5%', type: 'ring' },
        { size: 140, bottom: '10%', left: '5%', type: 'solid' },
      ]} />
      <div className="slide-inner">
        <Reveal><div className="problem-pill red">Problem 2</div></Reveal>
        <Reveal delay={0.1}>
          <div className="title">Dark Cutting Beef</div>
          <div className="subtitle">Pre-slaughter stress destroys meat quality. $288M/year in packer discounts.</div>
        </Reveal>
        <div className="stat-circles" style={{ marginTop: 40, justifyContent: 'flex-start' }}>
          {[
            { num: '$288M', label: 'Annual losses', delay: 0.2 },
            { num: '1.8%', label: 'Incidence', delay: 0.3 },
            { num: '-$38.75', label: 'Per cwt discount', delay: 0.4 },
          ].map((s) => (
            <ScaleIn key={s.label} delay={s.delay} className="stat-circle">
              <div className="stat-circle-ring red"><div className="stat-num red">{s.num}</div></div>
              <div className="stat-unit">{s.label}</div>
            </ScaleIn>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ═══ S5 — GUT MOTILITY ═══ */
function S5() {
  return (
    <div className="slide" id="slide-4">
      <SlideLogo />
      <Circles config={[
        { size: 400, top: '-10%', left: '-8%', type: 'solid' },
        { size: 120, bottom: '20%', right: '10%', type: 'ring' },
      ]} />
      <div className="slide-inner">
        <Reveal><div className="problem-pill red">Problem 3</div></Reveal>
        <Reveal delay={0.1}>
          <div className="title">The cow is a meat factory.<br />The bottleneck is the gut.</div>
          <div className="subtitle">The most common surgery on cattle is the stomach window. VNS can modulate gut motility and improve feed-to-meat ratio.</div>
        </Reveal>
        <div className="stat-circles" style={{ marginTop: 40, justifyContent: 'flex-start' }}>
          <ScaleIn delay={0.3} className="stat-circle">
            <div className="stat-circle-ring green"><div className="stat-num green">$19-25</div></div>
            <div className="stat-unit">Value per head</div>
          </ScaleIn>
          <ScaleIn delay={0.4} className="stat-circle">
            <div className="stat-circle-ring green"><div className="stat-num green">3%</div></div>
            <div className="stat-unit">FCR improvement</div>
          </ScaleIn>
        </div>
      </div>
    </div>
  )
}

/* ═══ S6 — VNS IS PROVEN + TRL LADDER ═══ */
function S6() {
  return (
    <div className="slide bg-img bg-cattle compact" id="slide-5">
      <SlideLogo />
      <Circles config={[
        { size: 500, top: '-15%', right: '-10%', type: 'green-solid' },
        { size: 180, bottom: '10%', left: '8%', type: 'ring' },
      ]} />
      <div className="slide-inner">
        <div className="h-layout">
          <div className="h-layout-left">
            <Reveal><div className="label">The Technology</div></Reveal>
            <Reveal delay={0.1}>
              <div className="title">VNS is <span className="hi">50 years old</span>.<br />FDA-approved.</div>
              <div className="subtitle">We're the first to apply it to cattle.</div>
            </Reveal>
            <Reveal delay={0.2}>
              <div className="fda-badge" style={{ marginTop: 16 }}><div className="fda-dot" /><span>SetPoint Medical PMA — Aug 2025</span></div>
            </Reveal>
          </div>
          <div className="h-layout-right" style={{ flex: 1 }}>
        <Reveal delay={0.3}>
          <div className="trl-ladder" style={{ marginTop: 0 }}>
            <div className="trl-item beachhead">
              <div className="trl-circle s1">1</div>
              <div><div className="trl-title">Anti-inflammatory (BRD)</div></div>
              <div className="trl-tag high">HIGH TRL</div>
            </div>
            <div className="trl-item">
              <div className="trl-circle s2">2</div>
              <div><div className="trl-title">Pre-slaughter stress</div></div>
              <div className="trl-tag med">MED TRL</div>
            </div>
            <div className="trl-item">
              <div className="trl-circle s3">3</div>
              <div><div className="trl-title">Gut motility</div></div>
              <div className="trl-tag low">RESEARCH</div>
            </div>
          </div>
        </Reveal>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ═══ S7 — DEVICE + TECHNICAL WORK ═══ */
function S7() {
  return (
    <div className="slide compact" id="slide-6">
      <SlideLogo />
      <Circles config={[
        { size: 300, bottom: '-10%', right: '-5%', type: 'solid' },
        { size: 100, top: '15%', left: '5%', type: 'ring' },
      ]} />
      <div className="slide-inner">
        <div className="h-layout">
          <div className="h-layout-left">
            <Reveal><div className="label">The Device</div></Reveal>
            <Reveal delay={0.1}>
              <div className="title"><span className="hi">Cervical VNS</span>.<br />Needle-based. 15 min.</div>
              <div className="subtitle">Replicates an existing cattle surgery under local anaesthesia.</div>
            </Reveal>
            <Reveal delay={0.3}>
              <div className="device-pills" style={{ marginTop: 16 }}>
                <div className="device-pill"><strong>15 min</strong> procedure</div>
                <div className="device-pill"><strong>0</strong> food safety risk</div>
                <div className="device-pill"><strong>AFE</strong> neural recording</div>
              </div>
            </Reveal>
          </div>
          <div className="h-layout-right" style={{ flex: 1 }}>
            <Reveal delay={0.2}>
              <div className="device-grid" style={{ gridTemplateColumns: '1fr', gap: 10 }}>
                <div className="device-card">
                  <div className="pill">ELECTRODE</div>
                  <div className="device-card-title">Biocompatible nerve cuff — Imperial Green group</div>
                </div>
                <div className="device-card">
                  <div className="pill">STIMULATION</div>
                  <div className="device-card-title">MintNeuro ASIC — programmable protocols</div>
                </div>
                <div className="device-card">
                  <div className="pill">CLOSED LOOP</div>
                  <div className="device-card-title">Ultrasound imaging feedback</div>
                </div>
              </div>
            </Reveal>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ═══ S8 — WHITE SPACE ═══ */
function S8() {
  return (
    <div className="slide sage" id="slide-7">
      <SlideLogo />
      <Circles config={[
        { size: 350, top: '-10%', right: '-8%', type: 'green-solid' },
        { size: 150, bottom: '15%', left: '5%', type: 'ring' },
      ]} />
      <div className="slide-inner" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Reveal><div className="label">White Space</div></Reveal>
        <Reveal delay={0.1}>
          <div className="title" style={{ textAlign: 'center' }}><span className="hi">Zero</span> competition.</div>
        </Reveal>
        <Reveal delay={0.2}>
          <div className="table-wrap">
            <table className="cmp-table">
              <thead><tr><th>Species</th><th>Morphometry</th><th>VNS Trials</th><th>Devices</th></tr></thead>
              <tbody>
                <tr><td>Human</td><td style={{color:'var(--green)'}}>&#9679; Complete</td><td style={{color:'var(--green)'}}>1,000+</td><td style={{color:'var(--green)'}}>FDA approved</td></tr>
                <tr><td>Pig</td><td style={{color:'var(--green)'}}>&#9679; Complete</td><td style={{color:'var(--green)'}}>Organotopy mapped</td><td style={{color:'var(--text-muted)'}}>&#9675; None</td></tr>
                <tr><td>Sheep</td><td style={{color:'var(--green-light)'}}>&#9680; Partial</td><td style={{color:'var(--green)'}}>Chronic awake</td><td style={{color:'var(--text-muted)'}}>&#9675; None</td></tr>
                <tr className="hl-row"><td style={{color:'var(--green)'}}>Bovine</td><td style={{color:'var(--red)'}}>&#9675; None</td><td style={{color:'var(--red)'}}>&#9675; None</td><td style={{color:'var(--red)'}}>&#9675; None</td></tr>
              </tbody>
            </table>
          </div>
        </Reveal>
        <Reveal delay={0.35}>
          <div style={{ textAlign: 'center', marginTop: 28, fontSize: 16, fontWeight: 700 }}>
            First to generate bovine vagus morphometry <span className="hi">owns the design space</span>.
          </div>
        </Reveal>
      </div>
    </div>
  )
}

/* ═══ S9 — UNIT ECONOMICS ═══ */
function S9() {
  return (
    <div className="slide compact" id="slide-8">
      <SlideLogo />
      <Circles config={[
        { size: 400, top: '-10%', left: '-8%', type: 'solid' },
        { size: 120, bottom: '15%', right: '10%', type: 'ring' },
      ]} />
      <div className="slide-inner">
        <Reveal><div className="label">Unit Economics</div></Reveal>
        <Reveal delay={0.1}>
          <div className="title"><span className="hi">$29-63</span> value per head.</div>
        </Reveal>
        <Reveal delay={0.2}>
          <div className="econ-layout">
            <div className="econ-bars">
              {[
                { label: 'Feed efficiency', v: '$19-25', w: '100%', delay: 0.3 },
                { label: 'Antibiotic premium', v: '$5-20', w: '75%', delay: 0.4 },
                { label: 'BRD reduction', v: '$4-15', w: '55%', delay: 0.5 },
                { label: 'Dark cutting', v: '$1-3', w: '20%', delay: 0.6 },
              ].map((b) => (
                <div className="econ-bar-row" key={b.label}>
                  <div className="econ-bar-label">{b.label}</div>
                  <div className="econ-bar-track">
                    <motion.div className="econ-bar-fill" initial={{ width: 0 }} whileInView={{ width: b.w }} viewport={{ once: true }} transition={{ duration: 1, delay: b.delay, ease: [0.16, 1, 0.3, 1] }}>
                      <span className="econ-bar-val">{b.v}</span>
                    </motion.div>
                  </div>
                </div>
              ))}
            </div>
            <div className="econ-summary">
              <ScaleIn delay={0.5}>
                <div className="econ-circle-big">
                  <div className="econ-big-num">$5-39</div>
                  <div className="econ-big-label">Net margin / head</div>
                </div>
              </ScaleIn>
              <Reveal delay={0.6}>
                <div className="econ-detail-row">
                  <div className="econ-detail-circle"><div className="econ-detail-num">$29-63</div><div className="econ-detail-label">Value</div></div>
                  <div style={{ fontSize: 20, color: 'var(--text-muted)', fontWeight: 300 }}>-</div>
                  <div className="econ-detail-circle"><div className="econ-detail-num">$10-24</div><div className="econ-detail-label">BOM at 100K</div></div>
                </div>
              </Reveal>
              <Reveal delay={0.7}>
                <div className="econ-tam"><div className="econ-tam-num">$500M+</div><div className="econ-tam-label">Total addressable market</div></div>
              </Reveal>
            </div>
          </div>
        </Reveal>
        <Reveal delay={0.8}>
          <div style={{ textAlign: 'center', marginTop: 20, fontSize: 13, fontWeight: 600, color: 'var(--text-sec)' }}>
            Mechanisms 1+2 cover device cost. Mechanism 3 drives profitability. Data play is pure upside.
          </div>
        </Reveal>
      </div>
    </div>
  )
}

/* ═══ S10 — VALIDATION ═══ */
function S10() {
  return (
    <div className="slide sage" id="slide-9">
      <SlideLogo />
      <Circles config={[
        { size: 350, top: '-10%', right: '-8%', type: 'green-solid' },
        { size: 150, bottom: '15%', left: '5%', type: 'ring' },
      ]} />
      <div className="slide-inner" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Reveal><div className="label">Validation</div></Reveal>
        <Reveal delay={0.1}>
          <div className="title" style={{ textAlign: 'center' }}>Validated by <span className="hi">the industry</span>.</div>
        </Reveal>
        <div className="val-grid">
          {[
            { icon: <Activity size={22} />, text: 'Dr. Ron Tessman (Elanco, 17yr) confirmed mechanism', delay: 0.15 },
            { icon: <Users size={22} />, text: '8+ operators confirmed $80-200/head', delay: 0.25 },
            { icon: <ShieldCheck size={22} />, text: '"No internal measurement exists" — Tessman', delay: 0.35 },
            { icon: <DollarSign size={22} />, text: '$20-50 diagnostic, up to $100 with therapy', delay: 0.45 },
            { icon: <Cpu size={22} />, text: 'Nexa Labs (YC S25) confirmed reg path', delay: 0.55 },
          ].map((v, i) => (
            <ScaleIn key={i} delay={v.delay} className="val-item">
              <div className="val-circle">{v.icon}</div>
              <div className="val-text">{v.text}</div>
            </ScaleIn>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ═══ S11 — DATA FLYWHEEL ═══ */
function S11() {
  return (
    <div className="slide moonshot-bg compact" id="slide-10">
      <SlideLogo />
      <div className="slide-inner" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
        <Reveal>
          <div style={{ fontSize: 'clamp(18px, 2vw, 24px)', fontWeight: 600, color: 'rgba(255,255,255,0.6)', marginBottom: 8 }}>The Data</div>
          <div style={{ fontSize: 'clamp(48px, 8vw, 96px)', fontWeight: 800, letterSpacing: '-3px', lineHeight: 1 }}>
            <span className="cow-text">Mooooo-nshot</span>
          </div>
        </Reveal>
        <Reveal delay={0.15}>
          <div className="subtitle" style={{ textAlign: 'center', margin: '20px auto 0', maxWidth: 600 }}>
            Every device records vagal nerve activity 24/7. 1,000 cows in year one builds the world's largest mammal peripheral nerve dataset.
          </div>
        </Reveal>
        <div className="flywheel-visual" style={{ marginTop: 40 }}>
          <ScaleIn delay={0.3} className="flywheel-circle input">
            <div className="flywheel-num">1,000</div>
            <div className="flywheel-label" style={{ color: 'rgba(255,255,255,0.6)' }}>Cows year one</div>
          </ScaleIn>
          <motion.div className="flywheel-arrow" initial={{ opacity: 0, x: -10 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ delay: 0.4 }}>&rarr;</motion.div>
          <ScaleIn delay={0.5} className="flywheel-circle output">
            <div className="flywheel-num">1,000x</div>
            <div className="flywheel-label">World's vagal dataset</div>
          </ScaleIn>
        </div>
      </div>
    </div>
  )
}

/* ═══ S12 — ROADMAP ═══ */
function S12() {
  return (
    <div className="slide sage" id="slide-11">
      <SlideLogo />
      <Circles config={[
        { size: 400, bottom: '-15%', right: '-10%', type: 'green-solid' },
        { size: 160, top: '10%', left: '5%', type: 'ring' },
      ]} />
      <div className="slide-inner" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Reveal><div className="label">Roadmap</div></Reveal>
        <Reveal delay={0.1}>
          <div className="title" style={{ textAlign: 'center' }}><span className="hi">$1M</span> to proof of concept.</div>
        </Reveal>
        <div className="roadmap-row">
          {[
            { cost: '$20K', time: 'Mo 1-2', name: 'Anatomy', desc: 'Cadaver dissection, IJV-to-nerve mapping', style: 's1' },
            { cost: '$75K', time: 'Mo 3-6', name: 'Dose Titration', desc: 'Heart rate NTS activation in calves', style: 's2' },
            { cost: '$200K', time: 'Mo 6-12', name: 'LPS Model', desc: 'Cytokine panel vs sham', style: 's3' },
            { cost: '$750K', time: 'Mo 12-24', name: 'Field Trial', desc: '200 cattle, 150-day finishing', style: 's4' },
          ].map((item, i) => (
            <div key={item.name} style={{ display: 'flex', alignItems: 'flex-start', gap: 0 }}>
              <ScaleIn delay={0.2 + i * 0.15} className="roadmap-item">
                <div className={`roadmap-circle ${item.style}`}>
                  <div className="roadmap-cost">{item.cost}</div>
                  <div className="roadmap-time">{item.time}</div>
                </div>
                <div className="roadmap-name">{item.name}</div>
                <div className="roadmap-desc">{item.desc}</div>
              </ScaleIn>
              {i < 3 && <div className="roadmap-connector" />}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ═══ S13 — CLOSE ═══ */
function S13() {
  return (
    <div className="slide bg-img bg-clear-close" id="slide-12">
      <SlideLogo />
      <Circles config={[
        { size: 500, top: '-20%', left: '-12%', type: 'ring' },
        { size: 300, bottom: '-10%', right: '-8%', type: 'ring' },
      ]} />
      <div className="slide-inner">
        <div className="close-wrap">
          <Reveal>
            <img src="/logo.png" alt="BoVa" className="logo-close" />
          </Reveal>
          <Reveal delay={0.2}>
            <div className="close-brand">BoVa</div>
          </Reveal>
          <Reveal delay={0.4}>
            <div className="close-motto">Healthier cattle, one moo at a time.</div>
          </Reveal>
        </div>
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════
   PRESENTER NOTES
   ═══════════════════════════════════════ */
const NOTES = [
  {
    slide: 'SLIDE 1',
    title: 'HOOK',
    body: `<span class="cue">"$1.3 billion lost every year to two preventable conditions in cattle. The technology to fix both already exists. It was FDA-approved for humans last year. Nobody has applied it to the beef industry. Until now."</span>`,
  },
  {
    slide: 'SLIDE 2',
    title: 'FARMING HASN\'T CHANGED',
    body: `<span class="cue">"Consumers don't want antibiotics or hormones. Lab-grown meat is decades away. Methane is still unsolved. And cows are farmed the same way we've done it for thousands of years. The industry is ready for a real innovation."</span>`,
  },
  {
    slide: 'SLIDE 3',
    title: 'BRD',
    body: `<span class="cue">"BRD. Billion-dollar problem. 16% of cattle get sick at arrival. Published cost is $23 a case — that's just the drug. Real cost: $80 to $200 all-in. We confirmed that with operators. Current fix: mass antibiotics. Drug resistance is growing. California already banned it."</span>`,
  },
  {
    slide: 'SLIDE 4',
    title: 'DARK CUTTING',
    body: `<span class="cue">"Second problem. Pre-slaughter stress spikes cortisol, depletes glycogen, destroys meat quality. $288 million a year. Nearly $39 per carcass in packer discounts. Different mechanism, but addressable through the same nerve."</span>`,
  },
  {
    slide: 'SLIDE 5',
    title: 'GUT MOTILITY',
    body: `<span class="cue">"Third opportunity. A cow is a meat factory and the bottleneck is the digestive system. The most common surgery on cattle is literally cutting a window in their stomach. Cervical VNS can modulate gut motility and improve feed-to-meat ratio. This is our research bet — mechanisms 1 and 2 are the beachhead."</span>`,
  },
  {
    slide: 'SLIDE 6',
    title: 'VNS IS PROVEN',
    body: `<span class="cue">"VNS is 50 years old. It's not speculative science. SetPoint Medical got FDA PMA approval in August 2025 for the anti-inflammatory mechanism. We didn't invent the technology. We're the first to apply it to cattle. Three mechanisms, tiered by readiness: inflammation is our beachhead, stress is secondary, gut motility is the research play."</span>`,
  },
  {
    slide: 'SLIDE 7',
    title: 'DEVICE',
    body: `<span class="cue">"Cervical vagus nerve. Closest to the skin. 15-minute procedure under local anaesthesia — replicates an existing cattle surgery. Biocompatible cuff electrode developed with Imperial, MintNeuro stimulation chips, closed-loop ultrasound feedback. Plus an analog front-end to record neural activity 24/7. The device doesn't just stimulate — it generates data."</span>`,
  },
  {
    slide: 'SLIDE 8',
    title: 'WHITE SPACE',
    body: `<span class="cue">"Humans: complete data, FDA devices. Pigs: full morphometry. Sheep: chronic recordings. Bovine: nothing. Zero. No one has ever stimulated a cow's vagus nerve. First team to generate this dataset owns the electrode design space."</span>`,
  },
  {
    slide: 'SLIDE 9',
    title: 'UNIT ECONOMICS',
    body: `<span class="cue">"$29 to $63 value per head. Device costs $10-24 at scale. Mechanisms 1 and 2 cover the device cost. Mechanism 3 drives profitability. The data play is pure upside. $500 million TAM, US only."</span>`,
  },
  {
    slide: 'SLIDE 10',
    title: 'VALIDATION',
    body: `<span class="cue">"We spoke with Dr. Ron Tessman — DVM PhD, 17 years at Bayer, Merial, and Elanco. He confirmed BRD damage is driven by runaway host inflammation, not just bacteria. He said the biggest industry problem is no internal measurement system exists. A device that senses and stimulates is exactly what's missing. His pricing envelope: $20-50 for diagnosis, up to $100 with therapy. 8+ operators confirmed $80-200 all-in costs. Nexa Labs confirmed regulatory path."</span>`,
  },
  {
    slide: 'SLIDE 11',
    title: 'DATA PLAY',
    body: `<span class="cue">"Every device we implant doesn't just stimulate — it records. 24/7 vagal nerve data. 1,000 cows in year one gives us the world's largest mammal peripheral nerve dataset. That data subsidises our costs, advances the science, and is directly licensable to human VNS companies — SetPoint, LivaNova, Inspire. Same playbook as Loyal with dog longevity. Serious science, accessible outcomes."</span>`,
  },
  {
    slide: 'SLIDE 12',
    title: 'ROADMAP',
    body: `<span class="cue">"$20K anatomy. $75K dose titration. $200K inflammation model. $750K field trial. $1 million total. 24 months to commercial proof of concept."</span>`,
  },
  {
    slide: 'SLIDE 13',
    title: 'CLOSE',
    body: `<span class="cue">"$1.3 billion in losses. Zero competitors. $1 million to proof of concept. The science is FDA-validated. We are the team to close the gap."</span>

Don't say thank you. Don't say any questions. Stop.`,
  },
]

function NotesPanel({ currentSlide, open, onToggle }) {
  const note = NOTES[currentSlide] || NOTES[0]
  return (
    <>
      <button className={`notes-toggle ${open ? 'active' : ''}`} onClick={onToggle} title="Toggle notes (N)">N</button>
      {!open && <div className="notes-hint">Press N for notes</div>}
      <div className={`notes-panel ${open ? 'open' : ''}`}>
        <div className="notes-inner">
          <div className="notes-slide-label">{note.slide}</div>
          <div className="notes-title">{note.title}</div>
          <div className="notes-body" dangerouslySetInnerHTML={{ __html: note.body }} />
        </div>
      </div>
    </>
  )
}

/* ═══════════════════════════════════════
   APP
   ═══════════════════════════════════════ */
export default function App() {
  const [cur, setCur] = useState(0)
  const [notesOpen, setNotesOpen] = useState(false)

  const onScroll = useCallback(() => {
    setCur(Math.min(Math.round(window.scrollY / window.innerHeight), TOTAL - 1))
  }, [])

  useEffect(() => {
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [onScroll])

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'n' || e.key === 'N') {
        setNotesOpen(p => !p)
        return
      }
      if (e.key === 'ArrowDown' || e.key === ' ' || e.key === 'j') {
        e.preventDefault()
        document.getElementById(`slide-${Math.min(cur + 1, TOTAL - 1)}`)?.scrollIntoView({ behavior: 'smooth' })
      } else if (e.key === 'ArrowUp' || e.key === 'k') {
        e.preventDefault()
        document.getElementById(`slide-${Math.max(cur - 1, 0)}`)?.scrollIntoView({ behavior: 'smooth' })
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [cur])

  return (
    <>
      <div className="progress-bar" style={{ width: `${((cur + 1) / TOTAL) * 100}%` }} />
      <nav className="nav-dots">
        {Array.from({ length: TOTAL }).map((_, i) => (
          <button key={i} className={`nav-dot ${i === cur ? 'active' : ''}`} onClick={() => document.getElementById(`slide-${i}`)?.scrollIntoView({ behavior: 'smooth' })} aria-label={`Slide ${i + 1}`} />
        ))}
      </nav>
      <S1 /><S2 /><S3 /><S4 /><S5 /><S6 /><S7 /><S8 /><S9 /><S10 /><S11 /><S12 /><S13 />
      <NotesPanel currentSlide={cur} open={notesOpen} onToggle={() => setNotesOpen(p => !p)} />
    </>
  )
}
