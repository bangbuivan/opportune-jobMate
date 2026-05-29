const API_BASE_URL = 'http://localhost:8000';

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initDragAndDrop();
    initCareerMatch();
    initJobMatcher();
    initSkillBridge();
    initATSTuneUp();
    initJobRadar();
    initResumeBuilder();
    initCoverLetter();
    initInterviewPrep();
    initDashboard();
    lucide.createIcons();
});

// --- NAVIGATION (SPA) ---
function initNavigation() {
    const navLinks = document.querySelectorAll('nav a');
    const views = document.querySelectorAll('.view');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            const targetId = link.getAttribute('data-target');
            views.forEach(v => {
                if (v.id === targetId) {
                    v.classList.remove('hidden');
                } else {
                    v.classList.add('hidden');
                }
            });
        });
    });
}

// --- GLOBAL DRAG AND DROP ---
function initDragAndDrop() {
    const dropAreas = document.querySelectorAll('.file-drop-area');
    dropAreas.forEach(area => {
        const input = area.querySelector('input[type="file"]');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            area.addEventListener(eventName, preventDefaults, false);
        });
        function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            area.addEventListener(eventName, () => area.classList.add('dragover'), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            area.addEventListener(eventName, () => area.classList.remove('dragover'), false);
        });
        
        area.addEventListener('drop', (e) => {
            if(e.dataTransfer.files.length) {
                input.files = e.dataTransfer.files;
                updateFileUI(area, input.files[0].name);
            }
        });
        
        input.addEventListener('change', () => {
            if(input.files.length) updateFileUI(area, input.files[0].name);
        });
    });

    function updateFileUI(area, name) {
        let p = area.querySelector('p:not(.btn)');
        if(!p) {
            p = document.createElement('p');
            area.appendChild(p);
        }
        p.textContent = `Đã chọn: ${name}`;
        p.style.color = 'var(--primary)';
        p.style.fontWeight = '600';
    }
}

// --- CAREER MATCH ---
function initCareerMatch() {
    const form = document.getElementById('uploadForm-career');
    const input = document.getElementById('fileInput-career');
    const topN = document.getElementById('topN-career');
    const topNValue = document.getElementById('topNValue-career');
    const btn = document.getElementById('submitBtn-career');
    const loader = document.getElementById('loader-career');
    const results = document.getElementById('resultsSection-career');

    topN.addEventListener('input', e => topNValue.textContent = e.target.value);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if(!input.files.length) return alert('Vui lòng chọn một CV.');

        const formData = new FormData();
        formData.append('file', input.files[0]);
        formData.append('search_method', document.querySelector('input[name="search_method"]:checked').value);
        formData.append('top_n', topN.value);

        btn.disabled = true; loader.classList.remove('hidden'); results.classList.add('hidden');

        try {
            const res = await fetch(`${API_BASE_URL}/api/recommend-jobs`, { method: 'POST', body: formData });
            const data = await res.json();
            if(data.success) {
                // Profile
                document.getElementById('resName').textContent = data.personal_info.name || '-';
                document.getElementById('resEmail').textContent = data.personal_info.email || '-';
                document.getElementById('resPhone').textContent = data.personal_info.phone || '-';
                document.getElementById('resDegree').textContent = data.personal_info.degree || '-';
                
                const skillsDiv = document.getElementById('resSkills');
                skillsDiv.innerHTML = data.personal_info.skills.map(s => `<span class="badge">${s}</span>`).join('') || '-';

                // Jobs
                const list = document.getElementById('jobsList-career');
                document.getElementById('jobsCount-career').textContent = `${data.recommended_jobs.length} kết quả phù hợp`;
                
                list.innerHTML = data.recommended_jobs.map((job, i) => `
                    <div class="job-card" style="animation-delay: ${i*0.1}s">
                        <div class="job-header">
                            <div><h3 class="job-title">${job.title || job.position}</h3><div class="job-company">${job.workplace || job.company || '-'}</div></div>
                        </div>
                        <div class="job-meta">
                            ${job.match_count ? `<div class="meta-item"><i data-lucide="check"></i> ${job.match_count} kỹ năng</div>` : ''}
                        </div>
                        <div class="job-description">${(job.description || job.job_role_and_duties || '').substring(0, 200)}...</div>
                    </div>
                `).join('') || '<div class="glass-panel text-center">Không tìm thấy công việc phù hợp.</div>';
                
                lucide.createIcons();
                results.classList.remove('hidden');
                results.scrollIntoView({behavior:'smooth'});
            } else alert(data.error);
        } catch(e) { alert('Lỗi API'); } finally { btn.disabled = false; loader.classList.add('hidden'); }
    });
}

