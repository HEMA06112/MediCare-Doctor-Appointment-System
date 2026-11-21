document.documentElement.classList.add('js');

const revealElements = document.querySelectorAll([
    'header',
    'body > section',
    'body > center',
    'body > fieldset',
    'body > footer',
    'section > fieldset',
    '#container > #card',
    '#field > fieldset',
    '#info > div',
    '#data > fieldset > div',
    '#detail > fieldset > div',
    '#review > div > fieldset',
    '#left > section > div',
    '#left > section > #right',
].join(','));

if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) {
    revealElements.forEach((element) => element.classList.add('is-visible'));
} else {
    const observer = new IntersectionObserver((entries, currentObserver) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                currentObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.12,
        rootMargin: '0px 0px -40px 0px',
    });

    revealElements.forEach((element, index) => {
        element.dataset.scrollReveal = '';
        element.style.setProperty('--reveal-delay', `${Math.min(index % 6, 4) * 70}ms`);
        observer.observe(element);
    });
}
