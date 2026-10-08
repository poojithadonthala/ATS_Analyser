import re
from collections import Counter

WEIGHTS={'required':40,'optional':10,'semantic':10,'education':10,'experience':10,'projects':10,'resume_quality':5,'language':5}
ALIASES={'machine learning':['machine learning','machine-learning','ml'], 'scikit-learn':['scikit-learn','sklearn'], 'javascript':['javascript','js'], 'natural language processing':['natural language processing','nlp']}
def normalize(s): return re.sub(r'[^a-z0-9]+',' ',s.lower()).strip()
def skill_match(text, skill):
    n=normalize(skill)
    variants=ALIASES.get(n,[n])
    if n=='python': variants=['python']
    for v in variants:
        if re.search(r'(?<![a-z0-9])'+re.escape(v)+r'(?![a-z0-9])',text.lower()):
            i=text.lower().find(v)
            return {'skill':skill,'matched':True,'evidence':text[max(0,i-55):i+len(v)+75].replace('\n',' ').strip()}
    return {'skill':skill,'matched':False,'evidence':None}
def analyze(text, job):
    low=text.lower(); req=[s.strip() for s in job.required_skills.splitlines() if s.strip()]; opt=[s.strip() for s in job.optional_skills.splitlines() if s.strip()]
    required=[skill_match(text,s) for s in req]; optional=[skill_match(text,s) for s in opt]
    section_words=['education','experience','projects','skills','certification']
    sections={s:bool(re.search(r'(?im)^\s*'+s+r'\b',text)) for s in section_words}
    reqscore=100*sum(x['matched'] for x in required)/len(required) if required else 0
    optscore=100*sum(x['matched'] for x in optional)/len(optional) if optional else 0
    words=set(re.findall(r'[a-z]{3,}',normalize(job.description))); overlap=len(words & set(re.findall(r'[a-z]{3,}',normalize(text))))
    semantic=min(100, round(overlap/max(1,len(words))*250))
    education=80 if sections['education'] else 25
    experience=75 if sections['experience'] else 45
    projects=80 if sections['projects'] else 35
    quality=round(sum(sections.values())/len(sections)*100)
    sentences=[s.strip() for s in re.split(r'[.!?\n]+',text) if len(s.split())>5]
    action=['built','developed','designed','implemented','analyzed','created','led','optimized','deployed','managed']
    lang=min(100,55+sum(any(s.lower().startswith(v) for v in action) for s in sentences)*5)
    scores={'required':round(reqscore),'optional':round(optscore),'semantic':semantic,'education':education,'experience':experience,'projects':projects,'resume_quality':quality,'language':lang}
    total=round(sum(scores[k]*WEIGHTS[k] for k in WEIGHTS)/100)
    found=[x['skill'] for x in required+optional if x['matched']]; missing=[x['skill'] for x in required if not x['matched']]
    strengths=[]; weaknesses=[]; recommendations=[]
    if found: strengths.append('Resume evidence found for '+', '.join(found[:8])+'.')
    if sections['education']: strengths.append('An education section was detected.')
    if missing: weaknesses.append('Required skills without explicit resume evidence: '+', '.join(missing)+'.'); recommendations.append({'category':'High priority','recommendation':'If genuinely possessed, add evidence for: '+', '.join(missing)+'. Otherwise use the gap to guide learning.'})
    if not sections['projects']: weaknesses.append('No standard Projects heading was detected.'); recommendations.append({'category':'High priority','recommendation':'Add a Projects section with your specific contribution and technologies.'})
    if not any(any(s.lower().startswith(v) for v in action) for s in sentences): recommendations.append({'category':'Medium priority','recommendation':'Start accomplishment statements with accurate action verbs.'})
    if not re.search(r'\b\d+%?\b',text): recommendations.append({'category':'Medium priority','recommendation':'Add a measurable result if available; do not estimate or invent metrics.'})
    detail={'scores':scores,'required_skills':required,'optional_skills':optional,'keywords':{'job_description_terms':sorted(words)[:50],'overlap_count':overlap},'semantic_explanation':'Lexical overlap estimate based on job-description terms; this baseline is not an embedding model and may miss conceptual matches.','education_analysis':{'score':education,'note':'Section-presence heuristic only; verify degree requirements manually.'},'experience_analysis':{'score':experience,'note':'Section-presence heuristic only; projects and internships can provide fresher evidence.'},'projects_analysis':{'score':projects,'note':'Project section presence heuristic; no achievements or metrics are inferred.'},'resume_quality':{'score':quality,'sections':sections},'language_analysis':{'score':lang,'note':'Lightweight action-verb heuristic; not a grammar checker.'},'strengths':strengths,'weaknesses':weaknesses,'missing_skills':{'critical':missing,'optional':[x['skill'] for x in optional if not x['matched']]},'corrections':[],'recommendations':recommendations,'qualification_status':'QUALIFIED' if total>=job.minimum_score else 'NOT QUALIFIED','minimum_score':job.minimum_score}
    return total,detail
