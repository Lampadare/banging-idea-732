import React, { useState, useMemo } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, AreaChart, Area } from 'recharts'
import { Calculator, Activity, FlaskConical, DollarSign, LineChart as LineChartIcon, Heart, Beaker, TrendingDown, Zap } from 'lucide-react'
import './App.css'

const GREEN = '#2DA87A'
const RED = '#C45B3C'
const AMBER = '#E5A030'
const LIGHT = '#6BC4A0'
const COLORS = [GREEN, LIGHT, AMBER, '#A8DBCA']

/* ════════════════════════════════════════
   DEVICE COST DATA per approach
   ════════════════════════════════════════ */
const APPROACHES = {
  cuff: {
    name: 'Phase 1 — Nerve Cuff (Research)',
    surgeryTime: '30-60 min',
    description: 'Research-grade surgical pilot for mechanism validation. Not a product cost.',
    sections: [
      { title: 'Device Components (research grade)', items: [
        { name: 'Pt-Ir nerve cuff electrode (pilot fab)', lo: 600, hi: 1200 },
        { name: 'Stimulation + recording ASIC', lo: 100, hi: 200 },
        { name: 'Analog front-end + ADC', lo: 80, hi: 150 },
        { name: 'Microcontroller', lo: 6, hi: 12 },
        { name: 'Primary lithium battery + PMIC', lo: 30, hi: 55 },
        { name: 'Biocompatible encapsulation (silicone/parylene)', lo: 50, hi: 100 },
        { name: 'PCB fabrication + assembly (low volume)', lo: 50, hi: 90 },
        { name: 'Lead wires (Pt-Ir, silicone insulated)', lo: 20, hi: 40 },
      ]},
      { title: 'Procedure — Veterinary Surgery', items: [
        { name: 'Veterinarian surgical time (45 min @ $200/hr)', lo: 140, hi: 220 },
        { name: 'Vet tech / assistant (45 min)', lo: 30, hi: 50 },
        { name: 'Sedation (xylazine 0.05mg/kg IV)', lo: 6, hi: 12 },
        { name: 'Local anaesthesia (lidocaine 2%)', lo: 2, hi: 5 },
      ]},
      { title: 'Procedure — Imaging', items: [
        { name: 'Portable ultrasound (amortised per head)', lo: 10, hi: 20 },
      ]},
      { title: 'Procedure — Consumables', items: [
        { name: 'Sterile surgical drape + field', lo: 4, hi: 8 },
        { name: 'Scalpel + surgical tools (amortised)', lo: 3, hi: 8 },
        { name: 'Sterile gloves + prep', lo: 3, hi: 6 },
      ]},
      { title: 'Post-Procedure', items: [
        { name: 'Anti-inflammatory (meloxicam / flunixin)', lo: 2, hi: 5 },
        { name: 'Follow-up check (day 3, 5 min vet time)', lo: 6, hi: 12 },
      ]},
    ],
  },
  stentResearch: {
    name: 'Phase 2 — Stent Prototype (Catheter)',
    surgeryTime: '8-12 min',
    description: 'Catheter-only procedure. No surgery, no sedation beyond chute restraint.',
    sections: [
      { title: 'Device Components (prototype)', items: [
        { name: 'Stent electrode array (prototype fab)', lo: 24, hi: 60 },
        { name: 'Stimulation + recording ASIC', lo: 12, hi: 25 },
        { name: 'Microcontroller + power management', lo: 3, hi: 8 },
        { name: 'Primary cell battery (duty cycled)', lo: 4, hi: 8 },
        { name: 'Polymer encapsulation', lo: 5, hi: 10 },
        { name: 'Assembly + sterile packaging', lo: 4, hi: 10 },
      ]},
      { title: 'Procedure — Technician (catheter)', items: [
        { name: 'Trained technician (10 min @ $50/hr, chute-side)', lo: 6, hi: 10 },
      ]},
      { title: 'Procedure — Consumables', items: [
        { name: 'Single-use delivery catheter', lo: 5, hi: 12 },
        { name: 'Introducer sheath', lo: 4, hi: 10 },
        { name: 'Heparinised saline flush', lo: 1, hi: 3 },
        { name: 'Sterile gloves + prep', lo: 2, hi: 4 },
      ]},
    ],
  },
  stentCommercial: {
    name: 'Phase 3 — Stent at Scale (100k units)',
    surgeryTime: '8-12 min',
    description: 'Commercial BOM at 100k manufacturing volumes. Catheter-only.',
    sections: [
      { title: 'Device BOM @ 100k units', items: [
        { name: 'Nitinol stent scaffold', lo: 10, hi: 18 },
        { name: 'Thin-film electrode array', lo: 8, hi: 15 },
        { name: 'Stimulation + recording ASIC', lo: 8, hi: 12 },
        { name: 'MCU', lo: 1, hi: 1 },
        { name: 'Primary cell battery (duty cycled, 150d)', lo: 3, hi: 5 },
        { name: 'Power supply passives', lo: 1, hi: 2 },
        { name: 'Polymer encapsulation', lo: 3, hi: 6 },
        { name: 'Delivery catheter (single-use)', lo: 5, hi: 10 },
        { name: 'Assembly + sterile packaging', lo: 3, hi: 5 },
      ]},
      { title: 'Procedure — Technician (catheter)', items: [
        { name: 'Trained technician (10 min @ $50/hr)', lo: 4, hi: 6 },
      ]},
      { title: 'Procedure — Consumables', items: [
        { name: 'Venipuncture kit', lo: 1, hi: 2 },
        { name: 'Heparin flush + gloves', lo: 1, hi: 1 },
      ]},
    ],
  },
}

/* ════════════════════════════════════════
   ECONOMICS CALCULATOR
   ════════════════════════════════════════ */
