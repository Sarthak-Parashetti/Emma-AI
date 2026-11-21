"""
Offline benchmark of Emma's command-understanding stage: planner -> normalize -> rule-based NLU.
Controllers are NOT executed, so no Windows APIs, microphone or network are needed.
Usage:  python emma_nlu_benchmark.py <path-to-Emma/backend>
"""
import sys, time, types, json, statistics, platform
backend = sys.argv[1] if len(sys.argv) > 1 else "."
sys.path.insert(0, backend)
stub = types.ModuleType("desktop.command_router"); stub.route_command = lambda intent: None
sys.modules["desktop.command_router"] = stub          # avoid importing Windows-only controllers
from agent.planner import create_plan
from agent.executor import normalize
from desktop.nlu.engine import parse

T = [
 ("search google for python tutorials", [("browser_action","google_search")]),
 ("search youtube for lofi music", [("browser_action","youtube_search")]),
 ("open youtube", [("browser_action","website")]), ("open github", [("browser_action","website")]),
 ("open gmail", [("browser_action","website")]), ("open linkedin", [("browser_action","website")]),
 ("open stackoverflow", [("browser_action","website")]), ("open reddit", [("browser_action","website")]),
 ("launch chatgpt", [("browser_action","website")]), ("please open google", [("browser_action","website")]),
 ("can you search google for weather in pune", [("browser_action","google_search")]),
 ("search the web for python tutorials", [("browser_action","google_search")]),
 ("google machine learning", [("browser_action","google_search")]), ("go to youtube", [("browser_action","website")]),
 ("open settings", [("system_action","settings")]), ("open task manager", [("system_action","task_manager")]),
 ("open control panel", [("system_action","control_panel")]), ("open command prompt", [("system_action","cmd")]),
 ("open powershell", [("system_action","powershell")]), ("open calculator", [("system_action","calculator")]),
 ("open notepad", [("system_action","notepad")]), ("open device manager", [("system_action","device_manager")]),
 ("open registry editor", [("system_action","registry_editor")]), ("open sound settings", [("system_action","sound_settings")]),
 ("start the task manager", [("system_action","task_manager")]), ("launch settings", [("system_action","settings")]),
 ("show me the task manager", [("system_action","task_manager")]),
 ("what time is it", [("system_action","current_time")]), ("what is the date today", [("system_action","current_date")]),
 ("what day is it", [("system_action","current_day")]), ("battery status", [("system_action","battery_status")]),
 ("how much battery is left", [("system_action","battery_status")]), ("cpu usage", [("system_action","cpu_usage")]),
 ("how is my cpu doing", [("system_action","cpu_usage")]), ("ram usage", [("system_action","ram_usage")]),
 ("how much memory is being used", [("system_action","ram_usage")]), ("disk usage", [("system_action","disk_usage")]),
 ("how much disk space do i have", [("system_action","disk_usage")]), ("system uptime", [("system_action","system_uptime")]),
 ("what is my ip address", [("system_action","ip_address")]), ("what is my computer name", [("system_action","hostname")]),
 ("which operating system am i running", [("system_action","operating_system")]),
 ("open chrome", [("app_action","open")]), ("open visual studio code", [("app_action","open")]),
 ("open vscode", [("app_action","open")]), ("open spotify", [("app_action","open")]),
 ("launch discord", [("app_action","open")]), ("start whatsapp", [("app_action","open")]), ("run excel", [("app_action","open")]),
 ("close chrome", [("app_action","close")]), ("close spotify", [("app_action","close")]), ("quit discord", [("app_action","close")]),
 ("exit vscode", [("app_action","close")]), ("terminate notepad", [("app_action","close")]), ("kill chrome", [("app_action","close")]),
 ("restart chrome", [("app_action","restart")]), ("is chrome running", [("app_action","is_running")]),
 ("list running apps", [("app_action","list_running")]), ("show running applications", [("app_action","list_running")]),
 ("please open word", [("app_action","open")]), ("could you open powerpoint", [("app_action","open")]),
 ("minimize chrome", [("window_action","minimize")]), ("maximize chrome", [("window_action","maximize")]),
 ("restore notepad", [("window_action","restore")]), ("switch to chrome", [("window_action","activate")]),
 ("focus vscode", [("window_action","activate")]), ("bring spotify to front", [("window_action","activate")]),
 ("hide discord", [("window_action","minimize")]), ("fullscreen chrome", [("window_action","maximize")]),
 ("list windows", [("window_action","list")]), ("show windows", [("window_action","list")]),
 ("minimise the browser window", [("window_action","minimize")]),
 ("create folder projects", [("file_action","create_folder")]), ("create file notes.txt", [("file_action","create_file")]),
 ("delete file notes.txt", [("file_action","delete_file")]), ("search file resume", [("file_action","search_file")]),
 ("rename old.txt to new.txt", [("file_action","rename_file")]), ("move report.pdf to documents", [("file_action","move_file")]),
 ("copy report.pdf to desktop", [("file_action","copy_file")]), ("make a new folder called photos", [("file_action","create_folder")]),
 ("find the file budget", [("file_action","search_file")]),
 ("play music", [("media_action","play_pause")]), ("pause", [("media_action","play_pause")]),
 ("pause the music", [("media_action","play_pause")]), ("next song", [("media_action","next")]), ("skip", [("media_action","next")]),
 ("previous song", [("media_action","previous")]), ("mute", [("media_action","mute")]), ("mute the volume", [("media_action","mute")]),
 ("take a screenshot", [("screenshot_action","take")]), ("capture the screen", [("screenshot_action","take")]),
 ("read the text on my screen", [("ocr_action","read")]), ("extract text from screenshot", [("ocr_action","read")]),
 ("what is on my screen", [("vision_action","describe")]), ("describe my screen", [("vision_action","describe")]),
 ("scan this page for phishing", [("security_action","scan")]), ("is this website safe", [("security_action","scan")]),
 ("check this page for scams", [("security_action","scan")]),
 ("open notepad and open calculator", [("system_action","notepad"),("system_action","calculator")]),
 ("open chrome and search google for python", [("app_action","open"),("browser_action","google_search")]),
 ("open youtube and then open github", [("browser_action","website"),("browser_action","website")]),
 ("take a screenshot and then read the text on my screen", [("screenshot_action","take"),("ocr_action","read")]),
 ("open spotify, then play music", [("app_action","open"),("media_action","play_pause")]),
 ("minimize chrome; open notepad", [("window_action","minimize"),("system_action","notepad")]),
 ("open vscode and open chrome and open spotify", [("app_action","open")]*3),
 ("search google for salt and pepper recipes", [("browser_action","google_search")]),
 ("search youtube for tom and jerry", [("browser_action","youtube_search")]),
 ("create folder research and notes", [("file_action","create_folder")]),
 ("how are you today", None), ("tell me a joke", None), ("explain how photosynthesis works", None), ("who wrote hamlet", None),
 ("what is the capital of france", None), ("write a poem about the sea", None), ("thanks emma", None),
 ("give me tips to study better", None), ("recommend a good movie", None), ("translate hello to hindi", None),
]
PARAPHRASE = {"please open google","can you search google for weather in pune","search the web for python tutorials","google machine learning",
 "go to youtube","start the task manager","show me the task manager","launch settings","how much battery is left","how is my cpu doing",
 "how much memory is being used","how much disk space do i have","what is my computer name","which operating system am i running",
 "what is my ip address","what time is it","what is the date today","what day is it","please open word","could you open powerpoint",
 "bring spotify to front","hide discord","fullscreen chrome","minimise the browser window","make a new folder called photos",
 "find the file budget","pause the music","skip","mute the volume","capture the screen","read the text on my screen",
 "extract text from screenshot","what is on my screen","describe my screen","scan this page for phishing","is this website safe",
 "check this page for scams","show running applications","is chrome running","exit vscode","quit discord","kill chrome","terminate notepad",
 "launch chatgpt","launch discord","start whatsapp","run excel","show windows","list running apps"}
