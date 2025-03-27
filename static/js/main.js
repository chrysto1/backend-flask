// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle functionality
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            document.querySelector('.main-nav ul').classList.toggle('show');
        });
    }
    
    // Dropdown menu functionality
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('mouseenter', function() {
            this.classList.add('active');
        });
        
        dropdown.addEventListener('mouseleave', function() {
            this.classList.remove('active');
        });
    });
    
    // Load more courses button
    const loadMoreBtn = document.querySelector('.load-more-btn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            // Em um site real, aqui seria feita uma requisição AJAX
            // para carregar mais cursos, mas para este exemplo,
            // vamos apenas mostrar um alerta
            alert('Carregando mais cursos...');
        });
    }
    
    // Search form submission
    const searchBtn = document.querySelector('.search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            const area = document.getElementById('area').value;
            const unidade = document.getElementById('unidade').value;
            
            if (!area && !unidade) {
                alert('Por favor, selecione pelo menos uma opção de filtro');
                return false;
            }
            
            // Em um site real, aqui seria feito o redirecionamento
            // para uma página de resultados de busca
            alert(`Buscando cursos na área: ${area || 'todas'}, unidade: ${unidade || 'todas'}`);
        });
    }
    
    // Search icon functionality
    const searchIcon = document.querySelector('.search i');
    if (searchIcon) {
        searchIcon.addEventListener('click', function() {
            // Em um site real, aqui seria mostrado um formulário de busca
            alert('Abrir formulário de busca');
        });
    }
});

// static/js/main.js

// Script para controlar os slides
let slideIndex = 5; // Começando pelo slide 5 (ativo)

function showSlide(n) {
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');
    
    // Ajuste para loop circular
    if (n > slides.length) {slideIndex = 1}
    if (n < 1) {slideIndex = slides.length}
    
    // Esconde todos os slides
    for (let i = 0; i < slides.length; i++) {
        slides[i].classList.remove('active');
    }
    
    // Remove a classe ativa de todos os pontos
    for (let i = 0; i < dots.length; i++) {
        dots[i].classList.remove('active');
    }
    
    // Mostra o slide atual e ativa o ponto correspondente
    slides[slideIndex-1].classList.add('active');
    dots[slideIndex-1].classList.add('active');
}

function currentSlide(n) {
    slideIndex = n;
    showSlide(slideIndex);
}

// Adiciona rotação automática (opcional)
setInterval(function() {
    slideIndex++;
    showSlide(slideIndex);
}, 5000);

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    showSlide(slideIndex);
});