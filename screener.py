#!/usr/bin/env python3
"""CryptoEarlyRadar - MoltStreet Intelligence Screener"""
import os,json,time,smtplib,datetime,urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

WATCHLIST={
  "HYPE":{"id":"hyperliquid","github":"hyperliquid-dex/node"},
  "ONDO":{"id":"ondo-finance","github":""},
  "PENDLE":{"id":"pendle","github":"pendle-finance/pendle-core-v2-public"},
  "SUI":{"id":"sui","github":"MystenLabs/sui"},
  "JUP":{"id":"jupiter-exchange-solana","github":""},
  "KAITO":{"id":"kaito","github":""},
  "GRASS":{"id":"grass","github":""},
  "DRIFT":{"id":"drift-protocol","github":"drift-labs/protocol-v2"},
  "BERA":{"id":"berachain-bera","github":"berachain/beacon-kit"},
  "ENA":{"id":"ethena","github":""},
  "VIRTUAL":{"id":"virtual-protocol","github":""},
  "RESOLV":{"id":"resolv","github":""},
}
THRESHOLD=65
GMAIL="italiamolt5@gmail.com"
def fetch(url,t=10):
  try:
    req=urllib.request.Request(url,headers={"User-Agent":"CryptoRadar/1.0"})
    with urllib.request.urlopen(req,timeout=t) as r:
      return json.loads(r.read())
  except: return None
def clamp(v,lo=0,hi=100): return max(lo,min(hi,v))
def get_cg():
  ids=",".join(v["id"] for v in WATCHLIST.values())
  d=fetch(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={ids}&order=market_cap_desc&per_page=30&page=1&sparkline=false&price_change_percentage=7d,30d")
  return {c["symbol"].upper():c for c in d} if d else {}
def get_fg():
  d=fetch("https://api.alternative.me/fng/?limit=7")
  if not d: return None,None
  vals=[int(x["value"]) for x in d["data"]]
  return vals[0],vals[0]-vals[-1]
def get_gh(repo):
  if not repo: return None
  tok=os.environ.get("Github_token","")
  h={"User-Agent":"CryptoRadar/1.0"}
  if tok: h["Authorization"]=f"Bearer {tok}"
  def _f(u):
    try:
      req=urllib.request.Request(u,headers=h)
      with urllib.request.urlopen(req,timeout=10) as r: return json.loads(r.read())
    except: return None
  ca=_f(f"https://api.github.com/repos/{repo}/stats/commit_activity")
  ri=_f(f"https://api.github.com/repos/{repo}")
  c=sum(w.get("total",0) for w in ca[-4:]) if ca else 0
  s=ri.get("stargazers_count",0) if ri else 0
  return {"commits_4w":c,"stars":s}
def score(cg,gh,fg):
  s=0; bd={}
  ath=cg.get("ath_change_percentage",0)
  a=clamp((-ath/90)*25,0,25); s+=a; bd["ath_discount"]=round(a,1)
  vol=cg.get("total_volume",0); mc=max(cg.get("market_cap",1),1)
  v=clamp((vol/mc)*80,0,20); s+=v; bd["vol_momentum"]=round(v,1)
  p7=cg.get("price_change_percentage_7d_in_currency") or 0
  ps=clamp((p7/30)*15,0,15) if p7>0 else clamp(15+(p7/30)*15,0,15)
  s+=ps; bd["price_7d"]=round(ps,1)
  fg_s=clamp(((100-(fg or 50))/100)*15,0,15); s+=fg_s; bd["fg_contrarian"]=round(fg_s,1)
  if gh:
    gh_s=clamp((gh.get("commits_4w",0)/200)*8,0,8)+clamp((gh.get("stars",0)/10000)*7,0,7)
  else: gh_s=5.0
  s+=gh_s; bd["github"]=round(gh_s,1)
  mc_m=mc/1e6
  ms=10 if mc_m<100 else 7 if mc_m<500 else 4 if mc_m<2000 else 1
  s+=ms; bd["mcap_upside"]=ms
  return round(s,1),bd
def main():
  print("CryptoEarlyRadar starting...")
  fg,fgt=get_fg()
  fg_lbl="Extreme Fear" if fg and fg<25 else "Fear" if fg and fg<45 else "Neutral" if fg and fg<56 else "Greed"
  cg=get_cg()
  print(f"F&G:{fg} ({fg_lbl}) | Coins:{len(cg)}")
  results=[]
  for sym,meta in WATCHLIST.items():
    data=cg.get(sym,{})
    if not data:
      for k,v in cg.items():
        if k.lower()==sym.lower(): data=v; break
    if not data: continue
    gh=get_gh(meta["github"]) if meta.get("github") else None
    if meta.get("github"): time.sleep(0.3)
    sc,bd=score(data,gh,fg)
    results.append({"symbol":sym,"score":sc,"breakdown":bd,
      "price":data.get("current_price",0),
      "mcap_m":data.get("market_cap",0)/1e6,
      "p7d":data.get("price_change_percentage_7d_in_currency") or 0,
      "ath_chg":data.get("ath_change_percentage",0),
      "volume":data.get("total_volume",0)})
  results.sort(key=lambda x:x["score"],reverse=True)
  print("\n"+"="*65)
  print("  SYM      SCORE      PRICE     MCAP      7d%    ATH%  SIG")
  print("-"*65)
  alerts=[]
  for r in results:
    sig="ALERT" if r["score"]>=THRESHOLD else ("WATCH" if r["score"]>=50 else "hold")
    sym=r["symbol"]; sc=r["score"]; pr=r["price"]; mc=r["mcap_m"]
    p7=r["p7d"]; at=r["ath_chg"]
    print(f"  {sym:8}{sc:>8.1f} ${pr:>11,.4f} ${mc:>7.1f}M {p7:>+7.2f}% {at:>+8.1f}%  {sig}")
    if r["score"]>=THRESHOLD: alerts.append(r)
  print("="*65)
  out={"generated_at":datetime.datetime.now(datetime.UTC).isoformat(),
       "fear_greed":{"index":fg,"trend":fgt,"label":fg_lbl},"projects":results}
  with open("data.json","w") as f: json.dump(out,f,indent=2)
  print("\nSaved data.json")
  if alerts:
    app_pw=os.environ.get("Mail_apppassword","")
    if app_pw:
      body="\n".join([f"  {r['symbol']}: Score {r['score']} | ${r['price']:.4f} | ATH:{r['ath_chg']:+.1f}%" for r in alerts])
      msg=MIMEMultipart(); msg["Subject"]=f"CryptoRadar: {len(alerts)} ALERT(s)"
      msg["From"]=GMAIL; msg["To"]=GMAIL
      msg.attach(MIMEText(f"ALERTS:\n\n{body}\n\nF&G:{fg} ({fg_lbl})","plain"))
      try:
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
          s.login(GMAIL,app_pw); s.send_message(msg)
        print("Alert email sent")
      except Exception as e: print(f"Email err:{e}")
  return results

if __name__=="__main__": main()
