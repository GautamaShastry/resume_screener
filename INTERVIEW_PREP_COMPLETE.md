# Resume Analyzer - Complete Interview Preparation Guide

## 🏗️ ARCHITECTURE OVERVIEW

### System Components
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React + Vite  │────▶│  Spring Boot    │────▶│  Flask + AI     │
│   Port: 5173    │     │  Port: 8001     │     │  Port: 6000     │
│   (Frontend)    │     │  (Backend API)  │     │  (AI Service)   │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                        ┌────────▼────────┐
                        │   PostgreSQL    │
                        │   Port: 5432    │
                        └─────────────────┘
```

### Why This Architecture?

**Q: Why decouple Spring Boot and Flask?**

> "We chose a microservices approach for several reasons:
> 1. **Language Optimization**: Python has superior ML/NLP libraries (spaCy, Sentence Transformers, LangChain). Java excels at enterprise features (security, transactions, ORM).
> 2. **Independent Scaling**: AI processing is CPU/GPU intensive. We can scale Flask horizontally without affecting the auth/database layer.
> 3. **Fault Isolation**: If the AI service crashes, users can still login, view history, and upload files. The backend gracefully handles AI unavailability.
> 4. **Team Specialization**: ML engineers work on Flask, backend engineers on Spring Boot, without stepping on each other."

---

## 🤖 MULTI-AGENT SYSTEM (LangGraph)

### The 6 Agents

| Agent | Purpose | Tools Used | Why Separate? |
|-------|---------|------------|---------------|
| **Resume Parser** | Extract text, sections, skills | PyMuPDF, spaCy, GPT-4 | Specialized in document parsing |
| **Job Parser** | Extract requirements, skills | spaCy, GPT-4 | Different parsing logic than resumes |
| **Matcher** | Calculate compatibility score | Sentence Transformers | Pure computation, no LLM needed |
| **ATS Optimizer** | Generate ATS recommendations | GPT-4 | Creative generation task |
| **Career Advisor** | Provide career guidance | GPT-4 (temp=0.7) | Higher creativity needed |
| **Report Generator** | Create PDF/HTML reports | ReportLab, Matplotlib | No AI, just formatting |

### Why Multiple Agents Reduce Hallucinations

**Q: "Why not use one big prompt?"**

> "Single prompts suffer from:
> 1. **Context Overload**: GPT-4 loses focus with 4000+ token prompts
> 2. **Task Confusion**: Mixing extraction + analysis + generation = inconsistent outputs
> 3. **No Validation**: Can't verify intermediate results
>
> Our mulbackAnalyhod = "fallckMetba", fallerviceame = "aiSeaker(nircuitBr
@Cation
// Configur
pendency></defactId>
oot3</artiring-bilience4j-sptId>resifacrtpId>
    <a4j</grou.resiliencethubio.gi<groupId>dency>
    ml
<depenpom.x
// Add to ava```jce4j)

en(Resilit Breaker Circui
### d)
d AdShoul (What You PATTERNSE RESILIENC-

## 🛡️ 
--
"' messageilableervice unavalts or a 'sesu cached r*: Return*Fallback*. *lay
> 3nential dewith expo3 retries f**: with Backof*Retry  2. *seconds
>sk for 30  calling Flares, stopfailuter 5  Af*:uit Breaker*. **Circ
> 1 add:ldction, I wou In produ user. to therrorturns an eils and reequest fa r, the"Currently

> own?"**s dif Flask iQ: "What 

**);
}
```.getBody(onsespurn re   
    ret;
 lt)esury.save(rsultRepositoatchRe m
   ;d"))ysisI"anal.get(dy()tBoresponse.gesisId(tAnaly.sesult    rey"));
act("accury().geod.getBre(responseMatchScoet result.s
   ult();hResw Matc result = neMatchResult
    tgreSQLPosto e results av  // 4. S    );
    
class
     Map.     
eaders),(body, httpEntity<>      new H
  hod.POST,Met        Httpnalyze",
/api/a000st:6://localhohttp
        "hange(ate.excmplestTese = rap> responity<MntponseE
    Res AI serviceFlask // 3. Call 
    
   ());Description.get", jobTextbDescriptionody.add("jo  });
    b }
  leName();me.getFi return resu() {etFilenamering glic St   pubrride
       @Ove {
      eData())etFilme.gresuResource(ByteArray new le",d("fiad   body.Map<>();
 ltiValuedMu new Linkebody =, Object> ueMap<StringltiVal    Muquest
reipart Prepare mult 2.   //
    ;
  d).get()riptionIId(jobDescindBy.fpositorynReioescriptjobD = ption jobJobDescri;
    Id).get()esumeById(rository.findesumeRepsume = rre    Resume ostgreSQL
from P/ 1. Fetch {
    /ptionId) g jobDescri Long resumeId,Resume(Lonct> match Objeng,Map<Stria
public ce.javServisultMatchRe
// 

```java It WorksN

