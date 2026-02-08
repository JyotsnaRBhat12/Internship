function sanitize(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

const form = document.getElementById('feedbackForm');
if (form) {
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const ratingSelected = document.querySelector('input[name="stars"]:checked');
        const entry = {
            name: sanitize(document.getElementById('userName').value),
            email: sanitize(document.getElementById('userEmail').value),
            rating: ratingSelected ? parseInt(ratingSelected.value) : 0,
            message: sanitize(document.getElementById('userMessage').value),
            date: new Date().toLocaleString()
        };

        const list = JSON.parse(localStorage.getItem('feedbackStore')) || [];
        list.push(entry);
        localStorage.setItem('feedbackStore', JSON.stringify(list));

        const status = document.getElementById('statusMessage');
        status.textContent = "✓ Feedback saved successfully";
        status.style.display = "block";
        status.style.background = "#f0fdf4";
        status.style.color = "#166534";
        status.style.border = "1px solid #bbf7d0";

        form.reset();
        setTimeout(() => { status.style.display = "none"; }, 3000);
    });
}


const displayArea = document.getElementById('displayArea');
if (displayArea) {
    let currentPage = 1;
    const itemsPerPage = 3;

    function render() {
        const list = JSON.parse(localStorage.getItem('feedbackStore')) || [];
        displayArea.innerHTML = list.length === 0 ? "<p style='text-align:center; color:#94a3b8;'>No entries found.</p>" : "";
        
        const start = (currentPage - 1) * itemsPerPage;
        const pageData = list.slice(start, start + itemsPerPage);

        pageData.forEach(item => {
            const starString = "★".repeat(item.rating) + "☆".repeat(5 - item.rating);
            displayArea.innerHTML += `
                <div class="feedback-card">
                    <span class="name">${item.name}</span>
                    <span class="email">${item.email}</span>
                    <p class="msg">${item.message}</p>
                    <div class="card-footer">
                        <span class="stars-display">${starString}</span>
                        <span class="date">${item.date}</span>
                    </div>
                </div>`;
        });
        renderPagination(list.length);
    }

    function renderPagination(total) {
        const nav = document.getElementById('pagination');
        nav.innerHTML = "";
        const pages = Math.ceil(total / itemsPerPage);
        for (let i = 1; i <= pages; i++) {
            const btn = document.createElement('button');
            btn.innerText = i;
            btn.className = `page-btn ${i === currentPage ? 'active' : ''}`;
            btn.onclick = () => { currentPage = i; render(); };
            nav.appendChild(btn);
        }
    }

    render();

    document.getElementById('clearBtn').onclick = () => {
        if(confirm("Permanently clear all feedback data?")) {
            localStorage.removeItem('feedbackStore');
            render();
        }
    };
}