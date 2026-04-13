/* Admin UI script: navigation, simple templates, and API stubs
   - Replace `API_BASE` with your backend base path (e.g. '/api')
   - `loadSection(name)` renders a simple view into #panelContainer
*/
const API_BASE = '/api'; // update this when backend is ready

function apiRequest(path, opts = {}){
  const url = API_BASE + path;
  const headers = Object.assign({'Content-Type':'application/json'}, opts.headers || {});
  return fetch(url, Object.assign({}, opts, {headers}))
    .then(async res => {
      if (!res.ok) throw new Error(await res.text());
      try { return await res.json(); } catch { return null; }
    });
}

function apiGet(path){ return apiRequest(path, {method:'GET'}); }
function apiPost(path, body){ return apiRequest(path, {method:'POST', body:JSON.stringify(body)}); }
function apiPut(path, body){ return apiRequest(path, {method:'PUT', body:JSON.stringify(body)}); }
function apiDelete(path){ return apiRequest(path, {method:'DELETE'}); }

function setCounts(data){
  if (data.students != null) document.getElementById('studentsCount').textContent = data.students;
  if (data.courses  != null) document.getElementById('coursesCount').textContent = data.courses;
  if (data.quizzes  != null) document.getElementById('quizzesCount').textContent = data.quizzes;
}

function renderActivity(list){
  const tbody = document.getElementById('activityBody');
  tbody.innerHTML = '';
  if (!list || list.length === 0){
    tbody.innerHTML = '<tr><td colspan="3">No activity yet.</td></tr>';
    return;
  }
  list.forEach(it => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${it.time||''}</td><td>${it.user||''}</td><td>${it.action||''}</td>`;
    tbody.appendChild(tr);
  });
}

function loadDashboard(){
  document.getElementById('pageTitle').textContent = 'Dashboard';
  // try loading counts and activities from backend, fallback to demo
  apiGet('/stats').then(setCounts).catch(()=>setCounts({students:1240,courses:18,quizzes:72}));
  apiGet('/activities').then(renderActivity).catch(()=>renderActivity([
    {time:'10:12',user:'Ravi',action:'Submitted Quiz'},
    {time:'09:55',user:'Seema',action:'Enrolled Course'},
  ]));
}

function renderStudentsTable(students){
  const html = `
    <div class="panel">
      <h2>Students</h2>
      <table>
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Actions</th></tr></thead>
        <tbody id="studentsBody">
        ${students && students.length ? students.map(s=>`<tr><td>${s.id}</td><td>${s.name}</td><td>${s.email}</td><td><button data-id="${s.id}" class="btn-edit">Edit</button> <button data-id="${s.id}" class="btn-del">Delete</button></td></tr>`).join('') : '<tr><td colspan="4">No students</td></tr>'}
        </tbody>
      </table>
    </div>`;
  document.getElementById('panelContainer').innerHTML = html;
}

function loadStudents(){
  document.getElementById('pageTitle').textContent = 'Students';
  apiGet('/students').then(data=>{
    renderStudentsTable(data || []);
    attachStudentHandlers();
  }).catch(()=>{
    renderStudentsTable([{id:1,name:'Demo Student',email:'demo@ex.com'}]);
    attachStudentHandlers();
  });
}

function attachStudentHandlers(){
  document.querySelectorAll('.btn-del').forEach(b=>b.addEventListener('click', async e=>{
    const id = e.currentTarget.dataset.id;
    if (!confirm('Delete student '+id+'?')) return;
    try { await apiDelete('/students/'+id); loadStudents(); } catch(err){ alert('Delete failed: '+err.message); }
  }));
}

function loadSection(name){
  switch(name){
    case 'dashboard': loadDashboard(); break;
    case 'students': loadStudents(); break;
    default:
      document.getElementById('pageTitle').textContent = name.charAt(0).toUpperCase()+name.slice(1);
      document.getElementById('panelContainer').innerHTML = `<div class="panel"><h2>${name.charAt(0).toUpperCase()+name.slice(1)}</h2><p>Manage ${name} here. Connect endpoints like <code>/api/${name}</code>.</p></div>`;
  }
}

document.addEventListener('DOMContentLoaded', function(){
  const toggle = document.getElementById('toggleBtn');
  const sidebar = document.getElementById('sidebar');
  toggle.addEventListener('click', ()=>{ sidebar.classList.toggle('open'); });

  // nav links
  const links = document.querySelectorAll('#sidebar nav a[data-section]');
  links.forEach(a=>a.addEventListener('click', e=>{
    e.preventDefault();
    links.forEach(x=>x.classList.remove('active'));
    e.currentTarget.classList.add('active');
    const section = e.currentTarget.dataset.section;
    loadSection(section);
  }));

  // initial load
  loadDashboard();
});
