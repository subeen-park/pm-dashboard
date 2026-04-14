from flask import Flask, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import json, os, uuid, requests as req
import pandas as pd
from datetime import datetime, date, timedelta

app = Flask(__name__)
CORS(app)

DATA_DIR      = os.path.join(os.path.dirname(__file__), 'data')
PROJECTS_FILE = os.path.join(DATA_DIR, 'projects.json')
TASKS_DIR     = os.path.join(DATA_DIR, 'tasks')
WEBHOOK_FILE  = os.path.join(DATA_DIR, 'webhook.json')
LOGS_FILE     = os.path.join(DATA_DIR, 'logs.json')

def read_json(path, default):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return default

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def tasks_path(project_id):
    return os.path.join(TASKS_DIR, f'{project_id}.json')

def diff_days(end_str):
    try:
        return (datetime.strptime(end_str, '%Y-%m-%d').date() - date.today()).days
    except:
        return None

def get_status(task):
    p = int(task.get('progress', 0))
    d = diff_days(task.get('endDate', ''))
    if p >= 100:   return 'done'
    if d is None:  return 'pending'
    if d < 0:      return 'overdue'
    if d <= 7:     return 'risk'
    if p > 0:      return 'progress'
    return 'pending'

def calc_project_stats(project_id):
    tasks = read_json(tasks_path(project_id), [])
    total = len(tasks)
    if total == 0:
        return {'total': 0, 'progress': 0, 'status': 'pending'}
    done  = sum(1 for t in tasks if get_status(t) == 'done')
    over  = any(get_status(t) == 'overdue' for t in tasks)
    risk  = any(get_status(t) == 'risk'    for t in tasks)
    prog  = round(sum(int(t.get('progress', 0)) for t in tasks) / total) if total > 0 else 0
    if over:  status = 'overdue'
    elif risk: status = 'risk'
    elif done == total: status = 'done'
    elif done > 0 or prog > 0: status = 'progress'
    else: status = 'pending'
    return {'total': total, 'progress': prog, 'status': status}

