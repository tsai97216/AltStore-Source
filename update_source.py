import os
import json
import requests
from packaging import version as pkg_version

# =========================
# 🌙 Chi Sources 基本設定
# =========================
FILENAME = "apps.json"

YOUR_GITHUB_ID = "tsai97216"
DISPLAY_NAME = "Chi Sources"

SOURCE_URL = f"https://{YOUR_GITHUB_ID}.github.io/My-AltStore-Source/{FILENAME}"
SOURCE_ICON_URL = f"https://raw.githubusercontent.com/{YOUR_GITHUB_ID}/My-AltStore-Source/main/source_icon.PNG"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# =========================
# 📦 GitHub Apps
# =========================
LOCAL_APPS = [
    {
        "repo": "bggRGjQaUbCoE/PiliPlus",
        "name": "PiliPlus",
        "bundleID": "com.bgg.piliplus",
        "icon": "https://raw.githubusercontent.com/bggRGjQaUbCoE/PiliPlus/main/assets/images/logo/desktop/logo_large.png",
        "subtitle": "第三方 Bilibili 客戶端",
        "desc": "提供自動全螢幕、音量均衡、彈幕過濾等功能。",
        "color": "7DCEA0",
    }
]

# =========================
# 🌐 AppTesters（4個）
# =========================
SOURCE_DATA_URL = "https://raw.githubusercontent.com/apptesters-org/AppTesters_Repo/main/apps.json"

TARGET_APPS = {
    "Facebook",
    "Threads",
    "Instagram",
    "EeveeSpotify"
}

APP_STYLE = {
    "Facebook": {"color": "1877F2", "subtitle": "Facebook修改版"},
    "Threads": {"color": "2D2D2D", "subtitle": "Threads修改版"},
    "Instagram": {"color": "E4405F", "subtitle": "Instagram修改版"},
    "EeveeSpotify": {"color": "1DB954", "subtitle": "Spotify修改版"},
}

# =========================
# 🌐 Ballermc repo（YT系）
# =========================
YT_REPO = "https://repo.ballermc.com/repo.json"

YT_STYLE = {
    "YTPlusM": {
        "color": "FF4D4D",
        "subtitle": "YouTube 修改版"
    },
    "YouTube Music Ultimate+": {
        "color": "FF4D4D",
        "subtitle": "YouTube Music 修改版"
    }
}