function EconomicsPage() {
  const [approach, setApproach] = useState('cuff')
  const [herdSize, setHerdSize] = useState(200)
  const [brdRate, setBrdRate] = useState(16.2)
  const [brdCost, setBrdCost] = useState(50)
  const [brdReduction, setBrdReduction] = useState(25)
  const [darkCutRate, setDarkCutRate] = useState(1.8)
  const [darkCutDiscount, setDarkCutDiscount] = useState(38.75)
  const [darkCutReduction, setDarkCutReduction] = useState(30)
  const [scaleUnits, setScaleUnits] = useState(100000)
  const [pilotSize, setPilotSize] = useState(20)
  const [controlPct, setControlPct] = useState(50)
  const [trialDays, setTrialDays] = useState(150)
  const [vetVisitsPerWeek, setVetVisitsPerWeek] = useState(2)
  const [dataAnalysisCost, setDataAnalysisCost] = useState(5000)

  const ap = APPROACHES[approach]

  const calc = useMemo(() => {
    const sectionTotals = ap.sections.map(sec => ({
      title: sec.title,
      items: sec.items,
      totalLo: sec.items.reduce((s, i) => s + i.lo, 0),
      totalHi: sec.items.reduce((s, i) => s + i.hi, 0),
      total: sec.items.reduce((s, i) => s + (i.lo + i.hi) / 2, 0),
    }))

    const totalPerHeadLo = sectionTotals.reduce((s, sec) => s + sec.totalLo, 0)
    const totalPerHeadHi = sectionTotals.reduce((s, sec) => s + sec.totalHi, 0)
    const totalPerHead = (totalPerHeadLo + totalPerHeadHi) / 2
    const deviceBOM = sectionTotals.filter(s => s.title.includes('Component') || s.title.includes('BOM')).reduce((s, sec) => s + sec.total, 0)
    const procedureCost = sectionTotals.filter(s => s.title.includes('Procedure')).reduce((s, sec) => s + sec.total, 0)
    const postCost = sectionTotals.filter(s => s.title.includes('Post')).reduce((s, sec) => s + sec.total, 0)
    const surgeryCost = procedureCost + postCost

    const brdSaving = (brdRate / 100) * brdCost * (brdReduction / 100)
    const darkCutSaving = (darkCutRate / 100) * darkCutDiscount * 8 * (darkCutReduction / 100)
    const totalValue = brdSaving + darkCutSaving
    const margin = totalValue - totalPerHead
    const totalHerdValue = totalValue * herdSize
    const totalHerdCost = totalPerHead * herdSize
    const totalHerdMargin = margin * herdSize
    const roi = totalPerHead > 0 ? ((totalValue / totalPerHead - 1) * 100) : 0

    // Pilot economics
    const treatmentHead = Math.round(pilotSize * (1 - controlPct / 100))
    const controlHead = pilotSize - treatmentHead
    const pilotDeviceCost = treatmentHead * totalPerHead
    const pilotWeeks = Math.ceil(trialDays / 7)
    const pilotVetMonitoring = pilotWeeks * vetVisitsPerWeek * 50
    const pilotDataAnalysis = dataAnalysisCost
    const pilotBloodwork = pilotSize * 4 * 25
    const pilotOverhead = pilotSize * 5 * (trialDays / 30)
    const pilotTotalFixed = pilotVetMonitoring + pilotDataAnalysis + pilotBloodwork + pilotOverhead
    const pilotTotal = pilotDeviceCost + pilotTotalFixed

    return {
      sectionTotals, deviceBOM, surgeryCost, totalPerHead,
      totalPerHeadLo, totalPerHeadHi,
      brdSaving, darkCutSaving, totalValue, margin, roi,
      totalHerdValue, totalHerdCost, totalHerdMargin,
      treatmentHead, controlHead, pilotDeviceCost, pilotVetMonitoring,
      pilotDataAnalysis, pilotBloodwork, pilotOverhead,
      pilotTotalFixed, pilotTotal, pilotWeeks,
    }
  }, [approach, herdSize, brdRate, brdCost, brdReduction, darkCutRate, darkCutDiscount, darkCutReduction, pilotSize, controlPct, trialDays, vetVisitsPerWeek, dataAnalysisCost])

  const valueBreakdown = [
    { name: 'BRD reduction', value: Math.round(calc.brdSaving * 100) / 100 },
    { name: 'Dark cutting', value: Math.round(calc.darkCutSaving * 100) / 100 },
  ]

  const costVsValue = [
    { name: 'Device', cost: calc.deviceBOM, value: 0 },
    { name: 'Procedure', cost: calc.surgeryCost, value: 0 },
    { name: 'BRD saving', cost: 0, value: calc.brdSaving },
    { name: 'Dark cutting', cost: 0, value: calc.darkCutSaving },
  ]

  return (
    <>
      <div className="page-title">Unit Economics Calculator</div>

      <div className="approach-tabs">
        {Object.entries(APPROACHES).map(([key, val]) => (
          <button key={key} className={`approach-tab ${approach === key ? 'active' : ''}`} onClick={() => setApproach(key)}>
            {val.name}
          </button>
        ))}
      </div>

      <div className="card-grid">
        <div className="card"><div className="card-label">Value per head</div><div className="card-value">${calc.totalValue.toFixed(0)}</div><div className="card-sub">BRD + dark cutting avoided</div></div>
        <div className="card"><div className="card-label">Cost per head</div><div className="card-value red" style={{ fontSize: 22 }}>${calc.totalPerHeadLo}–{calc.totalPerHeadHi}</div><div className="card-sub">Device + procedure ({ap.surgeryTime})</div></div>
        <div className="card"><div className="card-label">Net margin</div><div className="card-value" style={{ color: calc.margin > 0 ? GREEN : RED }}>${calc.margin.toFixed(0)}</div><div className="card-sub">Per head</div></div>
        <div className="card"><div className="card-label">ROI</div><div className="card-value" style={{ color: calc.roi > 0 ? GREEN : RED }}>{calc.roi.toFixed(0)}%</div><div className="card-sub">Return on device cost</div></div>
      </div>

      <div className="two-col">
        <div>
          <div className="slider-section">
            <div className="slider-title">Revenue Assumptions</div>
            <div className="slider-grid">
              <Slider label="Herd size" value={herdSize} set={setHerdSize} min={50} max={5000} step={50} suffix=" head" />
              <Slider label="BRD incidence" value={brdRate} set={setBrdRate} min={5} max={30} step={0.1} suffix="%" />
              <Slider label="BRD cost per case" value={brdCost} set={setBrdCost} min={30} max={250} prefix="$" />
              <Slider label="BRD reduction" value={brdReduction} set={setBrdReduction} min={10} max={50} suffix="%" />
              <Slider label="Dark cut rate" value={darkCutRate} set={setDarkCutRate} min={0.5} max={5} step={0.1} suffix="%" />
              <Slider label="Dark cut discount" value={darkCutDiscount} set={setDarkCutDiscount} min={20} max={60} step={0.25} prefix="$" suffix="/cwt" />
              <Slider label="Dark cut reduction" value={darkCutReduction} set={setDarkCutReduction} min={10} max={60} suffix="%" />
            </div>
          </div>

          <div className="slider-section">
            <div className="slider-title">Pilot Program Assumptions</div>
            <div className="slider-grid">
              <Slider label="Pilot size" value={pilotSize} set={setPilotSize} min={10} max={200} step={5} suffix=" head" />
              <Slider label="Control group" value={controlPct} set={setControlPct} min={25} max={75} suffix="%" />
              <Slider label="Trial duration" value={trialDays} set={setTrialDays} min={30} max={180} step={10} suffix=" days" />
              <Slider label="Vet visits / week" value={vetVisitsPerWeek} set={setVetVisitsPerWeek} min={1} max={5} />
              <Slider label="Data analysis budget" value={dataAnalysisCost} set={setDataAnalysisCost} min={1000} max={20000} step={1000} prefix="$" />
              <Slider label="Scale projection" value={scaleUnits} set={setScaleUnits} min={100} max={100000} step={100} suffix=" units" />
            </div>
          </div>
        </div>

        <div>
          <div className="chart-card">
            <div className="chart-title">Value Breakdown per Head</div>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={valueBreakdown} layout="vertical" margin={{ left: 100 }}>
                <XAxis type="number" tickFormatter={v => `$${v}`} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 13, fontWeight: 600 }} />
                <Tooltip formatter={v => `$${v.toFixed(2)}`} />
                <Bar dataKey="value" fill={GREEN} radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <div className="chart-title">Cost vs Value per Head</div>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={costVsValue} margin={{ left: 20 }}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tickFormatter={v => `$${v}`} />
                <Tooltip formatter={v => `$${v.toFixed(2)}`} />
                <Bar dataKey="cost" fill={RED} radius={[6, 6, 0, 0]} name="Cost" />
                <Bar dataKey="value" fill={GREEN} radius={[6, 6, 0, 0]} name="Value" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="two-col" style={{ marginTop: 24 }}>
        <div className="chart-card">
          <div className="chart-title">Full Cost Breakdown — {ap.name}</div>
          <table className="cost-table">
            <thead><tr><th>Item</th><th>Cost range</th></tr></thead>
            <tbody>
              {calc.sectionTotals.map(sec => (
                <React.Fragment key={sec.title}>
                  <tr><td colSpan={2} style={{ fontWeight: 700, color: 'var(--green)', fontSize: 12, letterSpacing: 1, textTransform: 'uppercase', paddingTop: 16, borderBottom: 'none' }}>{sec.title}</td></tr>
                  {sec.items.map(i => (
                    <tr key={i.name}><td>{i.name}</td><td>{i.lo === i.hi ? `$${i.lo}` : `$${i.lo}–${i.hi}`}</td></tr>
                  ))}
                  <tr style={{ borderBottom: '2px solid var(--border)' }}><td style={{ fontWeight: 700 }}>Subtotal</td><td style={{ fontWeight: 700 }}>${sec.totalLo}–{sec.totalHi}</td></tr>
                </React.Fragment>
              ))}
              <tr className="total-row"><td>Total per head</td><td>${calc.totalPerHeadLo}–{calc.totalPerHeadHi}</td></tr>
            </tbody>
          </table>
        </div>

        <div className="chart-card">
          <div className="chart-title">Phase Cost Comparison (log scale, range per head)</div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={Object.entries(APPROACHES).map(([key, a]) => {
              const lo = a.sections.reduce((s, sec) => s + sec.items.reduce((ss, i) => ss + i.lo, 0), 0)
              const hi = a.sections.reduce((s, sec) => s + sec.items.reduce((ss, i) => ss + i.hi, 0), 0)
              return { name: a.name.split(' — ')[0], low: lo, range: hi - lo, lo, hi, label: `$${lo}–${hi}` }
            })} margin={{ left: 20, top: 30 }}>
              <XAxis dataKey="name" tick={{ fontSize: 13, fontWeight: 700 }} />
              <YAxis scale="log" domain={[1, 3000]} tickFormatter={v => `$${v}`} ticks={[10, 100, 1000, 3000]} />
              <Tooltip formatter={(v, name, item) => name === 'range' ? `$${item.payload.lo}–${item.payload.hi}` : `$${v}`} />
              <Bar dataKey="low" stackId="a" fill="transparent" name="min" />
              <Bar dataKey="range" stackId="a" radius={[6, 6, 0, 0]} name="range"
                   label={{ position: 'top', formatter: (v, item) => item && item.payload ? item.payload.label : '', fontSize: 11, fontWeight: 700, fill: 'var(--text)' }}>
                {Object.entries(APPROACHES).map(([key]) => (
                  <Cell key={key} fill={key === approach ? GREEN : '#C9D5CF'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Pilot Program Total Cost */}
      <div className="chart-card" style={{ marginTop: 24 }}>
        <div className="chart-title">Pilot Program Budget — {pilotSize} head, {trialDays} days</div>
        <div className="card-grid" style={{ marginBottom: 16 }}>
          <div className="card"><div className="card-label">Treatment group</div><div className="card-value">{calc.treatmentHead}</div><div className="card-sub">Devices implanted</div></div>
          <div className="card"><div className="card-label">Control group</div><div className="card-value" style={{ color: 'var(--text-sec)' }}>{calc.controlHead}</div><div className="card-sub">Sham / no device</div></div>
          <div className="card"><div className="card-label">Duration</div><div className="card-value" style={{ color: 'var(--text-sec)' }}>{calc.pilotWeeks}w</div><div className="card-sub">{trialDays} days</div></div>
        </div>
        <table className="cost-table">
          <thead><tr><th>Pilot Cost Item</th><th>Cost</th></tr></thead>
          <tbody>
            <tr><td>Devices ({calc.treatmentHead} head x ${calc.totalPerHead}/head)</td><td>${calc.pilotDeviceCost.toLocaleString()}</td></tr>
            <tr><td>Vet monitoring ({calc.pilotWeeks} weeks x {vetVisitsPerWeek}/week x $50/visit)</td><td>${calc.pilotVetMonitoring.toLocaleString()}</td></tr>
            <tr><td>Bloodwork ({pilotSize} head x 4 draws x $25)</td><td>${calc.pilotBloodwork.toLocaleString()}</td></tr>
            <tr><td>Data analysis + biostatistics</td><td>${calc.pilotDataAnalysis.toLocaleString()}</td></tr>
            <tr><td>Record keeping + overhead ({pilotSize} head x {Math.round(trialDays/30)} months)</td><td>${calc.pilotOverhead.toLocaleString()}</td></tr>
            <tr className="total-row"><td>Total Pilot Cost</td><td>${calc.pilotTotal.toLocaleString()}</td></tr>
          </tbody>
        </table>
      </div>

      {/* Herd summary */}
      <div className="card-grid" style={{ marginTop: 12 }}>
        <div className="card"><div className="card-label">Herd value</div><div className="card-value">${(calc.totalHerdValue).toLocaleString(undefined, {maximumFractionDigits: 0})}</div><div className="card-sub">{herdSize} head</div></div>
        <div className="card"><div className="card-label">Herd cost</div><div className="card-value red">${(calc.totalHerdCost).toLocaleString(undefined, {maximumFractionDigits: 0})}</div><div className="card-sub">Device + procedure</div></div>
        <div className="card"><div className="card-label">Net margin</div><div className="card-value" style={{ color: calc.totalHerdMargin > 0 ? GREEN : RED }}>${(calc.totalHerdMargin).toLocaleString(undefined, {maximumFractionDigits: 0})}</div></div>
      </div>
    </>
  )
}

/* ════════════════════════════════════════
   HERD DASHBOARD (farmer view mockup)
   ════════════════════════════════════════ */
const MOCK_COWS = [
  { id: 'BV-001', tag: '#4421', hr: 72, temp: 38.6, activity: 'Normal', status: 'healthy', vagalTone: 0.82, daysIn: 12, x: 25, y: 30 },
  { id: 'BV-002', tag: '#4422', hr: 88, temp: 39.4, activity: 'Low', status: 'alert', vagalTone: 0.61, daysIn: 8, x: 55, y: 20 },
  { id: 'BV-003', tag: '#4423', hr: 68, temp: 38.5, activity: 'Normal', status: 'healthy', vagalTone: 0.79, daysIn: 22, x: 70, y: 55 },
  { id: 'BV-004', tag: '#4424', hr: 95, temp: 40.1, activity: 'Very Low', status: 'critical', vagalTone: 0.42, daysIn: 5, x: 15, y: 65 },
  { id: 'BV-005', tag: '#4425', hr: 74, temp: 38.7, activity: 'Normal', status: 'healthy', vagalTone: 0.85, daysIn: 18, x: 45, y: 50 },
  { id: 'BV-006', tag: '#4426', hr: 82, temp: 39.1, activity: 'Moderate', status: 'alert', vagalTone: 0.58, daysIn: 3, x: 80, y: 30 },
  { id: 'BV-007', tag: '#4427', hr: 70, temp: 38.4, activity: 'High', status: 'healthy', vagalTone: 0.88, daysIn: 30, x: 35, y: 75 },
  { id: 'BV-008', tag: '#4428', hr: 66, temp: 38.3, activity: 'Normal', status: 'healthy', vagalTone: 0.91, daysIn: 45, x: 60, y: 75 },
  { id: 'BV-009', tag: '#4429', hr: 71, temp: 38.5, activity: 'Normal', status: 'healthy', vagalTone: 0.84, daysIn: 15, x: 20, y: 45 },
  { id: 'BV-010', tag: '#4430', hr: 76, temp: 38.8, activity: 'Normal', status: 'healthy', vagalTone: 0.77, daysIn: 10, x: 50, y: 35 },
  { id: 'BV-011', tag: '#4431', hr: 69, temp: 38.4, activity: 'High', status: 'healthy', vagalTone: 0.86, daysIn: 28, x: 75, y: 15 },
  { id: 'BV-012', tag: '#4432', hr: 84, temp: 39.2, activity: 'Low', status: 'alert', vagalTone: 0.55, daysIn: 6, x: 40, y: 15 },
  { id: 'BV-013', tag: '#4433', hr: 73, temp: 38.6, activity: 'Normal', status: 'healthy', vagalTone: 0.80, daysIn: 20, x: 88, y: 50 },
  { id: 'BV-014', tag: '#4434', hr: 67, temp: 38.3, activity: 'Normal', status: 'healthy', vagalTone: 0.89, daysIn: 35, x: 30, y: 55 },
  { id: 'BV-015', tag: '#4435', hr: 75, temp: 38.7, activity: 'Normal', status: 'healthy', vagalTone: 0.81, daysIn: 14, x: 65, y: 40 },
  { id: 'BV-016', tag: '#4436', hr: 70, temp: 38.5, activity: 'Normal', status: 'healthy', vagalTone: 0.83, daysIn: 25, x: 12, y: 20 },
  { id: 'BV-017', tag: '#4437', hr: 79, temp: 39.0, activity: 'Moderate', status: 'healthy', vagalTone: 0.72, daysIn: 9, x: 85, y: 70 },
  { id: 'BV-018', tag: '#4438', hr: 68, temp: 38.4, activity: 'Normal', status: 'healthy', vagalTone: 0.87, daysIn: 40, x: 48, y: 65 },
  { id: 'BV-019', tag: '#4439', hr: 91, temp: 39.6, activity: 'Very Low', status: 'alert', vagalTone: 0.48, daysIn: 4, x: 72, y: 80 },
  { id: 'BV-020', tag: '#4440', hr: 65, temp: 38.2, activity: 'High', status: 'healthy', vagalTone: 0.93, daysIn: 50, x: 22, y: 82 },
  { id: 'BV-021', tag: '#4441', hr: 71, temp: 38.5, activity: 'Normal', status: 'healthy', vagalTone: 0.85, daysIn: 11, x: 18, y: 38 },
  { id: 'BV-022', tag: '#4442', hr: 73, temp: 38.6, activity: 'Normal', status: 'healthy', vagalTone: 0.82, daysIn: 17, x: 52, y: 28 },
  { id: 'BV-023', tag: '#4443', hr: 68, temp: 38.4, activity: 'Normal', status: 'healthy', vagalTone: 0.88, daysIn: 23, x: 68, y: 45 },
  { id: 'BV-024', tag: '#4444', hr: 80, temp: 39.0, activity: 'Moderate', status: 'alert', vagalTone: 0.64, daysIn: 7, x: 82, y: 22 },
  { id: 'BV-025', tag: '#4445', hr: 72, temp: 38.5, activity: 'Normal', status: 'healthy', vagalTone: 0.84, daysIn: 27, x: 38, y: 42 },
  { id: 'BV-026', tag: '#4446', hr: 74, temp: 38.7, activity: 'Normal', status: 'healthy', vagalTone: 0.80, daysIn: 13, x: 72, y: 62 },
  { id: 'BV-027', tag: '#4447', hr: 69, temp: 38.4, activity: 'High', status: 'healthy', vagalTone: 0.89, daysIn: 33, x: 42, y: 72 },
  { id: 'BV-028', tag: '#4448', hr: 77, temp: 38.9, activity: 'Normal', status: 'healthy', vagalTone: 0.76, daysIn: 19, x: 15, y: 58 },
  { id: 'BV-029', tag: '#4449', hr: 67, temp: 38.3, activity: 'Normal', status: 'healthy', vagalTone: 0.90, daysIn: 38, x: 58, y: 20 },
  { id: 'BV-030', tag: '#4450', hr: 70, temp: 38.5, activity: 'Normal', status: 'healthy', vagalTone: 0.87, daysIn: 24, x: 78, y: 78 },
  { id: 'BV-031', tag: '#4451', hr: 72, temp: 38.6, activity: 'Normal', status: 'healthy', vagalTone: 0.83, daysIn: 16, x: 32, y: 24 },
  { id: 'BV-032', tag: '#4452', hr: 75, temp: 38.8, activity: 'Normal', status: 'healthy', vagalTone: 0.79, daysIn: 11, x: 62, y: 50 },
  { id: 'BV-033', tag: '#4453', hr: 68, temp: 38.4, activity: 'High', status: 'healthy', vagalTone: 0.89, daysIn: 29, x: 25, y: 68 },
  { id: 'BV-034', tag: '#4454', hr: 86, temp: 39.3, activity: 'Low', status: 'alert', vagalTone: 0.59, daysIn: 5, x: 85, y: 38 },
  { id: 'BV-035', tag: '#4455', hr: 71, temp: 38.5, activity: 'Normal', status: 'healthy', vagalTone: 0.85, daysIn: 21, x: 48, y: 80 },
  { id: 'BV-036', tag: '#4456', hr: 69, temp: 38.4, activity: 'Normal', status: 'healthy', vagalTone: 0.86, daysIn: 35, x: 12, y: 48 },
  { id: 'BV-037', tag: '#4457', hr: 73, temp: 38.6, activity: 'Normal', status: 'healthy', vagalTone: 0.82, daysIn: 12, x: 82, y: 55 },
  { id: 'BV-038', tag: '#4458', hr: 70, temp: 38.5, activity: 'Normal', status: 'healthy', vagalTone: 0.85, daysIn: 26, x: 38, y: 58 },
  { id: 'BV-039', tag: '#4459', hr: 67, temp: 38.3, activity: 'Normal', status: 'healthy', vagalTone: 0.91, daysIn: 42, x: 55, y: 82 },
  { id: 'BV-040', tag: '#4460', hr: 72, temp: 38.6, activity: 'Normal', status: 'healthy', vagalTone: 0.84, daysIn: 15, x: 28, y: 15 },
]

const MOCK_HR_TREND = Array.from({ length: 24 }, (_, i) => ({
  hour: `${i}:00`,
  healthy: 65 + Math.random() * 10,
  alert: 78 + Math.random() * 15,
  critical: 88 + Math.random() * 12,
}))

function CowIcon({ size = 20, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      {/* Head */}
      <ellipse cx="12" cy="11" rx="5" ry="6" />
      {/* Horns */}
      <path d="M7 7 Q4 3 3 5" />
      <path d="M17 7 Q20 3 21 5" />
      {/* Ears */}
      <path d="M7.5 8 Q5 7 5.5 9" />
      <path d="M16.5 8 Q19 7 18.5 9" />
      {/* Eyes */}
      <circle cx="10" cy="10" r="0.8" fill={color} stroke="none" />
      <circle cx="14" cy="10" r="0.8" fill={color} stroke="none" />
      {/* Nostrils */}
      <circle cx="10.5" cy="13.5" r="0.6" fill={color} stroke="none" />
      <circle cx="13.5" cy="13.5" r="0.6" fill={color} stroke="none" />
      {/* Muzzle */}
      <path d="M9 13 Q12 16 15 13" />
    </svg>
  )
}

function useCowPositions(cows) {
  const [positions, setPositions] = useState(() =>
    cows.map(c => ({ id: c.id, x: c.x, y: c.y, targetX: c.x, targetY: c.y }))
  )

  React.useEffect(() => {
    const interval = setInterval(() => {
      setPositions(prev => prev.map(p => {
        // Pick new target occasionally
        const needsNewTarget = Math.abs(p.x - p.targetX) < 0.2 && Math.abs(p.y - p.targetY) < 0.2
        const targetX = needsNewTarget ? Math.max(8, Math.min(88, p.targetX + (Math.random() - 0.5) * 5)) : p.targetX
        const targetY = needsNewTarget ? Math.max(8, Math.min(85, p.targetY + (Math.random() - 0.5) * 5)) : p.targetY
        const speed = 0.002
        return {
          ...p,
          x: p.x + (targetX - p.x) * speed,
          y: p.y + (targetY - p.y) * speed,
          targetX,
          targetY,
        }
      }))
    }, 100)
    return () => clearInterval(interval)
  }, [])

  return positions
}

function HerdPage() {
  const [selected, setSelected] = useState(null)
  const positions = useCowPositions(MOCK_COWS)
  const healthy = MOCK_COWS.filter(c => c.status === 'healthy').length
  const alert = MOCK_COWS.filter(c => c.status === 'alert').length
  const critical = MOCK_COWS.filter(c => c.status === 'critical').length
  const selectedCow = MOCK_COWS.find(c => c.id === selected)

  // Individual HR trend for selected cow
  const cowHrTrend = useMemo(() => {
    if (!selectedCow) return []
    const base = selectedCow.hr
    return Array.from({ length: 24 }, (_, i) => ({
      hour: `${i}:00`,
      bpm: Math.round(base + Math.sin(i / 3) * 5 + (Math.random() - 0.5) * 8),
    }))
  }, [selected])

  return (
    <>
      <div className="page-title">Herd Monitor</div>
      <div className="pilot-badge"><FlaskConical size={14} /> Phase 1 Pilot — 40 Head Trial</div>

      <div className="card-grid">
        <div className="card"><div className="card-label">Total monitored</div><div className="card-value">{MOCK_COWS.length}</div></div>
        <div className="card"><div className="card-label">Healthy</div><div className="card-value">{healthy}</div></div>
        <div className="card"><div className="card-label">Alert</div><div className="card-value amber">{alert}</div></div>
        <div className="card"><div className="card-label">Critical</div><div className="card-value red">{critical}</div></div>
      </div>

      <div className="two-col">
        {/* Paddock Map */}
        <div className="chart-card" style={{ position: 'relative' }}>
          <div className="chart-title">Paddock View — Click to select</div>
          <div className="paddock-map">
            {/* Fence border */}
            <svg className="paddock-fence" viewBox="0 0 500 400" preserveAspectRatio="none">
              <rect x="10" y="10" width="480" height="380" rx="20" fill="none" stroke="var(--border)" strokeWidth="3" strokeDasharray="12 6" />
              {/* Water trough */}
              <rect x="420" y="30" width="50" height="20" rx="4" fill="var(--green-bg)" stroke="var(--green-light)" strokeWidth="1" />
              <text x="445" y="44" textAnchor="middle" fontSize="8" fill="var(--text-muted)">Water</text>
              {/* Feed bunk */}
              <rect x="30" y="350" width="120" height="20" rx="4" fill="var(--amber-bg)" stroke="var(--amber)" strokeWidth="1" />
              <text x="90" y="364" textAnchor="middle" fontSize="8" fill="var(--text-muted)">Feed Bunk</text>
            </svg>
            {/* Cow icons */}
            {MOCK_COWS.map(cow => {
              const pos = positions.find(p => p.id === cow.id) || { x: cow.x, y: cow.y }
              return (
                <button
                  key={cow.id}
                  className={`paddock-cow ${cow.status} ${selected === cow.id ? 'selected' : ''}`}
                  style={{ left: `${pos.x}%`, top: `${pos.y}%`, transition: 'left 0.1s linear, top 0.1s linear' }}
                  onClick={() => setSelected(selected === cow.id ? null : cow.id)}
                  title={`${cow.id} — ${cow.status}`}
                >
                  <img src="/cow.png" alt="cow" className="paddock-cow-img" />
                  <span className="paddock-cow-label">{cow.tag}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Detail panel or herd chart */}
        {selectedCow ? (
          <div className="chart-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <div className="chart-title" style={{ marginBottom: 0 }}>{selectedCow.id} {selectedCow.tag}</div>
              <div className={`cow-status ${selectedCow.status}`}>{selectedCow.status}</div>
            </div>
            <div className="cow-metrics" style={{ marginBottom: 20 }}>
              <div className="cow-metric">
                <div className="cow-metric-val" style={{ color: selectedCow.hr > 85 ? RED : selectedCow.hr > 80 ? AMBER : GREEN }}>{selectedCow.hr}</div>
                <div className="cow-metric-label">BPM</div>
              </div>
              <div className="cow-metric">
                <div className="cow-metric-val" style={{ color: selectedCow.temp > 39.5 ? RED : selectedCow.temp > 39 ? AMBER : GREEN }}>{selectedCow.temp}°C</div>
                <div className="cow-metric-label">Temp</div>
              </div>
              <div className="cow-metric">
                <div className="cow-metric-val" style={{ color: selectedCow.vagalTone > 0.7 ? GREEN : selectedCow.vagalTone > 0.5 ? AMBER : RED }}>{(selectedCow.vagalTone * 100).toFixed(0)}%</div>
                <div className="cow-metric-label">Vagal Tone</div>
              </div>
              <div className="cow-metric">
                <div className="cow-metric-val">{selectedCow.activity}</div>
                <div className="cow-metric-label">Activity</div>
              </div>
              <div className="cow-metric">
                <div className="cow-metric-val">{selectedCow.daysIn}d</div>
                <div className="cow-metric-label">Days in</div>
              </div>
            </div>
            <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-sec)', marginBottom: 8 }}>Heart Rate — 24h</div>
            <ResponsiveContainer width="100%" height={180}>
              <AreaChart data={cowHrTrend}>
                <XAxis dataKey="hour" tick={{ fontSize: 10 }} interval={3} />
                <YAxis domain={[50, 110]} tick={{ fontSize: 10 }} />
                <Tooltip />
                <Area type="monotone" dataKey="bpm" fill={selectedCow.status === 'critical' ? RED : selectedCow.status === 'alert' ? AMBER : GREEN} fillOpacity={0.15} stroke={selectedCow.status === 'critical' ? RED : selectedCow.status === 'alert' ? AMBER : GREEN} strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
            <div style={{ marginTop: 16, fontSize: 12, color: 'var(--text-muted)' }}>
              VNS Protocol: {selectedCow.daysIn <= 28 ? 'Anti-inflammatory (Week ' + Math.ceil(selectedCow.daysIn / 7) + '/4)' : 'Monitoring only'}
            </div>
          </div>
        ) : (
          <div className="chart-card">
            <div className="chart-title">Heart Rate — 24h Trend (All)</div>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={MOCK_HR_TREND}>
                <XAxis dataKey="hour" tick={{ fontSize: 11 }} interval={3} />
                <YAxis domain={[55, 110]} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="healthy" stroke={GREEN} strokeWidth={2} dot={false} name="Healthy avg" />
                <Line type="monotone" dataKey="alert" stroke={AMBER} strokeWidth={2} dot={false} name="Alert" />
                <Line type="monotone" dataKey="critical" stroke={RED} strokeWidth={2} dot={false} name="Critical" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Per-cow dose response — only visible when a cow is selected */}
      {selectedCow && <CowDoseResponse cow={selectedCow} />}
    </>
  )
}

/* ════════════════════════════════════════
   PER-COW DOSE RESPONSE SECTION
   ════════════════════════════════════════ */
function CowDoseResponse({ cow }) {
  const [freq, setFreq] = useState(20)
  const [pulseWidth, setPulseWidth] = useState(250)
  const [amplitude, setAmplitude] = useState(1.5)

  const doseResponse = useMemo(() => {
    const points = []
    for (let a = 0; a <= 5; a += 0.1) {
      const tnfSuppression = 80 * Math.pow(a, 2) / (Math.pow(1.8, 2) + Math.pow(a, 2))
      const cardiacRisk = a > 2 ? 100 * Math.pow(a - 2, 1.5) / (Math.pow(1, 1.5) + Math.pow(a - 2, 1.5)) : 0
      const rumenStasis = a > 2.5 ? 100 * Math.pow(a - 2.5, 2) / (Math.pow(0.8, 2) + Math.pow(a - 2.5, 2)) : 0
      points.push({
        amp: parseFloat(a.toFixed(1)),
        tnf: Math.min(100, tnfSuppression),
        cardiac: Math.min(100, cardiacRisk),
        rumen: Math.min(100, rumenStasis),
      })
    }
    return points
  }, [])

  const currentPoint = doseResponse.find(p => Math.abs(p.amp - amplitude) < 0.05) || doseResponse[0]
  const safetyMargin = currentPoint ? Math.max(0, currentPoint.tnf - Math.max(currentPoint.cardiac, currentPoint.rumen)) : 0

  const cortisolTimeseries = useMemo(() => Array.from({ length: 30 }, (_, i) => {
    const baseline = 8
    const treatmentEffect = Math.max(0, 4 * (1 - Math.exp(-i / 14)))
    return {
      day: i + 1,
      treatment: Math.max(2, baseline - treatmentEffect + (Math.random() - 0.5) * 1.5),
      sham: baseline + (Math.random() - 0.5) * 1.5,
    }
  }), [cow.id])

  const hrvTrace = useMemo(() => Array.from({ length: 60 }, (_, i) => ({
    t: i,
    rmssd: 42 + Math.sin(i / 8) * 8 + (Math.random() - 0.5) * 4,
  })), [cow.id])

  return (
    <>
      <div className="dose-section-header">
        <Zap size={16} />
        <span>Dose Response — {cow.id} {cow.tag}</span>
      </div>

      {/* Three-column input/safety/efficacy panels */}
      <div className="dr-grid">
        <div className="dr-col">
          <div className="dr-col-label input">
            <span className="dr-dot" style={{ background: '#8B5CF6' }} />
            INPUT — STIMULATION
          </div>
          <div className="dr-item">
            <div className="dr-item-title">Pulse parameters</div>
            <div className="dr-item-desc">Frequency, amplitude, pulse width swept across animals. Building the dose-response curve that doesn't exist yet.</div>
          </div>
          <div className="slider-section" style={{ marginTop: 12, padding: 16 }}>
            <Slider label="Frequency" value={freq} set={setFreq} min={1} max={50} suffix=" Hz" />
            <div style={{ height: 10 }} />
            <Slider label="Pulse width" value={pulseWidth} set={setPulseWidth} min={50} max={1000} step={10} suffix=" µs" />
            <div style={{ height: 10 }} />
            <Slider label="Amplitude" value={amplitude} set={setAmplitude} min={0.1} max={5} step={0.1} suffix=" mA" />
          </div>
        </div>

        <div className="dr-col">
          <div className="dr-col-label">
            <span className="dr-dot" style={{ background: GREEN }} />
            SAFETY READOUT
          </div>
          <div className="dr-item">
            <div className="dr-item-title"><Heart size={14} style={{ display: 'inline', marginRight: 6, color: GREEN }} /> HRV <span className="dr-arrow up">↑</span></div>
            <div className="dr-item-desc">Real-time. Confirms vagal efferent activation. Drops if cardiac branch over-stimulated — immediate safety interlock.</div>
          </div>
          <div className="dr-item">
            <div className="dr-item-title"><Activity size={14} style={{ display: 'inline', marginRight: 6, color: GREEN }} /> Rumen contractions <span className="dr-arrow up">↑</span></div>
            <div className="dr-item-desc">Confirms GI efferents active. Loss of contractions = bloat risk. Continuous bolus monitor.</div>
          </div>
        </div>

        <div className="dr-col">
          <div className="dr-col-label">
            <span className="dr-dot" style={{ background: RED }} />
            EFFICACY READOUT
          </div>
          <div className="dr-item">
            <div className="dr-item-title"><Beaker size={14} style={{ display: 'inline', marginRight: 6, color: RED }} /> TNF-α <span className="dr-arrow down">↓</span></div>
            <div className="dr-item-desc">Gold standard. Borovikova 2000 showed 75–80% suppression in rodents. Weekly blood draw. This is the BRD inflammation signal.</div>
          </div>
          <div className="dr-item">
            <div className="dr-item-title"><TrendingDown size={14} style={{ display: 'inline', marginRight: 6, color: RED }} /> Cortisol <span className="dr-arrow down">↓</span></div>
            <div className="dr-item-desc">Salivary — no restraint. Tracks the stress-immune axis over 30 days. Expected nadir at day 14.</div>
          </div>
        </div>
      </div>

      {/* Live readouts */}
      <div className="card-grid">
        <div className="card">
          <div className="card-label">TNF-α suppression</div>
          <div className="card-value">{currentPoint?.tnf.toFixed(0)}%</div>
          <div className="card-sub">At {amplitude} mA</div>
        </div>
        <div className="card">
          <div className="card-label">Cardiac risk</div>
          <div className="card-value" style={{ color: currentPoint?.cardiac > 20 ? RED : GREEN }}>{currentPoint?.cardiac.toFixed(0)}%</div>
          <div className="card-sub">Bradycardia threshold</div>
        </div>
        <div className="card">
          <div className="card-label">Rumen stasis risk</div>
          <div className="card-value" style={{ color: currentPoint?.rumen > 20 ? RED : GREEN }}>{currentPoint?.rumen.toFixed(0)}%</div>
          <div className="card-sub">Bloat / Hoflund</div>
        </div>
        <div className="card">
          <div className="card-label">Safety margin</div>
          <div className="card-value" style={{ color: safetyMargin > 40 ? GREEN : safetyMargin > 20 ? AMBER : RED }}>{safetyMargin.toFixed(0)}%</div>
          <div className="card-sub">Therapeutic window</div>
        </div>
      </div>

      <div className="chart-card">
        <div className="chart-title">Dose–Response Curve — Efficacy vs Safety</div>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={doseResponse}>
            <XAxis dataKey="amp" label={{ value: 'Stimulation amplitude (mA)', position: 'insideBottom', offset: -5, fontSize: 11 }} tick={{ fontSize: 11 }} />
            <YAxis label={{ value: 'Response (%)', angle: -90, position: 'insideLeft', fontSize: 11 }} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v, name) => [`${v.toFixed(1)}%`, name]} />
            <Line type="monotone" dataKey="tnf" stroke={GREEN} strokeWidth={3} dot={false} name="TNF-α suppression" />
            <Line type="monotone" dataKey="cardiac" stroke={AMBER} strokeWidth={2} dot={false} name="Cardiac risk" strokeDasharray="5 3" />
            <Line type="monotone" dataKey="rumen" stroke={RED} strokeWidth={2} dot={false} name="Rumen stasis risk" strokeDasharray="5 3" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="two-col">
        <div className="chart-card">
          <div className="chart-title">Cortisol — 30-day trend (treatment vs sham)</div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={cortisolTimeseries}>
              <XAxis dataKey="day" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Line type="monotone" dataKey="treatment" stroke={GREEN} strokeWidth={2} dot={false} name="Treatment" />
              <Line type="monotone" dataKey="sham" stroke={RED} strokeWidth={2} dot={false} name="Sham" strokeDasharray="4 3" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <div className="chart-title">HRV (RMSSD) — real-time trace</div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={hrvTrace}>
              <XAxis dataKey="t" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Area type="monotone" dataKey="rmssd" fill={GREEN} fillOpacity={0.15} stroke={GREEN} strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  )
}

/* ════════════════════════════════════════
   SLIDER COMPONENT
   ════════════════════════════════════════ */
function Slider({ label, value, set, min, max, step = 1, prefix = '', suffix = '', isRed = false }) {
  return (
    <div className="slider-item">
      <div className="slider-label">
        <span>{label}</span>
        <span className={`slider-val ${isRed ? 'red' : ''}`}>{prefix}{typeof value === 'number' && value % 1 !== 0 ? value.toFixed(1) : value}{suffix}</span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value} onChange={e => set(Number(e.target.value))} />
    </div>
  )
}

/* ════════════════════════════════════════
   DOSE RESPONSE PAGE
   ════════════════════════════════════════ */
function DoseResponsePage() {
  const [freq, setFreq] = useState(20)
  const [pulseWidth, setPulseWidth] = useState(250)
  const [amplitude, setAmplitude] = useState(1.5)

  // Hill equation for dose-response
  const doseResponse = useMemo(() => {
    const points = []
    for (let a = 0; a <= 5; a += 0.1) {
      const tnfSuppression = 80 * Math.pow(a, 2) / (Math.pow(1.8, 2) + Math.pow(a, 2))
      const cardiacRisk = a > 2 ? 100 * Math.pow(a - 2, 1.5) / (Math.pow(1, 1.5) + Math.pow(a - 2, 1.5)) : 0
      const rumenStasis = a > 2.5 ? 100 * Math.pow(a - 2.5, 2) / (Math.pow(0.8, 2) + Math.pow(a - 2.5, 2)) : 0
      points.push({
        amp: parseFloat(a.toFixed(1)),
        tnf: Math.min(100, tnfSuppression),
        cardiac: Math.min(100, cardiacRisk),
        rumen: Math.min(100, rumenStasis),
      })
    }
    return points
  }, [])

  const currentPoint = doseResponse.find(p => Math.abs(p.amp - amplitude) < 0.05) || doseResponse[0]
  const safeWindow = amplitude <= 2 && amplitude >= 1
  const safetyMargin = currentPoint ? Math.max(0, currentPoint.tnf - Math.max(currentPoint.cardiac, currentPoint.rumen)) : 0

  // 30-day cortisol timeseries (simulated)
  const cortisolTimeseries = useMemo(() => {
    return Array.from({ length: 30 }, (_, i) => {
      const baseline = 8
      const treatmentEffect = Math.max(0, 4 * (1 - Math.exp(-i / 14)))
      return {
        day: i + 1,
        treatment: Math.max(2, baseline - treatmentEffect + (Math.random() - 0.5) * 1.5),
        sham: baseline + (Math.random() - 0.5) * 1.5,
      }
    })
  }, [])

  // HRV real-time (simulated)
  const hrvTrace = useMemo(() => Array.from({ length: 60 }, (_, i) => ({
    t: i,
    rmssd: 42 + Math.sin(i / 8) * 8 + (Math.random() - 0.5) * 4,
  })), [])

  return (
    <>
      <div className="page-title">Dose Response & Safety Window</div>
      <div className="pilot-badge"><FlaskConical size={14} /> Deliverable: safety & efficacy dashboard for regulatory + investor audiences</div>

      {/* Three column layout: Input / Safety / Efficacy */}
      <div className="dr-grid">
        {/* INPUT */}
        <div className="dr-col">
          <div className="dr-col-label input">
            <span className="dr-dot" style={{ background: '#8B5CF6' }} />
            INPUT — STIMULATION
          </div>
          <div className="dr-item">
            <div className="dr-item-title">Pulse parameters</div>
            <div className="dr-item-desc">Frequency, amplitude, pulse width swept across animals. Building the dose-response curve that doesn't exist yet.</div>
          </div>
          <div className="slider-section" style={{ marginTop: 12, padding: 16 }}>
            <Slider label="Frequency" value={freq} set={setFreq} min={1} max={50} suffix=" Hz" />
            <div style={{ height: 10 }} />
            <Slider label="Pulse width" value={pulseWidth} set={setPulseWidth} min={50} max={1000} step={10} suffix=" µs" />
            <div style={{ height: 10 }} />
            <Slider label="Amplitude" value={amplitude} set={setAmplitude} min={0.1} max={5} step={0.1} suffix=" mA" />
          </div>
        </div>

        {/* SAFETY */}
        <div className="dr-col">
          <div className="dr-col-label">
            <span className="dr-dot" style={{ background: GREEN }} />
            SAFETY READOUT
          </div>
          <div className="dr-item">
            <div className="dr-item-title"><Heart size={14} style={{ display: 'inline', marginRight: 6, color: GREEN }} /> HRV <span className="dr-arrow up">↑</span></div>
            <div className="dr-item-desc">Real-time. Confirms vagal efferent activation. Drops if cardiac branch over-stimulated — immediate safety interlock.</div>
          </div>
          <div className="dr-item">
            <div className="dr-item-title"><Activity size={14} style={{ display: 'inline', marginRight: 6, color: GREEN }} /> Rumen contractions <span className="dr-arrow up">↑</span></div>
            <div className="dr-item-desc">Confirms GI efferents active. Loss of contractions = bloat risk. Continuous bolus monitor.</div>
          </div>
        </div>

        {/* EFFICACY */}
        <div className="dr-col">
          <div className="dr-col-label">
            <span className="dr-dot" style={{ background: RED }} />
            EFFICACY READOUT
          </div>
          <div className="dr-item">
            <div className="dr-item-title"><Beaker size={14} style={{ display: 'inline', marginRight: 6, color: RED }} /> TNF-α <span className="dr-arrow down">↓</span></div>
            <div className="dr-item-desc">Gold standard. Borovikova 2000 showed 75–80% suppression in rodents. Weekly blood draw. This is the BRD inflammation signal.</div>
          </div>
          <div className="dr-item">
            <div className="dr-item-title"><TrendingDown size={14} style={{ display: 'inline', marginRight: 6, color: RED }} /> Cortisol <span className="dr-arrow down">↓</span></div>
            <div className="dr-item-desc">Salivary — no restraint. Tracks the stress-immune axis over 30 days. Expected nadir at day 14.</div>
          </div>
        </div>
      </div>

      {/* Live readouts row */}
      <div className="card-grid">
        <div className="card">
          <div className="card-label">TNF-α suppression</div>
          <div className="card-value">{currentPoint?.tnf.toFixed(0)}%</div>
          <div className="card-sub">At {amplitude} mA</div>
        </div>
        <div className="card">
          <div className="card-label">Cardiac risk</div>
          <div className="card-value" style={{ color: currentPoint?.cardiac > 20 ? RED : GREEN }}>{currentPoint?.cardiac.toFixed(0)}%</div>
          <div className="card-sub">Bradycardia threshold</div>
        </div>
        <div className="card">
          <div className="card-label">Rumen stasis risk</div>
          <div className="card-value" style={{ color: currentPoint?.rumen > 20 ? RED : GREEN }}>{currentPoint?.rumen.toFixed(0)}%</div>
          <div className="card-sub">Bloat / Hoflund</div>
        </div>
        <div className="card">
          <div className="card-label">Safety margin</div>
          <div className="card-value" style={{ color: safetyMargin > 40 ? GREEN : safetyMargin > 20 ? AMBER : RED }}>{safetyMargin.toFixed(0)}%</div>
          <div className="card-sub">{safeWindow ? 'Within therapeutic window' : 'Outside window'}</div>
        </div>
      </div>

      {/* Dose response curve */}
      <div className="chart-card">
        <div className="chart-title">Dose–Response Curve — Efficacy vs Safety</div>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={doseResponse}>
            <XAxis dataKey="amp" label={{ value: 'Stimulation amplitude (mA)', position: 'insideBottom', offset: -5, fontSize: 11 }} tick={{ fontSize: 11 }} />
            <YAxis label={{ value: 'Response (%)', angle: -90, position: 'insideLeft', fontSize: 11 }} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v, name) => [`${v.toFixed(1)}%`, name]} />
            <Line type="monotone" dataKey="tnf" stroke={GREEN} strokeWidth={3} dot={false} name="TNF-α suppression" />
            <Line type="monotone" dataKey="cardiac" stroke={AMBER} strokeWidth={2} dot={false} name="Cardiac risk" strokeDasharray="5 3" />
            <Line type="monotone" dataKey="rumen" stroke={RED} strokeWidth={2} dot={false} name="Rumen stasis risk" strokeDasharray="5 3" />
          </LineChart>
        </ResponsiveContainer>
        <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginTop: 12, fontSize: 11, color: 'var(--text-muted)' }}>
          <div><span style={{ display: 'inline-block', width: 12, height: 3, background: GREEN, marginRight: 6, verticalAlign: 'middle' }} />TNF-α suppression (efficacy)</div>
          <div><span style={{ display: 'inline-block', width: 12, height: 3, background: AMBER, marginRight: 6, verticalAlign: 'middle' }} />Cardiac (safety)</div>
          <div><span style={{ display: 'inline-block', width: 12, height: 3, background: RED, marginRight: 6, verticalAlign: 'middle' }} />Rumen (safety)</div>
        </div>
      </div>

      {/* Cortisol + HRV */}
      <div className="two-col">
        <div className="chart-card">
          <div className="chart-title">Cortisol — 30-day trend (treatment vs sham)</div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={cortisolTimeseries}>
              <XAxis dataKey="day" label={{ value: 'Day', position: 'insideBottom', offset: -5, fontSize: 10 }} tick={{ fontSize: 10 }} />
              <YAxis label={{ value: 'ng/mL', angle: -90, position: 'insideLeft', fontSize: 10 }} tick={{ fontSize: 10 }} />
              <Tooltip />
              <Line type="monotone" dataKey="treatment" stroke={GREEN} strokeWidth={2} dot={false} name="Treatment" />
              <Line type="monotone" dataKey="sham" stroke={RED} strokeWidth={2} dot={false} name="Sham" strokeDasharray="4 3" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <div className="chart-title">HRV (RMSSD) — real-time trace</div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={hrvTrace}>
              <XAxis dataKey="t" label={{ value: 'seconds', position: 'insideBottom', offset: -5, fontSize: 10 }} tick={{ fontSize: 10 }} />
              <YAxis label={{ value: 'ms', angle: -90, position: 'insideLeft', fontSize: 10 }} tick={{ fontSize: 10 }} />
              <Tooltip />
              <Area type="monotone" dataKey="rmssd" fill={GREEN} fillOpacity={0.15} stroke={GREEN} strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Deliverable section */}
      <div className="deliverable-card">
        <div className="deliverable-label">
          <span>DELIVERABLE</span>
          <div className="deliverable-title">Safety & efficacy dashboard for regulatory and investor audiences</div>
        </div>
        <ul className="deliverable-list">
          <li>Dose-response curve: TNF-α suppression vs cardiac and rumen safety margin at each parameter set</li>
          <li>First published bovine VNS stimulation parameters — the dataset that defines the field</li>
          <li>FDA-CVM submission package foundation: safety biomarkers, efficacy signal, n=20 powered pilot</li>
        </ul>
      </div>
    </>
  )
}

/* ════════════════════════════════════════
   APP
   ════════════════════════════════════════ */
export default function App() {
  const [page, setPage] = useState('economics')

  return (
    <div className="app">
      <div className="sidebar">
        <div className="sidebar-logo">
          <img src="/logo.png" alt="BoVa" />
          <span>BoVa</span>
        </div>
        <nav className="sidebar-nav">
          <button className={`nav-item ${page === 'economics' ? 'active' : ''}`} onClick={() => setPage('economics')}>
            <Calculator size={18} /> Economics
          </button>
          <button className={`nav-item ${page === 'herd' ? 'active' : ''}`} onClick={() => setPage('herd')}>
            <Activity size={18} /> Herd Monitor
          </button>
        </nav>
      </div>
      <main className="main">
        {page === 'economics' && <EconomicsPage />}
        {page === 'herd' && <HerdPage />}
      </main>
    </div>
  )
}
