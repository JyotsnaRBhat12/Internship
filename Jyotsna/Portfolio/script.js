document.addEventListener("DOMContentLoaded", () => {
    
    const sections = document.querySelectorAll("section");
    const navLinks = document.querySelectorAll(".nav-link");

    window.addEventListener("scroll", () => {
        let current = "";

        sections.forEach((section) => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.pageYOffset >= sectionTop - 150) {
                current = section.getAttribute("id");
            }
        });

        navLinks.forEach((link) => {
            link.classList.remove("active");
            if (link.getAttribute("href").includes(current)) {
                link.classList.add("active");
            }
        });
    });

    const form = document.getElementById("contactForm");
    const emailInput = document.getElementById("email");
    const messageBox = document.getElementById("formMessage");

    if (!form) return; 

    const emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,}$/i;

    emailInput.addEventListener("input", () => {
        if (!emailInput.value.match(emailPattern)) {
            emailInput.style.borderColor = "red";
        } else {
            emailInput.style.borderColor = "#00e5ff"; 
        }
    });

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        if (!emailInput.value.match(emailPattern)) {
            messageBox.style.color = "red";
            messageBox.innerText = "Please enter a valid email address!";
            return;
        }

        // Success State
        messageBox.style.color = "#00e5ff";
        messageBox.innerText = "Message sent successfully! ";

        form.reset();
        
        emailInput.style.borderColor = ""; 
    });

});


const revealOnScroll = () => {
    const elements = document.querySelectorAll('.home-content, .project-card, .contact-wrapper');
    
    elements.forEach((el) => {
        const elementTop = el.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;
        
        if (elementTop < windowHeight - 100) {
            el.classList.add('appear');
        }
    });
};

window.addEventListener('scroll', revealOnScroll);
window.addEventListener('load', revealOnScroll);