def add_log(log_type, title, detail):
    logs = read_json(LOGS_FILE, [])
    logs.insert(0, {'type': log_type, 'title': title, 'detail': detail,
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M')})
    write_json(LOGS_FILE, logs[:50])

def build_message(task, project_name, trigger):
    emoji = {'done':'✅','progress':'🔵','risk':'⚠️','overdue':'🚨','pending':'⏳'}
    s = get_status(task)
    return (f"{emoji.get(s,'📋')} *[WBS 알림]* {trigger}\n\n"
            f"📁 프로젝트: {project_name}\n"
            f"📌 태스크: {task.get('task','')}\n"
            f"👤 담당자: {task.get('assignee','미지정')}\n"
            f"📂 그룹: {task.get('group','')}\n"
            f"📅 마감일: {task.get('endDate','')}\n"
            f"📊 진행률: {task.get('progress',0)}%")

def send_webhook(text):
    wh = read_json(WEBHOOK_FILE, {})
    if not wh.get('type'): return False, '웹훅 설정 없음'
    try:
        if wh['type'] == 'telegram':
            token, chat = wh.get('token',''), wh.get('chat','')
            if not token or not chat: return False, 'Token/Chat ID 없음'
            r = req.post(f"https://api.telegram.org/bot{token}/sendMessage",
                         json={'chat_id': chat, 'text': text, 'parse_mode': 'Markdown'}, timeout=10)
        else:
            url = wh.get('url','')
            if not url: return False, 'Webhook URL 없음'
            r = req.post(url, json={'text': text}, timeout=10)
        return r.ok, r.text
    except Exception as e:
        return False, str(e)

def daily_check():
    if not read_json(WEBHOOK_FILE, {}).get('type'): return
    projects = read_json(PROJECTS_FILE, [])
    for proj in projects:
        tasks = read_json(tasks_path(proj['id']), [])
        for t in tasks:
            if int(t.get('progress', 0)) >= 100: continue
            d = diff_days(t.get('endDate', ''))
            if d is None: continue
            if d == 7:
                ok, _ = send_webhook(build_message(t, proj['name'], 'D-7 마감 7일 전'))
                add_log('warning' if ok else 'error', f"D-7 {t['task']}", proj['name'])
            elif d == 1:
                ok, _ = send_webhook(build_message(t, proj['name'], '⚡ D-1 내일 마감'))
                add_log('warning' if ok else 'error', f"D-1 긴급 {t['task']}", proj['name'])
            elif d < 0:
                ok, _ = send_webhook(build_message(t, proj['name'], f'🚨 {abs(d)}일 초과 지연'))
                add_log('error', f"지연 {t['task']}", f"{proj['name']} · {abs(d)}일 초과")

scheduler = BackgroundScheduler()
scheduler.add_job(daily_check, 'cron', hour=9, minute=0)
scheduler.start()

@app.route('/api/projects', methods=['GET'])
def get_projects():
    projects = read_json(PROJECTS_FILE, [])
    result = [{**p, **calc_project_stats(p['id'])} for p in projects]
    return jsonify(result)

@app.route('/api/projects', methods=['POST'])
def create_project():
    projects = read_json(PROJECTS_FILE, [])
    proj = request.json
    proj['id'] = str(uuid.uuid4())[:8]
    proj['createdAt'] = datetime.now().strftime('%Y-%m-%d')
    projects.append(proj)
    write_json(PROJECTS_FILE, projects)
    write_json(tasks_path(proj['id']), [])
    return jsonify(proj), 201

@app.route('/api/projects/<pid>', methods=['GET'])
def get_project(pid):
    projects = read_json(PROJECTS_FILE, [])
    proj = next((p for p in projects if p['id'] == pid), None)
    if not proj: return jsonify({'error': 'not found'}), 404
    return jsonify({**proj, **calc_project_stats(pid)})

@app.route('/api/projects/<pid>', methods=['PUT'])
def update_project(pid):
    projects = read_json(PROJECTS_FILE, [])
    for i, p in enumerate(projects):
        if p['id'] == pid:
            projects[i] = {**p, **request.json, 'id': pid}
            write_json(PROJECTS_FILE, projects)
            return jsonify(projects[i])
    return jsonify({'error': 'not found'}), 404

@app.route('/api/projects/<pid>', methods=['DELETE'])
def delete_project(pid):
    projects = [p for p in read_json(PROJECTS_FILE, []) if p['id'] != pid]
    write_json(PROJECTS_FILE, projects)
    tf = tasks_path(pid)
    if os.path.exists(tf): os.remove(tf)
    return jsonify({'ok': True})

@app.route('/api/projects/<pid>/tasks', methods=['GET'])
def get_tasks(pid):
    return jsonify(read_json(tasks_path(pid), []))

@app.route('/api/projects/<pid>/tasks', methods=['POST'])
def create_task(pid):
    tasks = read_json(tasks_path(pid), [])
    task  = {**request.json, 'id': str(uuid.uuid4())[:8]}
    tasks.append(task)
    write_json(tasks_path(pid), tasks)
    return jsonify(task), 201

@app.route('/api/projects/<pid>/tasks/<tid>', methods=['PUT'])
def update_task(pid, tid):
    tasks = read_json(tasks_path(pid), [])
    for i, t in enumerate(tasks):
        if t['id'] == tid:
            tasks[i] = {**t, **request.json, 'id': tid}
            write_json(tasks_path(pid), tasks)
            return jsonify(tasks[i])
    return jsonify({'error': 'not found'}), 404

@app.route('/api/projects/<pid>/tasks/<tid>', methods=['DELETE'])
def delete_task(pid, tid):
    tasks = [t for t in read_json(tasks_path(pid), []) if t['id'] != tid]
    write_json(tasks_path(pid), tasks)
    return jsonify({'ok': True})

@app.route('/api/projects/<pid>/tasks/upload', methods=['POST'])
def upload_tasks_excel(pid):
    if 'file' not in request.files:
        return jsonify({'error': '파일이 전달되지 않았습니다.'}), 400
    file = request.files['file']
    
    try:
        if file.filename.endswith('.csv'):
            try:
                df_raw = pd.read_csv(file, encoding='utf-8', header=None)
            except UnicodeDecodeError:
                file.seek(0)
                df_raw = pd.read_csv(file, encoding='cp949', header=None)
        else:
            try:
                df_raw = pd.read_excel(file, header=None)
            except ImportError:
                return jsonify({'error': "서버 환경에 'openpyxl' 라이브러리가 설치되어 있지 않습니다."}), 500

        df_raw = df_raw.fillna('')

        header_idx = -1
        for i, row in df_raw.iterrows():
            row_str = ' '.join(str(x) for x in row.values).lower()
            if 'task' in row_str or '태스크' in row_str or 'group' in row_str:
                header_idx = i
                break
                
        if header_idx == -1:
            return jsonify({'error': '제목 줄을 찾을 수 없습니다.'}), 400

        df = df_raw.iloc[header_idx+1:].copy()
        df.columns = df_raw.iloc[header_idx]
        
        tasks = read_json(tasks_path(pid), [])
        added_count = 0

        def get_val(row, possible_keys, default=''):
            for key in possible_keys:
                for col in df.columns:
                    if str(col).strip().lower() == key.lower():
                        return str(row.get(col, default)).strip()
            return default

        for _, row in df.iterrows():
            if not any(str(v).strip() for v in row.values): continue
                
            t_name = get_val(row, ['Task', '태스크명', '태스크', '작업명'])
            s_name = get_val(row, ['Subtask', '상세작업', '서브태스크'])
            if not t_name and not s_name: continue

            task_name = f"[{t_name}] {s_name}" if t_name and s_name else (t_name or s_name)
            
            # 💡 JIRA 컬럼 읽기 추가
            jira_val = get_val(row, ['Jira', '지라', 'Link', '링크'])

            group_val = get_val(row, ['Team', 'Group', '그룹', '팀'], '기획')
            assignee  = get_val(row, ['Assignee', '담당자'])
            
            start_date = get_val(row, ['Start Date', '시작일', '시작'])
            if not start_date: start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = get_val(row, ['End Date', '마감일', '종료일'])
            
            prog_val = get_val(row, ['Progress', '진행률', '진척도'], '0').replace('%', '')
            try:
                progress = int(float(prog_val)) if prog_val else 0
            except:
                progress = 0
                
            note = get_val(row, ['Note', '메모', '비고'])

            task = {
                'id': str(uuid.uuid4())[:8],
                'group': group_val,
                'task': task_name,
                'assignee': assignee,
                'startDate': start_date[:10],
                'endDate': end_date[:10],
                'progress': progress,
                'note': note,
                'jira': jira_val # 💡 JIRA 데이터 저장
            }
            tasks.append(task)
            added_count += 1
            
        write_json(tasks_path(pid), tasks)
        return jsonify({'ok': True, 'count': added_count}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<pid>/tasks/upload-sheets', methods=['POST'])
def upload_from_sheets(pid):
    csv_url = request.json.get('csv_url', '')
    if not csv_url:
        return jsonify({'error': 'csv_url이 없습니다'}), 400
    try:
        import io
        r = req.get(csv_url, timeout=15)
        r.raise_for_status()
        try:
            df_raw = pd.read_csv(io.StringIO(r.content.decode('utf-8')), header=None)
        except UnicodeDecodeError:
            df_raw = pd.read_csv(io.StringIO(r.content.decode('cp949')), header=None)

        df_raw = df_raw.fillna('')
        header_idx = -1
        for i, row in df_raw.iterrows():
            row_str = ' '.join(str(x) for x in row.values).lower()
            if 'task' in row_str or '태스크' in row_str or 'group' in row_str:
                header_idx = i; break
        if header_idx == -1:
            return jsonify({'error': '헤더 행을 찾을 수 없습니다'}), 400

        df = df_raw.iloc[header_idx+1:].copy()
        df.columns = df_raw.iloc[header_idx]

        def get_val(row, keys, default=''):
            for key in keys:
                for col in df.columns:
                    if str(col).strip().lower() == key.lower():
                        return str(row.get(col, default)).strip()
            return default

        tasks = read_json(tasks_path(pid), [])
        count = 0
        for _, row in df.iterrows():
            if not any(str(v).strip() for v in row.values): continue
            t_name = get_val(row, ['Task','태스크명','태스크','작업명'])
            s_name = get_val(row, ['Subtask','상세작업','서브태스크'])
            if not t_name and not s_name: continue
            task_name = f"[{t_name}] {s_name}" if t_name and s_name else (t_name or s_name)
            jira_val  = get_val(row, ['Jira','지라','Link','링크'])
            group_val = get_val(row, ['Team','Group','그룹','팀'], '기획')
            assignee  = get_val(row, ['Assignee','담당자'])
            start_date= get_val(row, ['Start Date','시작일','시작']) or datetime.now().strftime('%Y-%m-%d')
            end_date  = get_val(row, ['End Date','마감일','종료일'])
            prog_raw  = get_val(row, ['Progress','진행률','진척도'], '0').replace('%','')
            try:    progress = int(float(prog_raw)) if prog_raw else 0
            except: progress = 0
            note = get_val(row, ['Note','메모','비고'])
            tasks.append({
                'id': str(uuid.uuid4())[:8], 'group': group_val,
                'task': task_name, 'assignee': assignee,
                'startDate': start_date[:10], 'endDate': end_date[:10] if end_date else '',
                'progress': progress, 'note': note, 'jira': jira_val
            })
            count += 1
        write_json(tasks_path(pid), tasks)
        return jsonify({'ok': True, 'count': count}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_webhook():
    wh = read_json(WEBHOOK_FILE, {})
    return jsonify({**wh, 'token': '***' if wh.get('token') else ''})

@app.route('/api/webhook', methods=['POST'])
def save_webhook():
    write_json(WEBHOOK_FILE, request.json)
    return jsonify({'ok': True})

@app.route('/api/webhook/test', methods=['POST'])
def test_webhook():
    dummy = {'task':'[테스트] WBS Manager 연동 확인','group':'QA',
             'assignee':'담당자1','endDate':str(date.today()+timedelta(days=3)),'progress':0}
    ok, msg = send_webhook(build_message(dummy, 'Test Project', '테스트 메시지'))
    add_log('success' if ok else 'error', '테스트 전송', '성공' if ok else msg)
    return jsonify({'ok': ok, 'message': '전송 성공' if ok else msg})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify(read_json(LOGS_FILE, []))

@app.route('/api/notify/now', methods=['POST'])
def notify_now():
    daily_check()
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)