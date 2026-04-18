import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { ShieldOff, FlaskConical, Thermometer, Pill, Users, ShieldCheck, DollarSign, Beaker, Cpu, Activity, ChevronLeft, ChevronRight } from 'lucide-react'
import './App.css'

const TOTAL = 22

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

/* Paper-slam entrance — drops from above with rotation, overshoots, settles */
function SlamImage({ src, className = '', delay = 0, finalRotate = 0, fromRotate = -25 }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-80px' })
  return (
    <motion.img
      ref={ref}
      src={src}
      alt=""
      className={className}
      initial={{ opacity: 0, scale: 2.4, rotate: fromRotate, y: -220 }}
      animate={inView ? {
        opacity: [0, 1, 1, 1],
        scale: [2.4, 0.92, 1.04, 1],
        y: [-220, 18, -6, 0],
        rotate: [fromRotate, finalRotate - 3, finalRotate + 1.5, finalRotate],
      } : {}}
      transition={{
        duration: 0.72,
        delay,
        times: [0, 0.55, 0.8, 1],
        ease: [0.22, 1, 0.36, 1],
      }}
    />
  )
}

function SlideLogo() {
  return <img src="/logo.png" alt="Bova" className="slide-logo" />
}

function Circles({ config }) {
  return config.map((c, i) => (
    <div key={i} className={`deco-circle ${c.type || 'solid'}`} style={{ width: c.size, height: c.size, top: c.top, bottom: c.bottom, left: c.left, right: c.right }} />
  ))
}

/* ═══ S1 — HOOK ═══ */
function S1() {
  return (
    <div className="slide bg-img bg-clear hook-video-bg hook-centered" id="slide-0">
      <video className="hook-video" src="/cow-closeup.mp4" autoPlay loop muted playsInline />
      <div className="hook-video-overlay" />
      <SlideLogo />
      <div className="slide-inner">
        <Reveal delay={0.2}>
          <div className="hook-headline">1.3 billion dollars lost every year.</div>
        </Reveal>
      </div>
    </div>
  )
}

/* ═══ PROBLEM CIRCLES — three broken systems ═══ */
function S_ProblemCircles() {
  const problems = [
    { n: '01', title: 'Stress-degraded meat' },
    { n: '02', title: 'Chronic disease' },
    { n: '03', title: 'Antibiotic overreliance' },
  ]
  return (
    <div className="slide sage" id="slide-problem-circles">
      <SlideLogo />
      <div className="slide-inner" style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Reveal>
          <div className="label">The Problem</div>
        </Reveal>
        <Reveal delay={0.1}>
          <div className="title" style={{ fontSize: 'clamp(32px, 4.2vw, 52px)', marginBottom: 56, textAlign: 'center' }}>
            Three broken systems.
          </div>
        </Reveal>
        <div className="problem-circles">
          {problems.map((p, i) => (
            <ScaleIn key={i} delay={0.2 + i * 0.15}>
              <div className="problem-circle">
                <div className="problem-circle-num">{p.n}</div>
                <div className="problem-circle-title">{p.title}</div>
              </div>
            </ScaleIn>
          ))}
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
    <div className="slide moonshot-bg compact" id="slide-10" style={{ justifyContent: 'flex-start' }}>
      <SlideLogo />
      <div className="slide-inner" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', justifyContent: 'flex-start', paddingTop: '4vh' }}>
        <Reveal>
          <div style={{ fontSize: 'clamp(36px, 5vw, 60px)', fontWeight: 700, color: 'rgba(255,255,255,0.7)', marginBottom: 16, letterSpacing: '-1px' }}>The Data</div>
          <div style={{ fontSize: 'clamp(56px, 9vw, 120px)', fontWeight: 800, letterSpacing: '-3px', lineHeight: 1 }}>
            <span className="cow-text">Mooooo-nshot</span>
          </div>
        </Reveal>
        <div className="flywheel-visual" style={{ marginTop: 40 }}>
          <ScaleIn delay={0.3} className="flywheel-circle input">
            <div className="flywheel-num">100,000</div>
            <div className="flywheel-label" style={{ color: 'rgba(255,255,255,0.7)' }}>Cows</div>
          </ScaleIn>
          <motion.div className="flywheel-arrow" initial={{ opacity: 0, x: -10 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ delay: 0.4 }}>&rarr;</motion.div>
          <ScaleIn delay={0.5} className="flywheel-circle output" style={{ width: 260, height: 260 }}>
            <div className="flywheel-label" style={{ fontSize: 15, fontWeight: 700, maxWidth: 190, lineHeight: 1.5, letterSpacing: 0.3, textTransform: 'uppercase', padding: '0 8px' }}>
              The world's largest mammal peripheral nerve dataset
            </div>
          </ScaleIn>
        </div>
      </div>
    </div>
  )
}

