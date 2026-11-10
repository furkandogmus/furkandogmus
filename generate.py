import datetime, json, os, urllib.request
from xml.sax.saxutils import escape

USER = "furkandogmus"
WIDTH = 60
ART_X, INFO_X, TOP, LINE = 15, 300, 30, 20

THEMES = {
    "dark": dict(bg="#161b22", fg="#c9d1d9", key="#ffa657", value="#a5d6ff", dots="#616e7f"),
    "light": dict(bg="#f6f8fa", fg="#24292f", key="#953800", value="#0a3069", dots="#c2cfde"),
}


def stats():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    q = """{user(login:"%s"){followers{totalCount}
      contributionsCollection{contributionCalendar{totalContributions}}
      repositories(ownerAffiliations:OWNER,privacy:PUBLIC,first:100){totalCount nodes{stargazerCount}}}}""" % USER
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": q}).encode(),
                                 {"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    u = json.load(urllib.request.urlopen(req))["data"]["user"]
    return dict(repos=u["repositories"]["totalCount"],
                stars=sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
                followers=u["followers"]["totalCount"],
                contrib=u["contributionsCollection"]["contributionCalendar"]["totalContributions"])


def since(start):
    today = datetime.date.today()
    months = (today.year - start.year) * 12 + today.month - start.month - (today.day < start.day)
    return f"{months // 12} years, {months % 12} months"


def info_lines(s):
    return [
        ("title", "furkan@dogmus"),
        ("kv", "OS", "macOS, Linux (RHEL)"),
        ("kv", "Uptime", "on GitHub " + since(datetime.date(2020, 8, 13))),
        ("kv", "Host", "Hacettepe University"),
        ("kv", "Kernel", "DevOps Engineer"),
        ("kv", "Shell", "zsh, bash"),
        ("blank",),
        ("kv", "Languages.Programming", "Go, Bash, Python"),
        ("kv", "Languages.Infra", "YAML, HCL, Dockerfile"),
        ("kv", "Languages.Real", "Turkish, English"),
        ("blank",),
        ("kv", "Focus", "Kubernetes (CKA / CKAD / CKS)"),
        ("kv", "Interests.Platform", "Kubernetes, IaC, GitOps"),
        ("kv", "Interests.Observability", "Prometheus, Grafana, ELK"),
        ("kv", "Interests.Systems", "Linux, networking, storage"),
        ("gap",),
        ("title", "- Contact"),
        ("kv", "Email.Personal", "furkandogmus9183@gmail.com"),
        ("kv", "GitHub", USER),
        ("kv", "Location", "Ankara, Türkiye"),
        ("gap",),
        ("title", "- GitHub Stats"),
        ("kv", "Repos", f"{s['repos']} public  |  Stars: {s['stars']}"),
        ("kv", "Contributions", f"{s['contrib']} (last year)  |  Followers: {s['followers']}"),
    ]


def render(theme, art, s):
    t = THEMES[theme]
    rows = max(len(art), len(info_lines(s)))
    h = TOP + (rows - 1) * LINE + 20
    w = INFO_X + WIDTH * 9.7 + 20
    out = [f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="Consolas,'DejaVu Sans Mono',Menlo,monospace" width="{w:.0f}px" height="{h}px" font-size="16px">
<style>.key{{fill:{t['key']}}}.value{{fill:{t['value']}}}.cc{{fill:{t['dots']}}}text,tspan{{white-space:pre}}</style>
<rect width="{w:.0f}px" height="{h}px" fill="{t['bg']}" rx="15"/>
<text x="{ART_X}" y="{TOP}" fill="{t['fg']}">"""]
    for i, line in enumerate(art):
        out.append(f'<tspan x="{ART_X}" y="{TOP + i * LINE}">{escape(line)}</tspan>')
    out.append(f'</text>\n<text x="{INFO_X}" y="{TOP}" fill="{t["fg"]}">')
    for i, item in enumerate(info_lines(s)):
        y = TOP + i * LINE
        if item[0] == "title":
            dash = "-" + "—" * (WIDTH - len(item[1]) - 2) + "-"
            out.append(f'<tspan x="{INFO_X}" y="{y}">{escape(item[1])}</tspan> {dash}')
        elif item[0] == "blank":
            out.append(f'<tspan x="{INFO_X}" y="{y}" class="cc">. </tspan>')
        elif item[0] == "kv":
            _, k, v = item
            keys = "".join(('.' if j else '') + f'<tspan class="key">{escape(p)}</tspan>'
                           for j, p in enumerate(k.split(".")))
            dots = " " + "." * max(WIDTH - 2 - len(k) - 1 - len(v) - 2, 1) + " "
            out.append(f'<tspan x="{INFO_X}" y="{y}" class="cc">. </tspan>{keys}:'
                       f'<tspan class="cc">{dots}</tspan><tspan class="value">{escape(v)}</tspan>')
    out.append("</text>\n</svg>\n")
    return "\n".join(out)


if __name__ == "__main__":
    art = open("ascii_portrait.txt").read().rstrip("\n").split("\n")
    s = stats()
    for theme in THEMES:
        open(f"{theme}_mode.svg", "w").write(render(theme, art, s))