### HowMUNICATIOOMOT ↔ FLASK CG BO
## 🔄 SPRIN"

---
e.architectur to our esn't applyh dog, whicookie sendinutomatic c a exploit attacksders. CSRFion heaorizatkens in AuthJWT toss tateleAPI uses ses. Our kith coons wied sessioowser-bas is for brctionF prote

> "CSRF?"**ble CSR"Why disa`

**Q: ld();
}
``.bui       class)
 Filter.ionAuthenticatwordUsernamePassAuthFilter, re(jwtBefoFilter   .addSS))
     licy.STATELEnCreationPossioionPolicy(SeCreatonssiss.se       se> 
     ement(sess -sessionManag       . )
         Protected
  //            ()    atedauthentic).yRequest(   .an         c
/ Publi()  /").permitAllapi/auth/**atchers("/ .requestM     
       authauth ->pRequests(rizeHttutho
        .a)))nSource(onfiguratioe(corsCnSourcuratioconfigcors.s -> or     .cors(c   REST API
 bled forDisa())  // f.disablecsrf -> csrrf(    .csn http
    
    retury http) {ecurittpS(HterChainrityFiltcuChain serityFilterc Secu@Bean
publi
```java
Config
urity "

### Secnring logiduership mail ownirms e Confn**:ior Verificat 3. **Usek window
>acimiting attutes, ls in 2 minOTP expiretection**: ng Pro 2. **Phishil access
>emaier needs , attackomised is comprasswordif pds**: Even olen Passwor:
> 1. **Sttys securin addiocattiuthenactor a"Two-f 
>?"**
ordpasswjust  of P instead"Why OT`

**Q: );
}
`` .compact(
       cret)S256, seorithm.HSignatureAlgignWith(        .s 24 hours
400000)) //86illis() + rentTimeMm.curSysteate(ation(new DpirtEx    .seate())
    At(new DetIssued
        .sject(email)etSub        .sr()
 Jwts.builde    returnl) {
tring emaiToken(Senerateg gblic Strinjava
puWTUtil.va
// J```ja

mentationT Imple

### JW header
```rization Authoude JWT in inclquestssequent re subAlled
4. JWT issu→ n expiry) -mi DB (2againstVerified  → ters OTP. User enl SMTP
3GmaiTP sent via rified → Oials ventCreden → logs i2. User PostgreSQL
Stored in Crypt → ed with Bd hashsworns up → Pas
1. User sig
```ow

### FlSYSTEMATION 🔐 AUTHENTIC
## 

---
iner"tan 512MB cons iry**: Fit*Memo. *se case
> 4 for our uodelsarger md as lgoo*: 95% as *Quality* *
> 3., no costno latencycalls, **: No API  2. **Localmpnet
>or s f200m0ms vs odes in ~5*: Enc 1. **Speed*e:
>LM becausse Mini cho"We
>  Best |
 Variable || API |g-ada-002 xt-embeddiner |
| te Slow | Bett 420MB | |t-base-v2| all-mpneGood |
MB | Fast | M-L6-v2 | 80niLll-Mi------|
| a--|------|---------------|lity |
|peed | Quaze | S| Model | Si

-v2?iniLM-L6y all-M

### Whsed." aren't misrdshave keywoures must-le-based ens 40% rukills, whileescribe sdates dndior how caexibility fllows fl weight asemantice 60% 
>
> Thb pairsjosume- re 500ing withr test ouance in Best bal/40:> - 60sing
zed paraphranalio strict, pe - 50/50: Toandidates
>d cifieched unqual mato lenient,0/20: To> - 8ios:
ltiple rattested mu*

> "We y?"*cificallpehy 60/40 s
**Q: "Wce"
erienears expars: "5+ yappear
- Yefied" must P certi"PMications: 
- CertiferallyAWS" lit have "ments: Mustrequire
- Hard s:**atche``

**C* 100
`_set)) job_skillsn(ched) / le = (len(matmatchll_et)
skils_sme_skilsufference(rells_set.dib_skissing = jomi_set)
job_skillstion(et.intersecme_skills_sed = resu
matchs)
n job_skill) for s it(s.lower(set = s_seob_skill)
jsume_skills in reor s() fs.lower = set(skills_set

resume_, ...}es', 'aws'et', 'kubernkerjava', 'doc{'python', 'skills = n_
commobased dataedefinem pratching fro mxact skill
# E
```pythonNER) - 40%
d (spaCy le-Base## Why Rumiss."

#'s a hard hatRES AWS, tREQUIf the job ms. But i platforboth cloudre ey'ecause thd' breuinst 'AWS reqly agaie' highperienc exscore 'Azureght ient. It mig is too lenmatchinc ti
> "Seman*
ic?"* 100% semant"Why not

**Q: ure"ed architectibuttr "dis relates to"systemsle Built scalab: " Contextmmer"
-thon progra"Py ≈ veloper"hon de "Pytnyms:- Syno"
ring teameeged engin ≈ "Mana team of 5""Ledraphrases: :**
- Patches**Ca`


``100dding2) * be, emng1ity(embeddisimilar= cosine_similarity iption)
scrb_deencode(jo= model.g2 embeddinme_text)
ncode(resuodel.e mmbedding1 =)
e80MB, fast6-v2 model (niLM-Lll-Mis ahon
# Use%

```pyts) - 60 Transformeric (Sentence# Why Semant
```

## * 0.4)_match+ (skillity * 0.6) imilar (semantic_s_score =ython
finalula
```pForm# The 

##brid)M (60/40 HyALGORITH 📊 SCORING ##

---

flicts."conly without neousges simulta messa adddvisor can Ad CareerOptimizer anth ATS ion where bol executlle paranablesThis e. s the listscatenateting, it conrierw of ovnstead`, i`messagesrite to ents wultiple agr. When mucegGraph red"It's a Lan

> ?"**tor.add]`, operaList[str]`Annotated[hat's the "WQ: 
**tr]
```
tional[serror: Op
    Auto-mergesr.add]  # ], operatot[strnnotated[Lismessages: A   tadata
 Me # 
   str]
    ce: List[career_advitr]
    st[s: Lidationsmens_recom   at)
 orAdvisptimizer/ O bywrittentions (ecommenda R  #  
  [str]
  ills: Listsing_skmis   ]
 ls: List[stred_skilch
    matfloattch_score: r)
    may Matcheitten balysis (wr    # Ans
    
arser writely Job P  # On  List[str]  kills: s
    job_ser writearsnly Resume Ptr]   # Ot[sLisskills:   resume_tes
   Parser wrinly Resume  # O        t: str ume_tex   res
 ts)pecific ageny sritten bed data (w    # Pars  
ion: str
  descript    job_
l[bytes]le: Optionaesume_fi
    rInput
    # TypedDict):ntState(s Agethon
clasent

```pytate Managemraph SangG

### Lds."ific fiel spec toly writecan on Agents hema.rces scte` enfo`AgentStatate**: yped S> 3. **Tam.
g downstrenatinucill hastead ofls early infaie, Agent 2 ags garbnt 1 output: If AgeValidation**se  2. **Stepwige.
>esn't judracts—doy extonlsume Parser  job. ReNEas O hh agent: Eacion**lizat*Specia. *oach:
> 1gent apprti-a