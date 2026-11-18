import {useEffect, useMemo, useState} from 'react'
import {createRoot} from 'react-dom/client'
import {Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis} from 'recharts'
import './styles.css'

type Cell = string | number | boolean | null
type Row = Record<string, Cell>
const pages = [
  {title:'Overview', icon:'◫', path:'dashboard/summary', extra:'revenue/trends', subtitle:'Track orders, revenue and customer activity across NovaCart.'},
  {title:'Sales Analytics', icon:'↗', path:'revenue/trends', subtitle:'Monthly net revenue and changes over time.'},
  {title:'Customer Intelligence', icon:'◎', path:'customers/segments', subtitle:'Purchase behavior by recency, frequency and monetary value.'},
  {title:'Retention & Cohorts', icon:'▦', path:'customers/cohorts', subtitle:'Follow each first-purchase cohort over subsequent months.'},
  {title:'Marketing Analytics', icon:'◇', path:'marketing/funnel', extra:'marketing/campaigns', subtitle:'Track conversion and attributed campaign revenue.'},
  {title:'Product Analytics', icon:'□', path:'products/performance', subtitle:'Compare units sold, sales, margins and current stock.'},
  {title:'Experimentation', icon:'⚗', path:'experiments', subtitle:'Compare control and treatment for NovaCart’s checkout test.'},
  {title:'Data Quality', icon:'✓', path:'quality', subtitle:'Review integrity checks against the published dataset.'},
  {title:'Pipeline Monitoring', icon:'◷', path:'pipelines/runs', subtitle:'Inspect dataset refresh history and publication results.'},
  {title:'Reports & Exports', icon:'↓', path:'reports/export', subtitle:'Download reports for Excel, Power BI or Tableau.'},
]
const money = new Set('gross_revenue net_revenue refunds gross_profit average_order_value rolling_3_month_revenue average_observed_value spend attributed_revenue sales_before_refunds profit_before_refunds'.split(' '))
const label = (key:string) => key.replaceAll('_',' ').replace(/\bpct\b/g,'%').replace(/\bpp\b/g,'(pp)').replace(/^./, c => c.toUpperCase())
const dollars = (value:number) => new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(value/100)
function display(key:string,value:Cell) {
  if(value === null) return '—'
  if(money.has(key)) return dollars(Number(value))
  if(typeof value === 'number') return value.toLocaleString('en-US',{maximumFractionDigits:key==='p_value'?6:2})
  return String(value)
}

function DataTable({rows, title}:{rows:Row[],title:string}) {
  const [filter,setFilter] = useState('')
  const [sort,setSort] = useState<{key:string,asc:boolean}>()
  const [page,setPage] = useState(0)
  const columns = Object.keys(rows[0] ?? {})
  const visible = useMemo(() => {
    const filtered = rows.filter(row => Object.values(row).some(value => String(value).toLowerCase().includes(filter.toLowerCase())))
    if(sort) filtered.sort((a,b) => String(a[sort.key] ?? '').localeCompare(String(b[sort.key] ?? ''),undefined,{numeric:true})*(sort.asc?1:-1))
    return filtered
  },[rows,filter,sort])
  const current = Math.min(page, Math.max(0, Math.ceil(visible.length/12)-1))
  return <section className="panel"><div className="section-head"><h2>{title}</h2><label>Filter loaded rows <input value={filter} onChange={e=>{setFilter(e.target.value);setPage(0)}} placeholder="Type to filter" /></label></div>
    {visible.length ? <><div className="table-wrap"><table><thead><tr>{columns.map(key=><th key={key} aria-sort={sort?.key===key?(sort.asc?'ascending':'descending'):'none'}><button onClick={()=>{setSort({key,asc:sort?.key===key?!sort.asc:true});setPage(0)}}>{label(key)} ↕</button></th>)}</tr></thead>
    <tbody>{visible.slice(current*12,current*12+12).map((row,i)=><tr key={i}>{columns.map(key=><td key={key}>{display(key,row[key])}</td>)}</tr>)}</tbody></table></div>
    <footer><span>{current*12+1}–{Math.min(current*12+12,visible.length)} of {visible.length}</span><button disabled={current===0} onClick={()=>setPage(current-1)}>Previous</button><button disabled={current*12+12>=visible.length} onClick={()=>setPage(current+1)}>Next</button></footer></>:<p>No matching records.</p>}</section>
}

function Trend({rows}:{rows:Row[]}) {
  return <section className="panel chart"><h2>Monthly net revenue</h2><p>USD, after discounts and refunds</p><div className="plot"><ResponsiveContainer width="100%" height="100%"><AreaChart data={rows} margin={{top:10,right:14,left:12,bottom:8}}>
    <defs><linearGradient id="net" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#2a9b81" stopOpacity=".42"/><stop offset="1" stopColor="#2a9b81" stopOpacity=".03"/></linearGradient></defs>
    <CartesianGrid vertical={false} stroke="#e2ebe7"/><XAxis dataKey="month" tickFormatter={v=>String(v).slice(0,7)} tick={{fontSize:11}} minTickGap={25}/><YAxis tickFormatter={v=>'$'+Math.round(v/100000)+'k'} tick={{fontSize:11}}/>
    <Tooltip formatter={v=>[dollars(Number(v)),'Net revenue']}/><Area dataKey="net_revenue" stroke="#147863" strokeWidth={3} fill="url(#net)" isAnimationActive={false}/>
  </AreaChart></ResponsiveContainer></div></section>
}