/* ═══ S11b — DATASET LICENSING (Moonshot follow-up) ═══ */
function S11b_Licensing() {
  return (
    <div className="slide moonshot-bg" id="slide-10b">
      <SlideLogo />
      <div className="slide-inner" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
        <Reveal>
          <div style={{ fontSize: 'clamp(28px, 3.5vw, 44px)', fontWeight: 800, color: 'white', letterSpacing: '-0.8px', lineHeight: 1.2, maxWidth: 900, marginBottom: 16 }}>
            At <span style={{ color: 'var(--green-light)' }}>100,000 cattle</span>, we hold a dataset licensable to <span style={{ color: 'var(--green-light)' }}>billion-dollar businesses</span>
          </div>
        </Reveal>
        <Reveal delay={0.15}>
          <div style={{ fontSize: 'clamp(16px, 1.8vw, 20px)', fontWeight: 500, color: 'rgba(255,255,255,0.65)', maxWidth: 760, margin: '0 auto 48px' }}>
            These companies build vagal stimulation devices — but none of them have access to chronic vagal recording data at scale yet. We do.
          </div>
        </Reveal>
        <Reveal delay={0.3}>
          <div className="licensing-logos">
            <div className="licensing-logo-card">
              <img src="/logos/setpoint.svg" alt="SetPoint Medical" />
            </div>
            <div className="licensing-logo-card">
              <img src="/logos/livanova.svg" alt="LivaNova" />
            </div>
            <div className="licensing-logo-card">
              <img src="/logos/inspire.svg" alt="Inspire Medical Systems" className="invert-logo" />
            </div>
          </div>
        </Reveal>
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
            { cost: '$20K', time: 'Mo 1-2', name: 'Anatomy', desc: 'Cadaver dissection, common carotid to nerve mapping', style: 's1' },
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

/* ═══ Shared phase card layout (used by Unit Economics & Roadmap) ═══ */
function PhaseCardsSlide({ id, title, labels, phases }) {
  return (
    <div className="slide" id={id}>
      <SlideLogo />
      <div className="slide-inner">
        <Reveal>
          <div className="title" style={{ marginBottom: 40, color: 'var(--green)', fontSize: 'clamp(40px, 5.5vw, 64px)', textAlign: 'center' }}>{title}</div>
        </Reveal>
        <div className="phase-layout">
          <div className="phase-labels">
            {labels.map(l => <div key={l} className="phase-label">{l}</div>)}
          </div>
          <div className="phase-cards-row">
            {phases.map((p, i) => (
              <ScaleIn key={p.num} delay={0.2 + i * 0.15} className={`phase-card-v2 tier-${i + 1} ${p.highlight ? 'highlight' : ''}`}>
                <div className="phase-card-num">{p.num}</div>
                <div className="phase-card-title">{p.title}</div>
                <div className="phase-card-rows">
                  {p.values.map((v, vi) => (
                    <div key={vi} className="phase-card-value">{v}</div>
                  ))}
                </div>
              </ScaleIn>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

/* ═══ S13 — UNIT ECONOMICS (three circles) ═══ */
function S13_Roadmap() {
  const phases = [
    {
      num: '01',
      phaseLabel: 'PHASE 1',
      title: 'Electrode Cuff',
      units: '40',
      cost: '$1,150–2,200',
      total: '$50–90k',
      tier: 1,
    },
    {
      num: '02',
      phaseLabel: 'PHASE 2',
      title: 'VNS Efficacy Trial',
      units: '40',
      cost: '$70–165',
      total: '$200–400k',
      tier: 2,
    },
    {
      num: '03',
      phaseLabel: 'PHASE 3',
      title: 'Stent at Scale',
      units: '100,000',
      cost: '$48–83',
      total: '$4.8M–8.3M',
      tier: 3,
      highlight: true,
    },
  ]
  return (
    <div className="slide" id="slide-12">
      <SlideLogo />
      <div className="slide-inner">
        <Reveal>
          <div className="title" style={{ marginBottom: 48, color: 'var(--green)', fontSize: 'clamp(40px, 5.5vw, 64px)', textAlign: 'center' }}>Unit Economics</div>
        </Reveal>
        <div className="econ-circles">
          {phases.map((p, i) => (
            <ScaleIn key={p.num} delay={0.2 + i * 0.15} className={`econ-circle tier-${p.tier}`}>
              <div className="econ-circle-ring">
                <div className="econ-circle-inner">
                  <div className="econ-circle-num">{p.phaseLabel}</div>
                  <div className="econ-circle-total">{p.cost}</div>
                  <div className="econ-circle-total-label">per head</div>
                </div>
              </div>
              <div className="econ-circle-caption">
                <div className="econ-circle-title">{p.title}</div>
                <div className="econ-circle-stats">
                  <span><strong>{p.units}</strong> units</span>
                  <span className="dot">·</span>
                  <span><strong>{p.total}</strong> total</span>
                </div>
              </div>
            </ScaleIn>
          ))}
        </div>
        <Reveal delay={0.65}>
          <div className="phase-outcome">
            <div className="phase-outcome-pill">
              <div className="po-label">Phase 3 Margin</div>
              <div className="po-value">Breakeven → +$12/head</div>
            </div>
          </div>
        </Reveal>
      </div>
    </div>
  )
}

/* ═══ S14 — ROADMAP (wavy path + circles & cards) ═══ */
function S14_Roadmap() {
  const phases = [
    {
      num: '01',
      title: 'Nerve Cuff Validation',
    },
    {
      num: '02',
      title: 'VNS Efficacy Trial',
    },
    {
      num: '03',
      title: 'Stent at Scale',
      highlight: true,
    },
  ]
  return (
    <div className="slide" id="slide-13">
      <SlideLogo />
      <div className="slide-inner">
        <Reveal>
          <div className="title" style={{ marginBottom: 32, color: 'var(--green)', fontSize: 'clamp(40px, 5.5vw, 64px)', textAlign: 'center' }}>Roadmap</div>
        </Reveal>
        <div className="roadmap-wavy">
          <svg className="roadmap-wavy-path" viewBox="0 0 1000 200" preserveAspectRatio="none">
            <path
              d="M 140 150 Q 320 20 500 110 T 850 40"
              fill="none"
              stroke="var(--green)"
              strokeWidth="6"
              strokeDasharray="14 10"
              strokeLinecap="round"
            />
            <polygon points="830,20 880,40 830,60" fill="var(--green)" />
          </svg>
          {phases.map((p, i) => (
            <ScaleIn key={p.num} delay={0.2 + i * 0.2} className={`roadmap-item-v2 ${p.highlight ? 'highlight' : ''}`}>
              <div className="roadmap-circle-v2">{p.num}</div>
              <div className="roadmap-card-v2">
                <div className="roadmap-card-title">{p.title}</div>
                {p.timeline && <div className="roadmap-card-timeline">{p.timeline}</div>}
                {p.units && <div className="roadmap-card-meta">{p.units}</div>}
                {p.output && <div className="roadmap-card-output">{p.output}</div>}
              </div>
            </ScaleIn>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ═══ S14b — PHASE 1 DETAIL ═══ */
function S14b_Phase1() {
  return (
    <div className="slide" id="slide-14b">
      <SlideLogo />
      <div className="slide-inner">
        <Reveal>
          <div className="phase-header">
            <div className="phase-header-pill">PHASE 01</div>
            <div className="title" style={{ color: 'var(--green)', fontSize: 'clamp(36px, 4.5vw, 52px)', marginBottom: 0 }}>Nerve Cuff Validation</div>
          </div>
        </Reveal>
        <div className="phase1-layout-v2">
          {/* Left: vertical stat circles */}
          <Reveal delay={0.1}>
            <div className="phase1-stats-col">
              <div className="phase-detail-circle">
                <div className="phase-detail-num">40</div>
                <div className="phase-detail-label">Animals</div>
              </div>
              <div className="phase-detail-circle">
                <div className="phase-detail-num">30d</div>
                <div className="phase-detail-label">Trial</div>
              </div>
              <div className="phase-detail-circle">
                <div className="phase-detail-num">6</div>
                <div className="phase-detail-label">Biomarkers</div>
              </div>
            </div>
          </Reveal>
          {/* Middle: stimulate → measure → analyse cycle */}
          <Reveal delay={0.2}>
            <div className="phase1-cycle">
              <div className="cycle-label">Study Cycle</div>
              <div className="cycle-diagram">
                <svg className="cycle-arrows" viewBox="0 0 400 340" preserveAspectRatio="xMidYMid meet">
                  <defs>
                    <marker id="cycle-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto">
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--green)" />
                    </marker>
                  </defs>
                  <path d="M 175 110 L 115 215" fill="none" stroke="var(--green)" strokeWidth="2.5" strokeLinecap="round" markerEnd="url(#cycle-arrow)" />
                  <path d="M 127 270 L 273 270" fill="none" stroke="var(--green)" strokeWidth="2.5" strokeLinecap="round" markerEnd="url(#cycle-arrow)" />
                  <path d="M 285 215 L 225 110" fill="none" stroke="var(--green)" strokeWidth="2.5" strokeLinecap="round" markerEnd="url(#cycle-arrow)" />
                </svg>
                <div className="cycle-node stim-node">
                  <div className="cycle-node-title">Stimulate</div>
                  <div className="cycle-node-sub">VNS cuff active</div>
                </div>
                <div className="cycle-node measure-node">
                  <div className="cycle-node-title">Measure</div>
                  <div className="cycle-node-sub">Blood draw, HRV</div>
                </div>
                <div className="cycle-node analyse-node">
                  <div className="cycle-node-title">Analyse</div>
                  <div className="cycle-node-sub">Biomarker response</div>
                </div>
              </div>
            </div>
          </Reveal>
          {/* Right: biomarker buckets stacked */}
          <Reveal delay={0.3}>
            <div className="phase1-buckets">
              <div className="cycle-label">Biomarker Buckets</div>
              <div className="bucket-stack">
                <div className="bucket-row bucket-row-1">
                  <div className="bucket-row-title">Device Works</div>
                  <div className="bucket-row-sub">Vagal activation confirmed</div>
                  <div className="bucket-row-tags">
                    <span className="marker">Heart Rate</span>
                    <span className="marker">HRV</span>
                  </div>
                </div>
                <div className="bucket-row bucket-row-2">
                  <div className="bucket-row-title">Biology Responds</div>
                  <div className="bucket-row-sub">Cholinergic pathway active</div>
                  <div className="bucket-row-tags">
                    <span className="marker">TNF-α</span>
                    <span className="marker">IL-6</span>
                  </div>
                </div>
                <div className="bucket-row bucket-row-3">
                  <div className="bucket-row-title">BRD Relevant</div>
                  <div className="bucket-row-sub">Disease pathway signal</div>
                  <div className="bucket-row-tags">
                    <span className="marker">Haptoglobin</span>
                    <span className="marker">N:L Ratio</span>
                  </div>
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </div>
  )
}

/* ═══ S14c — PHASE 2 DETAIL ═══ */
function S14c_Phase2() {
  return (
    <div className="slide" id="slide-14c">
      <SlideLogo />
      <div className="slide-inner">
        <Reveal>
          <div className="phase-header">
            <div className="phase-header-pill">PHASE 02</div>
            <div className="title" style={{ color: 'var(--green)', fontSize: 'clamp(36px, 4.5vw, 52px)', marginBottom: 0 }}>VNS Efficacy Trial</div>
          </div>
        </Reveal>
        <Reveal delay={0.1}>
          <div className="phase-detail-top">
            <div className="phase-detail-circle">
              <div className="phase-detail-num">120–150</div>
              <div className="phase-detail-label">Animals</div>
            </div>
            <div className="phase-detail-circle">
              <div className="phase-detail-num">30d</div>
              <div className="phase-detail-label">Trial</div>
            </div>
            <div className="phase-detail-circle">
              <div className="phase-detail-num">3</div>
              <div className="phase-detail-label">Groups</div>
            </div>
          </div>
        </Reveal>
        <Reveal delay={0.25}>
          <div className="phase-bucket-grid">
            <div className="phase-bucket">
              <div className="phase-bucket-pill">Group A</div>
              <div className="phase-bucket-title">Active VNS + SOC</div>
              <div className="phase-bucket-sub">Active stimulation + standard of care antibiotics</div>
            </div>
            <div className="phase-bucket">
              <div className="phase-bucket-pill">Group B</div>
              <div className="phase-bucket-title">Sham + SOC</div>
              <div className="phase-bucket-sub">Sham device + standard of care antibiotics</div>
            </div>
            <div className="phase-bucket">
              <div className="phase-bucket-pill">Group C</div>
              <div className="phase-bucket-title">SOC Only</div>
              <div className="phase-bucket-sub">Standard of care baseline</div>
            </div>
          </div>
        </Reveal>
      </div>
    </div>
  )
}

/* ═══ S14d — PHASE 3 / DEVICE ═══ */
function S14d_Phase3() {
  return (
    <div className="slide" id="slide-14d">
      <SlideLogo />
      <div className="slide-inner">
        <Reveal>
          <div className="phase-header">
            <div className="phase-header-pill">PHASE 03 · THE DEVICE</div>
            <div className="title" style={{ color: 'var(--green)', fontSize: 'clamp(36px, 4.5vw, 52px)', marginBottom: 0 }}>Endovascular Stentrode</div>
          </div>
        </Reveal>
        <Reveal delay={0.1}>
          <div className="phase3-stack">
            <img src="/stentrode.png" alt="Stentrode" className="phase3-image-flat" />
            <div className="phase3-meta-card">
              <div className="phase3-meta-item">
                <div className="phase3-meta-label">Delivery</div>
                <div className="phase3-meta-value">Endovascular</div>
              </div>
              <div className="phase3-meta-divider" />
              <div className="phase3-meta-item">
                <div className="phase3-meta-label">Placement</div>
                <div className="phase3-meta-value">Common Carotid Artery</div>
              </div>
              <div className="phase3-meta-divider" />
              <div className="phase3-meta-item">
                <div className="phase3-meta-label">Procedure</div>
                <div className="phase3-meta-value">8–12 min</div>
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </div>
  )
}

/* ═══ TESSMAN 3 KEY POINTS ═══ */
function S_TessmanPoints() {
  const points = [
    {
      title: 'Treatment Cost',
      body: <>Current BRD treatment runs about <strong>$50 a head</strong>.</>,
    },
    {
      title: 'No Internal Measurement',
      body: <>No accurate <strong>internal measurement system</strong> exists in the industry today.</>,
    },
    {
      title: 'The Gap We Fill',
      body: <>No device on the market can <strong>both sense and stimulate</strong>. That's exactly what we're building.</>,
      ours: true,
    },
  ]
  return (
    <div className="slide" id="slide-tessman-pts">
      <SlideLogo />
      <div className="slide-inner">
        <Reveal>
          <div style={{ textAlign: 'center', marginBottom: 56 }}>
            <div style={{ fontSize: 14, fontWeight: 800, letterSpacing: 3, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>EXPERT VALIDATION</div>
            <div className="title" style={{ color: 'var(--green)', fontSize: 'clamp(36px, 4.5vw, 52px)', marginBottom: 0 }}>Three things we heard</div>
          </div>
        </Reveal>
        <div className="tessman-points">
          {points.map((p, i) => (
            <ScaleIn key={i} delay={0.2 + i * 0.15} className={`tessman-simple-wrap ${p.ours ? 'ours' : ''}`}>
              {p.ours && <div className="tessman-ours-badge">OUR SOLUTION</div>}
              <div className="tessman-simple-circle">
                <div className="tessman-simple-title">{p.title}</div>
                <div className="tessman-simple-body">{p.body}</div>
              </div>
            </ScaleIn>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ═══ TESSMAN CITATION SLIDE ═══ */
function S_Tessman() {
  return (
    <div className="slide sage" id="slide-tessman">
      <SlideLogo />
      <div className="slide-inner" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Reveal>
          <div className="label" style={{ textAlign: 'center' }}>Field Validation</div>
        </Reveal>
        <Reveal delay={0.1}>
          <div className="title" style={{ textAlign: 'center', fontSize: 'clamp(34px, 4.5vw, 52px)', marginBottom: 12 }}>
            We spoke with <span className="hi">Dr. Ronald Tessman DVM PhD</span>.
          </div>
        </Reveal>
        <Reveal delay={0.2}>
          <div className="subtitle" style={{ textAlign: 'center', margin: '0 auto 40px', maxWidth: 760 }}>
            17 years as a beef cattle technical consultant at Bayer, Merial, and Elanco. We walked him through our device and pricing thesis.
          </div>
        </Reveal>
        <ScaleIn delay={0.3}>
          <div className="lt-stack">
            <div className="lower-third">
              <div className="lt-header">
                <div className="lt-avatar">
                  <img src="/tessman.png" alt="Dr. Ronald Tessman" />
                </div>
                <div className="lt-name-block">
                  <div className="lt-name">Dr. Ronald Tessman DVM PhD</div>
                  <div className="lt-title">Beef Cattle Technical Consultant · 17 years of experience</div>
                </div>
                <div className="lt-logos">
                  <img src="/logos/bayer.svg" alt="Bayer" className="lt-logo-img" />
                  <img src="/logos/merial.svg" alt="Merial" className="lt-logo-img" />
                  <img src="/logos/elanco.svg" alt="Elanco" className="lt-logo-img" />
                </div>
              </div>
            </div>
            <div className="lt-wtp-card">
              <div className="lt-wtp-label">Willingness to pay</div>
              <div className="lt-wtp-values">
                <div className="lt-wtp-circle">
                  <div className="lt-wtp-num">$30</div>
                  <div className="lt-wtp-sub">today</div>
                </div>
                <div className="lt-wtp-arrow">→</div>
                <div className="lt-wtp-circle highlight">
                  <div className="lt-wtp-num">$60</div>
                  <div className="lt-wtp-sub">with proof</div>
                </div>
              </div>
            </div>
          </div>
        </ScaleIn>
      </div>
    </div>
  )
}

/* ═══ VAGUS NERVE CONTROLS (Problem section) ═══ */
function S_VagusControls() {
  const functions = [
    { title: 'Inflammation', body: 'Cholinergic anti-inflammatory pathway' },
    { title: 'Digestion', body: 'Rumen + gut motility' },
    { title: 'Stress', body: 'Autonomic cortisol regulation' },
    { title: 'Immune', body: 'Splenic macrophage signalling' },
    { title: 'Eructation', body: 'Methane release + bloat' },
  ]
  return (
    <div className="slide vagus-video-bg" id="slide-vagus-fns">
      <video
        className="vagus-video"
        src="/vagusnerve.mp4"
        autoPlay
        loop
        muted
        playsInline
      />
      <div className="vagus-video-overlay" />
      <SlideLogo />
      <div className="slide-inner" style={{ textAlign: 'center', position: 'relative', zIndex: 2 }}>
        <Reveal><div className="label">Across Mammalian Species</div></Reveal>
        <Reveal delay={0.1}>
          <div className="title" style={{ marginBottom: 40, fontSize: 'clamp(32px, 4.5vw, 52px)', color: 'white' }}>
            The vagus nerve <span style={{ color: 'var(--green-light)' }}>controls everything</span>.
          </div>
        </Reveal>
        <div className="vagus-grid">
          {functions.map((f, i) => (
            <ScaleIn key={f.title} delay={0.2 + i * 0.12} className="vagus-card">
              <div className="vagus-card-title">{f.title}</div>
              <div className="vagus-card-body">{f.body}</div>
            </ScaleIn>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ═══ VNS IS PROVEN (FDA 1997) ═══ */
function S_VNSProven() {
  return (
    <div className="slide" id="slide-vns-proven">
      <SlideLogo />
      {/* FDA decision document slammed down with the approval line highlighted */}
      <div className="fda-paper-frame">
        <SlamImage src="/fda-approval-2.jpeg" className="fda-paper-single" delay={0.4} fromRotate={-14} finalRotate={-2} />
        <motion.div
          className="fda-highlight"
          initial={{ scaleX: 0, opacity: 0 }}
          whileInView={{ scaleX: 1, opacity: 1 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.75, delay: 1.35, ease: [0.22, 1, 0.36, 1] }}
        />
      </div>
      <div className="slide-inner vns-proven-layout">
        <div className="vns-proven-header">
          <Reveal>
            <div className="label">Not New Science</div>
          </Reveal>
          <Reveal delay={0.1}>
            <div className="title" style={{ fontSize: 'clamp(36px, 5vw, 60px)', marginBottom: 0 }}>
              Vagus nerve stimulation has been <span className="hi">FDA-approved since 1997</span>.
            </div>
          </Reveal>
        </div>
      </div>
    </div>
  )
}

/* ═══ GOAT DISSECTION — wet lab proof ═══ */
function S_GoatDemo() {
  return (
    <div className="slide demo-fullscreen" id="slide-goat-demo">
      <video className="demo-fullscreen-video" src="/goat.mp4" autoPlay loop muted playsInline />
      <div className="demo-fullscreen-overlay" />
      <SlideLogo />
      <div className="demo-fullscreen-meta">
        <Reveal>
          <div className="demo-fullscreen-title">Anatomical validation study.</div>
        </Reveal>
      </div>
    </div>
  )
}

/* ═══ DEVICE — NERVE CUFF ═══ */
function S_DeviceCuff() {
  return (
    <div className="slide" id="slide-device-cuff">
      <SlideLogo />
      <div className="slide-inner">
        <Reveal>
          <div className="phase-header">
            <div className="phase-header-pill">THE DEVICE</div>
            <div className="title" style={{ color: 'var(--green)', fontSize: 'clamp(36px, 4.5vw, 52px)', marginBottom: 0, textAlign: 'center' }}>Bova Nerve Cuff</div>
          </div>
        </Reveal>
        <Reveal delay={0.1}>
          <div className="device-spec-row">
            <div className="device-spec-card">
              <div className="device-spec-num">8</div>
              <div className="device-spec-label">Electrode Sites</div>
              <div className="device-spec-sub">Fascicle-selective stimulation</div>
            </div>
            <div className="device-spec-card">
              <div className="device-spec-num">5 yr</div>
              <div className="device-spec-label">Implant Life</div>
              <div className="device-spec-sub">Polymer encapsulated</div>
            </div>
            <div className="device-spec-card">
              <div className="device-spec-num">IPG</div>
              <div className="device-spec-label">Pulse Generator</div>
              <div className="device-spec-sub">Implantable, closed-loop</div>
            </div>
          </div>
        </Reveal>
        <Reveal delay={0.3}>
          <div className="device-cuff-tagline">
            Eight electrodes because that's what our models show is the sweet spot for <span className="hi">fascicle-selective stimulation</span>.
          </div>
        </Reveal>
      </div>
    </div>
  )
}

/* ═══ PRODUCT DEMO — exploded view (full-bleed) ═══ */
function S_DemoExploded() {
  return (
    <div className="slide demo-fullscreen" id="slide-demo-exploded">
      <video className="demo-fullscreen-video" src="/exploded-view.mp4" autoPlay loop muted playsInline />
      <div className="demo-fullscreen-overlay" />
      <SlideLogo />
      <div className="demo-fullscreen-meta">
        <Reveal>
          <div className="demo-fullscreen-title">The Build</div>
        </Reveal>
      </div>
    </div>
  )
}

/* ═══ PRODUCT DEMO — MEA connector (full-bleed) ═══ */
function S_DemoMEA() {
  return (
    <div className="slide demo-fullscreen" id="slide-demo-mea">
      <video className="demo-fullscreen-video" src="/mea-connector.mp4" autoPlay loop muted playsInline />
      <div className="demo-fullscreen-overlay" />
      <SlideLogo />
      <div className="demo-fullscreen-meta">
        <Reveal>
          <div className="demo-fullscreen-title">The Connector</div>
        </Reveal>
      </div>
    </div>
  )
}

/* ═══ NERVE FIELDS — cross-section field + sweet spot combined ═══ */
function S_NerveFields() {
  return (
    <div className="slide nerve-slide" id="slide-nerve-fields">
      <SlideLogo />
      <div className="slide-inner nerve-minimal">
        <Reveal>
          <div className="label nerve-label">Simulation · 03</div>
        </Reveal>
        <Reveal delay={0.1}>
          <div className="nerve-title-center">
            Eight contacts. <span className="nerve-hi">Sweet spot.</span>
          </div>
        </Reveal>
        <div className="nerve-dual-figures">
          <ScaleIn delay={0.2} className="nerve-figure-hero nerve-figure-dual">
            <img src="/nerve1.jpg" alt="Cross-section field distribution" className="nerve-figure" />
          </ScaleIn>
          <ScaleIn delay={0.3} className="nerve-figure-hero nerve-figure-dual">
            <img src="/nerve2.jpg" alt="Optimal target regions — top 6 fascicles" className="nerve-figure" />
          </ScaleIn>
        </div>
        <Reveal delay={0.4}>
          <div className="nerve-eta-row">
            <div className="nerve-eta">
              <div className="nerve-eta-val">0.62</div>
              <div className="nerve-eta-label">Bipolar</div>
            </div>
            <div className="nerve-eta-arrow">→</div>
            <div className="nerve-eta">
              <div className="nerve-eta-val">0.83</div>
              <div className="nerve-eta-label">4 contact</div>
            </div>
            <div className="nerve-eta-arrow">→</div>
            <div className="nerve-eta highlight">
              <div className="nerve-eta-val">0.85</div>
              <div className="nerve-eta-label">8 contact</div>
            </div>
            <div className="nerve-eta-arrow">=</div>
            <div className="nerve-eta dimmed">
              <div className="nerve-eta-val">0.85</div>
              <div className="nerve-eta-label">16 contact</div>
            </div>
          </div>
        </Reveal>
      </div>
    </div>
  )
}

/* ═══ NERVE 3 — pig → bovine PCA transform ═══ */
function S_Nerve3() {
  return (
    <div className="slide nerve-slide" id="slide-nerve-3">
      <SlideLogo />
      <div className="slide-inner nerve-minimal">
        <Reveal>
          <div className="label nerve-label">Simulation · 01</div>
        </Reveal>
        <Reveal delay={0.1}>
          <div className="nerve-title-center">Pig → bovine.</div>
        </Reveal>
        <ScaleIn delay={0.2} className="nerve-figure-hero nerve-figure-hero-wide">
          <img src="/nerve3.png" alt="P12-1 pig to bovine PCA transform" className="nerve-figure nerve-figure-wide" />
        </ScaleIn>
        <Reveal delay={0.35}>
          <div className="nerve-caption">57 vagal + 46 sympathetic fascicles · first bovine vagosympathetic trunk model</div>
        </Reveal>
      </div>
    </div>
  )
}

/* ═══ NERVE 4 — video demonstration (full-bleed) ═══ */
function S_Nerve4() {
  return (
    <div className="slide demo-fullscreen" id="slide-nerve-4">
      <video className="demo-fullscreen-video" src="/nerve5.mp4" autoPlay loop muted playsInline />
      <div className="demo-fullscreen-overlay" />
      <SlideLogo />
      <div className="demo-fullscreen-meta">
        <Reveal>
          <div className="demo-fullscreen-label nerve-label">Simulation · 02</div>
        </Reveal>
        <Reveal delay={0.1}>
          <div className="demo-fullscreen-title">FEM in motion.</div>
        </Reveal>
      </div>
    </div>
  )
}

/* ═══ SIMULATION — FIRST BOVINE VNS FEM ═══ */
function S_Simulation() {
  return (
    <div className="slide sage sim-result-slide" id="slide-simulation">
      <SlideLogo />
      <div className="slide-inner sim-result-layout">
        <Reveal>
          <div className="label">The Result</div>
        </Reveal>
        <Reveal delay={0.1}>
          <div className="sim-result-title">
            Selectivity Index = <span className="hi">1.00</span>
          </div>
        </Reveal>
        <ScaleIn delay={0.2}>
          <div className="sim-result-caption">at 0.91 mA · 2,850 axons · first bovine VNS simulation ever run</div>
        </ScaleIn>
      </div>
    </div>
  )
}

/* ═══ CONCLUSION / QR CODE ═══ */
function S_Conclusion() {
  return (
    <div className="slide sage" id="slide-conclusion">
      <SlideLogo />
      <div className="slide-inner" style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Reveal>
          <div className="label">The Ask</div>
        </Reveal>
        <Reveal delay={0.1}>
          <div className="title" style={{ fontSize: 'clamp(36px, 5vw, 60px)', marginBottom: 12 }}>
            Our first experiment costs <span className="hi">$5,000</span>.
          </div>
        </Reveal>
        <Reveal delay={0.2}>
          <div className="subtitle" style={{ textAlign: 'center', margin: '0 auto 36px', maxWidth: 700 }}>
            Ex vivo bovine cervical vagus — abattoir tissue, morphometry and impedance spectroscopy. Turns every simulation number into real-tissue data before a single live animal.
          </div>
        </Reveal>
        <Reveal delay={0.3}>
          <a
            className="conclusion-qr"
            href="https://bova.martinlombard.com"
            target="_blank"
            rel="noopener noreferrer"
          >
            <div className="qr-url">bova.martinlombard.com</div>
            <div className="qr-box">
              <img src="/qrcode.png" alt="Scan for Bova report" />
            </div>
            <div className="qr-label">Read the full Bova report</div>
          </a>
        </Reveal>
      </div>
    </div>
  )
}

/* ═══ FONT PICKER (temporary) ═══ */
function FontPicker() {
  const fonts = [
    // Clean serifs
    { name: 'Fraunces', family: "'Fraunces', serif", weight: 800, vibe: 'Warm editorial' },
    { name: 'Recoleta', family: "'Recoleta', serif", weight: 700, vibe: 'Premium rounded' },
    { name: 'Playfair Display', family: "'Playfair Display', serif", weight: 900, vibe: 'High contrast' },
    { name: 'DM Serif Display', family: "'DM Serif Display', serif", weight: 400, vibe: 'Elegant hairline' },
    { name: 'Cormorant', family: "'Cormorant Garamond', serif", weight: 700, vibe: 'Literary classic' },
    { name: 'Libre Bodoni', family: "'Libre Bodoni', serif", weight: 700, vibe: 'Clean bodoni' },
    { name: 'Crimson Pro', family: "'Crimson Pro', serif", weight: 700, vibe: 'Book serif' },
    { name: 'Instrument Serif', family: "'Instrument Serif', serif", weight: 400, vibe: 'Modern editorial' },

    // Clean modern sans
    { name: 'Clash Display', family: "'Clash Display', sans-serif", weight: 700, vibe: 'Confident brand' },
    { name: 'Space Grotesk', family: "'Space Grotesk', sans-serif", weight: 700, vibe: 'Techy geometric' },
    { name: 'General Sans', family: "'General Sans', sans-serif", weight: 600, vibe: 'Neutral SaaS' },
    { name: 'Manrope', family: "'Manrope', sans-serif", weight: 800, vibe: 'Rounded geometric' },
    { name: 'Outfit', family: "'Outfit', sans-serif", weight: 800, vibe: 'Modern geometric' },
    { name: 'Epilogue', family: "'Epilogue', sans-serif", weight: 800, vibe: 'Sharp grotesque' },
    { name: 'Inter Tight', family: "'Inter Tight', sans-serif", weight: 800, vibe: 'Clean tight' },
    { name: 'Sora', family: "'Sora', sans-serif", weight: 800, vibe: 'Minimal techy' },
    { name: 'Bricolage', family: "'Bricolage Grotesque', sans-serif", weight: 800, vibe: 'Soft grotesque' },
  ]
  return (
    <div className="slide" id="slide-font-picker" style={{ background: 'var(--bg-soft)' }}>
      <SlideLogo />
      <div className="slide-inner">
        <Reveal>
          <div className="title" style={{ marginBottom: 24, color: 'var(--green)', fontSize: 'clamp(32px, 4vw, 48px)', textAlign: 'center' }}>Logo Font Options</div>
        </Reveal>
        <div className="font-grid">
          {fonts.map((f, i) => (
            <ScaleIn key={f.name} delay={0.1 + i * 0.08}>
              <div className="font-option">
                <div
                  className="font-preview"
                  style={{
                    fontFamily: f.family,
                    fontWeight: f.weight,
                    fontStyle: f.italic ? 'italic' : 'normal',
                  }}
                >
                  Bova
                </div>
                <div className="font-name">{f.name}</div>
                <div className="font-vibe">{f.vibe}</div>
              </div>
            </ScaleIn>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ═══ S15 — CLOSE ═══ */
function S13() {
  return (
    <div className="slide close-black close-hero-bg" id="slide-14">
      <div className="slide-inner">
        <div className="close-wrap">
          <Reveal>
            <img src="/logo.png" alt="Bova" className="logo-close-big" />
          </Reveal>
          <Reveal delay={0.2}>
            <div className="close-brand-big">Bova</div>
          </Reveal>
          <Reveal delay={0.4}>
            <div className="close-motto-big">Neuromodulation for the herd.</div>
          </Reveal>
        </div>
      </div>
      <Reveal delay={0.6}>
        <a
          className="dashboard-cta"
          href="https://bova-dashboard.vercel.app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <span className="dashboard-cta-label">Live Dashboard</span>
          <span className="dashboard-cta-arrow">→</span>
        </a>
      </Reveal>
    </div>
  )
}


/* ═══════════════════════════════════════
   APP
   ═══════════════════════════════════════ */
export default function App() {
  const [cur, setCur] = useState(0)

  const goTo = useCallback((i) => {
    const clamped = Math.max(0, Math.min(i, TOTAL - 1))
    // Use explicit pixel scroll so scroll-snap-type: mandatory can't fight us
    window.scrollTo({ top: clamped * window.innerHeight, behavior: 'smooth' })
  }, [])

  const onScroll = useCallback(() => {
    setCur(Math.min(Math.round(window.scrollY / window.innerHeight), TOTAL - 1))
  }, [])

  useEffect(() => {
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [onScroll])

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === ' ' || e.key === 'j') {
        e.preventDefault()
        goTo(cur + 1)
      } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft' || e.key === 'k') {
        e.preventDefault()
        goTo(cur - 1)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [cur, goTo])

  return (
    <>
      <div className="progress-bar" style={{ width: `${((cur + 1) / TOTAL) * 100}%` }} />
      <nav className="nav-arrows" aria-label="Slide navigation">
        <button
          className="nav-arrow"
          onClick={() => goTo(cur - 1)}
          disabled={cur === 0}
          aria-label="Previous slide"
        >
          <ChevronLeft size={22} strokeWidth={2.5} />
        </button>
        <div className="nav-arrow-count">{cur + 1} / {TOTAL}</div>
        <button
          className="nav-arrow"
          onClick={() => goTo(cur + 1)}
          disabled={cur === TOTAL - 1}
          aria-label="Next slide"
        >
          <ChevronRight size={22} strokeWidth={2.5} />
        </button>
      </nav>
      {/* ═══ THE PROBLEM — Dameer (42s) ═══ */}
      <S1 />                {/* Hook — $1.3B lost, same nerve different animal */}
      <S_ProblemCircles />  {/* Three broken systems — stress meat / disease / antibiotics */}
      <S_VagusControls />   {/* Vagus controls: inflammation / gut / stress / immune */}
      <S_VNSProven />       {/* VNS FDA-approved since 1997, never in cattle + 600kg simpler */}
      <S_GoatDemo />        {/* Goat dissection wet-lab video (proof the procedure works) */}

      {/* ═══ THE DEVICE — Martin (~50s) ═══ */}
      <S_DeviceCuff />      {/* Nerve cuff — 8 electrodes, IPG, 5yr life */}
      <S_DemoExploded />    {/* Full-screen exploded-view CAD video */}
      <S_DemoMEA />         {/* Full-screen MEA connector CAD video */}
      <S_Nerve3 />          {/* Pig -> bovine PCA transform (comes first) */}
      <S_Nerve4 />          {/* FEM video demonstration */}
      <S_NerveFields />     {/* Cross-section field + sweet spot combined */}

      {/* ═══ ROADMAP & COMPETITIVE EDGE — Sidney ═══ */}
      <S_Tessman />         {/* Tessman lower-third citation */}
      <S14_Roadmap />       {/* Commercial roadmap (wavy path) */}
      <S14b_Phase1 />       {/* Phase 1 — Nerve cuff validation */}
      <S14c_Phase2 />       {/* Phase 2 — VNS efficacy trial (CVM + feedlot) */}
      <S14d_Phase3 />       {/* Phase 3 — Stentrode, minimally invasive long-term */}
      <S_TessmanPoints />   {/* Tessman 3 key points — validation before economics */}
      <S13_Roadmap />       {/* Unit economics circles */}
      <S11 />               {/* Moonshot — 100k cows */}
      <S11b_Licensing />    {/* Licensing to SetPoint/LivaNova/Inspire */}

      {/* ═══ CONCLUSION ═══ */}
      <S_Conclusion />      {/* $5,000 first experiment + QR / blog */}
      <S13 />               {/* Bova logo + motto close */}
    </>
  )
}