// --- JOB MATCHER ---
function initJobMatcher() {
    const form = document.getElementById('uploadForm-matcher');
    const btn = document.getElementById('submitBtn-matcher');
    const loader = document.getElementById('loader-matcher');
    const results = document.getElementById('resultsSection-matcher');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const resInput = document.getElementById('fileInput-matcher-resume');
        const jdInput = document.getElementById('fileInput-matcher-jd');
        const jdText = document.getElementById('jd-text-matcher').value;

        if(!resInput.files.length) return alert('Vui lòng tải lên CV.');
        if(!jdInput.files.length && !jdText.trim()) return alert('Vui lòng tải lên JD hoặc dán văn bản mô tả công việc.');

        const formData = new FormData();
        formData.append('resume', resInput.files[0]);
        if(jdInput.files.length) formData.append('jd_file', jdInput.files[0]);
        if(jdText.trim()) formData.append('jd_text', jdText);

        btn.disabled = true; loader.classList.remove('hidden'); results.classList.add('hidden');

        try {
            const res = await fetch(`${API_BASE_URL}/api/job-matcher`, { method: 'POST', body: formData });
            const data = await res.json();
            if(data.success) {
                document.getElementById('matcher-score').textContent = data.score;
                document.getElementById('matcher-hard').textContent = data.hard_pct + '%';
                document.getElementById('matcher-soft').textContent = data.soft_pct + '%';
                
                document.getElementById('matcher-matched-skills').innerHTML = data.matched_hard.map(s => `<span class="badge success">${s}</span>`).join('');
                document.getElementById('matcher-missing-skills').innerHTML = data.missing_hard.map(s => `<span class="badge danger">${s}</span>`).join('');

                results.classList.remove('hidden');
                results.scrollIntoView({behavior:'smooth'});
            } else alert(data.error);
        } catch(e) { alert('Lỗi API'); } finally { btn.disabled = false; loader.classList.add('hidden'); }
    });
}