ARGAND = {"search google for salt and pepper recipes","search youtube for tom and jerry","create folder research and notes"}
def category(m, e):
    if e is None: return "out_of_scope"
    if m in ARGAND: return "compound_arg"
    if len(e) > 1: return "compound"
    return "paraphrase" if m in PARAPHRASE else "canonical"
def pipeline(msg):
    out = []
    for t in create_plan(msg):
        t.target = normalize(t.target); r = parse(t.target)
        out.append((r["intent"], r["action"]) if r else None)
    return out
rows, lat = [], []
for msg, exp in T:
    runs = []
    for _ in range(5):
        t0 = time.perf_counter(); got = pipeline(msg); runs.append((time.perf_counter()-t0)*1e6)
    med = statistics.median(runs); lat.append(med)
    ok = all(g is None for g in got) if exp is None else (got == exp)
    rows.append({"cat": category(msg, exp), "utterance": msg, "expected": exp, "got": got, "ok": ok, "us": round(med,1)})
cats, dom = {}, {}
for r in rows:
    a = cats.setdefault(r["cat"], [0,0]); a[0]+=r["ok"]; a[1]+=1
    if r["expected"]:
        d = r["expected"][0][0]; b = dom.setdefault(d,[0,0]); b[0]+=r["ok"]; b[1]+=1
act = [r for r in rows if r["expected"] is not None]
s = {"python": platform.python_version(), "platform": platform.platform(), "total": len(rows),
     "overall": [sum(r["ok"] for r in rows), len(rows)], "actionable": [sum(r["ok"] for r in act), len(act)],
     "per_category": cats, "per_domain": dom,
     "latency_us": {"median": round(statistics.median(lat),1), "mean": round(statistics.mean(lat),1),
                    "p95": round(sorted(lat)[int(0.95*len(lat))-1],1), "max": round(max(lat),1)}}
json.dump({"summary": s, "rows": rows}, open("benchmark_results.json","w"), indent=1)
print(json.dumps(s, indent=1)); print("\nFAILURES:")
for r in rows:
    if not r["ok"]: print(f'- [{r["cat"]}] {r["utterance"]!r}  expected={r["expected"]}  got={r["got"]}')