# =========================
# 📡 fetch
# =========================
def fetch_json(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print(f"⚠️ fetch failed {url}: {r.status_code}")
            return None
        return r.json()
    except:
        return None


def fetch_remote():
    data = fetch_json(SOURCE_DATA_URL)
    return data["apps"] if data else []


def fetch_yt_repo():
    data = fetch_json(YT_REPO)
    if not data:
        return []
    return data.get("apps", [])

# =========================
# 🔥 version helper
# =========================
def get_version(app):
    v = app.get("version")
    if v:
        return v

    versions = app.get("versions") or []
    if versions:
        return versions[0].get("version", "0.0.0")

    return "0.0.0"


def keep_latest_only(apps):
    latest = {}

    for app in apps:
        bid = app.get("bundleIdentifier")
        if not bid:
            continue

        ver = get_version(app)

        if bid not in latest:
            latest[bid] = app
            continue

        old_ver = get_version(latest[bid])

        try:
            if pkg_version.parse(ver) > pkg_version.parse(old_ver):
                latest[bid] = app
        except:
            latest[bid] = app

    return list(latest.values())

# =========================
# 🐙 GitHub builder
# =========================
def build_from_github(app):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    url = f"https://api.github.com/repos/{app['repo']}/releases/latest"

    r = requests.get(url, headers=headers)
    data = r.json()

    assets = data.get("assets", [])
    ipa = next((a for a in assets if a["name"].endswith(".ipa")), None)

    return {
        "name": app["name"],
        "bundleIdentifier": app["bundleID"],
        "developerName": app["repo"].split("/")[0],
        "subtitle": app["subtitle"],
        "localizedDescription": app["desc"],
        "iconURL": app["icon"],
        "tintColor": app["color"],
        "category": "entertainment",
        "screenshots": [],
        "versions": [
            {
                "version": (data.get("tag_name") or "").replace("v", ""),
                "date": (data.get("published_at") or "")[:10],
                "localizedDescription": (data.get("body") or "")[:1000],
                "downloadURL": ipa["browser_download_url"] if ipa else "",
                "size": ipa["size"] if ipa else 0,
            }
        ]
    }

# =========================
# 🌐 AppTesters builder
# =========================
def build_from_apptesters(app):
    name = app.get("name")

    style = APP_STYLE.get(name, {
        "color": None,
        "subtitle": "Imported from AppTesters"
    })

    return {
        "name": name,
        "bundleIdentifier": app.get("bundleIdentifier"),
        "developerName": "AppTesters",
        "subtitle": style["subtitle"],
        "localizedDescription": app.get("localizedDescription", ""),
        "iconURL": app.get("iconURL") or app.get("icon"),
        "tintColor": style["color"],
        "category": "social",
        "screenshots": [],
        "versions": [
            {
                "version": app.get("version", ""),
                "date": app.get("versionDate", ""),
                "localizedDescription": app.get("localizedDescription", ""),
                "downloadURL": app.get("downloadURL") or app.get("down"),
                "size": app.get("size", 0),
            }
        ]
    }

# =========================
# 🧠 YT repo builder
# =========================
def build_from_yt(app):
    name = app.get("name")
    style = YT_STYLE.get(name, {"color": None, "subtitle": "YouTube Mod"})

    versions = app.get("versions", [])
    v = versions[0] if versions else {}

    return {
        "name": name,
        "bundleIdentifier": app.get("bundleIdentifier"),
        "developerName": "Ballermc",
        "subtitle": style["subtitle"],
        "localizedDescription": app.get("localizedDescription", ""),
        "iconURL": app.get("iconURL"),
        "tintColor": style["color"],
        "category": "entertainment",
        "screenshots": [],
        "versions": [
            {
                "version": v.get("version", ""),
                "date": (v.get("date") or "")[:10],
                "localizedDescription": v.get("localizedDescription", ""),
                "downloadURL": v.get("downloadURL", ""),
                "size": v.get("size", 0),
            }
        ]
    }

# =========================
# 🚀 main
# =========================
def update_source():
    print(f"🚀 正在更新 {DISPLAY_NAME}...")

    apps_list = []

    # GitHub
    for app in LOCAL_APPS:
        apps_list.append(build_from_github(app))

    # AppTesters
    remote = fetch_remote()
    remote = [a for a in remote if a.get("name") in TARGET_APPS]
    remote = keep_latest_only(remote)

    for app in remote:
        apps_list.append(build_from_apptesters(app))

    # YT repo
    yt_data = fetch_yt_repo()
    yt_apps = [a for a in yt_data.get("apps", []) if a.get("name") in YT_STYLE]

    for app in yt_apps:
        apps_list.append(build_from_yt(app))

    # source
    source_data = {
        "name": DISPLAY_NAME,
        "identifier": f"com.{DISPLAY_NAME.lower().replace(' ', '')}.source",
        "sourceURL": SOURCE_URL,
        "subtitle": "iOS IPA Source",
        "description": f"{DISPLAY_NAME} auto curated source",
        "website": f"https://github.com/{YOUR_GITHUB_ID}/My-AltStore-Source",
        "iconURL": SOURCE_ICON_URL,
        "featuredApps": [a["bundleIdentifier"] for a in apps_list],
        "apps": apps_list,
        "news": []
    }

    with open(FILENAME, "w", encoding="utf-8") as f:
        json.dump(source_data, f, indent=2, ensure_ascii=False)

    print("🎉 Chi Sources 更新完成")


if __name__ == "__main__":
    update_source()
