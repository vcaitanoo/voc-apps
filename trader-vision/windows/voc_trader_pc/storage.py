from __future__ import annotations
from pathlib import Path
from dataclasses import asdict,fields
import os,json
from .models import Settings

APP_DIR=Path(os.environ.get('APPDATA') or Path.home())/'VOCTraderVisionPC'
CONFIG_FILE=APP_DIR/'settings.json'
JOURNAL_FILE=APP_DIR/'demo_journal.jsonl'

def load_settings()->Settings:
    if not CONFIG_FILE.exists():return Settings()
    try:
        raw=json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        allowed={x.name for x in fields(Settings)}
        return Settings(**{k:v for k,v in raw.items() if k in allowed})
    except (ValueError,TypeError):return Settings()

def save_settings(settings:Settings):
    APP_DIR.mkdir(parents=True,exist_ok=True)
    tmp=CONFIG_FILE.with_suffix('.tmp')
    tmp.write_text(json.dumps(asdict(settings),ensure_ascii=False,indent=2),encoding='utf-8')
    tmp.replace(CONFIG_FILE)
