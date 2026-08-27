# -*- coding: utf-8 -*-
import app
import json

client = app.app.test_client()

with client.session_transaction() as sess:
    sess['user'] = {'id': 1, 'role': 'admin', 'email': 'admin@example.com'}

# GET /tasks
res = client.get('/tasks')
print('GET /tasks status:', res.status_code)
html = res.get_data(as_text=True)

c1 = 'single-task-employee' in html
c2 = u'Aufgabe f\u00fcr' in html
c3 = "employee_id: document.getElementById('single-task-employee').value" in html

print('single-task-employee found:', c1)
print('Aufgabe fuer found:', c2)
print('employee_id JS expression found:', c3)

# POST /api/tasks/single without employee_id
res_post = client.post('/api/tasks/single', json={})
print('POST /api/tasks/single status:', res_post.status_code)
print('POST /api/tasks/single content-type:', res_post.content_type)
print('POST /api/tasks/single payload:', res_post.get_data(as_text=True))