// --- SKILL BRIDGE ---
async function initSkillBridge() {
    const select = document.getElementById('role-select');
    try {
        const res = await fetch(`${API_BASE_URL}/api/skill-bridge/roles`);
        const data = await res.json();
        if(data.success) {
            select.innerHTML = '<option value="">-- Chọn vị trí mục tiêu --</option>' + 
                data.roles.map(r => `<option value="${r}">${r}</option>`).join('');
        }
    } catch(e) { select.innerHTML = '<option value="">Lỗi tải danh sách vị trí</option>'; }

    const form = document.getElementById('uploadForm-skill');
    const btn = document.getElementById('submitBtn-skill');
    const loader = document.getElementById('loader-skill');
    const results = document.getElementById('resultsSection-skill');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = document.getElementById('fileInput-skill-resume');
        const key = document.getElementById('skill-gemini-key').value;

        if(!input.files.length) return alert('Vui lòng tải lên CV.');

        const formData = new FormData();
        formData.append('file', input.files[0]);
        formData.append('role', select.value);
        if(key) formData.append('gemini_key', key);

        btn.disabled = true; loader.classList.remove('hidden'); results.classList.add('hidden');

        try {
            const res = await fetch(`${API_BASE_URL}/api/skill-bridge/analyze`, { method: 'POST', body: formData });
            const data = await res.json();
            if(data.success) {
                document.getElementById('skill-matched').innerHTML = data.matched_skills.map(s => `<span class="badge success">${s}</span>`).join('') || '-';
                document.getElementById('skill-missing').innerHTML = data.missing_skills.map(s => `<span class="badge warning">${s}</span>`).join('') || 'Không có! Bạn đã sẵn sàng!';
                
                // Render custom learning roadmap diagram
                const nodesContainer = document.getElementById('skill-roadmap-nodes');
                const detailCard = document.getElementById('skill-phase-detail-card');
                const roadmapPanel = document.getElementById('skill-roadmap-panel');
                
                if (nodesContainer && detailCard && data.roadmap) {
                    roadmapPanel.classList.remove('hidden');
                    
                    // Helper to check if a task is already completed (fuzzy matching matched skills)
                    const isSkillCompleted = (title, subTasks = []) => {
                        const matched = data.matched_skills || [];
                        const textToMatch = (title + " " + subTasks.join(" ")).toLowerCase();
                        return matched.some(skill => textToMatch.includes(skill.toLowerCase()));
                    };

                    // State container for task completions (ticked status)
                    const completedTasksState = {};
                    const completedSubTasksState = {};
                    data.roadmap.forEach((domain, dIdx) => {
                        (domain.tasks || []).forEach((task, tIdx) => {
                            const taskCompleted = isSkillCompleted(task.task_title || "Chủ đề", task.sub_tasks || []);
                            completedTasksState[`${dIdx}-${tIdx}`] = taskCompleted;
                            (task.sub_tasks || []).forEach((sub, sIdx) => {
                                completedSubTasksState[`${dIdx}-${tIdx}-${sIdx}`] = taskCompleted;
                            });
                        });
                    });

                    // Overhaul roadmap display into mindmap tree structure
                    nodesContainer.className = "roadmap-mindmap";
                    
                    let mindmapHtml = `
                        <div class="roadmap-root-node">
                            <i data-lucide="compass" style="width: 20px; height: 20px;"></i>
                            <span>Lộ trình: ${select.value}</span>
                        </div>
                        <div class="roadmap-branches-wrapper">
                    `;
                    
                    data.roadmap.forEach((domain, dIdx) => {
                        const domainPhase = domain.phase || `Vùng ${dIdx + 1}`;
                        const domainTitle = domain.title || "Chuyên đề";
                        const tasks = domain.tasks || [];
                        
                        mindmapHtml += `
                            <div class="roadmap-branch">
                                <div class="branch-header-node">
                                    <span class="domain-meta">${domainPhase}</span>
                                    <div>${domainTitle}</div>
                                </div>
                                <div class="branch-tasks-container">
                        `;
                        
                        tasks.forEach((task, tIdx) => {
                            const taskTitle = task.task_title || "Chủ đề";
                            const subTasks = task.sub_tasks || [];
                            
                            // Check if completed dynamically based on state
                            const completed = completedTasksState[`${dIdx}-${tIdx}`];
                            const statusClass = completed ? "task-leaf-completed" : "task-leaf-todo";
                            const statusIcon = completed ? "✓" : "";
                            
                            mindmapHtml += `
                                    <div class="task-leaf-node ${statusClass}" data-domain="${dIdx}" data-task="${tIdx}">
                                        <span class="task-leaf-title">${taskTitle}</span>
                                        <span class="node-status-badge">${statusIcon}</span>
                                    </div>
                            `;
                        });
                        
                        mindmapHtml += `
                                </div>
                            </div>
                        `;
                    });
                    
                    mindmapHtml += `</div>`;
                    nodesContainer.innerHTML = mindmapHtml;
                    
                    // Helper to render active task details
                    function renderActiveTask(dIdx, tIdx) {
                        const domain = data.roadmap[dIdx];
                        const task = domain.tasks[tIdx];
                        const domainTag = domain.phase || `Vùng ${dIdx + 1}`;
                        const taskTitle = task.task_title || "Chủ đề";
                        const subTasks = task.sub_tasks || [];
                        
                        // Clear active classes and set on clicked node
                        nodesContainer.querySelectorAll('.task-leaf-node').forEach(node => {
                            const nd = parseInt(node.getAttribute('data-domain'));
                            const nt = parseInt(node.getAttribute('data-task'));
                            if (nd === dIdx && nt === tIdx) {
                                node.classList.add('active');
                            } else {
                                node.classList.remove('active');
                            }
                        });
                        
                        let detailHtml = `
                            <span class="phase-tag">${domainTag} - Nhiệm vụ chi tiết</span>
                            <h4 class="phase-title" style="display: flex; align-items: center; gap: 0.5rem; color: white;">
                                <i data-lucide="compass" style="color: var(--primary); width: 22px; height: 22px;"></i>
                                ${taskTitle}
                            </h4>
                            <p class="phase-desc" style="margin-bottom: 1.5rem;">Nhấp chọn các mục bên dưới để đánh dấu tiến độ tự học của bạn.</p>
                            <div class="phase-tasks-wrapper">
                                <ul class="phase-checklist">
                        `;
                        
                        subTasks.forEach((sub, sIdx) => {
                            const isChecked = completedSubTasksState[`${dIdx}-${tIdx}-${sIdx}`] ? "checked" : "";
                            detailHtml += `
                                <li class="phase-checklist-item ${isChecked}">
                                    <input type="checkbox" id="sub-${dIdx}-${tIdx}-${sIdx}" ${completedSubTasksState[`${dIdx}-${tIdx}-${sIdx}`] ? "checked" : ""}>
                                    <label for="sub-${dIdx}-${tIdx}-${sIdx}">${sub}</label>
                                </li>
                            `;
                        });
                        
                        detailHtml += `
                                </ul>
                            </div>
                        `;
                        
                        detailCard.innerHTML = detailHtml;
                        lucide.createIcons();
                        
                        // Bind checkbox event listeners
                        detailCard.querySelectorAll('.phase-checklist-item input[type="checkbox"]').forEach(checkbox => {
                            checkbox.addEventListener('change', (e) => {
                                const idParts = e.target.id.split('-');
                                const sd = parseInt(idParts[1]);
                                const st = parseInt(idParts[2]);
                                const ss = parseInt(idParts[3]);
                                
                                completedSubTasksState[`${sd}-${st}-${ss}`] = e.target.checked;
                                
                                const li = e.target.closest('.phase-checklist-item');
                                if(e.target.checked) {
                                    li.classList.add('checked');
                                } else {
                                    li.classList.remove('checked');
                                }
                                
                                // Re-evaluate task completion state
                                const subCount = (data.roadmap[sd].tasks[st].sub_tasks || []).length;
                                let allChecked = subCount > 0;
                                for (let i = 0; i < subCount; i++) {
                                    if (!completedSubTasksState[`${sd}-${st}-${i}`]) {
                                        allChecked = false;
                                        break;
                                    }
                                }
                                
                                completedTasksState[`${sd}-${st}`] = allChecked;
                                
                                // Update roadmap leaf badge class in real-time
                                const leafNode = nodesContainer.querySelector(`.task-leaf-node[data-domain="${sd}"][data-task="${st}"]`);
                                if (leafNode) {
                                    const badge = leafNode.querySelector('.node-status-badge');
                                    if (allChecked) {
                                        leafNode.classList.remove('task-leaf-todo');
                                        leafNode.classList.add('task-leaf-completed');
                                        badge.textContent = '✓';
                                    } else {
                                        leafNode.classList.remove('task-leaf-completed');
                                        leafNode.classList.add('task-leaf-todo');
                                        badge.textContent = '';
                                    }
                                }
                            });
                        });
                    }
                    
                    // Helper to toggle task completion state when badge is clicked
                    function toggleTaskCompletion(leafNode, dIdx, tIdx) {
                        const nextState = !completedTasksState[`${dIdx}-${tIdx}`];
                        completedTasksState[`${dIdx}-${tIdx}`] = nextState;
                        
                        // Sync all subtasks
                        const subCount = (data.roadmap[dIdx].tasks[tIdx].sub_tasks || []).length;
                        for (let i = 0; i < subCount; i++) {
                            completedSubTasksState[`${dIdx}-${tIdx}-${i}`] = nextState;
                        }
                        
                        const badge = leafNode.querySelector('.node-status-badge');
                        if (nextState) {
                            leafNode.classList.remove('task-leaf-todo');
                            leafNode.classList.add('task-leaf-completed');
                            badge.textContent = '✓';
                        } else {
                            leafNode.classList.remove('task-leaf-completed');
                            leafNode.classList.add('task-leaf-todo');
                            badge.textContent = '';
                        }
                        
                        // If this task is active, sync its checkboxes in details card immediately
                        const activeNode = nodesContainer.querySelector('.task-leaf-node.active');
                        if (activeNode) {
                            const ad = parseInt(activeNode.getAttribute('data-domain'));
                            const at = parseInt(activeNode.getAttribute('data-task'));
                            if (ad === dIdx && at === tIdx) {
                                renderActiveTask(dIdx, tIdx);
                            }
                        }
                    }

                    // Render first task initially
                    if (data.roadmap.length > 0 && data.roadmap[0].tasks.length > 0) {
                        renderActiveTask(0, 0);
                    }
                    
                    // Add click handlers on nodes and status badges
                    nodesContainer.querySelectorAll('.task-leaf-node').forEach(node => {
                        const dIdx = parseInt(node.getAttribute('data-domain'));
                        const tIdx = parseInt(node.getAttribute('data-task'));
                        
                        node.addEventListener('click', (e) => {
                            // If clicked on the circle status badge, trigger toggle state
                            if (e.target.closest('.node-status-badge')) {
                                e.stopPropagation();
                                toggleTaskCompletion(node, dIdx, tIdx);
                                return;
                            }
                            renderActiveTask(dIdx, tIdx);
                        });
                    });
                    
                    lucide.createIcons();
                }
                
                results.classList.remove('hidden');
                results.scrollIntoView({behavior:'smooth'});
            } else alert(data.error);
        } catch(e) { alert('Lỗi API'); } finally { btn.disabled = false; loader.classList.add('hidden'); }
    });
}

