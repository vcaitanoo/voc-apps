#!/usr/bin/env python3
import argparse, base64, gzip, json, re
from pathlib import Path
from urllib.parse import urlparse


def gitlab_parts(project_url: str):
    u = urlparse(project_url.rstrip('/'))
    if u.scheme != 'https' or u.netloc.lower() != 'gitlab.com':
        raise SystemExit('Use a URL HTTPS de projeto em gitlab.com')
    path = u.path.strip('/')
    if '/' not in path:
        raise SystemExit('URL deve apontar para namespace/projeto')
    return path


def restore_main_activity(recovered: Path):
    main_java = recovered / 'MainActivity.java'
    packed = recovered / 'MainActivity.java.gz.b64'
    if not main_java.exists() and packed.exists():
        raw = base64.b64decode(packed.read_text(encoding='ascii').strip())
        main_java.write_bytes(gzip.decompress(raw))
    return main_java


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project_url', help='Ex.: https://gitlab.com/namespace/voc-apps')
    ap.add_argument('--branch', default='main')
    ap.add_argument('--root', default='.')
    args = ap.parse_args()

    root = Path(args.root)
    project_path = gitlab_parts(args.project_url)
    raw = f'https://gitlab.com/{project_path}/-/raw/{args.branch}'
    catalog_url = f'{raw}/manifest.json'

    manifest_path = root / 'manifest.json'
    data = json.loads(manifest_path.read_text(encoding='utf-8'))

    warnings = []
    for app in data.get('apps', []):
        if app.get('distribution', 'apk') != 'apk':
            continue
        app_id = app['id']
        version = app.get('versionName', '')
        candidates = list((root / 'apks' / app_id).rglob('*.apk')) if (root / 'apks' / app_id).exists() else []
        matching = [p for p in candidates if version and version in p.as_posix()]
        if len(matching) == 1:
            rel = matching[0].relative_to(root).as_posix()
            app['apkUrl'] = f'{raw}/{rel}'
        elif app.get('status') == 'published':
            warnings.append(f'{app_id}: APK publicado atual não está preservado localmente; URL não foi trocada')

    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    recovered = root / 'migration' / 'gitlab' / 'recovered-v1.2.4'
    catalog_java = recovered / 'CatalogClient.java'
    if catalog_java.exists():
        txt = catalog_java.read_text(encoding='utf-8')
        txt = re.sub(
            r'static final String CATALOG_URL\s*=\s*\n\s*"[^"]+";',
            'static final String CATALOG_URL =\n            "' + catalog_url + '";',
            txt,
            count=1,
        )
        catalog_java.write_text(txt, encoding='utf-8')

    main_java = restore_main_activity(recovered)
    if main_java.exists():
        txt = main_java.read_text(encoding='utf-8').replace(
            'A consultar o catálogo no GitHub…', 'A consultar o catálogo…'
        )
        main_java.write_text(txt, encoding='utf-8')

    report = {
        'gitlabProject': args.project_url.rstrip('/'),
        'branch': args.branch,
        'catalogUrl': catalog_url,
        'warnings': warnings,
        'nextRequiredAction': 'Recuperar/validar o projeto Android completo da 1.2.4 antes de gerar a versão-ponte.'
    }
    (root / 'gitlab-finalization-report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