function App(){
  const [index,setIndex]=useState(0)
  const [start,setStart]=useState('2024-01-01')
  const [end,setEnd]=useState('2025-12-31')
  const [range,setRange]=useState({start,end})
  const [rows,setRows]=useState<Row[]>([])
  const [extra,setExtra]=useState<Row[]>([])
  const [error,setError]=useState('')
  const [loading,setLoading]=useState(true)
  const [revision,setRevision]=useState(0)
  const page=pages[index]
  const reports=index===9
  const params=new URLSearchParams(range).toString()
  const exportUrl=(format:string,report='Revenue')=>'/api/v1/reports/export?'+params+'&'+new URLSearchParams({format,report})
  useEffect(()=>{
    if(reports) return
    const controller=new AbortController()
    setLoading(true);setError('')
    async function load(path:string):Promise<Row[]>{
      const response=await fetch('/api/v1/'+path+'?'+params,{signal:controller.signal})
      if(!response.ok) throw new Error('The request failed ('+response.status+'). Check the date range or retry.')
      return response.json()
    }
    Promise.all([load(page.path),page.extra?load(page.extra):Promise.resolve([])])
      .then(([data,second])=>{setRows(data);setExtra(second)})
      .catch(err=>{if(!controller.signal.aborted) setError(String(err.message))})
      .finally(()=>{if(!controller.signal.aborted) setLoading(false)})
    return ()=>controller.abort()
  },[page,params,reports,revision])
  const summary = rows[0] ?? {}
  return <div className="layout">
    <aside><div className="brand"><span className="mark" aria-hidden="true">▥</span><div>DataFlow<small>INTELLIGENCE</small></div></div>
    <nav aria-label="Dashboard pages">{pages.map(({title,icon},i)=><button key={title} aria-current={index===i?'page':undefined} onClick={()=>{if(i!==index){setLoading(true);setIndex(i)}}}><span aria-hidden="true">{icon}</span>{title}</button>)}</nav>
    <div className="workspace"><span className="dot"/>NovaCart demo workspace</div></aside>
    <main><header><div>NovaCart <span>/</span> {page.title}</div><a href="/docs">API reference ↗</a></header>
    <div className="content"><div className="intro"><div><h1>{page.title}</h1><p>{page.subtitle}</p></div>
    <form onSubmit={e=>{e.preventDefault();setRange({start,end})}}><label>From<input type="date" required value={start} onChange={e=>setStart(e.target.value)}/></label><label>Through<input type="date" min={start} required value={end} onChange={e=>setEnd(e.target.value)}/></label><button className="primary">Apply</button></form></div>
    {reports ? <section className="panel exports"><h2>Download analytics</h2><p>Workbook values use USD. CSV monetary columns use cents.</p><a className="primary" href={exportUrl('xlsx')}>Download Excel workbook</a><div className="export-grid">{['Summary','Revenue','Cohorts','Segments','Funnel','Campaigns','Products','Quality'].map(name=><a key={name} href={exportUrl('csv',name)}>{name} CSV ↓</a>)}</div></section>
    :loading?<p role="status">Loading analytics…</p>:error?<section className="panel"><p role="alert">{error}</p><button onClick={()=>setRevision(revision+1)}>Retry</button></section>:<>
    {index===0 && <><div className="cards">{['net_revenue','orders','active_customers','average_order_value'].map(key=><article className="panel kpi" key={key}><span>{label(key)}</span><strong>{display(key,summary[key] ?? null)}</strong></article>)}</div><Trend rows={extra}/></>}
    {index===1 && <Trend rows={rows}/>}
    {index===4 && <section className="panel chart"><h2>Purchase funnel</h2><div className="plot"><ResponsiveContainer width="100%" height="100%"><BarChart data={['sessions','carts','conversions'].map(key=>({stage:label(key),count:summary[key]}))}><CartesianGrid vertical={false} stroke="#e2ebe7"/><XAxis dataKey="stage"/><YAxis/><Tooltip/><Bar dataKey="count" fill="#147863" radius={[5,5,0,0]} isAnimationActive={false}/></BarChart></ResponsiveContainer></div></section>}
    <DataTable key={page.path} rows={rows} title={index===0?'Financial summary':page.title+' details'}/>
    {index===4 && <DataTable rows={extra} title="Campaign attribution"/>}
    {index===8 && <button onClick={()=>setRevision(revision+1)}>Reload pipeline history</button>}
    </>}
    <p className="footnote">Synthetic demo data · USD · Reporting window is inclusive</p>
    </div></main></div>
}
createRoot(document.getElementById('root')!).render(<App/>)