// --- ATS TUNEUP ---
function initATSTuneUp() {
    const radios = document.querySelectorAll('input[name="ats_method"]');
    const keyGroup = document.getElementById('gemini-key-group');
    
    radios.forEach(r => {
        r.addEventListener('change', (e) => {
            keyGroup.style.display = e.target.value === 'ai' ? 'block' : 'none';
        });
    });

    const form = document.getElementById('uploadForm-ats');
    const btn = document.getElementById('submitBtn-ats');
    const loader = document.getElementById('loader-ats');
    const results = document.getElementById('resultsSection-ats');
    const container = document.getElementById('ats-results-container');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = document.getElementById('fileInput-ats-resume');
        const method = document.querySelector('input[name="ats_method"]:checked').value;
        const key = document.getElementById('gemini-key').value;

        if(!input.files.length) return alert('Vui lòng tải lên CV.');
        if(method === 'ai' && !key) return alert('Vui lòng nhập Gemini API Key.');

        const formData = new FormData();
        formData.append('file', input.files[0]);
        formData.append('analysis_type', method);
        if(key) formData.append('gemini_key', key);

        btn.disabled = true; loader.classList.remove('hidden'); results.classList.add('hidden');

        try {
            const res = await fetch(`${API_BASE_URL}/api/ats-tuneup`, { method: 'POST', body: formData });
            const data = await res.json();
            if(data.success) {
                container.innerHTML = '';
                
                // Render category scorecard
                const scorecardGrid = document.getElementById('ats-scorecard-grid');
                if(scorecardGrid && data.scores) {
                    scorecardGrid.innerHTML = Object.entries(data.scores).map(([category, val]) => `
                        <div class="scorecard-item">
                            <span class="scorecard-label">${category}</span>
                            <span class="scorecard-value">${val}/100</span>
                            <div class="mini-progress-track">
                                <div class="mini-progress-fill" data-value="${val}" style="width: 0%"></div>
                            </div>
                        </div>
                    `).join('');
                    
                    // Trigger animation in the next tick
                    setTimeout(() => {
                        scorecardGrid.querySelectorAll('.mini-progress-fill').forEach(fill => {
                            const val = fill.getAttribute('data-value');
                            fill.style.width = `${val}%`;
                        });
                    }, 50);
                }

                if(data.type === 'local') {
                    // Local rule-based rendering
                    data.results.forEach(step => {
                        let html = `<div class="ats-step"><h3><i data-lucide="check-square"></i> Bước ${step.step}: ${step.title}</h3>`;
                        step.findings.forEach(f => {
                            const icon = f[0] === 'success' ? 'check-circle' : (f[0] === 'warning' ? 'alert-triangle' : 'info');
                            html += `<div class="ats-finding ${f[0]}"><i data-lucide="${icon}"></i> ${f[1]}</div>`;
                        });
                        html += `</div>`;
                        container.insertAdjacentHTML('beforeend', html);
                    });
                } else {
                    // AI results rendering
                    const ai = data.results;
                    if(ai.ATS_Score) {
                        container.insertAdjacentHTML('beforeend', `
                            <div class="glass-panel text-center mb-2" style="margin-bottom:2rem;">
                                <h2>Điểm ATS AI</h2>
                                <div class="score-circle">${ai.ATS_Score}</div>
                            </div>
                        `);
                    }
                    for (const [category, details] of Object.entries(ai)) {
                        if(category === 'ATS_Score') continue;
                        let html = `<div class="ats-step"><h3><i data-lucide="sparkles"></i> ${category}</h3>`;
                        if(details.Positives) {
                            details.Positives.forEach(p => html += `<div class="ats-finding success"><i data-lucide="check"></i> ${p}</div>`);
                        }
                        if(details.Negatives) {
                            details.Negatives.forEach(n => html += `<div class="ats-finding warning"><i data-lucide="alert-circle"></i> ${n}</div>`);
                        }
                        html += `</div>`;
                        container.insertAdjacentHTML('beforeend', html);
                    }
                }
                lucide.createIcons();
                results.classList.remove('hidden');
                results.scrollIntoView({behavior:'smooth'});
            } else alert(data.error);
        } catch(e) { alert('Lỗi API'); } finally { btn.disabled = false; loader.classList.add('hidden'); }
    });
}

// --- JOB RADAR ---
function initJobRadar() {
    const form = document.getElementById('radar-form');
    const results = document.getElementById('resultsSection-radar');
    const container = document.getElementById('radar-links-container');

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const role = document.getElementById('radar-role').value.trim();
        const loc = document.getElementById('radar-loc').value.trim();
        if(!role || !loc) return;

        const roleEnc = encodeURIComponent(role);
        const locEnc = encodeURIComponent(loc);
        const roleDash = role.toLowerCase().replace(/ /g, '-');
        const locDash = loc.toLowerCase().replace(/ /g, '-');

        const platforms = [
            { name: 'LinkedIn', url: `https://www.linkedin.com/jobs/search/?keywords=${roleEnc}&location=${locEnc}`, icon: 'linkedin' },
            { name: 'Foundit', url: `https://www.foundit.in/srp/results?query=${roleEnc}&location=${locEnc}`, icon: 'briefcase' },
            { name: 'Indeed', url: `https://www.indeed.com/jobs?q=${roleEnc}&l=${locEnc}`, icon: 'globe' },
            { name: 'Naukri', url: `https://www.naukri.com/${roleDash}-jobs-in-${locDash}`, icon: 'book' },
            { name: 'Instahyre', url: `https://www.instahyre.com/jobs/?q=${roleEnc}&l=${locEnc}`, icon: 'zap' }
        ];

        container.innerHTML = platforms.map(p => `
            <a href="${p.url}" target="_blank" class="job-card" style="display:flex; align-items:center; gap:1rem; text-decoration:none;">
                <i data-lucide="${p.icon}" style="color:var(--primary); width:32px; height:32px;"></i>
                <h3 style="color:white; font-size:1.25rem;">Tìm kiếm trên ${p.name}</h3>
            </a>
        `).join('');

        lucide.createIcons();
        results.classList.remove('hidden');
        results.scrollIntoView({behavior:'smooth'});
    });
}

// --- RESUME BUILDER ---
function initResumeBuilder() {
    const form = document.getElementById('builder-form');
    const btn = document.getElementById('builder-submitBtn');
    const loader = document.getElementById('loader-builder');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const payload = {
            gemini_key: document.getElementById('builder-gemini-key').value,
            tone: document.getElementById('builder-tone').value,
            resume_data: {
                personal: {
                    name: document.getElementById('b-name').value,
                    title: document.getElementById('b-title').value,
                    email: document.getElementById('b-email').value,
                    phone: document.getElementById('b-phone').value,
                    location: document.getElementById('b-location').value,
                    linkedin: document.getElementById('b-linkedin').value,
                    website: "", github: ""
                },
                summary: document.getElementById('b-summary').value,
                skills: {
                    technical: document.getElementById('b-tech').value.split(',').map(s=>s.trim()).filter(Boolean),
                    soft: document.getElementById('b-soft').value.split(',').map(s=>s.trim()).filter(Boolean)
                },
                experience: [{
                    job_title: document.getElementById('b-exp-title').value,
                    company: document.getElementById('b-exp-company').value,
                    location: "",
                    start_date: document.getElementById('b-exp-start').value,
                    end_date: document.getElementById('b-exp-end').value,
                    responsibilities: document.getElementById('b-exp-desc').value.split('\n').filter(Boolean)
                }],
                education: [], projects: [], certifications: [], achievements_hobbies: { achievements: [], hobbies: [] }
            }
        };

        btn.disabled = true; loader.classList.remove('hidden');

        try {
            const res = await fetch(`${API_BASE_URL}/api/resume-builder`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if(res.ok) {
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${payload.resume_data.personal.name.replace(/ /g, '_')}_Resume.docx`;
                document.body.appendChild(a);
                a.click();
                a.remove();
            } else {
                const data = await res.json();
                alert(data.error || 'Không thể tạo CV');
            }
        } catch(e) {
            alert('Lỗi API');
        } finally {
            btn.disabled = false; loader.classList.add('hidden');
        }
    });
}

// --- COVER LETTER ---
function initCoverLetter() {
    const form = document.getElementById('cover-form');
    const btn = document.getElementById('submitBtn-cover');
    const loader = document.getElementById('loader-cover');
    const results = document.getElementById('resultsSection-cover');
    const output = document.getElementById('cover-letter-output');
    const copyBtn = document.getElementById('copy-cover-btn');
    const downloadBtn = document.getElementById('download-cover-btn');
    const downloadDocxBtn = document.getElementById('download-docx-cover-btn');
    
    let generatedCoverLetter = "";
    let candidateInfo = { name: "Tên ứng viên", email: "ungvien@example.com", phone: "090-000-0000" };

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const resInput = document.getElementById('fileInput-cover-resume');
        const jdInput = document.getElementById('fileInput-cover-jd');
        const jdText = document.getElementById('jd-text-cover').value;
        const tone = document.getElementById('cover-tone').value;
        const key = document.getElementById('cover-gemini-key').value;

        if(!resInput.files.length) return alert('Vui lòng tải lên CV.');
        if(!jdInput.files.length && !jdText.trim()) return alert('Vui lòng tải lên JD hoặc dán văn bản mô tả công việc.');

        const formData = new FormData();
        formData.append('file', resInput.files[0]);
        if(jdInput.files.length) formData.append('jd_file', jdInput.files[0]);
        if(jdText.trim()) formData.append('jd_text', jdText);
        formData.append('tone', tone);
        formData.append('gemini_key', key);

        btn.disabled = true; loader.classList.remove('hidden'); results.classList.add('hidden');

        try {
            const res = await fetch(`${API_BASE_URL}/api/cover-letter`, { method: 'POST', body: formData });
            const data = await res.json();
            if(data.success) {
                generatedCoverLetter = data.cover_letter;
                if(data.personal_info) {
                    candidateInfo = data.personal_info;
                }
                output.value = generatedCoverLetter;
                results.classList.remove('hidden');
                results.scrollIntoView({behavior:'smooth'});
            } else alert(data.error);
        } catch(e) { alert('Lỗi API'); } finally { btn.disabled = false; loader.classList.add('hidden'); }
    });

    copyBtn.addEventListener('click', () => {
        if(!generatedCoverLetter) return;
        navigator.clipboard.writeText(generatedCoverLetter).then(() => {
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = `<i data-lucide="check"></i> Đã sao chép!`;
            lucide.createIcons();
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                lucide.createIcons();
            }, 2000);
        });
    });

    downloadBtn.addEventListener('click', () => {
        if(!generatedCoverLetter) return;
        const blob = new Blob([generatedCoverLetter], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Cover_Letter.txt`;
        document.body.appendChild(a);
        a.click();
        a.remove();
    });

    downloadDocxBtn.addEventListener('click', async () => {
        if(!generatedCoverLetter) return;
        
        downloadDocxBtn.disabled = true;
        const originalHtml = downloadDocxBtn.innerHTML;
        downloadDocxBtn.innerHTML = `<i data-lucide="loader"></i> Đang tải xuống...`;
        lucide.createIcons();
        
        try {
            const payload = {
                name: candidateInfo.name,
                email: candidateInfo.email,
                phone: candidateInfo.phone,
                body_text: generatedCoverLetter
            };
            
            const res = await fetch(`${API_BASE_URL}/api/cover-letter/download-docx`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (res.ok) {
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Cover_Letter_${candidateInfo.name.replace(/ /g, '_')}.docx`;
                document.body.appendChild(a);
                a.click();
                a.remove();
            } else {
                alert('Không thể tạo thư xin việc DOCX');
            }
        } catch(e) {
            alert('Lỗi API khi tải xuống DOCX');
        } finally {
            downloadDocxBtn.disabled = false;
            downloadDocxBtn.innerHTML = originalHtml;
            lucide.createIcons();
        }
    });
}

// --- INTERVIEW PREP ---
function initInterviewPrep() {
    const setupForm = document.getElementById('interview-setup-form');
    const startBtn = document.getElementById('submitBtn-interview-start');
    const setupLoader = document.getElementById('loader-interview-setup');
    
    const activeSection = document.getElementById('interview-active');
    const questionText = document.getElementById('active-question-text');
    const responseText = document.getElementById('interview-user-response');
    const stepIndicator = document.getElementById('interview-step-indicator');
    const progressFill = document.getElementById('interview-progress-fill');
    
    const prevBtn = document.getElementById('interview-prev-btn');
    const nextBtn = document.getElementById('interview-next-btn');
    
    const evaluatingLoader = document.getElementById('loader-interview-evaluating');
    const resultsSection = document.getElementById('interview-results');
    const scoreText = document.getElementById('interview-score');
    const feedbackSummary = document.getElementById('interview-feedback-summary');
    const breakdownContainer = document.getElementById('interview-breakdown-container');
    const restartBtn = document.getElementById('interview-restart-btn');

    let questions = [];
    let answers = [];
    let currentStep = 0;
    let resumeText = "";
    let jdText = "";

    setupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const resInput = document.getElementById('fileInput-interview-resume');
        const jdInput = document.getElementById('fileInput-interview-jd');
        const jdVal = document.getElementById('jd-text-interview').value;
        const key = document.getElementById('interview-gemini-key').value;

        if(!resInput.files.length) return alert('Vui lòng tải lên CV.');
        if(!jdInput.files.length && !jdVal.trim()) return alert('Vui lòng tải lên JD hoặc dán văn bản mô tả công việc.');

        const formData = new FormData();
        formData.append('file', resInput.files[0]);
        if(jdInput.files.length) formData.append('jd_file', jdInput.files[0]);
        if(jdVal.trim()) formData.append('jd_text', jdVal);
        formData.append('gemini_key', key);

        startBtn.disabled = true; setupLoader.classList.remove('hidden'); resultsSection.classList.add('hidden');

        try {
            const res = await fetch(`${API_BASE_URL}/api/interview/questions`, { method: 'POST', body: formData });
            const data = await res.json();
            if(data.success && data.questions && data.questions.length > 0) {
                questions = data.questions;
                resumeText = data.resume_text;
                jdText = data.jd_text;
                answers = new Array(questions.length).fill("");
                currentStep = 0;

                // Transition UI
                document.getElementById('interview-setup').classList.add('hidden');
                activeSection.classList.remove('hidden');
                renderQuestion();
            } else alert(data.error || 'Không thể tạo câu hỏi. Hãy kiểm tra nhật ký.');
        } catch(e) { alert('Lỗi API'); } finally { startBtn.disabled = false; setupLoader.classList.add('hidden'); }
    });

    function renderQuestion() {
        questionText.textContent = questions[currentStep];
        responseText.value = answers[currentStep] || "";
        stepIndicator.textContent = `Câu hỏi ${currentStep + 1} trên ${questions.length}`;
        progressFill.style.width = `${((currentStep) / questions.length) * 100}%`;
        
        prevBtn.disabled = (currentStep === 0);
        if(currentStep === questions.length - 1) {
            nextBtn.innerHTML = `Nộp bài phỏng vấn <i data-lucide="check"></i>`;
        } else {
            nextBtn.innerHTML = `Câu hỏi tiếp theo <i data-lucide="chevron-right"></i>`;
        }
        lucide.createIcons();
    }

    prevBtn.addEventListener('click', () => {
        answers[currentStep] = responseText.value;
        if(currentStep > 0) {
            currentStep--;
            renderQuestion();
        }
    });

    nextBtn.addEventListener('click', async () => {
        answers[currentStep] = responseText.value;
        if(currentStep < questions.length - 1) {
            currentStep++;
            renderQuestion();
        } else {
            // Submit
            activeSection.classList.add('hidden');
            evaluatingLoader.classList.remove('hidden');

            const key = document.getElementById('interview-gemini-key').value;
            const payload = {
                resume_text: resumeText,
                jd_text: jdText,
                questions: questions,
                answers: answers,
                gemini_key: key
            };

            try {
                const res = await fetch(`${API_BASE_URL}/api/interview/evaluate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if(data.success && data.evaluation) {
                    renderEvaluation(data.evaluation);
                } else alert(data.error || 'Không thể đánh giá phỏng vấn.');
            } catch(e) { 
                alert('Lỗi API'); 
                activeSection.classList.remove('hidden');
            } finally { 
                evaluatingLoader.classList.add('hidden'); 
            }
        }
    });

    function renderEvaluation(evaluation) {
        const score = evaluation.OverallScore || 0;
        scoreText.textContent = score;

        if (score >= 80) {
            feedbackSummary.textContent = "Hiệu suất xuất sắc! Bạn đã trả lời các câu hỏi một cách rõ ràng, áp dụng phương pháp STAR và thể hiện năng lực vững vàng.";
        } else if (score >= 60) {
            feedbackSummary.textContent = "Làm tốt lắm! Bạn đã trả lời tốt các câu hỏi, nhưng việc thêm nhiều thành tích định lượng hơn hoặc làm rõ hành động cụ thể sẽ giúp câu trả lời của bạn nổi bật hơn nữa.";
        } else {
            feedbackSummary.textContent = "Hãy tiếp tục luyện tập. Nhận xét đã chỉ ra những chi tiết quan trọng bạn bỏ sót. Vui lòng xem lại các câu trả lời gợi ý bên dưới.";
        }

        breakdownContainer.innerHTML = (evaluation.Evaluation || []).map((item, i) => `
            <div class="ats-step">
                <h4 style="font-size:1.15rem; font-weight:700; color:white; margin-bottom:0.75rem;">Câu hỏi ${i+1}: ${item.Question}</h4>
                <div class="ats-finding info" style="background: rgba(255,255,255,0.02); color: #cbd5e1;">
                    <strong>Câu trả lời của bạn:</strong> ${item.Answer || '*[Không có câu trả lời]*'}
                </div>
                <div class="ats-finding warning" style="display:flex; flex-direction:column; align-items:flex-start; gap:0.25rem; background: rgba(245, 158, 11, 0.05); border-left: 4px solid var(--warning);">
                    <strong style="color:var(--warning);">Điểm số: ${item.Score}/10</strong>
                    <div style="color:#cbd5e1; margin-top:0.25rem;">${item.Feedback}</div>
                </div>
                <div class="glass-panel" style="background: rgba(16, 185, 129, 0.03); border-color: rgba(16, 185, 129, 0.15); margin-top:1rem; padding:1.25rem;">
                    <strong style="color:var(--success); display:block; margin-bottom:0.5rem;"><i data-lucide="sparkles" style="width:16px; height:16px; vertical-align:-2px; margin-right:4px;"></i> Câu trả lời gợi ý:</strong>
                    <div style="line-height:1.5; color:#cbd5e1;">${item.ExcellentResponse}</div>
                </div>
            </div>
        `).join('');

        lucide.createIcons();
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({behavior:'smooth'});
    }

    restartBtn.addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        document.getElementById('interview-setup').classList.remove('hidden');
        setupForm.reset();
        questions = [];
        answers = [];
        currentStep = 0;
        resumeText = "";
        jdText = "";
    });
}

// --- DASHBOARD ---
function initDashboard() {
    const cards = document.querySelectorAll('.feature-nav-card');
    cards.forEach(card => {
        card.addEventListener('click', () => {
            const targetView = card.getAttribute('data-view');
            const navLink = document.querySelector(`nav a[data-target="${targetView}"]`);
            if (navLink) {
                navLink.click();
            }
        });
    });
}
